from pages.editor.editor_page import EditorPage


class FlowEditor:
    """工具栏「流程」弹出的「可视化流程编排」浮层（基于 React Flow 的节点图）。

    用途：给大屏配「事件 → (条件) → 动作」的交互链路。竖向流程，节点
    顶部圆点是入口(target)、底部圆点是出口(source)。

    现状：能拖/加/连节点、能「保存并关闭」，但**点节点弹不出配置面板**
    （单击/双击/右键都没反应）—— 节点无法绑定具体组件/参数，功能未完成。
    """

    # 左侧面板的节点类型
    NODE_TYPES = {
        '事件': ['Click', 'DblClick', 'Hover', 'Threshold', 'Timer'],
        '条件': ['GT', 'LT', 'EQ'],
        '动作': ['Alert', 'Navigate', 'Refresh', 'Modal', 'Linkage'],
    }

    def __init__(self, page):
        self.page = page
        self.flow = page.locator('.react-flow')
        self.title = page.get_by_text('可视化流程编排')
        self.save_close_button = page.get_by_role('button', name='保存并关闭')

    def open(self):
        EditorPage(self.page).flow_button.click()
        self.flow.wait_for(state='visible')
        return self

    def palette_item(self, label):
        return self.page.get_by_text(label, exact=True)

    def nodes(self):
        return self.page.locator('.react-flow__node')

    def edges(self):
        return self.page.locator('.react-flow__edge')

    def add_node(self, label):
        """点左侧节点类型 → 画布多一个节点。"""
        n0 = self.nodes().count()
        self.palette_item(label).first.click()
        self.nodes().nth(n0).wait_for(state='visible')

    def connect(self, from_idx, to_idx):
        """从 from 节点底部圆点拖到 to 节点顶部圆点。"""
        src = self.nodes().nth(from_idx).locator(
            '.react-flow__handle-bottom, .react-flow__handle.source').first
        tgt = self.nodes().nth(to_idx).locator(
            '.react-flow__handle-top, .react-flow__handle.target').first
        sb, tb = src.bounding_box(), tgt.bounding_box()
        self.page.mouse.move(sb['x'] + sb['width'] / 2, sb['y'] + sb['height'] / 2)
        self.page.mouse.down()
        self.page.mouse.move(tb['x'] + tb['width'] / 2, tb['y'] + tb['height'] / 2, steps=20)
        self.page.mouse.up()
        self.page.wait_for_timeout(400)

    def save_and_close(self):
        self.save_close_button.click()
        self.flow.wait_for(state='hidden')
