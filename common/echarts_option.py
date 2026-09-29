"""从 echarts-for-react 组件里把正在画的 option 读出来。

页面没把 `window.echarts` 挂到全局，`getInstanceByDom` 用不了。
echarts-for-react 的 React 实例上有 `getEchartsInstance()`，沿 DOM 往上
走到 `.echarts-for-react`，顺着 fiber 就能拿到当前 option。

这不是读属性面板的 HTML，是读图表真正在画的那份配置：系列类型、图例位置、
阈值线、绑上去的字段名和数据点。像素指纹只能看出「变了」，看不出「变成了什么」。
"""
import time


_READ_OPTION_JS = """
el => {
  const findFiber = (node) => {
    const key = Object.keys(node).find(k =>
      k.startsWith('__reactFiber') || k.startsWith('__reactInternalInstance'));
    return key ? node[key] : null;
  };
  let node = el;
  while (node) {
    let fiber = findFiber(node);
    for (let i = 0; i < 40 && fiber; i++) {
      const inst = fiber.stateNode;
      if (inst && typeof inst.getEchartsInstance === 'function') {
        const chart = inst.getEchartsInstance();
        if (chart && typeof chart.getOption === 'function') {
          return JSON.parse(JSON.stringify(chart.getOption()));
        }
      }
      fiber = fiber.return;
    }
    node = node.parentElement;
  }
  return null;
}
"""


_DATA_POINT_JS = """
(el, args) => {
  const findFiber = (node) => {
    const key = Object.keys(node).find(k =>
      k.startsWith('__reactFiber') || k.startsWith('__reactInternalInstance'));
    return key ? node[key] : null;
  };
  let node = el;
  while (node) {
    let fiber = findFiber(node);
    for (let i = 0; i < 40 && fiber; i++) {
      const inst = fiber.stateNode;
      if (inst && typeof inst.getEchartsInstance === 'function') {
        const chart = inst.getEchartsInstance();
        const option = chart.getOption();
        const series = option.series[args.seriesIndex];
        const dataIndex = args.dataIndex === null
          ? Math.floor(series.data.length / 2)
          : args.dataIndex;
        const raw = series.data[dataIndex];
        const value = Array.isArray(raw) ? raw[1]
          : (typeof raw === 'number' ? raw : raw.value);
        const y = Array.isArray(value) ? value[value.length - 1] : value;
        const x = option.xAxis[0].data[dataIndex];
        const point = chart.convertToPixel({seriesIndex: args.seriesIndex}, [x, y]);
        return {x: point[0], y: point[1], dataIndex, xValue: x};
      }
      fiber = fiber.return;
    }
    node = node.parentElement;
  }
  return null;
}
"""


def as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def first_dict(value):
    for item in as_list(value):
        if isinstance(item, dict):
            return item
    return {}


def unwrap_style(value):
    """echarts getOption 里 lineStyle / areaStyle / textStyle 经常是对象或单元素数组。"""
    if isinstance(value, list):
        return value[0] if value and isinstance(value[0], dict) else {}
    return value if isinstance(value, dict) else {}


def get_option(locator):
    """locator 可以是 canvas，也可以是图表组件里任意子孙。读不到返回 None。"""
    return locator.evaluate(_READ_OPTION_JS)


def wait_option(locator, getter, expected, timeout_ms=8000, settle_ms=150):
    """等到 getter(option) == expected。换类型 / 换主题有入场动画，不能读一次就算。"""
    deadline = time.time() + timeout_ms / 1000
    last = None
    while time.time() < deadline:
        opt = get_option(locator)
        last = getter(opt) if opt else None
        if last == expected:
            return opt
        locator.page.wait_for_timeout(settle_ms)
    raise AssertionError(
        f'图表 option 等到超时（{timeout_ms}ms）：期望 {expected!r}，实际 {last!r}')


def data_point_position(locator, series_index=0, data_index=None):
    """返回某个真实数据点在图表内的像素坐标，供 Playwright 做真实鼠标悬停。"""
    return locator.evaluate(_DATA_POINT_JS, {
        'seriesIndex': series_index,
        'dataIndex': data_index,
    })


def series_list(opt):
    return [s for s in as_list((opt or {}).get('series')) if isinstance(s, dict)]


def series_types(opt):
    return [s.get('type') for s in series_list(opt)]


def series_names(opt):
    return [s.get('name') for s in series_list(opt)]


def series_data(opt, name=None):
    """某个系列的 data 数组。name 为空就取第一条。"""
    for s in series_list(opt):
        if name is None or s.get('name') == name:
            return as_list(s.get('data'))
    return []


def legend(opt):
    return first_dict((opt or {}).get('legend'))


def tooltip(opt):
    return first_dict((opt or {}).get('tooltip'))


def xaxis(opt):
    return first_dict((opt or {}).get('xAxis'))


def line_widths(opt):
    widths = []
    for s in series_list(opt):
        style = unwrap_style(s.get('lineStyle'))
        width = style.get('width')
        if isinstance(width, list):
            width = width[0] if width else None
        if width is not None:
            widths.append(float(width))
    return widths


def area_opacities(opt):
    opacities = []
    for s in series_list(opt):
        style = unwrap_style(s.get('areaStyle'))
        opacity = style.get('opacity')
        if isinstance(opacity, list):
            opacity = opacity[0] if opacity else None
        if opacity is not None:
            opacities.append(float(opacity))
    return opacities


def mark_line_y_values(opt):
    """所有系列 markLine 上的 yAxis 阈值。"""
    values = []
    for s in series_list(opt):
        mark = s.get('markLine') or {}
        if isinstance(mark, list):
            mark = mark[0] if mark else {}
        for item in as_list(mark.get('data')):
            if isinstance(item, dict) and 'yAxis' in item:
                values.append(float(item['yAxis']))
            elif isinstance(item, list):
                for part in item:
                    if isinstance(part, dict) and 'yAxis' in part:
                        values.append(float(part['yAxis']))
    return values


def data_zoom_visible(opt):
    zooms = [z for z in as_list((opt or {}).get('dataZoom')) if isinstance(z, dict)]
    if not zooms:
        return False
    return any(z.get('show', True) and z.get('type') in (None, 'slider', 'inside') for z in zooms)


def legend_side(opt):
    """把 echarts legend 的 top/bottom/left/orient 收成『顶部 / 底部 / 左侧』。"""
    box = legend(opt)
    orient = box.get('orient')
    left = box.get('left')
    top = box.get('top')
    bottom = box.get('bottom')
    if orient == 'vertical' or left in (0, '0', 'left'):
        return '左侧'
    if top in (0, '0', 'top') or (bottom in (None, 'auto') and top not in (None, 'auto')):
        return '顶部'
    return '底部'


def numeric_points(data):
    """把系列 data 收成纯数字列表（pie 的 {name,value} / 折线的裸数字都认）。"""
    out = []
    for item in as_list(data):
        if isinstance(item, (int, float)):
            out.append(float(item))
        elif isinstance(item, list) and len(item) >= 2 and isinstance(item[1], (int, float)):
            out.append(float(item[1]))
        elif isinstance(item, dict) and isinstance(item.get('value'), (int, float)):
            out.append(float(item['value']))
    return out
