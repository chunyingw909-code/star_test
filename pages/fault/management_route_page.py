import json
import re

from common.utils import api_fetch, wait_until_stable
from pages.fault.mui_pager import MuiTablePager


class FaultManagementRoutePage:
    """独立路由版故障管理：表格以及展开行里的原因、影响、预案和规则。"""

    TABLE_HEADERS = ('编码', '名称', '分系统', '严重等级', '状态', '操作')
    TEST_CODE_PREFIXES = ('AUTOTEST-', 'ZZTEST-')
    _COL_CODE, _COL_NAME, _COL_SUBSYSTEM, _COL_SEVERITY, _COL_STATUS = 2, 3, 4, 5, 6

    def __init__(self, page):
        self.page = page

        # 页面、表格和分页
        self.heading = page.get_by_role('heading', name='故障库管理')
        self.new_button = page.get_by_role('button', name='新建故障')
        self.import_button = page.get_by_role('button', name='批量导入')
        self.table = page.locator('table').filter(has_text='编码')
        self.thead = self.table.locator('thead')
        self._rows = self.table.locator('tbody tr')
        self._pager = MuiTablePager(page, page, self._settle)

        # 新建/编辑共用弹窗
        self.dialog = page.get_by_role('dialog')
        self.dialog_title = self.dialog.get_by_role('heading')
        self.code_input = self.dialog.get_by_label('故障编码')
        self.name_input = self.dialog.get_by_label('故障名称 (中文)')
        self.type_input = self.dialog.get_by_label('故障类型 (英文)')
        self.subsystem_select = self.dialog.get_by_label('分系统')
        self.severity_select = self.dialog.get_by_label('严重等级')
        self.description_input = self.dialog.get_by_label('描述')
        self.target_module_input = self.dialog.get_by_label('目标模块')
        self.sat_model_input = self.dialog.get_by_label('卫星型号 (预留)')
        self.cancel_button = self.dialog.get_by_role('button', name='取消')
        self.save_button = self.dialog.get_by_role('button', name='保存')
        self._helper_texts = self.dialog.locator('.MuiFormHelperText-root')
        self.confirm_cancel_button = self.dialog.get_by_role('button', name='取消')
        self.confirm_ok_button = self.dialog.get_by_role('button', name='确定')

        # 展开行和四个详情 Tab；页面同一时刻只展开一行
        self.detail_row = self._rows.filter(
            has=page.get_by_role('tab', name=re.compile(r'^原因'))
        )
        self.cause_tab = self.detail_row.get_by_role('tab', name=re.compile(r'^原因'))
        self.effect_tab = self.detail_row.get_by_role('tab', name=re.compile(r'^影响'))
        self.plan_tab = self.detail_row.get_by_role('tab', name=re.compile(r'^预案'))
        self.rule_tab = self.detail_row.get_by_role('tab', name=re.compile(r'^规则'))

        # 原因 Tab
        self.cause_description_input = self.detail_row.get_by_label('原因描述')
        self.cause_probability_select = self.detail_row.get_by_label('概率')
        self.cause_add_button = self.detail_row.get_by_role('button', name='添加')

        # 影响 Tab
        self.effect_description_input = self.detail_row.get_by_label('影响描述')
        self.effect_level_select = self.detail_row.get_by_label('层级')
        self.effect_add_button = self.detail_row.get_by_role('button', name='添加')

        # 预案 Tab
        self.plan_name_input = self.detail_row.get_by_label('预案名称')
        self.plan_scene_input = self.detail_row.get_by_label('仿真场景ID')
        self.plan_add_button = self.detail_row.get_by_role('button', name='添加')
        self.plan_link_select = self.detail_row.get_by_label('从预案库关联')
        self.plan_link_button = self.detail_row.get_by_role('button', name='关联')
        # 点「关联」之后的二次确认弹窗——专用定位，跟新建/编辑/删除共用的 self.dialog
        # 区分开，靠标题「关联预案」筛出来，不会跟别的弹窗混。
        self.link_confirm_dialog = page.get_by_role('dialog').filter(has_text='关联预案')
        self.link_confirm_ok = self.link_confirm_dialog.get_by_role('button', name='确定')
        self.link_confirm_cancel = self.link_confirm_dialog.get_by_role('button', name='取消')
        # 关联成功后的提示条（MuiSnackbar/Alert，文字是「已关联预案」）
        self.link_success_toast = page.locator('.MuiAlert-root').filter(has_text='已关联预案')

        # 规则 Tab
        self.rule_param_input = self.detail_row.get_by_label('参数编码')
        self.rule_type_select = self.detail_row.get_by_label('类型')
        self.rule_expression_input = self.detail_row.get_by_label('判据表达式')
        self.rule_priority_input = self.detail_row.get_by_label('优先级')
        self.rule_add_button = self.detail_row.get_by_role('button', name='添加')

    # ---------- 表格读取、排序和分页 ----------

    def rows(self):
        """当前页故障数据行；展开后的详情行会被排除。"""
        return self._rows.filter(has=self.table.locator('td').nth(self._COL_CODE - 1))

    def row_by_code(self, code):
        """当前页中编码精确匹配的故障行。"""
        return self._rows.filter(has=self.page.get_by_text(code, exact=True))

    def _column_texts(self, column):
        return [text.strip() for text in self.table.locator(
            f'tbody tr td:nth-child({column})'
        ).all_inner_texts() if text.strip()]

    def codes(self):
        return self._column_texts(self._COL_CODE)

    def row_info(self, code):
        cells = self.row_by_code(code).locator('td').all_inner_texts()
        return {
            'code': cells[self._COL_CODE - 1].strip(),
            'name': cells[self._COL_NAME - 1].strip(),
            'subsystem': cells[self._COL_SUBSYSTEM - 1].strip(),
            'severity': cells[self._COL_SEVERITY - 1].strip(),
            'status': cells[self._COL_STATUS - 1].strip(),
        }

    def _settle(self):
        wait_until_stable(self.page, self.codes)

    def wait_for_data(self):
        self.table.locator('tbody td').first.wait_for(state='visible')
        self._settle()

    def sort_by_code(self):
        self.thead.get_by_text('编码', exact=True).click()
        self._settle()

    def row_count(self):
        return len(self.codes())

    def total_count(self):
        return self._pager.total_count()

    def page_range(self):
        return self._pager.page_range()

    def rows_per_page(self):
        return self._pager.rows_per_page()

    def set_rows_per_page(self, number):
        self._pager.set_rows_per_page(number)

    def goto_next_page(self):
        self._pager.goto_next_page()

    def all_codes(self):
        self._pager.goto_first_page()
        per_page = self.rows_per_page()
        pages = max(1, -(-self.total_count() // per_page))
        result = list(self.codes())
        for _ in range(pages - 1):
            self.goto_next_page()
            result.extend(self.codes())
        return result

    def show_code_across_pages(self, code):
        """从第一页逐页找编码；排序是前端当前页排序，不能拿它代替跨页查找。"""
        self._pager.goto_first_page()
        pages = max(1, -(-self.total_count() // self.rows_per_page()))
        for page_number in range(pages):
            if self.row_by_code(code).count():
                return
            if page_number < pages - 1:
                self.goto_next_page()
        raise AssertionError(f'管理表格全部分页均未找到故障编码：{code}')

    # ---------- 故障新建、导入、编辑和危险操作 ----------

    def open_new_dialog(self):
        self.new_button.click()
        self.dialog.wait_for(state='visible')

    def open_edit_dialog(self, code):
        self._require_test_code(code)
        self.row_by_code(code).locator('button').nth(1).click()
        self.dialog.wait_for(state='visible')

    def fill_form(self, *, code=None, name=None, fault_type=None, subsystem=None,
                  severity=None, description=None, target_module=None, sat_model=None):
        fields = (
            (self.code_input, code), (self.name_input, name),
            (self.type_input, fault_type), (self.description_input, description),
            (self.target_module_input, target_module), (self.sat_model_input, sat_model),
        )
        for field, value in fields:
            if value is not None:
                field.fill(value)
        if subsystem is not None:
            self._select(self.subsystem_select, subsystem)
        if severity is not None:
            self._select(self.severity_select, severity)

    def _select(self, select, option):
        select.click()
        self.page.get_by_role('option', name=option, exact=True).click()

    def helper_texts(self):
        return self._helper_texts.all_inner_texts()

    def save(self):
        self.save_button.click()

    def save_and_response(self, method):
        with self.page.expect_response(
                lambda response: response.request.method == method
                and re.search(r'/api/fault/[^/]+$', response.url)) as info:
            self.save_button.click()
        body = info.value.json()
        self.dialog.wait_for(state='hidden')
        return body.get('data', body)

    def create_fault(self, *, code, name, fault_type, description='', target_module='satellite'):
        self.open_new_dialog()
        self.fill_form(code=code, name=name, fault_type=fault_type,
                       description=description, target_module=target_module)
        with self.page.expect_response(
                lambda response: response.request.method == 'POST'
                and response.url.endswith('/api/fault')) as info:
            self.save_button.click()
        body = info.value.json()
        self.dialog.wait_for(state='hidden')
        return body.get('data', body)

    def import_faults(self, items, filename='autotest-faults.json'):
        payload = {
            'name': filename,
            'mimeType': 'application/json',
            'buffer': json.dumps(items, ensure_ascii=False).encode('utf-8'),
        }
        with self.page.expect_response(
                lambda response: response.request.method == 'POST'
                and response.url.endswith('/api/fault/import')) as info:
            with self.page.expect_file_chooser() as chooser_info:
                self.import_button.click()
            chooser_info.value.set_files(payload)
        body = info.value.json()
        return body.get('data', body)

    def reload_and_show(self, code):
        """导入等操作不会主动刷新列表；重载后排序并把指定测试编码放到当前页。"""
        self.page.reload(wait_until='domcontentloaded')
        self.wait_for_data()
        self.set_rows_per_page(50)
        self.show_code_across_pages(code)
        self.row_by_code(code).wait_for(state='visible')

    def confirm_row_action(self, code, action_index, confirm=False):
        """触发行内废弃(2)/永久删除(3)，处理页面自己的确认弹窗。"""
        self._require_test_code(code)
        self.row_by_code(code).locator('button').nth(action_index).click()
        self.dialog.wait_for(state='visible')
        if confirm:
            self.confirm_ok_button.click()
        else:
            self.confirm_cancel_button.click()
        self.dialog.wait_for(state='hidden')

    # ---------- 展开行：原因、影响、预案和规则 ----------

    def expand(self, code):
        self._require_test_code(code)
        self.row_by_code(code).locator('button').first.click()
        self.detail_row.wait_for(state='visible')

    def open_detail_tab(self, name):
        {'原因': self.cause_tab, '影响': self.effect_tab,
         '预案': self.plan_tab, '规则': self.rule_tab}[name].click()

    def add_cause(self, description, probability='medium'):
        self.cause_description_input.fill(description)
        self._select(self.cause_probability_select, probability)
        return self._click_for_data(self.cause_add_button, 'POST', r'/causes$')

    def edit_cause(self, cause_id, old_description, new_description):
        field = self._input_with_value(old_description)
        field.fill(new_description)
        with self.page.expect_response(lambda r: r.request.method == 'PUT'
                                       and r.url.endswith(f'/causes/{cause_id}')):
            field.press('Tab')

    def delete_cause(self, cause_id, description):
        self._delete_child(self._item_with_input_value(description), f'/causes/{cause_id}')

    def add_effect(self, description, level='local'):
        self.effect_description_input.fill(description)
        if level != 'local':
            visible_option = {
                'parent': '上级影响',
                'final': '最终影响',
            }.get(level, level)
            self._select(self.effect_level_select, visible_option)
        return self._click_for_data(self.effect_add_button, 'POST', r'/effects$')

    def edit_effect(self, effect_id, old_description, new_description):
        field = self._input_with_value(old_description)
        field.fill(new_description)
        with self.page.expect_response(lambda r: r.request.method == 'PUT'
                                       and r.url.endswith(f'/effects/{effect_id}')):
            field.press('Tab')

    def delete_effect(self, effect_id, description):
        self._delete_child(self._item_with_input_value(description), f'/effects/{effect_id}')

    def add_plan(self, name, scene_id):
        self.plan_name_input.fill(name)
        self.plan_scene_input.fill(scene_id)
        return self._click_for_data(self.plan_add_button, 'POST', r'/api/fault/plans$')

    def open_link_confirm(self, option_text):
        """从预案库下拉选一条预案、点「关联」，把二次确认弹窗打出来，停在这一步不动。
        「这条预案原来挂哪个故障都行，关联后会从原来那个故障上摘掉」这句提示就是在
        这个弹窗里，调用方可以自己接着点确定或取消。"""
        self.plan_link_select.click()
        self.page.get_by_role('option').filter(has_text=option_text).click()
        self.plan_link_button.click()
        self.link_confirm_dialog.wait_for(state='visible')

    def link_plan(self, plan_id, option_text):
        """把 open_link_confirm 走到底：点确定，等接口真的发出去、弹窗关掉、
        成功提示条「已关联预案」出现。返回接口状态码。"""
        self.open_link_confirm(option_text)
        with self.page.expect_response(lambda r: r.request.method in ('POST', 'PUT', 'PATCH')
                                       and '/api/fault/plans' in r.url) as info:
            self.link_confirm_ok.click()
        self.link_confirm_dialog.wait_for(state='hidden')
        self.link_success_toast.wait_for(state='visible', timeout=5000)
        return info.value.status

    def cancel_link_plan(self, option_text):
        """把 open_link_confirm 走到底，但点取消——用来验证「取消不改数据」。"""
        self.open_link_confirm(option_text)
        self.link_confirm_cancel.click()
        self.link_confirm_dialog.wait_for(state='hidden')

    def delete_plan(self, plan_id, name):
        self._delete_child(self._item_with_text_and_button(name, '编辑'),
                           f'/api/fault/plans/{plan_id}')

    def add_rule(self, param_code, expression, rule_type='threshold', priority=1):
        self.rule_param_input.fill(param_code)
        self._select(self.rule_type_select, rule_type)
        self.rule_expression_input.fill(expression)
        self.rule_priority_input.fill(str(priority))
        return self._click_for_data(self.rule_add_button, 'POST', r'/rules$')

    def test_rule(self, rule_id, param_code, value):
        item = self._item_with_text_and_button(param_code, '测试')
        item.get_by_placeholder('输入测试值...').fill(str(value))
        with self.page.expect_response(lambda r: r.request.method == 'POST'
                                       and r.url.endswith(f'/rules/{rule_id}/test')):
            item.get_by_role('button', name='测试').click()
        return item

    def delete_rule(self, rule_id, param_code):
        self._delete_child(self._item_with_text_and_button(param_code, '测试'),
                           f'/rules/{rule_id}')

    def _click_for_data(self, button, method, url_pattern):
        with self.page.expect_response(lambda r: r.request.method == method
                                       and re.search(url_pattern, r.url)) as info:
            button.click()
        body = info.value.json()
        return body.get('data', body)

    def _item_with_input_value(self, value):
        field = self._input_with_value(value)
        return field.locator('xpath=ancestor::div[.//button][1]')

    def _input_with_value(self, value):
        """按当前 value 找原因/影响的行内编辑框。"""
        return self.detail_row.locator(f'input[value="{value}"]')

    def _item_with_text_and_button(self, text, button_name):
        text_node = self.detail_row.get_by_text(text, exact=True)
        return text_node.locator(
            f'xpath=ancestor::div[.//button[normalize-space()="{button_name}"]][1]'
        )

    def _delete_child(self, item, url_suffix):
        button = item.locator('button:has([data-testid="DeleteIcon"])')
        button.click()
        self.dialog.wait_for(state='visible')
        with self.page.expect_response(lambda r: r.request.method == 'DELETE'
                                       and r.url.endswith(url_suffix)):
            self.confirm_ok_button.click()
        self.dialog.wait_for(state='hidden')

    # ---------- 仅供 fixture 安全还原/清理 AUTOTEST 数据 ----------

    def api_fault(self, fault_id):
        payload = api_fetch(self.page, f'/api/fault/{fault_id}') or {}
        data = payload.get('data', payload)
        if not data:
            return None
        return data.get('fault', data)

    def api_update(self, fault_id, expected_code, body):
        current = self.api_fault(fault_id)
        self._require_matching_code(current, expected_code)
        return api_fetch(self.page, f'/api/fault/{fault_id}', method='PUT', body=body)

    def api_delete(self, fault_id, expected_code):
        current = self.api_fault(fault_id)
        if not current or not current.get('faultCode'):
            return
        self._require_matching_code(current, expected_code)
        api_fetch(self.page, f'/api/fault/{fault_id}', method='DELETE')

    @classmethod
    def _require_test_code(cls, code):
        if not code.startswith(cls.TEST_CODE_PREFIXES):
            raise ValueError(f'拒绝操作非测试故障：{code}')

    @classmethod
    def _require_matching_code(cls, record, expected_code):
        actual_code = record.get('faultCode')
        cls._require_test_code(actual_code or '')
        if actual_code != expected_code:
            raise ValueError(
                f'操作保护：实际编码 {actual_code!r} != 预期 {expected_code!r}'
            )
