from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


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
        try:
            # 10s：首屏慢时别误判成"向导没出现"而直接跳过（跳过会导致向导弹窗
            # 挡住后续操作）。向导没出现是正常情况（之前已配置），超时静默跳过。
            self.dialog.wait_for(state='visible', timeout=10000)
            self.next_button.click()
            self.next_button.wait_for(state='visible')  # 等第二步渲染
            self.next_button.click()
            self.finish_button.wait_for(state='visible')
            self.finish_button.click()
            self.dialog.wait_for(state='hidden')
        except PlaywrightTimeoutError:
            pass
