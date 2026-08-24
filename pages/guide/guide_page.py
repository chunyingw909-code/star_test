class GuidePage:
    def __init__(self, page):
        self.page = page
        self.dialog = self.page.get_by_role('dialog')
        self.next_button = self.dialog.get_by_role('button', name='下一步')
        self.prev_button = self.dialog.get_by_role('button', name='上一步')
        self.finish_button = self.dialog.get_by_role('button', name='完成配置')


    def active_step_label(self):
        # 当前步骤的名字
        return self.dialog.locator('.MuiStepLabel-label.Mui-active')

    def step_title(self):
        # 对话框标题
        return self.dialog.locator('.MuiDialogTitle-root')

    def complete(self):
        # 跳过向导页面
        try:
            self.dialog.wait_for(state='visible', timeout=5000)
            self.next_button.click()
            self.next_button.click()
            self.finish_button.click()
            self.dialog.wait_for(state='hidden')
        except TimeoutError:
            pass  # 没弹窗说明不需要引导，直接过