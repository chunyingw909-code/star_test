from pages.editor.common_style_props import CommonStyleMixin
from pages.editor.free_layout_page import FreeLayoutPage


class FreeInputPage(CommonStyleMixin, FreeLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        # 属性面板：面板顶部是组件名的 heading（面板里已经不再出现 InputWidget 这种类型名）
        self.prop_panel = page.get_by_role('heading', name='输入框', exact=True)
        self.prop_label = page.get_by_label('标签')
        self.prop_placeholder = page.get_by_label('占位提示')
        self.prop_default_value = page.get_by_label('默认值')
        self.prop_rows = page.get_by_label('行数', exact=True)

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

    # 预览态下真正渲染出来的输入框（排除顶部工具栏里的输入框）。
    # 默认值只在预览/运行时生效，要断言默认值就得进预览后看这个控件。
    def preview_input(self):
        # 预览态没有 .react-grid-item 外壳，按本组件的 placeholder 收窄，
        # 别命中遥测侧栏等页面上其它文本框
        return self.page.get_by_placeholder('请输入...')

    def preview_textarea(self):
        return self.page.locator(
            'xpath=//textarea[not(ancestor::*[@data-testid="dashboard-toolbar"]) '
            'and not(@aria-hidden="true")]'
        )