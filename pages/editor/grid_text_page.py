from pages.editor.grid_layout_page import GridLayoutPage


class GridTextPage(GridLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        # 属性面板
        self.prop_content = page.get_by_title('内容')
        self.prop_font_size = page.get_by_title('字号')
        self.prop_color = page.get_by_title('颜色', exact=True)
        self.prop_unit = page.get_by_title('单位')
        self.prop_weight = page.get_by_title('粗细')
        self.prop_align = page.get_by_title('对齐')