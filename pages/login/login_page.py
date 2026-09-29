import time


class LoginPage:
    """账号登录页（/login，目前只有 192.168.1.222 这台环境要过这一步）。

    表单就两个原生 input（文本=用户名、password=密码，都没有 maxlength/required
    属性）+「登录」按钮；按钮本身不会因为留空就被禁用，校验是点「登录」时才做的：
      - 有任一字段为空：本地拦截，不发请求，提示「请输入用户名和密码」
      - 账号不存在 / 密码错误：POST /api/auth/login 真的发了，HTTP 状态还是 200，
        业务失败包在响应体里（{"code":401,"message":"用户名或密码错误",...}），
        前端统一显示「登录失败，请检查用户名和密码」（不区分具体错在哪）。
    两种提示用的是同一个 MuiAlert（Error 态），一次只显示一条。
    成功登录后的跳转是 SPA 客户端路由（next/navigation router.push），不是整页刷新，
    networkidle 有时在跳转真正发生前就已经满足——login() 明确等到「离开登录页」或
    「出现错误提示」两者之一，不能光靠 networkidle 判断成没成功。
    密码框回车等价于点「登录」。
    页面自己在下方列了默认账号；自动化实际凭据统一从 config/secrets.yaml 读取。
    222 的固定 admin/user 均已完成首次改密，普通权限测试可直接复用固定 user；只有
    专门验证首次改密流程的用例才创建 forcePwdChange=true 的一次性账号。
    """

    def __init__(self, page):
        self.page = page
        self.username_input = page.locator('input[type="text"]').first
        self.password_input = page.locator('input[type="password"]').first
        self.login_button = page.get_by_role('button', name='登录', exact=True)
        self.error_alert = page.locator('.MuiAlert-root')
        # forcePwdChange 账号登录成功后弹的「首次登录，请设置新密码」弹窗：URL 还停在
        # /login（不算真的登录失败，是另一种「未完成登录」态），两个密码框都在这个
        # 弹窗范围内，背后登录表单自己的密码框还在 DOM 里，定位得限定在弹窗范围内
        self.force_change_dialog = page.get_by_role('dialog').filter(has_text='首次登录')
        self.new_password_input = self.force_change_dialog.locator('input[type="password"]').nth(0)
        self.confirm_password_input = self.force_change_dialog.locator('input[type="password"]').nth(1)
        self.confirm_change_button = self.force_change_dialog.get_by_role('button', name='确认修改')
        self.force_change_error = self.force_change_dialog.locator('.MuiAlert-root')

    def login(self, username, password, timeout_ms=8000):
        """填用户名/密码，点「登录」，等到「离开登录页」或「出现错误提示」两者之一。
        成功/失败都不超时报错——调用方自己看 page.url / error_alert 断言结果。"""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
        self.wait_result(timeout_ms)

    def complete_force_change(self, new_password, timeout_ms=8000):
        """填「首次登录，请设置新密码」弹窗（新密码 + 确认新密码都填同一个值）、点
        「确认修改」，等到「弹窗关了」或「出现校验错误」两者之一。两次不一致 /
        格式不对（少于 8 位或缺字母缺数字）都不会关弹窗，会在弹窗里弹一条 MuiAlert，
        跟登录本身的 error_alert 不是同一个元素。"""
        self.new_password_input.fill(new_password)
        self.confirm_password_input.fill(new_password)
        self.confirm_change_button.click()
        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            if not self.force_change_dialog.count() or self.force_change_error.count():
                break
            self.page.wait_for_timeout(100)
        self.page.wait_for_load_state('networkidle')

    def wait_result(self, timeout_ms=8000):
        """点「登录」或密码框回车之后都用这个等：等到「离开登录页」或「出现错误提示」
        两者之一。成功后的跳转是 SPA 客户端路由，networkidle 有时在跳转真正发生前就
        已经满足，不能只靠它判断成没成功。"""
        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            if '/login' not in self.page.url or self.error_alert.count():
                break
            self.page.wait_for_timeout(100)
        self.page.wait_for_load_state('networkidle')
