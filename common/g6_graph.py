"""从故障关系图的 AntV G6 实例里读正在画的样式。

节点和连线画在多层 canvas 上，DOM 里没有「高亮」这个 class。
页面也没把 graph 挂到 window。组件 props 上有 nodes/edges，实例放在
useRef 里，沿 React fiber 能拿到 getElementRenderStyle。

这读的是渲染器当前帧的样式，不是数据模型里那份。
命中的点会画成白色描边、线宽 2。模型里还给没命中的点写了 opacity 0.2，
但节点画布像素仍是原来的实色，所以不用透明度判断高亮。
描边从原色过渡到白色有动画，要等到这一帧真的落到目标值。
"""
import re
import time


_READ_JS = r"""
el => {
  const fiberKey = (node) => Object.keys(node).find(k =>
    k.startsWith('__reactFiber') || k.startsWith('__reactInternalInstance'));
  const findGraph = (start) => {
    let node = start;
    while (node) {
      const key = fiberKey(node);
      let fiber = key ? node[key] : null;
      for (let i = 0; fiber && i < 50; i++) {
        const props = fiber.memoizedProps;
        if (props && Array.isArray(props.nodes) && Array.isArray(props.edges)) {
          let cursor = fiber.memoizedState;
          for (let s = 0; cursor && s < 12; s++) {
            const ref = cursor.memoizedState;
            const graph = ref && ref.current;
            if (graph && typeof graph.getNodeData === 'function'
                && typeof graph.getElementRenderStyle === 'function') {
              return graph;
            }
            cursor = cursor.next;
          }
        }
        fiber = fiber.return;
      }
      node = node.parentElement;
    }
    return null;
  };
  const graph = findGraph(el);
  if (!graph) return null;
  const paint = (id) => {
    const style = graph.getElementRenderStyle(id) || {};
    const stroke = style.stroke == null ? '' : String(style.stroke);
    return {
      stroke,
      lineWidth: style.lineWidth == null ? 0 : style.lineWidth,
    };
  };
  const nodes = graph.getNodeData().map(n => {
    const pos = graph.getElementPosition(n.id);
    const bounds = graph.getElementRenderBounds(n.id);
    const client = graph.getClientByCanvas(pos);
    const center = bounds && bounds.center ? bounds.center : pos;
    return {
      id: n.id,
      label: (n.data && n.data.label) || '',
      nodeType: (n.data && n.data.nodeType) || '',
      style: paint(n.id),
      center: [center[0], center[1]],
      client: [client[0], client[1]],
    };
  });
  const edges = graph.getEdgeData().map(e => ({
    id: String(e.id),
    source: e.source,
    target: e.target,
    style: paint(e.id),
  }));
  const view = graph.getViewportCenter();
  return {nodes, edges, center: [view[0], view[1]]};
}
"""


def read_graph(locator):
    """locator 是关系图里任意一层 canvas。还没渲染完返回 None。"""
    return locator.evaluate(_READ_JS)


def wait_graph(locator, timeout_ms=8000, settle_ms=150):
    """等到 G6 已经画出至少一个节点。"""
    deadline = time.time() + timeout_ms / 1000
    last = None
    while time.time() < deadline:
        last = read_graph(locator)
        if last and last.get('nodes'):
            return last
        locator.page.wait_for_timeout(settle_ms)
    raise AssertionError(f'关系图没有画出来：{last!r}')


def _rgb(value):
    if not isinstance(value, str):
        return None
    text = value.strip().lower()
    if text in ('#fff', '#ffffff', 'white'):
        return (255, 255, 255)
    matched = re.fullmatch(r'#([0-9a-f]{6})', text)
    if matched:
        hex_color = matched.group(1)
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    matched = re.fullmatch(r'#([0-9a-f]{3})', text)
    if matched:
        return tuple(int(ch * 2, 16) for ch in matched.group(1))
    matched = re.fullmatch(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', text)
    if matched:
        return tuple(int(part) for part in matched.groups())
    return None


def is_white(stroke):
    rgb = _rgb(stroke)
    return rgb is not None and all(channel >= 250 for channel in rgb)


def is_lit(style):
    """命中态：白色描边、线宽加粗。动画没走完时这两项都还没到位。"""
    return float(style['lineWidth']) >= 1.5 and is_white(style['stroke'])


def is_plain(style):
    """没被点亮：保持自己的颜色，描边不加粗。"""
    return float(style['lineWidth']) <= 1.2 and not is_white(style['stroke'])


def is_restored(style):
    """取消高亮后描边回到原色，线宽也不再加粗。"""
    return is_plain(style)


def incident(snap, node_id):
    """点一个节点时会被一起点亮的节点和边：它自己，加上直接相连的邻居。"""
    nodes = {node_id}
    edges = set()
    for edge in snap['edges']:
        if edge['source'] == node_id or edge['target'] == node_id:
            edges.add(edge['id'])
            nodes.add(edge['source'])
            nodes.add(edge['target'])
    return nodes, edges


def search_hits(snap, keyword):
    """搜索框回车的命中规则：标签或 id 包含关键字（忽略大小写）。"""
    needle = keyword.lower()
    matched = [
        node for node in snap['nodes']
        if needle in node['label'].lower() or needle in node['id'].lower()
    ]
    ids = {node['id'] for node in matched}
    edges = {
        edge['id'] for edge in snap['edges']
        if edge['source'] in ids or edge['target'] in ids
    }
    return matched, ids, edges


def _problems(snap, lit_nodes, lit_edges, focus_id=None):
    problems = []
    for node in snap['nodes']:
        lit = node['id'] in lit_nodes
        ok = is_lit(node['style']) if lit else is_plain(node['style'])
        if not ok:
            state = '应是白色加粗描边' if lit else '不应是白色加粗描边'
            problems.append(f"节点「{node['label']}」{state}，实际 {node['style']}")
    for edge in snap['edges']:
        lit = edge['id'] in lit_edges
        ok = is_lit(edge['style']) if lit else is_plain(edge['style'])
        if not ok:
            state = '应是白色加粗描边' if lit else '不应是白色加粗描边'
            problems.append(f"连线 {edge['source']}→{edge['target']} {state}，实际 {edge['style']}")
    if focus_id is not None:
        node = next((item for item in snap['nodes'] if item['id'] == focus_id), None)
        if node is None:
            problems.append(f'找不到要居中的节点 {focus_id}')
        else:
            cx, cy = snap['center']
            nx, ny = node['center']
            if abs(cx - nx) > 8 or abs(cy - ny) > 8:
                problems.append(
                    f"视口中心 {snap['center']} 没有落到「{node['label']}」{node['center']}")
    return problems


def wait_paint(locator, lit_nodes, lit_edges, focus_id=None, timeout_ms=5000, settle_ms=150):
    """等到这一帧的高亮 / 压暗（以及可选的居中）都落到目标值。"""
    deadline = time.time() + timeout_ms / 1000
    last = None
    problems = ['关系图还没读到']
    while time.time() < deadline:
        last = read_graph(locator)
        if not last or not last.get('nodes'):
            locator.page.wait_for_timeout(settle_ms)
            continue
        problems = _problems(last, lit_nodes, lit_edges, focus_id)
        if not problems:
            return last
        locator.page.wait_for_timeout(settle_ms)
    raise AssertionError('关系图高亮没有画到预期：\n- ' + '\n- '.join(problems))


def wait_restored(locator, timeout_ms=5000, settle_ms=150):
    """等到点空白取消选中后，节点和连线都回到原色。"""
    deadline = time.time() + timeout_ms / 1000
    problems = ['关系图还没读到']
    while time.time() < deadline:
        snap = read_graph(locator)
        if not snap or not snap.get('nodes'):
            locator.page.wait_for_timeout(settle_ms)
            continue
        problems = []
        for node in snap['nodes']:
            if not is_restored(node['style']):
                problems.append(f"节点「{node['label']}」还没恢复，实际 {node['style']}")
        for edge in snap['edges']:
            if not is_restored(edge['style']):
                problems.append(
                    f"连线 {edge['source']}→{edge['target']} 还没恢复，实际 {edge['style']}")
        if not problems:
            return snap
        locator.page.wait_for_timeout(settle_ms)
    raise AssertionError('取消高亮后样式没有恢复：\n- ' + '\n- '.join(problems))
