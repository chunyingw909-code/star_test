from pages.editor.free_layout_page import FreeLayoutPage


class FreeDropdownPage(FreeLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        self.prop_panel = page.locator('.MuiBox-root', has_text='SelectWidget').last
        self.prop_label = page.get_by_label('标签')
        self.prop_options = page.get_by_label('选项 (逗号分隔)')
        self.prop_default_value = page.get_by_label('默认值')
        self.prop_api_url = page.get_by_label('API 地址')
        self.prop_field_name = page.get_by_label('字段名')

    # 画布上的标签文字
    def widget_label_text(self, index=0):
        return self.canvas_widgets().nth(index).locator('span.MuiTypography-caption').first

    # 画布上的下拉框（MUI Select combobox）
    def widget_select(self, index=0):
        return self.canvas_widgets().nth(index).locator('[role="combobox"]')
