class GridLayoutPage:
    COMPONENT_CATEGORIES = ['文本', '布局', '图表', '表格', '工业监控', '表单']

    COMPONENT_ITEMS = {
        '文本': ['文本'],
        '布局': ['容器', '占位'],
        '图表': ['图表'],
        '表格': ['表格'],
        '工业监控': ['仪表盘', '状态灯', '指示牌', '故障关系图'],
        '表单': ['输入框', '下拉框', '数值输入'],
    }
    def __init__(self, page):
        self.page = page
        # 画布
        self.canvas = page.get_by_test_id('dropzone:root:default-zone')

        # 删除复制按钮
        self.duplicate_button = page.locator('button[title="Duplicate"]')
        self.delete_button = page.locator('button[title="Delete"]')

        # 拖拽误触发"加载断点"后出现的弹窗
        self.breakpoint_dialog = page.get_by_role('dialog', name='断点恢复')
        self.breakpoint_dialog_close_button = self.breakpoint_dialog.get_by_role('button', name='关闭')

    # 根据test_id获取左侧组件库中的某个可拖拽项
    def drawer_item(self, name):
        return self.page.get_by_test_id(f'drawer-item:{name}')

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
        widget.click(force=True)

    # 点击画布空白处，右侧切回Page属性
    def click_canvas_blank(self):
        for _ in range(3):
            # x=900: 在组件右边缘731和viewport边缘1280之间
            # y=500: 在组件底部370下方
            self.page.mouse.click(900, 500)
            self.page.wait_for_timeout(300)
            if self.page.get_by_title('布局列数').is_visible():
                return