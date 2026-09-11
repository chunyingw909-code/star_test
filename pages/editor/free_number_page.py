from pages.editor.common_style_props import CommonStyleMixin
from pages.editor.free_layout_page import FreeLayoutPage


class FreeNumberPage(CommonStyleMixin, FreeLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        # 属性面板：面板顶部是组件名的 heading（面板里已经不再出现 NumberWidget 这种类型名）
        self.prop_panel = page.get_by_role('heading', name='数值输入', exact=True)
        self.prop_label = page.get_by_label('标签', exact=True)
        self.prop_default_value = page.get_by_label('默认值', exact=True)
        self.prop_min = page.get_by_label('最小值', exact=True)
        self.prop_max = page.get_by_label('最大值', exact=True)
        self.prop_step = page.get_by_label('步长', exact=True)
        self.prop_unit = page.get_by_label('单位', exact=True)

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
