from pages.editor.editor_page import EditorPage


class TemplateDialog:
    """工具栏「模板」按钮弹出的「选择页面模板」对话框。

    内置模板 + 用户「保存当前为模板」存下的自定义模板。
    点某个模板卡片会立即：关闭弹框 + 把该模板整套组件铺到画布，
    覆盖画布上原有的一切（没有二次确认 / 覆盖警告）。再点「模板」选另一个
    → 完全替换（不叠加）。模板铺上去后，每个子组件都能正常选中并编辑。

    「保存当前为模板」走浏览器原生 prompt（message=「模板名称:」，默认「新建面板」）：
      - dismiss → 不保存
      - accept(名称) → 右下角 toast「已保存为模板"名称"」，列表多一张「自定义大屏模板」卡片
    自定义模板卡片右上角 CloseIcon 可删，走原生 confirm「确定删除此模板？」：
      - dismiss → 保留；accept → toast「模板已删除」，卡片消失。
    """

    # 模板名 -> 应用后画布上必定出现的标志文本（唯一数据源）
    TEMPLATES = {
        '综合遥测总览大屏':   '卫星星座综合遥测总览',   # 标题 p 颜色 rgb(79, 195, 247)
        '故障研判与应急面板': '实时告警与研判分析',     # 标题 p 颜色 rgb(231, 76, 60)（红）
    }

    PROMPT_MESSAGE = '模板名称:'
    PROMPT_DEFAULT = '新建面板'
    DELETE_CONFIRM_MESSAGE = '确定删除此模板？'
    CUSTOM_CAPTION = '自定义大屏模板'

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
        """某个模板的卡片（是个 button），name 传模板名（TEMPLATES 的键或自定义名）。
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

    # ==================== 保存当前为模板（原生 prompt）====================

    def click_save_current_and_cancel(self):
        """点「保存当前为模板」并在原生 prompt 点取消 —— 不保存。"""
        self.page.once('dialog', lambda d: d.dismiss())
        self.save_current_button.click()

    def click_save_current_and_confirm(self, name):
        """点「保存当前为模板」并在原生 prompt 填名称点确定。"""
        self.page.once('dialog', lambda d: d.accept(name))
        self.save_current_button.click()

    # ==================== 删除自定义模板（原生 confirm）====================

    def delete_button(self, name):
        """自定义模板卡片右上角的关闭/删除图标（内置模板没有）。"""
        # 卡片 button 的父节点是 MuiCard paper，里面并列放着 CloseIcon 按钮
        return self.card(name).locator('xpath=..').locator('[data-testid="CloseIcon"]')

    def click_delete_and_cancel(self, name):
        """点删除图标并在原生 confirm 点取消 —— 模板保留。"""
        self.page.once('dialog', lambda d: d.dismiss())
        self.delete_button(name).click()

    def click_delete_and_confirm(self, name):
        """点删除图标并在原生 confirm 点确定 —— 模板被删。"""
        self.page.once('dialog', lambda d: d.accept())
        self.delete_button(name).click()

    def toast(self, text):
        """右下角成功/提示条。模板相关 toast 挂在 role=presentation 下，
        get_by_role('alert') 偶发读不到，改用 .MuiAlert-root。"""
        return self.page.locator('.MuiAlert-root').filter(has_text=text)
