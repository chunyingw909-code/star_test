from pages.editor.editor_page import EditorPage
from pages.editor.widget_catalog import WIDGETS, TYPES


class PluginManager:
    """工具栏「插件」按钮弹出的 Plugin Manager 对话框的页面对象。

    这个弹框是一张表格，12 行对应 12 个内置组件，每行一个开关。
    关掉某个组件的开关 = 停用该组件插件：该组件从「添加组件」菜单移除；画布上
    已放置的同类型组件出现「组件已禁用」徽标，点它右侧属性面板变成锁定提示，
    禁止编辑。
    开关状态会写回后端并持久化，所以任何用到本对象的 fixture，teardown 必须
    调用 enable_all() 把 12 个开关全部恢复成启用，否则污染后续用例。
    """

    # 表格应有的 12 行（label / type / category 的唯一数据源在 widget_catalog）
    WIDGETS = WIDGETS          # [{'label': '文本', 'type': 'TextWidget', 'category': '文本'}, ...]
    TYPES = TYPES             # ['TextWidget', 'ContainerWidget', ...]

    def __init__(self, page):
        self.page = page
        # 弹框根节点。open() 之后才可见；很多断言直接对它做 to_contain_text
        self.dialog = page.get_by_role('dialog')
        # 右下角关闭按钮（文案就是大写 CLOSE）
        self.close_button = self.dialog.get_by_role('button', name='CLOSE')
        # 弹框标题文字，用于「弹框确实打开了」这类断言
        self.title = self.dialog.get_by_text('Plugin Manager')
        # "N / 12 enabled" 那行计数文字。切换开关后对它断言最直观
        self.enabled_count = self.dialog.get_by_text('enabled').first
        # 标题下方的说明文字（"...hidden from the component library..."）
        self.description = self.dialog.get_by_text('hidden from the component library')

    # ---------- 开关弹框 ----------

    def open(self):
        """点工具栏「插件」按钮打开弹框，等它可见。返回 self，方便链式：
        pm = PluginManager(page).open()
        """
        EditorPage(self.page).plugin_button.click()
        self.dialog.wait_for(state='visible')
        return self

    def close(self):
        """点 CLOSE 关闭弹框，并等它消失。"""
        self.close_button.click()
        self.dialog.wait_for(state='hidden')

    def is_open(self):
        """弹框当前是否可见。teardown 里先判断，避免在已关闭的弹框上重复点 CLOSE。"""
        return self.dialog.is_visible()

    # ---------- 定位行与开关 ----------

    def rows(self):
        """表格 body 的所有行。用于断言行数 == 12。"""
        return self.dialog.locator('tbody tr')

    def row(self, widget_type):
        """按 Type 列文字（如 'ChartWidget'）定位某一行。
        Type 是唯一的，比中文显示名更稳（显示名可能和别处文字撞）。
        """
        return self.dialog.locator('tbody tr', has_text=widget_type)

    def checkbox(self, widget_type):
        """某一行里的开关（checkbox）。断言启用状态或直接点它用。"""
        return self.row(widget_type).locator('input[type="checkbox"]')

    def is_enabled(self, widget_type):
        """该组件插件当前是否启用（开关是否勾选）。"""
        return self.checkbox(widget_type).is_checked()

    def toggle(self, widget_type):
        """无脑翻转某个开关（不管当前状态）。少用，一般用 set_enabled 更明确。"""
        self.checkbox(widget_type).click()
        self.page.wait_for_timeout(300)

    def set_enabled(self, widget_type, enabled):
        """把某个组件的开关设成指定状态（幂等：已经是目标状态就不动）。
        用例里"关掉图表"写成 pm.set_enabled('ChartWidget', False)。
        """
        cb = self.checkbox(widget_type)
        if cb.is_checked() != enabled:
            cb.click()
            self.page.wait_for_timeout(300)

    # ---------- 读表格内容 ----------

    def row_types(self):
        """把表格里实际渲染的 Type 列（每行第 2 个单元格）读成字符串列表。
        用于「表格里的组件集合和组件清单完全一致」这种整体比对。
        """
        return self.dialog.locator('tbody tr td:nth-child(2)').all_inner_texts()

    # ---------- 复位 ----------

    def enable_all(self):
        """把 12 个开关全部恢复成启用。禁用状态会持久化到后端，
        每个用到 PluginManager 的 fixture 的 teardown 都必须调这个，否则串味。
        """
        for cb in self.dialog.locator('tbody tr input[type="checkbox"]').all():
            if not cb.is_checked():
                cb.click()
                self.page.wait_for_timeout(150)
