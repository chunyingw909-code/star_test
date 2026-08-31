from pages.editor.widget_catalog import by_category, CATEGORIES
from pages.editor.json_view_mixin import JsonViewMixin


class GridLayoutPage(JsonViewMixin):
    COMPONENT_ITEMS = by_category()
    COMPONENT_CATEGORIES = CATEGORIES

    # 组件对应插件被关闭后的锁定态文案（属性面板里显示）
    DISABLED_NOTICE = '该组件已禁用（对应插件已关闭），禁止编辑。重新启用插件后恢复。'

    def __init__(self, page):
        self.page = page
        # 画布
        self.canvas = page.get_by_test_id('dropzone:root:default-zone')

        # 删除复制按钮
        self.duplicate_button = page.locator('button[title="Duplicate"]')
        self.delete_button = page.locator('button[title="Delete"]')

        # 点画布空白后，右侧从"组件属性"切回 "Page(布局级)属性" 的标志控件
        self.page_props_marker = page.get_by_title('布局列数')

        # 拖拽误触发"加载断点"后出现的弹窗
        self.breakpoint_dialog = page.get_by_role('dialog', name='断点恢复')
        self.breakpoint_dialog_close_button = self.breakpoint_dialog.get_by_role('button', name='关闭')

        # —— Puck 编辑器工具条：视图切换 / 面板开关 / 撤销重做 ——
        # 无障碍名算不准（"<>JSON" 的 <>），按文字匹配
        self.ui_visual_button = page.locator('button', has_text='UI可视')
        self.json_button = page.locator('button', has_text='<>JSON')
        self.json_editor = page.locator('textarea')                     # <>JSON 模式的编辑区
        self.toggle_left_sidebar_button = page.get_by_title('Toggle left sidebar')   # 隐藏/显示左侧组件库
        self.toggle_right_sidebar_button = page.get_by_title('Toggle right sidebar')  # 隐藏/显示右侧属性面板
        self.undo_button = page.get_by_title('undo')
        self.redo_button = page.get_by_title('redo')
        # 栅格布局的「保存」= Puck MenuBar 里的 Publish（是 span 不是 <button>，无 button role）
        self.publish_button = page.locator('span[class*="_Button_"]', has_text='Publish')

    # 根据test_id获取左侧组件库中的某个可拖拽项
    def drawer_item(self, name):
        return self.page.get_by_test_id(f'drawer-item:{name}')

    # 分类折叠/展开按钮（标题 "Collapse 工业监控" 表示当前展开）
    def category_header(self, name):
        return self.page.locator(f'button[title="Collapse {name}"]')

    # 组件库里所有可拖拽项的 Type 列表（从 data-testid="drawer-item:X" 提取 X）
    def drawer_item_types(self):
        return self.page.eval_on_selector_all(
            '[data-testid^="drawer-item:"]',
            'els => els.map(e => e.getAttribute("data-testid").replace("drawer-item:", ""))'
        )

    # —— 组件对应插件被关闭后的锁定态 ——
    @property
    def disabled_panel_notice(self):
        return self.page.get_by_text(self.DISABLED_NOTICE)

    def widget_disabled_badge(self, index=0):
        return self.canvas_widgets().nth(index).get_by_text('组件已禁用', exact=True)

    # 将组件从左侧拖拽到画布，失败自动重试
    def drag_to_canvas(self, test_id_name, max_retries=3):
        source = self.drawer_item(test_id_name)
        self.canvas.wait_for(state='visible')

        for i in range(max_retries):
            # 上一次拖拽若误点到"加载断点"，会弹出断点恢复弹窗挡住后续操作，先关掉
            self._dismiss_breakpoint_dialog()

            source.scroll_into_view_if_needed()
            source_box = source.bounding_box()
            canvas_box = self.canvas.bounding_box()
            start_x = source_box['x'] + source_box['width'] / 2
            start_y = source_box['y'] + source_box['height'] / 2

            self.page.mouse.move(start_x, start_y)
            self.page.mouse.down()
            # 按下后先小幅移动，触发拖拽库的 drag-start 阈值，避免被识别成一次点击
            self.page.mouse.move(start_x + 5, start_y + 5, steps=5)
            self.page.wait_for_timeout(100)
            self.page.mouse.move(canvas_box['x'] + canvas_box['width'] / 2, canvas_box['y'] + canvas_box['height'] / 2,
                                 steps=30)
            self.page.mouse.up()
            self.page.wait_for_timeout(500)

            if self.canvas_widgets().count() > 0:
                # 成功这一拖也可能顺带弹出断点弹窗；不关掉的话它会盖在属性面板
                # 上层，后续对属性控件的 .click() 会被它拦截而超时
                self.page.wait_for_timeout(300)
                self._dismiss_breakpoint_dialog()
                return

        raise Exception(f'拖拽 {test_id_name} 失败，重试 {max_retries} 次')

    # 弹窗出现则关闭，未出现则跳过
    def _dismiss_breakpoint_dialog(self):
        if self.breakpoint_dialog.is_visible():
            self.breakpoint_dialog_close_button.click()
            self.breakpoint_dialog.wait_for(state='hidden')

    # 获取画布上所有组件
    def canvas_widgets(self):
        return self.canvas.locator('[data-puck-component]')

    # 点击画布上第index个组件，等待可见后强制点击
    def click_widget(self, index=0):
        widget = self.canvas_widgets().nth(index)
        widget.wait_for(state='visible')
        # force 点击会绕过命中检测，若组件中心恰好压着悬浮的"加载断点"按钮，
        # 会误触弹出断点弹窗，盖在属性面板上层导致后续 .click() 超时——点完立刻关掉
        widget.click(force=True)
        self._dismiss_breakpoint_dialog()

    # 点选组件并等右侧属性面板出现；点不出就 dismiss 断点弹窗后重点，最多 retries 次。
    # 偶发：拖拽刚落地时选中状态没生效 / 断点弹窗盖住面板 → prop.wait_for 30s 超时。
    def select_widget(self, prop, index=0, retries=3):
        from playwright.sync_api import TimeoutError as _PWTimeout
        for _ in range(retries - 1):
            try:
                self.click_widget(index)
                prop.wait_for(state='visible', timeout=8000)
                return
            except _PWTimeout:
                self._dismiss_breakpoint_dialog()
                self.page.wait_for_timeout(400)
        # 最后一次放开超时、失败就抛
        self.click_widget(index)
        prop.wait_for(state='visible', timeout=10000)

    # 复制 / 删除当前选中的组件。
    # 用 dispatch_event 把 click 事件直接派发到按钮上，绕过左侧组件库悬浮层的遮挡
    # （画布尺寸问题，开发待修；画布改好后这里可换回普通 .click()）。
    def duplicate_widget(self):
        self.duplicate_button.dispatch_event('click')
        self._dismiss_breakpoint_dialog()

    def delete_widget(self):
        self.delete_button.dispatch_event('click')
        self._dismiss_breakpoint_dialog()

    # 点击画布空白处，右侧切回 Page 属性。
    # 实测：点画布「内部」的空白区不会取消选中，点画布「下方」才行。
    # 所以不写死坐标，改成动态算：x = 画布水平中点，y = 画布底部再往下 40px，
    # 两者都夹在视口范围内。组件都落在画布内部，画布下方这条带子必然是空白。
    # 点击并重试 3 次，仍不生效就打印现场信息再报错。
    def click_canvas_blank(self):
        vp = self.page.viewport_size
        c = self.canvas.bounding_box()
        x = min(max(max(c['x'], 0) + min(c['width'], vp['width']) / 2, 4), vp['width'] - 4)
        y = min(c['y'] + c['height'] + 40, vp['height'] - 4)

        for _ in range(3):
            self.page.mouse.click(x, y)
            self.page.wait_for_timeout(300)
            if self.page_props_marker.is_visible():
                return

        print(f'[click_canvas_blank] 点击 ({x:.0f},{y:.0f}) 未切回 Page 属性；canvas={c}')
        raise Exception('click_canvas_blank: 画布下方空白点未能切回 Page 属性')

    # ==================== 面板开关 / 撤销重做 ====================

    def left_sidebar_visible(self):
        return self.page.locator('[data-testid^="drawer-item:"]').count() > 0

    def right_sidebar_visible(self):
        return self.page.locator('[class*="Sidebar--right"]').count() > 0

    def undo(self):
        self.undo_button.click()
        self._dismiss_breakpoint_dialog()

    def redo(self):
        self.redo_button.click()
        self._dismiss_breakpoint_dialog()

    # ==================== 保存（Publish）====================

    def save_layout(self, name):
        """填「布局名称」（主工具栏输入框）+ 点 Publish。
        随后按提示 toast（"保存成功"）断言。"""
        from pages.editor.editor_page import EditorPage
        EditorPage(self.page).layout_name_input.fill(name)
        self.publish_button.first.click()
