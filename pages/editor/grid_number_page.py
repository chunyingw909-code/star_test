from pages.editor.grid_layout_page import GridLayoutPage


class GridNumberPage(GridLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        # 特有属性（grid 用 title 定位）
        self.prop_col_span = page.get_by_title('跨列数')
        self.prop_label = page.get_by_title('标签')
        self.prop_default_value = page.get_by_title('默认值')
        self.prop_min = page.get_by_title('最小值')
        self.prop_max = page.get_by_title('最大值')
        self.prop_step = page.get_by_title('步长')
        self.prop_unit = page.get_by_title('单位')
        self.prop_api_url = page.get_by_title('API 地址')
        self.prop_field_name = page.get_by_title('字段名')

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
