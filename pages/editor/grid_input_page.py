from pages.editor.grid_layout_page import GridLayoutPage


class GridInputPage(GridLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        # 特有属性
        self.prop_col_span = page.get_by_title('跨列数')
        self.prop_label = page.get_by_title('标签')
        self.prop_placeholder = page.get_by_title('占位提示')
        self.prop_default_value = page.get_by_title('默认值')
        self.prop_rows = page.get_by_title('行数')
        self.prop_api_url = page.get_by_title('API 地址')
        self.prop_field_name = page.get_by_title('字段名')

    # 多行 radio
    def multiline_radio(self, value):
        bool_val = 'true' if value == '是' else 'false'
        return self.page.locator(f'//input[@name="multiline" and @value=\'{{\"value\":{bool_val}}}\']')

    def multiline_label(self, value):
        return self.multiline_radio(value).locator('xpath=..')

    # 画布上的标签文字
    def widget_label_text(self, index=0):
        return self.canvas_widgets().nth(index).locator('span.MuiTypography-caption').first

    # 画布上的输入框（单行模式）
    def widget_input(self, index=0):
        return self.canvas_widgets().nth(index).locator('input.MuiInputBase-input')

    # 画布上的文本域（多行模式）
    def widget_textarea(self, index=0):
        return self.canvas_widgets().nth(index).locator('textarea:not([aria-hidden="true"])')

    # 预览态下真正渲染出来的输入框（排除顶部工具栏里的输入框）。
    # 默认值只在预览/运行时生效，要断言默认值就得进预览后看这个控件。
    def preview_input(self):
        return self.page.locator(
            'xpath=//input[not(ancestor::*[@data-testid="dashboard-toolbar"]) '
            'and (@type="text" or not(@type))]'
        )

    def preview_textarea(self):
        return self.page.locator(
            'xpath=//textarea[not(ancestor::*[@data-testid="dashboard-toolbar"]) '
            'and not(@aria-hidden="true")]'
        )