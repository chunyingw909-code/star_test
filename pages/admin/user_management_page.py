import json
import time

from common.utils import api_fetch


class UserManagementPage:
    """头像菜单「用户管理」（/zh-CN/admin/users）：账号的增删改查 + 启停 + 重置密码。

    列表是一张表（不在特殊容器里，页面上没有别的表格会撞）：用户名（forcePwdChange
    为真时名字下面带「待改密」小字）/ 显示名 / 角色(Chip: 用户/管理员) / 状态(Chip:
    启用/禁用) / 最后登录 / 操作（编辑/重置密码/禁用或启用/删除四个按钮）。
    顶部 角色 / 状态 两个筛选下拉，「创建用户」按钮，MUI 分页（这台环境目前只有 2
    个账号，分页意义不大）。

    「创建用户」「编辑」「重置密码」都弹同一个 role=dialog（同一时刻只会开一个，
    定位符不分别声明）：
      创建：用户名 / 显示名 / 初始密码（至少 8 位、含字母和数字，首次登录强制改密）/
            角色 下拉（默认「用户」）。必填只卡用户名和初始密码，显示名不是必填。
      编辑：用户名（禁用，改不了）/ 显示名 / 角色 / 状态，没有密码字段。
      重置密码：新密码（同样至少 8 位、含字母和数字）+「该用户下次登录需修改」提示。
    「删除」是浏览器原生 confirm()（「确定删除用户 <name>？此操作不可恢复。」），
    「禁用」「启用」瞬间生效、没有任何二次确认。

    接口（供用例直接建 / 清数据用；同源，走 common.utils.api_fetch）：
      POST   /api/users        创建，body 里 roles 是「JSON 数组字符串」不是原生数组，
                                例如 '["USER"]'（抓包实测，不是笔误）
      DELETE /api/users/<id>   永久删除

    对应用例：testcases/admin/test_user_management.py
    """

    ROLES = ('用户', '管理员')
    STATUSES = ('启用', '禁用')

    # ---------- 定位（全部集中在 __init__）----------
    def __init__(self, page):
        self.page = page
        self.avatar_menu_button = page.locator('.MuiAvatar-root')
        self.menu_user_management_item = page.get_by_role('menuitem', name='用户管理')
        self.heading = page.get_by_role('heading', name='用户管理')
        self.new_button = page.get_by_role('button', name='创建用户')
        self._rows = page.locator('table tbody tr')
        self.role_filter = page.locator('.MuiFormControl-root', has_text='角色').get_by_role('combobox')
        self.status_filter = page.locator('.MuiFormControl-root', has_text='状态').get_by_role('combobox')
        # 创建/编辑/重置密码共用同一个弹窗，同一时刻只会开一个
        self.dialog = page.get_by_role('dialog')
        self.dialog_title = self.dialog.get_by_role('heading')
        self.username_input = self.dialog.locator('input[type="text"]').first
        self.display_name_input = self.dialog.locator('input[type="text"]').nth(1)
        self.password_input = self.dialog.locator('input[type="password"]').first
        # 「角色」「状态」下拉的 <label> 没有 for 关联到 combobox（不是标准 MUI 标签
        # 关联），get_by_label 定位不到，用「离它最近的 FormControl 里含这段文字」兜底，
        # 和筛选下拉（role_filter/status_filter）同一个套路
        self.role_select = self.dialog.locator('.MuiFormControl-root', has_text='角色').get_by_role('combobox')
        self.status_select = self.dialog.locator('.MuiFormControl-root', has_text='状态').get_by_role('combobox')
        self.save_button = self.dialog.get_by_role('button', name='保存')
        self.confirm_reset_button = self.dialog.get_by_role('button', name='确认重置')
        # 校验错误（必填 / 用户名重复 / 密码格式）不是 FormHelperText，是一个 MuiAlert；
        # 密码框下面那句「至少 8 位...」的静态提示才是 FormHelperText，两者不是同一个东西
        self.error_alert = self.dialog.locator('.MuiAlert-root')
        # 「删除」是原生 confirm()，不在弹窗里；操作失败（比如删除自己）时页面上单独
        # 弹一个同款 MuiAlert 提示，跟表单校验错误的 error_alert 不是同一个元素
        self.page_alert = page.locator('.MuiAlert-root')

    # ---------- 进入（给「点头像进用户管理」这条用例用）----------

    def open_via_avatar_menu(self):
        """点右上角头像、菜单里点「用户管理」，等表格出现。"""
        self.avatar_menu_button.click()
        self.menu_user_management_item.click()
        self._rows.first.wait_for(state='visible')

    # ---------- 列表：读 ----------

    def rows(self):
        return self._rows

    def row_by_username(self, username):
        """按用户名找行——用户名单独占列表第一列，筛选不会撞到显示名/角色里的同名字。"""
        return self._rows.filter(has_text=username)

    def row_info(self, username):
        """按用户名取这一行当前展示的 {username, pending_pwd_change, display_name,
        role, status, last_login}。"""
        row = self.row_by_username(username)
        cells = row.locator('td')
        first_col_lines = [t.strip() for t in cells.nth(0).inner_text().split('\n') if t.strip()]
        return {
            'username': first_col_lines[0],
            'pending_pwd_change': '待改密' in first_col_lines[1:],
            'display_name': cells.nth(1).inner_text().strip(),
            'role': cells.nth(2).inner_text().strip(),
            'status': cells.nth(3).inner_text().strip(),
            'last_login': cells.nth(4).inner_text().strip(),
        }

    def role_options(self):
        """「角色」筛选下拉的全部选项。"""
        return self._dropdown_options(self.role_filter)

    def status_options(self):
        """「状态」筛选下拉的全部选项。"""
        return self._dropdown_options(self.status_filter)

    def _dropdown_options(self, combobox):
        combobox.click()
        opts = [t.strip() for t in self.page.get_by_role('option').all_inner_texts()]
        self.page.keyboard.press('Escape')
        return opts

    def error_text(self):
        """弹窗当前的校验错误提示（必填项 / 用户名重复 / 密码格式），是一个 MuiAlert，
        不是 FormHelperText。没有错误时返回 None。"""
        return self.error_alert.inner_text() if self.error_alert.count() else None

    # ---------- 动作：列表 / 筛选 ----------

    def filter_role(self, name):
        """选「角色」筛选；name 传「全部」/「用户」/「管理员」。"""
        self._select(self.role_filter, name)

    def filter_status(self, name):
        """选「状态」筛选；name 传「全部」/「启用」/「禁用」。"""
        self._select(self.status_filter, name)

    def _select(self, combobox, text):
        """真正的单选下拉（筛选栏两个、弹窗里的「状态」）：点开、点目标项，自己会关。"""
        combobox.click()
        self.page.get_by_role('option', name=text, exact=True).click()

    def _select_role(self, combobox, target):
        """弹窗里的「角色」底层是 MUI 多选组件（界面上看是单选，抓包/查 class 证实
        MuiSelect-multiple）：点一次是「切换选中状态」不是「替换」，且选完不会自动
        关。进来前默认已经选中一项，这里把「选中的」和目标对齐——该选的选、不该选的
        取消，最后按 Escape 强制关掉，不然弹层会留在 DOM 里挡住后面的点击（比如
        保存按钮）。"""
        combobox.click()
        popover = self.page.locator('[role="presentation"].MuiPopover-root')
        popover.wait_for(state='visible', timeout=3000)
        for name in self.ROLES:
            option = self.page.get_by_role('option', name=name, exact=True)
            selected = 'Mui-selected' in (option.get_attribute('class') or '')
            if selected != (name == target):
                option.click()
        self.page.keyboard.press('Escape')
        popover.wait_for(state='hidden', timeout=3000)

    def open_create_dialog(self):
        self.new_button.click()
        self.dialog.wait_for(state='visible')

    def open_edit_dialog(self, username):
        self.row_by_username(username).get_by_role('button', name='编辑').click()
        self.dialog.wait_for(state='visible')

    def open_reset_password_dialog(self, username):
        self.row_by_username(username).get_by_role('button', name='重置密码').click()
        self.dialog.wait_for(state='visible')

    def toggle_status(self, username):
        """点这一行的「禁用」或「启用」按钮——按钮文字随当前状态显示两者之一，瞬间
        生效，没有二次确认。等状态列 Chip 文字真的翻转了再返回，不然紧接着读状态
        会读到点击前的旧值。"""
        row = self.row_by_username(username)
        before = self.row_info(username)['status']
        target = '禁用' if before == '启用' else '启用'
        btn = row.get_by_role('button', name='禁用')
        if not btn.count():
            btn = row.get_by_role('button', name='启用')
        btn.click()
        row.get_by_text(target, exact=True).wait_for(state='visible', timeout=5000)

    def delete(self, username, confirm=True):
        """点这一行的「删除」。confirm=True 点原生弹窗「确定」，False 点「取消」。"""
        self.page.once('dialog', lambda d: d.accept() if confirm else d.dismiss())
        self.row_by_username(username).get_by_role('button', name='删除').click()

    # ---------- 动作：弹窗表单 ----------

    def fill_create_form(self, username=None, display_name=None, password=None, role=None):
        """填「创建用户」表单，只传要改的字段。"""
        if username is not None:
            self.username_input.fill(username)
        if display_name is not None:
            self.display_name_input.fill(display_name)
        if password is not None:
            self.password_input.fill(password)
        if role is not None:
            self._select_role(self.role_select, role)

    def fill_edit_form(self, display_name=None, role=None, status=None):
        """填「编辑」表单，只传要改的字段（用户名改不了，不在这里）。"""
        if display_name is not None:
            self.display_name_input.fill(display_name)
        if role is not None:
            self._select_role(self.role_select, role)
        if status is not None:
            self._select(self.status_select, status)

    def save(self, timeout_ms=8000):
        """点「保存」，等到「弹窗关了」或「出现错误提示」两者之一——有的校验（比如
        用户名重复）要等后端返回才出现，不是点完立刻就有，不能点完马上就去读
        error_text()。表单有校验错误时弹窗不会关，调用方自己用 error_text() 断言。"""
        self.save_button.click()
        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            if not self.dialog.count() or self.error_alert.count():
                return
            self.page.wait_for_timeout(100)

    def save_and_get_created_id(self):
        """新建场景专用：点「保存」，等 POST /api/users 的响应回来，返回新建账号的 id。
        给「走 UI 新建、拿 id 之后用接口清理」的用例用。"""
        with self.page.expect_response(
                lambda r: r.request.method == 'POST' and r.url.endswith('/api/users')) as resp_info:
            self.save_button.click()
        return resp_info.value.json()['data']['id']

    def confirm_reset(self, new_password):
        """填「重置密码」弹窗的新密码并点「确认重置」。"""
        self.password_input.fill(new_password)
        self.confirm_reset_button.click()

    def close_dialog(self):
        """按 Escape 关掉当前弹窗（创建/编辑/重置密码弹窗都没有单独的「取消」按钮）。"""
        self.page.keyboard.press('Escape')
        self.dialog.wait_for(state='hidden')

    # ---------- 接口：供用例直接建 / 清数据（同源 fetch，走 common.utils.api_fetch）----------

    def api_create(self, username, display_name, password='Test1234', role='USER', status='ACTIVE'):
        """直接调 POST /api/users 建一个账号，不经过表单。返回创建后的完整对象（含 id）。
        给「测试要用到一个已存在账号，但不是在测新建流程本身」的用例当前置数据用。"""
        body = {
            'username': username, 'displayName': display_name, 'password': password,
            'roles': json.dumps([role]), 'status': status,
        }
        return api_fetch(self.page, '/api/users', method='POST', body=body)['data']

    def api_delete(self, user_id):
        """直接调 DELETE /api/users/<id> 删掉一个账号。给用例 teardown 清数据用；
        这个账号已经不在了也不报错。"""
        api_fetch(self.page, f'/api/users/{user_id}', method='DELETE')
