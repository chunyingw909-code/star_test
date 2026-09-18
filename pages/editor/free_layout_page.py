from pages.editor.widget_catalog import ACTIVE_LABELS
from pages.editor.json_view_mixin import JsonViewMixin
from pages.editor.editor_page import EditorPage


class FreeLayoutPage(JsonViewMixin):
    COMPONENT_NAMES = ACTIVE_LABELS

    # 组件对应插件被关闭后的锁定态文案（属性面板里显示）
    DISABLED_NOTICE = '该组件已禁用（对应插件已关闭），禁止编辑。重新启用插件后恢复。'

    def __init__(self, page):
        self.page = page
        # 工具栏级的东西（编辑/预览、分辨率、主题、模板、插件、新建、发布、
        # 布局名称、版本管理 tab）统一走这个，用例里不用再自己 new 一遍
        self.editor = EditorPage(page)
        # —— 自由布局子工具栏（画布上方那一条：GridStack 说明 · 保存 · 添加组件；
        #    以及 UI可视 / <>JSON 视图切换）——
        # 这两个按钮的无障碍名算不准（"<>JSON" 里的 <> 会坏事），一律按文字匹配
        self.ui_visual_button = page.locator('button', has_text='UI可视')
        self.json_button = page.locator('button', has_text='<>JSON')
        self.add_component_button = page.get_by_role('button', name='添加组件')
        # 布局「保存」按钮（exact 排除工具栏的"保存快照""发布"）
        self.save_button = page.get_by_role('button', name='保存', exact=True)
        # <>JSON 模式下的 JSON 编辑区
        self.json_editor = page.locator('textarea')
        # "自由布局（GridStack）· 12 列 / 行高 40px / 间距 8px" 这行说明，随 root 配置变化
        self.gridstack_caption = page.locator('span.MuiTypography-caption', has_text='GridStack')
        # 添加组件菜单
        self.menu = page.get_by_role('menu')
        # 画布
        self.canvas = page.locator('.react-grid-layout')

    # 根据名字获取添加组件菜单中的某一项
    def component_item(self, name):
        return self.page.get_by_role('menuitem', name=name)

    # 添加组件菜单里所有项的显示名（每项文本是「显示名\n分类」，取第一行）
    def add_menu_labels(self):
        return [t.splitlines()[0].strip()
                for t in self.menu.get_by_role('menuitem').all_inner_texts()]

    def close_add_menu(self):
        self.page.keyboard.press('Escape')

    # —— 组件对应插件被关闭后的锁定态 ——
    @property
    def disabled_panel_notice(self):
        return self.page.get_by_text(self.DISABLED_NOTICE)

    def widget_disabled_badge(self, index=0):
        return self.canvas_widgets().nth(index).get_by_text('组件已禁用', exact=True)

    # 获取画布上所有组件
    def canvas_widgets(self):
        return self.canvas.locator('.react-grid-item')

    # 点击画布上第index个组件，点了右侧才出属性面板
    def click_widget(self, index=0):
        self.canvas_widgets().nth(index).click()

    # 先hover让删除按钮出现，再点击删除
    def delete_widget(self, index=0):
        widget = self.canvas_widgets().nth(index)
        widget.hover()
        widget.get_by_test_id('CloseIcon').click()

    # ==================== 颜色控件 ====================
    # 面板里每个颜色属性都是一对：左边一个色块，右边一个十六进制文本框。
    # 色块是浏览器原生的 <input type="color">（title="打开调色盘"），点它弹出的
    # 是浏览器自带的调色盘 —— 那个调色盘不在页面 DOM 里，自动化点不进去。
    # 但可以直接给色块 fill() 一个颜色，效果等同于「用户在调色盘里选完了」，
    # 应用照样能收到，用这个来覆盖「通过色块改色」这条链路。

    def pick_option(self, combobox, name):
        """点开一个 MUI 下拉框并选中某一项（选项是 role=option，不是原生 select）。"""
        combobox.click()
        self.page.get_by_role('option', name=name, exact=True).click()
        self.page.wait_for_timeout(400)

    def color_swatch(self, label):
        """跟某个颜色文本框（如 '颜色' / '正常颜色'）配对的那个色块。"""
        return (self.page.locator('div:has(> input[type="color"])')
                .filter(has=self.page.get_by_label(label, exact=True))
                .locator('input[type="color"]').first)

    # 点击画布空白处，取消选中组件
    def click_canvas_blank(self):
        self.canvas.click(position={'x': 1, 'y': 1})

    # ==================== 保存 ====================

    def save_layout(self, name):
        """填「布局名称」（主工具栏那个输入框）+ 点保存。
        用例随后按提示 toast（"保存成功" / "请输入布局名称"）断言。"""
        from pages.editor.editor_page import EditorPage
        EditorPage(self.page).layout_name_input.fill(name)
        self.save_button.first.click()
