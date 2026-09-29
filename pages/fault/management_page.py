from common.utils import api_fetch, fault_root


class FaultManagementPage:
    """故障/预案库 -「管理」子标签：故障目录的增删改查。

    列表是卡片（在 fault-catalog-root 内，一次性展示全部，没有搜索框也不分页）：编码 +
    名称 + 严重等级 Chip + 分系统 + 三个操作图标（编辑 / 废弃 / 删除）。「新建故障」
    「编辑」都弹同一套 MUI Dialog 表单：故障编码 / 故障名称（中文）/ 故障类型（英文标识）
    三项必填，分系统 / 严重等级 / 目标模块 有默认值，描述可选。故障编码要求全局唯一——
    前端本地校验，重复时只提示、不发请求。

    「废弃」「删除」不是 MUI 弹窗，是浏览器原生 confirm()：
      废弃：「确定废弃该故障？（废弃后不再参与定位匹配）」——确定后这条从管理页列表消失
      删除：「确定永久删除该故障及全部关联数据？此操作不可恢复。」——确定后永久没了
    用 page.once('dialog', ...) 接，accept()=确定，dismiss()=取消。

    接口（供用例直接建 / 清数据用；同源，走 page.evaluate 里的 fetch，不用另起 HTTP 客户端）：
      POST   /api/fault                创建，body 同表单字段（不含 id），
                                        返回 {code,message,data:{...含 id}}
      DELETE /api/fault/<id>           永久删除，无 body

    对应用例：testcases/fault/test_fault_management.py
    """

    SUBSYSTEMS = ('power', 'ttc', 'electronics', 'aocs', 'isl', 'thermal')  # 分系统下拉选项（结构常量）
    SEVERITIES = ('Ⅰ 灾难', 'Ⅱ 严重', 'Ⅲ 一般', 'Ⅳ 轻微')                    # 严重等级下拉选项
    TEST_CODE_PREFIXES = ('AUTOTEST-', 'ZZTEST-')

    # ---------- 定位（全部集中在 __init__）----------
    def __init__(self, page):
        self.page = page
        self.root = fault_root(page)
        self.heading = self.root.get_by_role('heading', name='故障目录管理')
        self.new_button = self.root.get_by_role('button', name='新建故障')
        self._cards = self.root.locator('.MuiCard-root')
        # 新建/编辑弹窗（点开之后才有；新建/编辑共用同一套表单，标题不同）
        self.dialog = page.get_by_role('dialog')
        self.dialog_title = self.dialog.get_by_role('heading')
        self.code_input = self.dialog.get_by_label('故障编码')
        self.name_input = self.dialog.get_by_label('故障名称（中文）')
        self.type_input = self.dialog.get_by_label('故障类型（英文标识）')
        self.subsystem_select = self.dialog.get_by_label('分系统')
        self.severity_select = self.dialog.get_by_label('严重等级')
        self.description_input = self.dialog.get_by_label('描述')
        self.target_module_input = self.dialog.get_by_label('目标模块')
        self.dialog_cancel_button = self.dialog.get_by_role('button', name='取消')
        self.dialog_save_button = self.dialog.get_by_role('button', name='保存')
        self._dialog_helper_texts = self.dialog.locator('.MuiFormHelperText-root')

    # ---------- 列表：读（给 test_management_count_matches_catalog 等用）----------

    def cards(self):
        """全部故障卡片。管理页不分页，一次性展示。"""
        return self._cards

    def card_by_code(self, code):
        """按故障编码找卡片——编辑 / 废弃 / 删除都要先定位到具体这张。"""
        return self._cards.filter(has_text=code)

    def card_code(self, index=0):
        """第 index 张卡片的故障编码。给「拿一个已有编码当重复值」这类用例取值用。"""
        return self._cards.nth(index).locator('.MuiTypography-caption').first.inner_text().strip()

    def card_info(self, code):
        """按编码取卡片当前展示的 {code, name, severity, subsystem}。"""
        card = self.card_by_code(code)
        spans = card.locator('.MuiTypography-caption')
        return {
            'code': spans.first.inner_text().strip(),
            'name': spans.nth(1).inner_text().strip(),
            'severity': card.locator('.MuiChip-root').inner_text().strip(),
            'subsystem': spans.last.inner_text().strip(),
        }

    # ---------- 弹窗：读（给 test_management_new_* / _edit_* 用）----------

    def helper_texts(self):
        """表单当前的校验提示文案（必填项 / 编码重复）。"""
        return self._dialog_helper_texts.all_inner_texts()

    def dropdown_options(self, combobox):
        """打开下拉读出全部选项文本，再关掉。"""
        combobox.click()
        opts = [t.strip() for t in self.page.get_by_role('option').all_inner_texts()]
        self.page.keyboard.press('Escape')
        return opts

    # ---------- 动作：列表 ----------

    def open_new_dialog(self):
        """点「新建故障」，等弹窗出现。"""
        self.new_button.click()
        self.dialog.wait_for(state='visible')

    def open_edit_dialog(self, code):
        """点某张卡片的「编辑」，等弹窗出现。"""
        self.card_by_code(code).get_by_role('button', name='编辑').click()
        self.dialog.wait_for(state='visible')

    def discard(self, code, confirm=True):
        """点某张卡片的「废弃」。confirm=True 点原生弹窗「确定」，False 点「取消」。"""
        self._require_test_code(code)
        self.page.once('dialog', lambda d: d.accept() if confirm else d.dismiss())
        self.card_by_code(code).get_by_role('button', name='废弃').click()

    def delete(self, code, confirm=True):
        """点某张卡片的「删除」。confirm=True 点原生弹窗「确定」，False 点「取消」。"""
        self._require_test_code(code)
        self.page.once('dialog', lambda d: d.accept() if confirm else d.dismiss())
        self.card_by_code(code).get_by_role('button', name='删除').click()

    @classmethod
    def _require_test_code(cls, code):
        """ destructive 操作只允许自动化专用编码，阻止误删原有故障。"""
        if not code.startswith(cls.TEST_CODE_PREFIXES):
            raise ValueError(f'拒绝操作非测试故障：{code}')

    # ---------- 动作：弹窗表单 ----------

    def fill_form(self, code=None, name=None, fault_type=None,
                  subsystem=None, severity=None, description=None, target_module=None):
        """填表单，只传要改的字段。下拉（分系统 / 严重等级）传选项的显示文本。"""
        if code is not None:
            self.code_input.fill(code)
        if name is not None:
            self.name_input.fill(name)
        if fault_type is not None:
            self.type_input.fill(fault_type)
        if subsystem is not None:
            self._select(self.subsystem_select, subsystem)
        if severity is not None:
            self._select(self.severity_select, severity)
        if description is not None:
            self.description_input.fill(description)
        if target_module is not None:
            self.target_module_input.fill(target_module)

    def _select(self, combobox, text):
        combobox.click()
        self.page.get_by_role('option', name=text, exact=True).click()

    def save(self):
        """点「保存」。表单有校验错误时弹窗不会关，调用方自己用 helper_texts() 断言。"""
        self.dialog_save_button.click()

    def save_and_get_created_id(self):
        """新建场景专用：点「保存」，等 POST /api/fault 的响应回来，返回新建故障的 id。
        给「走 UI 新建、拿 id 之后用接口清理」的用例用。"""
        with self.page.expect_response(
                lambda r: r.request.method == 'POST' and r.url.endswith('/api/fault')) as resp_info:
            self.dialog_save_button.click()
        return resp_info.value.json()['data']['id']

    def cancel(self):
        """点「取消」，弹窗关闭、不保存。"""
        self.dialog_cancel_button.click()
        self.dialog.wait_for(state='hidden')

    # ---------- 接口：供用例直接建 / 清数据（同源 fetch，走 page.evaluate）----------

    def api_create(self, code, name, fault_type, subsystem='power', severity='III',
                    description='', target_module='satellite'):
        """直接调 POST /api/fault 建一条故障，不经过表单。返回创建后的完整对象（含 id）。
        给「测试要用到一条已存在故障，但不是在测新建流程本身」的用例当前置数据用。"""
        body = {
            'faultCode': code, 'faultName': name, 'faultType': fault_type,
            'subsystem': subsystem, 'severity': severity,
            'description': description, 'targetModule': target_module,
            'status': 'active',
        }
        return api_fetch(self.page, '/api/fault', method='POST', body=body)['data']

    def api_delete(self, fault_id, expected_code):
        """删除前按 ID 核对真实编码，只允许删除调用方创建的测试故障。"""
        payload = api_fetch(self.page, f'/api/fault/{fault_id}')
        data = (payload or {}).get('data', payload or {})
        actual = data.get('fault', data).get('faultCode') if isinstance(data, dict) else None
        if actual is None:
            return
        self._require_test_code(actual)
        if actual != expected_code:
            raise ValueError(
                f'删除保护：ID {fault_id} 实际编码 {actual!r} != 预期 {expected_code!r}'
            )
        api_fetch(self.page, f'/api/fault/{fault_id}', method='DELETE')
