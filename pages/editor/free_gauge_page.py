import re

from common import echarts_option as eco
from pages.editor.common_style_props import CommonStyleMixin
from pages.editor.free_layout_page import FreeLayoutPage


class FreeGaugePage(CommonStyleMixin, FreeLayoutPage):
    """仪表盘组件（自由布局）。

    标题、当前值、单位、量程和阈值色段都由 ECharts gauge 绘制，
    通过 gauge_state() 读取正在渲染的明确状态。
    """

    def __init__(self, page):
        super().__init__(page)
        # 属性面板：面板顶部是组件名的 heading
        self.prop_panel = page.get_by_role('heading', name='仪表盘', exact=True)
        self.prop_title = page.get_by_label('标题', exact=True)
        self.prop_min = page.get_by_label('最小值', exact=True)
        self.prop_max = page.get_by_label('最大值', exact=True)
        self.prop_value = page.get_by_label('当前值', exact=True)
        self.prop_unit = page.get_by_label('单位', exact=True)
        self.prop_thresholds = page.get_by_label('阈值 (绝对值，警告,危险)', exact=True)
        self.prop_size = page.get_by_label('尺寸 (px)', exact=True)

        # 画布上的仪表盘
        self.widget = self.canvas_widgets().first
        # 「Range: 0–100 V● LIVE」这行文字，最小值 / 最大值 / 单位都体现在这里
        self.widget_range = self.widget.get_by_text('Range:', exact=False)
        # echarts 那块，尺寸作用在它身上
        self.widget_chart = self.widget.locator('.echarts-for-react').first

    @staticmethod
    def _gauge_state(option):
        """把 ECharts gauge option 收成测试关心的用户属性。"""
        series = eco.series_list(option)[0]
        data = eco.as_list(series.get('data'))[0]
        detail = eco.unwrap_style(series.get('detail'))
        axis_line = eco.unwrap_style(series.get('axisLine'))
        line_style = eco.unwrap_style(axis_line.get('lineStyle'))
        raw_value = data.get('value')
        return {
            'title': data.get('name'),
            'value': float(raw_value) if raw_value is not None else None,
            'range': (float(series.get('min')), float(series.get('max'))),
            'detail': detail.get('formatter'),
            'bands': [(float(stop), color)
                      for stop, color in line_style.get('color', [])],
        }

    def gauge_state(self):
        """当前仪表盘正在渲染的标题、值、量程、单位格式和阈值色段。"""
        return self._gauge_state(eco.get_option(self.widget_chart))

    def wait_gauge(self, key, expected):
        """等待某项仪表盘状态更新到 expected，并返回最新 option。"""
        return eco.wait_option(
            self.widget_chart,
            lambda option: self._gauge_state(option)[key],
            expected,
        )

    def wait_live_value(self):
        """等待真实遥测样本进入仪表盘，返回当前数值。"""
        option = eco.wait_option(
            self.widget_chart,
            lambda current: self._gauge_state(current)['value'] is not None,
            True,
        )
        return self._gauge_state(option)['value']

    def range_text(self):
        """画布 Range 那行拆成 {'min','max','unit'}。文案形如 "Range: 10–50 kW● LIVE"。"""
        raw = self.widget_range.inner_text()
        m = re.search(r'Range:\s*([\d.-]+)[–-]([\d.-]+)\s*(\S+?)●', raw)
        assert m, f'Range 文案没解析出来：{raw!r}'
        return {'min': m.group(1), 'max': m.group(2), 'unit': m.group(3)}

    def chart_size(self):
        """echarts 那块的渲染宽高，四舍五入 (w, h)。尺寸属性生效的结果。"""
        box = self.widget_chart.bounding_box()
        return (round(box['width']), round(box['height'])) if box else (0, 0)
