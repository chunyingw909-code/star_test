from pages.editor.editor_page import EditorPage


class TemplateDialog:
    """工具栏「模板」按钮弹出的「选择页面模板」对话框。

    3 个内置模板。点某个模板卡片会立即：关闭弹框 + 把该模板整套组件铺到画布，
    覆盖画布上原有的一切（没有二次确认 / 覆盖警告）。再点「模板」选另一个
    → 完全替换（不叠加）。模板铺上去后，每个子组件都能正常选中并编辑。

    「模板」和 编辑/预览、分辨率、主题、新建、插件 一样是工具栏级的按钮，
    不区分自由/栅格布局，两种布局下都能打开、都能应用；应用后的内容与样式
    在两种布局下一致（只是顶层组件的包裹层级不同，别去断言顶层组件个数）。
    """

    # 模板名 -> 应用后画布上必定出现的标志文本（唯一数据源）
    TEMPLATES = {
        '综合遥测总览大屏':   '卫星星座综合遥测大屏',   # 标题 p 颜色 rgb(79, 195, 247)
        '故障研判与应急面板': '实时告警与研判分析',     # 标题 p 颜色 rgb(231, 76, 60)（红）
        '紧凑型场景配置表单': '新建数字验证仿真任务',
    }

    def __init__(self, page):
        self.page = page
        self.dialog = page.get_by_role('dialog')
        # 弹框标题文字，用于"弹框确实打开了"这类断言
        self.title = self.dialog.get_by_text('选择页面模板')
        # 底部两个动作按钮
        self.cancel_button = self.dialog.get_by_role('button', name='取消')
        # 「保存当前为模板」是另一条功能（把当前画布存成模板），不是模板选项
        self.save_current_button = self.dialog.get_by_role('button', name='保存当前为模板')

    def open(self):
        """点工具栏「模板」按钮打开弹框，等它可见。返回 self，方便链式。"""
        EditorPage(self.page).template_button.click()
        self.dialog.wait_for(state='visible')
        return self

    def card(self, name):
        """某个模板的卡片（是个 button），name 传模板名（TEMPLATES 的键）。
        卡片的无障碍名是「模板名 + 说明」，按模板名子串匹配即可。
        """
        return self.dialog.get_by_role('button', name=name)

    def cancel(self):
        """点「取消」关闭弹框，画布保持不变。"""
        self.cancel_button.click()
        self.dialog.wait_for(state='hidden')

    def apply(self, name):
        """选中并应用某个模板：点卡片 → 弹框自动关闭 → 模板已铺到画布。
        随后用例按 marker(name) 的标志文本断言画布内容。
        """
        self.card(name).click()
        self.dialog.wait_for(state='hidden')

    def marker(self, name):
        """该模板应用后画布上必定出现的标志文本。"""
        return self.TEMPLATES[name]
