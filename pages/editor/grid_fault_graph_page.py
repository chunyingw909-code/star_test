from pages.editor.grid_layout_page import GridLayoutPage


class GridFaultGraphPage(GridLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        self.prop_col_span = page.get_by_title('跨列数')
        self.prop_fault_id = page.get_by_title('故障 ID')

    # 画布上的组件
    def widget(self, index=0):
        return self.canvas_widgets().nth(index)
