from pages.editor.grid_layout_page import GridLayoutPage


class GridSpacerPage(GridLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        self.prop_col_span = page.get_by_title('跨列数')
        self.prop_columns = page.get_by_title('占位列数')
        # 面板里有两个 "高度 (px)"：占位组件自己的 height 在前，通用布局的 _h 在后
        self.prop_height = page.get_by_title('高度 (px)').first

    # 画布组件里第一个 div，高度跟着"高度 (px)"走
    def widget_inner(self, index=0):
        return self.canvas_widgets().nth(index).locator('div').first
