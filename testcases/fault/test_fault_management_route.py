import uuid

import allure
import pytest
from playwright.sync_api import expect

from common.dm8_client import fetch_rows
from pages.fault.management_route_page import FaultManagementRoutePage


def _unique_code(kind):
    return f'AUTOTEST-{kind}-{uuid.uuid4().hex[:10].upper()}'


def _created_id(payload):
    """兼容各子项接口直接返回对象或再包一层对象的响应。"""
    if isinstance(payload, dict):
        if payload.get('id'):
            return payload['id']
        for value in payload.values():
            found = _created_id(value)
            if found:
                return found
    return None


def _fault_rows(where):
    return fetch_rows(
        'SELECT "id", "faultCode", "faultName", "description", "targetModule", '
        '"subsystem", "severity", "status" '
        f'FROM SARSAT_SCHED."fault_catalog" WHERE {where}'
    )


@allure.feature('故障/预案库')
@allure.story('独立路由管理页')
@allure.title('管理表格展示完整列头，登记的 AUTOTEST 故障与数据库一致')
@allure.severity(allure.severity_level.BLOCKER)
def test_route_management_table_matches_registered_faults(
        management_route_page, fault_test_records):
    route = management_route_page

    headers = route.thead.locator('th').all_inner_texts()
    for expected in FaultManagementRoutePage.TABLE_HEADERS:
        assert expected in [text.strip() for text in headers]

    for record in fault_test_records:
        row = route.row_by_code(record['code'])
        expect(row).to_have_count(1)
        info = route.row_info(record['code'])
        db = _fault_rows(f'"id" = \'{record["id"]}\'')[0]
        assert info['code'] == db['faultCode'] == record['code']
        assert info['name'] == db['faultName'] == record['name']


@allure.feature('故障/预案库')
@allure.story('独立路由管理页')
@allure.title('编码表头两次排序覆盖全量分页，升序和降序都正确')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.xfail(
    strict=True,
    reason='已确认产品缺陷：编码排序只重排当前分页，第二页仍保留原分页数据',
)
def test_route_management_code_sort_is_global(management_route_page):
    route = management_route_page

    route.sort_by_code()
    first_order = route.all_codes()
    route.sort_by_code()
    second_order = route.all_codes()

    assert first_order in (sorted(first_order), sorted(first_order, reverse=True))
    assert second_order == list(reversed(first_order))


@allure.feature('故障/预案库')
@allure.story('独立路由管理页')
@allure.title('表格支持每页 10 行和下一页，页码及数据同步变化')
@allure.severity(allure.severity_level.CRITICAL)
def test_route_management_pagination(management_route_page):
    route = management_route_page
    total = route.total_count()
    route.set_rows_per_page(20)
    assert route.rows_per_page() == 20
    assert route.row_count() == min(20, total)
    assert route.page_range() == (1, min(20, total))
    if total > 20:
        first_page = set(route.codes())
        route.goto_next_page()
        assert route.page_range()[0] == 21
        assert not first_page.intersection(route.codes())


@allure.feature('故障/预案库')
@allure.story('独立路由管理页')
@allure.title('新建故障直接保存时，编码、名称和类型均提示必填且不提交')
@allure.severity(allure.severity_level.CRITICAL)
def test_route_management_create_required_fields(management_route_page):
    route = management_route_page
    route.open_new_dialog()
    route.save()

    messages = route.helper_texts()
    assert any('故障编码' in text for text in messages), messages
    assert any('故障名称' in text for text in messages), messages
    assert any('故障类型' in text for text in messages), messages
    expect(route.dialog).to_be_visible()
    route.cancel_button.click()


@allure.feature('故障/预案库')
@allure.story('独立路由管理页')
@allure.title('从界面新建 AUTOTEST 故障后，表格和 DM8 均保存准确字段')
@allure.severity(allure.severity_level.BLOCKER)
def test_route_management_create_persists_to_dm8(management_route_page):
    route = management_route_page
    code = _unique_code('CREATE')
    created = None
    try:
        created = route.create_fault(
            code=code,
            name='自动化-路由页新建',
            fault_type='autotest_route_create',
            description='AUTOTEST 路由页 UI 新建',
            target_module='AUTOTEST_SANDBOX',
        )
        fault_id = _created_id(created)
        assert fault_id, created

        expect(route.row_by_code(code)).to_have_count(1)
        rows = _fault_rows(f'"id" = \'{fault_id}\'')
        assert len(rows) == 1
        assert rows[0]['faultCode'] == code
        assert rows[0]['faultName'] == '自动化-路由页新建'
        assert rows[0]['description'] == 'AUTOTEST 路由页 UI 新建'
        assert rows[0]['targetModule'] == 'AUTOTEST_SANDBOX'
    finally:
        if created and _created_id(created):
            route.api_delete(_created_id(created), code)


@allure.feature('故障/预案库')
@allure.story('独立路由管理页')
@allure.title('批量导入 JSON 后，AUTOTEST 故障写入 DM8 且出现在表格')
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.xfail(
    strict=True,
    reason='已确认产品缺陷：导入记录已写入 DM8，但管理页重载并遍历全部分页仍不可见',
)
def test_route_management_import_persists_to_dm8(management_route_page):
    route = management_route_page
    code = _unique_code('IMPORT')
    fault_id = None
    try:
        route.import_faults([{
            'faultCode': code,
            'faultName': '自动化-JSON导入',
            'faultType': 'autotest_route_import',
            'subsystem': 'power',
            'severity': 'III',
            'description': 'AUTOTEST JSON 导入',
            'targetModule': 'AUTOTEST_SANDBOX',
            'status': 'active',
        }])

        rows = _fault_rows(f'"faultCode" = \'{code}\'')
        assert len(rows) == 1
        fault_id = rows[0]['id']
        assert rows[0]['faultName'] == '自动化-JSON导入'
        assert rows[0]['description'] == 'AUTOTEST JSON 导入'
        route.reload_and_show(code)
        expect(route.row_by_code(code)).to_have_count(1)
    finally:
        if fault_id:
            route.api_delete(fault_id, code)


@allure.feature('故障/预案库')
@allure.story('独立路由管理页')
@allure.title('编辑登记的 AUTOTEST 故障后，表格与 DM8 同步更新并在用例后还原')
@allure.severity(allure.severity_level.BLOCKER)
def test_route_management_edit_updates_dm8(
        management_route_page, restorable_route_fault):
    route = management_route_page
    record = restorable_route_fault
    new_name = f'自动化编辑-{uuid.uuid4().hex[:6]}'
    new_description = f'AUTOTEST-EDIT-{uuid.uuid4().hex}'

    route.open_edit_dialog(record['code'])
    expect(route.dialog_title).to_have_text('编辑故障')
    assert route.code_input.input_value() == record['code']
    route.fill_form(name=new_name, description=new_description,
                    target_module='AUTOTEST_EDITED')
    route.save_and_response('PUT')

    assert route.row_info(record['code'])['name'] == new_name
    rows = _fault_rows(f'"id" = \'{record["id"]}\'')
    assert rows[0]['faultName'] == new_name
    assert rows[0]['description'] == new_description
    assert rows[0]['targetModule'] == 'AUTOTEST_EDITED'


@allure.feature('故障/预案库')
@allure.story('独立路由管理页-原因')
@allure.title('原因经界面新增、失焦编辑和删除后，DM8 每一步均同步')
@allure.severity(allure.severity_level.BLOCKER)
def test_route_management_cause_crud(
        management_route_page, route_test_fault, route_mutation_scope):
    route = management_route_page
    original = route_mutation_scope + '-CAUSE'
    updated = original + '-UPDATED'
    route.expand(route_test_fault['code'])

    created = route.add_cause(original, probability='high')
    cause_id = _created_id(created)
    assert cause_id, created
    rows = fetch_rows(
        'SELECT "causeDescription", "probability", "fault_id" '
        f'FROM SARSAT_SCHED."fault_causes" WHERE "id" = \'{cause_id}\''
    )
    assert rows == [{
        'causeDescription': original,
        'probability': 'high',
        'fault_id': route_test_fault['id'],
    }]

    route.edit_cause(cause_id, original, updated)
    rows = fetch_rows(
        'SELECT "causeDescription" FROM SARSAT_SCHED."fault_causes" '
        f'WHERE "id" = \'{cause_id}\''
    )
    assert rows[0]['causeDescription'] == updated

    route.delete_cause(cause_id, updated)
    assert not fetch_rows(
        f'SELECT "id" FROM SARSAT_SCHED."fault_causes" WHERE "id" = \'{cause_id}\''
    )


@allure.feature('故障/预案库')
@allure.story('独立路由管理页-影响')
@allure.title('影响经界面新增、失焦编辑和删除后，DM8 每一步均同步')
@allure.severity(allure.severity_level.BLOCKER)
def test_route_management_effect_crud(
        management_route_page, route_test_fault, route_mutation_scope):
    route = management_route_page
    original = route_mutation_scope + '-EFFECT'
    updated = original + '-UPDATED'
    route.expand(route_test_fault['code'])
    route.open_detail_tab('影响')

    created = route.add_effect(original, level='local')
    effect_id = _created_id(created)
    assert effect_id, created
    rows = fetch_rows(
        'SELECT "effectDescription", "LEVEL", "fault_id" '
        f'FROM SARSAT_SCHED."fault_effects" WHERE "id" = \'{effect_id}\''
    )
    assert rows == [{
        'effectDescription': original,
        'LEVEL': 'local',
        'fault_id': route_test_fault['id'],
    }]

    route.edit_effect(effect_id, original, updated)
    rows = fetch_rows(
        'SELECT "effectDescription" FROM SARSAT_SCHED."fault_effects" '
        f'WHERE "id" = \'{effect_id}\''
    )
    assert rows[0]['effectDescription'] == updated

    route.delete_effect(effect_id, updated)
    assert not fetch_rows(
        f'SELECT "id" FROM SARSAT_SCHED."fault_effects" WHERE "id" = \'{effect_id}\''
    )


@allure.feature('故障/预案库')
@allure.story('独立路由管理页-预案')
@allure.title('处置预案经界面新增和删除后，名称、场景及关联故障同步到 DM8')
@allure.severity(allure.severity_level.BLOCKER)
def test_route_management_plan_create_delete(
        management_route_page, route_test_fault, route_mutation_scope):
    route = management_route_page
    name = route_mutation_scope + '-PLAN'
    scene_id = 'AUTOTEST-SCENE-01'
    route.expand(route_test_fault['code'])
    route.open_detail_tab('预案')

    created = route.add_plan(name, scene_id)
    plan_id = _created_id(created)
    assert plan_id, created
    rows = fetch_rows(
        'SELECT "name", "simSceneId", "faultId" '
        f'FROM SARSAT_SCHED."fault_plans" WHERE "id" = \'{plan_id}\''
    )
    assert rows == [{
        'name': name,
        'simSceneId': scene_id,
        'faultId': route_test_fault['id'],
    }]
    expect(route.detail_row.get_by_text(name, exact=True)).to_be_visible()

    route.delete_plan(plan_id, name)
    assert not fetch_rows(
        f'SELECT "id" FROM SARSAT_SCHED."fault_plans" WHERE "id" = \'{plan_id}\''
    )


@allure.feature('故障/预案库')
@allure.story('独立路由管理页-预案')
@allure.title('把预案从故障 A 改关联到故障 B，DM8 的 faultId 跟着变，两边界面都同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_route_management_link_existing_plan(management_route_page, route_mutation_scope):
    # 「从预案库关联」这个下拉框列的是全部预案（不是只列没挂故障的），本意是把一条
    # 预案从原来的故障改挂到另一个故障——不是「关联一条从没有过故障的预案」，正常
    # 业务里也不存在没有故障的预案（预案库本身没有新建入口，唯一建预案的方式是在
    # 某个故障详情里点「添加」，删故障会连它名下的预案一起删，不会留孤儿）。
    # 所以这里用两个真实故障 A/B 搭场景，而不是拿接口硬造一条 faultId=None 的假数据。
    route = management_route_page
    code_a, code_b = route_mutation_scope + '-A', route_mutation_scope + '-B'
    fault_a = route.create_fault(
        code=code_a, name='关联改绑测试-故障A', fault_type='autotest_link_a',
        target_module='AUTOTEST_SANDBOX',
    )
    fault_a_id = _created_id(fault_a)
    fault_b = route.create_fault(
        code=code_b, name='关联改绑测试-故障B', fault_type='autotest_link_b',
        target_module='AUTOTEST_SANDBOX',
    )
    fault_b_id = _created_id(fault_b)

    plan_name = route_mutation_scope + '-LINK-PLAN'
    route.expand(code_a)
    route.open_detail_tab('预案')
    plan = route.add_plan(plan_name, 'AUTOTEST-LINK-SCENE')
    plan_id = _created_id(plan)

    # 切到故障 B，把这条（当前挂在 A 下的）预案改关联过来——先只走到确认弹窗，
    # 断言弹窗文案本身对不对，再点确定
    route.page.keyboard.press('Escape')
    route.expand(code_b)
    route.open_detail_tab('预案')
    route.open_link_confirm(plan_name)
    expect(route.link_confirm_dialog, '确认弹窗应该点名要关联的预案和原来挂的故障').to_contain_text(
        f'{plan_name}')
    expect(route.link_confirm_dialog).to_contain_text(code_a)
    with route.page.expect_response(lambda r: r.request.method in ('POST', 'PUT', 'PATCH')
                                     and '/api/fault/plans' in r.url) as info:
        route.link_confirm_ok.click()
    assert info.value.status == 200, f'关联接口应该 200，实际 {info.value.status}'
    route.link_confirm_dialog.wait_for(state='hidden')
    expect(route.link_success_toast, '关联成功后应该有「已关联预案」提示').to_be_visible()

    rows = fetch_rows(f'SELECT "faultId" FROM SARSAT_SCHED."fault_plans" WHERE "id" = \'{plan_id}\'')
    assert rows[0]['faultId'] == fault_b_id, f'改关联后 faultId 应该指向故障B，实际 {rows[0]["faultId"]}'
    expect(route.detail_row.get_by_text(plan_name, exact=True)).to_be_visible()

    # 原来的故障 A 名下，这条预案应该已经不在了
    route.page.keyboard.press('Escape')
    route.expand(code_a)
    route.open_detail_tab('预案')
    expect(route.detail_row.get_by_text(plan_name, exact=True)).to_have_count(0)

    route.api_delete(fault_a_id, code_a)
    route.api_delete(fault_b_id, code_b)


@allure.feature('故障/预案库')
@allure.story('独立路由管理页-预案')
@allure.title('关联预案的确认弹窗点取消，数据库和两边界面都不该变')
@allure.severity(allure.severity_level.NORMAL)
def test_route_management_link_plan_cancel(management_route_page, route_mutation_scope):
    route = management_route_page
    code_a, code_b = route_mutation_scope + '-CANCELA', route_mutation_scope + '-CANCELB'
    fault_a = route.create_fault(
        code=code_a, name='关联取消测试-故障A', fault_type='autotest_link_cancel_a',
        target_module='AUTOTEST_SANDBOX',
    )
    fault_a_id = _created_id(fault_a)
    fault_b = route.create_fault(
        code=code_b, name='关联取消测试-故障B', fault_type='autotest_link_cancel_b',
        target_module='AUTOTEST_SANDBOX',
    )
    fault_b_id = _created_id(fault_b)

    plan_name = route_mutation_scope + '-CANCEL-PLAN'
    route.expand(code_a)
    route.open_detail_tab('预案')
    plan = route.add_plan(plan_name, 'AUTOTEST-CANCEL-SCENE')
    plan_id = _created_id(plan)

    route.page.keyboard.press('Escape')
    route.expand(code_b)
    route.open_detail_tab('预案')
    route.cancel_link_plan(plan_name)

    # 数据库：faultId 应该还是 A，没被改动
    rows = fetch_rows(f'SELECT "faultId" FROM SARSAT_SCHED."fault_plans" WHERE "id" = \'{plan_id}\'')
    assert rows[0]['faultId'] == fault_a_id, f'点取消不该改数据，实际 faultId 变成了 {rows[0]["faultId"]}'
    # 前端：B 这边看不到，A 那边还在
    expect(route.detail_row.get_by_text(plan_name, exact=True)).to_have_count(0)
    route.page.keyboard.press('Escape')
    route.expand(code_a)
    route.open_detail_tab('预案')
    expect(route.detail_row.get_by_text(plan_name, exact=True)).to_be_visible()

    route.api_delete(fault_a_id, code_a)
    route.api_delete(fault_b_id, code_b)


@allure.feature('故障/预案库')
@allure.story('独立路由管理页-规则')
@allure.title('遥测规则新增、试算和删除均有可观察结果，DM8 字段同步')
@allure.severity(allure.severity_level.BLOCKER)
def test_route_management_rule_add_test_delete(
        management_route_page, route_test_fault, route_mutation_scope):
    route = management_route_page
    param_code = route_mutation_scope + '-PARAM'
    route.expand(route_test_fault['code'])
    route.open_detail_tab('规则')

    created = route.add_rule(param_code, '> 50', rule_type='threshold', priority=3)
    rule_id = _created_id(created)
    assert rule_id, created
    rows = fetch_rows(
        'SELECT "paramCode", "conditionType", "conditionExpr", "priority", "fault_id" '
        f'FROM SARSAT_SCHED."fault_telemetry_rules" WHERE "id" = \'{rule_id}\''
    )
    assert rows == [{
        'paramCode': param_code,
        'conditionType': 'threshold',
        'conditionExpr': '> 50',
        'priority': '3',
        'fault_id': route_test_fault['id'],
    }]

    item = route.test_rule(rule_id, param_code, 60)
    expect(item.get_by_text('命中', exact=False)).to_be_visible()

    route.delete_rule(rule_id, param_code)
    assert not fetch_rows(
        'SELECT "id" FROM SARSAT_SCHED."fault_telemetry_rules" '
        f'WHERE "id" = \'{rule_id}\''
    )


@allure.feature('故障/预案库')
@allure.story('独立路由管理页')
@allure.title('废弃和永久删除点取消不改库；临时 AUTOTEST 故障确认删除后才消失')
@allure.severity(allure.severity_level.BLOCKER)
def test_route_management_destructive_confirmations(management_route_page):
    route = management_route_page
    code = _unique_code('DELETE')
    created = route.create_fault(
        code=code,
        name='自动化-删除确认',
        fault_type='autotest_delete_confirmation',
    )
    fault_id = _created_id(created)
    assert fault_id, created
    try:
        route.confirm_row_action(code, action_index=2, confirm=False)
        route.confirm_row_action(code, action_index=3, confirm=False)
        rows = _fault_rows(f'"id" = \'{fault_id}\'')
        assert len(rows) == 1
        assert rows[0]['status'] == 'active'
        expect(route.row_by_code(code)).to_have_count(1)

        route.confirm_row_action(code, action_index=3, confirm=True)
        expect(route.row_by_code(code)).to_have_count(0)
        assert not _fault_rows(f'"id" = \'{fault_id}\'')
    finally:
        route.api_delete(fault_id, code)
