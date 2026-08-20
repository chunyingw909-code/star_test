from pages.free_layout_page import FreeLayoutPage


class FreeTextPage(FreeLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        # 右侧属性面板
        self.prop_panel = page.locator('.css-1qupz7j')
        self.prop_content = page.get_by_label('内容')
        self.prop_font_size = page.get_by_label('字号')
        self.prop_color = page.get_by_label('颜色', exact=True)
        self.prop_weight = page.get_by_label('粗细')
        self.prop_unit = page.get_by_label('单位')
        self.prop_align = page.locator('.MuiFormControl-root', has_text='对齐').get_by_role('combobox')
        self.prop_weight = page.locator('.MuiFormControl-root', has_text='粗细').get_by_role('combobox')
