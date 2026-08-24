from pages.editor.free_layout_page import FreeLayoutPage


class FreeInputPage(FreeLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        self.prop_panel = page.locator('.MuiBox-root', has_text='InputWidget').first
        self.prop_label = page.get_by_label('标签')
        self.prop_placeholder = page.get_by_label('占位提示')
        self.prop_default_value = page.get_by_label('默认值')
        self.prop_rows = page.get_by_label('行数')
        self.prop_api_url = page.get_by_label('API 地址')
        self.prop_field_name = page.get_by_label('字段名')

    # 多行 单选
    def multiline_radio(self, value):
        return self.page.locator('.MuiBox-root.css-0', has_text='多行').get_by_label(value)

    # 画布上的标签文字
    def widget_label_text(self, index=0):
        return self.canvas_widgets().nth(index).locator('span.MuiTypography-caption').first

    # 画布上的输入框（单行模式）
    def widget_input(self, index=0):
        return self.canvas_widgets().nth(index).locator('input.MuiInputBase-input')

    # 画布上的文本域（多行模式）
    def widget_textarea(self, index=0):
        return self.canvas_widgets().nth(index).locator('textarea:not([aria-hidden="true"])')