# 页面编辑器
class EditorPage:
    # 两种布局的画布根元素
    CANVAS_FREE = '.react-grid-layout'
    CANVAS_GRID = '[data-testid="dropzone:root:default-zone"]'
    # 「大小屏切换」三档对应的画布固定宽度（与视口无关）
    RESOLUTIONS = {'fullhd': 1920, 'hd': 1366, 'tablet': 1024}
    # 「新建」按钮触发的浏览器原生 confirm 的文案
    NEW_CONFIRM_MESSAGE = '新建项目将清除当前编辑内容，是否继续？'

    def __init__(self, page):
        self.page = page

        # 顶部导航（不在工具栏里）：进入界面编辑器
        self.editor_button = page.get_by_role('button', name='界面编辑器')

        # ==================== 工具栏 dashboard-toolbar ====================
        # 一整条，从左到右一字排开，彼此同级、跟当前是自由还是栅格布局无关：
        #   布局名称输入 | 编辑·预览 | 自由·栅格 | 分辨率三档 | 主题 | 模板·插件·流程·新建·发布
        self.toolbar = page.get_by_test_id('dashboard-toolbar')

        # 布局名称输入框
        self.layout_name_input = self.toolbar.get_by_label('布局名称')

        # 编辑 / 预览（ToggleButtonGroup；DOM value=edit/preview，aria-pressed 标记当前档）
        # exact 限定：画布上文字含"编辑""预览"的组件不会被误匹配
        self.edit_button = self.toolbar.get_by_role('button', name='编辑', exact=True)
        self.preview_button = self.toolbar.get_by_role('button', name='预览', exact=True)

        # 自由布局 / 栅格布局（ToggleButtonGroup；注意 DOM 里 value 是 grid / puck，反直觉）
        self.free_layout_button = self.toolbar.get_by_role('button', name='自由布局')
        self.grid_layout_button = self.toolbar.get_by_role('button', name='栅格布局')

        # 屏幕大小三档（data-testid 唯一；aria-label 里带 "1920×1080 (大屏)" 等）
        self.fullhd_button = page.get_by_test_id('resolution-fullhd')
        self.hd_button = page.get_by_test_id('resolution-hd')
        self.tablet_button = page.get_by_test_id('resolution-tablet')

        # 主题切换（图标按钮；title 在 "切换至浅色主题"/"切换至深色主题" 之间翻）
        self.theme_toggle = page.get_by_test_id('dashboard-theme-toggle')

        # 右侧动作按钮组
        self.template_button = self.toolbar.get_by_role('button', name='模板')
        # "插件" 按钮算不出无障碍名，按工具栏内文字匹配
        self.plugin_button = self.toolbar.locator('button', has_text='插件')
        self.flow_button = self.toolbar.get_by_role('button', name='流程')
        self.new_button = self.toolbar.get_by_role('button', name='新建', exact=True)
        self.publish_button = self.toolbar.get_by_role('button', name='发布')

        # ==================== 右侧栏 ====================
        self.edit_manage_button = page.get_by_text('编辑管理', exact=True)
        self.version_manage_button = page.get_by_text('版本管理', exact=True)
        # 同样两个东西的 role=tab 定位（右抽屉顶部的 tab）
        self.edit_manage_tab = page.get_by_role('tab', name='编辑管理')
        self.version_manage_tab = page.get_by_role('tab', name='版本管理')
        # 「发布」弹出的「发布看板」对话框
        self.publish_dialog = page.get_by_role('dialog').filter(has_text='发布看板')
        # 右侧显示 Page(布局级) 属性时的标志控件（点空白 / 编辑管理 tab 都会切到它）
        self.page_props_marker = page.get_by_title('布局列数')

        # ==================== 画布结构（预览态整体消失）====================
        self.left_drawer_items = page.locator('[data-testid^="drawer-item:"]')
        self.right_property_panel = page.locator('[class*="Sidebar--right"]')
        self.puck_components = page.locator('[data-puck-component]')

    # 切到预览态。编辑态画布只是「设计态占位」，不吃 默认值 / 绑定 等运行时属性；
    # 预览态会真正挂载组件，默认值这类才会体现在渲染出来的控件上。
    def enter_preview(self):
        self.preview_button.click()
        # 等编辑壳（自由布局的 react-grid-item / 栅格的 puck 组件）卸载
        self.page.wait_for_selector('.react-grid-item, [data-puck-component]', state='detached')

    def exit_preview(self):
        self.edit_button.click()
        self.page.wait_for_selector('.react-grid-item, [data-puck-component]', state='attached')

    # ==================== 布局切换（自由 ↔ 栅格）====================

    def current_layout(self):
        """当前布局：'free' / 'grid'，按 自由布局/栅格布局 按钮的 aria-pressed 判断。"""
        if self.free_layout_button.get_attribute('aria-pressed') == 'true':
            return 'free'
        if self.grid_layout_button.get_attribute('aria-pressed') == 'true':
            return 'grid'
        return None

    def canvas(self):
        """当前布局的画布 locator（自由是 .react-grid-layout，栅格是 puck dropzone）。"""
        sel = self.CANVAS_GRID if self.current_layout() == 'grid' else self.CANVAS_FREE
        return self.page.locator(sel).first

    def all_widgets(self):
        """两种布局的画布组件合并（自由 .react-grid-item + 栅格 [data-puck-component]）。"""
        return self.page.locator('.react-grid-item, [data-puck-component]')

    def switch_to_free(self):
        self.free_layout_button.click()
        self.page.locator(self.CANVAS_FREE).first.wait_for(state='visible')

    def switch_to_grid(self):
        self.grid_layout_button.click()
        self.page.locator(self.CANVAS_GRID).wait_for(state='visible')

    @property
    def switch_toast(self):
        """布局切换后弹出的 Snackbar（role=alert），文案如
        "已切换到栅格布局（两种模式共享同一数据源）"。不是确认框、不阻塞操作。"""
        return self.page.get_by_role('alert')

    # ==================== 屏幕大小（分辨率）====================

    def resolution_button(self, key):
        """key: 'fullhd' / 'hd' / 'tablet'。"""
        return self.page.get_by_test_id(f'resolution-{key}')

    def set_resolution(self, key):
        """切换画布分辨率档位。点完等一下让画布宽度过渡结束再读。"""
        self.resolution_button(key).click()
        self.page.wait_for_timeout(400)

    def canvas_width(self):
        """当前画布渲染宽度（px，四舍五入）。对应 RESOLUTIONS 里的固定值。"""
        box = self.canvas().bounding_box()
        return round(box['width']) if box else None

    # ==================== 主题 ====================

    def theme_toggle_title(self):
        """切换按钮的 title：'切换至浅色主题'（=当前深色）/ '切换至深色主题'（=当前浅色）。"""
        return self.theme_toggle.get_attribute('title')

    def current_theme(self):
        """由按钮 title 反推当前主题：'dark' / 'light'。"""
        t = self.theme_toggle_title() or ''
        if '浅色' in t:      # "切换至浅色主题" → 当前是深色
            return 'dark'
        if '深色' in t:
            return 'light'
        return None

    # ==================== 新建 ====================
    # 「新建」会弹浏览器原生 confirm（不是 MUI 弹框，DOM 里找不到），
    # 必须用 page.on/once('dialog', ...) 处理。确定 → 画布清空；取消 → 画布不变。

    def click_new_and_confirm(self):
        """点「新建」并在原生确认框点「确定」——画布内容被清空。"""
        self.page.once('dialog', lambda d: d.accept())
        self.new_button.click()

    def click_new_and_cancel(self):
        """点「新建」并在原生确认框点「取消」——画布内容保持不变。"""
        self.page.once('dialog', lambda d: d.dismiss())
        self.new_button.click()

    # ==================== 刷新 ====================

    def reload_editor(self, layout='free'):
        """刷新浏览器并等回到指定布局的编辑态画布（layout: 'free' / 'grid'）。
        已保存的布局刷新后自动加载；没保存的会丢。若刷新后掉出编辑器则重新进。"""
        self.page.reload()
        self.page.wait_for_load_state('networkidle')
        sel = self.CANVAS_GRID if layout == 'grid' else self.CANVAS_FREE
        try:
            self.page.locator(sel).first.wait_for(state='visible', timeout=10000)
        except Exception:
            self.editor_button.click()
            self.edit_button.wait_for(state='visible'); self.edit_button.click()
            btn = self.grid_layout_button if layout == 'grid' else self.free_layout_button
            btn.wait_for(state='visible'); btn.click()
            self.page.locator(sel).first.wait_for(state='visible')
            self.edit_manage_button.click()
            self.page.wait_for_load_state('networkidle')