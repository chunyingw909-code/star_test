from pages.editor.free_layout_page import FreeLayoutPage


class FreeNumberPage(FreeLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        self.prop_panel = page.locator('.MuiBox-root', has_text='NumberWidget').last
        self.prop_label = page.get_by_label('标签', exact=True)
        self.prop_default_value = page.get_by_label('默认值', exact=True)
        self.prop_min = page.get_by_label('最小值', exact=True)
        self.prop_max = page.get_by_label('最大值', exact=True)
        self.prop_step = page.get_by_label('步长', exact=True)
        self.prop_unit = page.get_by_label('单位', exact=True)
        self.prop_api_url = page.get_by_label('API 地址', exact=True)
        self.prop_field_name = page.get_by_label('字段名', exact=True)

    # 画布上的标签文字
    def widget_label_text(self, index=0):
        return self.canvas_widgets().nth(index).locator('span.MuiTypography-caption').first

    # 画布上的数值输入框（min / max / step 属性会跟着右侧改）
    def widget_input(self, index=0):
        return self.canvas_widgets().nth(index).locator('input[type="number"]')

    # 预览态下真正渲染出来的数值框（工具栏那个 number 输入带 placeholder="自定义"，排除掉）
    def preview_input(self):
        return self.page.locator(
            'xpath=//input[@type="number" '
            'and not(ancestor::*[@data-testid="dashboard-toolbar"]) '
            'and not(@placeholder)]'
        )
