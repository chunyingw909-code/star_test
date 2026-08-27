from pages.editor.grid_layout_page import GridLayoutPage


class GridDropdownPage(GridLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        self.prop_col_span = page.get_by_title('跨列数')
        self.prop_label = page.get_by_title('标签')
        self.prop_options = page.get_by_title('选项 (逗号分隔)')
        self.prop_default_value = page.get_by_title('默认值')
        self.prop_api_url = page.get_by_title('API 地址')
        self.prop_field_name = page.get_by_title('字段名')

    # 画布上的标签文字
    def widget_label_text(self, index=0):
        return self.canvas_widgets().nth(index).locator('span.MuiTypography-caption').first
