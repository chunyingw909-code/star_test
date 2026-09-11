from pages.editor.common_style_props import CommonStyleMixin
from pages.editor.free_layout_page import FreeLayoutPage


class FreeFaultGraphPage(CommonStyleMixin, FreeLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        # 属性面板：面板顶部是组件名的 heading（面板里已经不再出现 FaultGraphWidget 这种类型名）
        self.prop_panel = page.get_by_role('heading', name='故障关系图', exact=True)
        self.prop_fault_id = page.get_by_label('故障 ID', exact=True)

    # 画布上的组件
    def widget(self, index=0):
        return self.canvas_widgets().nth(index)
