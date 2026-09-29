import uuid

import allure
import pytest
from playwright.sync_api import expect

from pages.fault.fault_catalog_page import FaultCatalogPage
from pages.fault.management_page import FaultManagementPage


def _unique_code():
    return f'ZZTEST-{uuid.uuid4().hex[:8].upper()}'


@allure.feature('故障/预案库')
@allure.story('管理')
@allure.title('管理页的故障卡片数量和目录页的总数一致')
@allure.severity(allure.severity_level.CRITICAL)
def test_management_count_matches_catalog(fault_library_page):
    # 两个子标签共用同一个 page，不能同时依赖 catalog_page / management_page 两个 fixture
    # （后进的会把 page 切到自己的子标签），改成用例里手动依次切换。
    page = fault_library_page.page

    fault_library_page.open_tab('目录')
    cp = FaultCatalogPage(page)
    cp.table.wait_for(state='visible')
    total = cp.total_count()

    fault_library_page.open_tab('管理')
    mp = FaultManagementPage(page)
    mp.cards().first.wait_for(state='visible')

    # 断言：管理页卡片数 == 目录页「共 N 条」
    assert mp.cards().count() == total, f'管理页 {mp.cards().count()} 张卡片，目录页共 {total} 条，对不上'


@allure.feature('故障/预案库')
@allure.story('管理')
@allure.title('「新建故障」直接点保存：故障编码/名称/类型 必填项都有提示')
@allure.severity(allure.severity_level.CRITICAL)
def test_management_new_requires_fields(management_page):
    mp = management_page
    mp.open_new_dialog()

    mp.save()

    # 断言：三个必填字段都提示了，弹窗还开着（没真的提交）
    texts = mp.helper_texts()
    assert any('故障编码' in t for t in texts), texts
    assert any('故障名称' in t for t in texts), texts
    assert any('故障类型' in t for t in texts), texts
    expect(mp.dialog).to_be_visible()

    mp.cancel()


@allure.feature('故障/预案库')
@allure.story('管理')
@allure.title('「新建故障」填一个已存在的故障编码：提示编码已存在，弹窗不关')
@allure.severity(allure.severity_level.CRITICAL)
def test_management_new_duplicate_code(management_page):
    mp = management_page
    dup_code = mp.card_code(0)          # 拿列表里已有的一个编码当重复值

    mp.open_new_dialog()
    mp.fill_form(code=dup_code, name='重复编码测试', fault_type='dup_test_type')
    mp.save()

    # 断言：提示编码已存在（带上具体编码），弹窗没关
    texts = mp.helper_texts()
    assert any(dup_code in t and '已存在' in t for t in texts), texts
    expect(mp.dialog).to_be_visible()

    mp.cancel()


@allure.feature('故障/预案库')
@allure.story('管理')
@allure.title('新建故障（分系统={subsystem}）：保存后管理数量 +1，卡片内容和所填一致')
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.parametrize('subsystem', FaultManagementPage.SUBSYSTEMS)
def test_management_create_fault(management_page, subsystem):
    mp = management_page
    before = mp.cards().count()
    code = _unique_code()
    name = f'自动化新建-{subsystem}'

    mp.open_new_dialog()
    mp.fill_form(code=code, name=name, fault_type=f'auto_create_{subsystem}', subsystem=subsystem)
    created_id = mp.save_and_get_created_id()

    # 断言：弹窗关闭、管理数量 +1
    expect(mp.dialog).to_have_count(0)
    assert mp.cards().count() == before + 1
    # 断言：新卡片内容（名称/分系统）和刚填的一致
    info = mp.card_info(code)
    assert info['name'] == name
    assert info['subsystem'] == subsystem

    mp.api_delete(created_id, code)  # 清理：只允许删除这条刚创建的测试数据


@allure.feature('故障/预案库')
@allure.story('管理')
@allure.title('新建故障填了内容后点取消：不会保存，管理数量不变')
@allure.severity(allure.severity_level.CRITICAL)
def test_management_new_cancel_discards(management_page):
    mp = management_page
    before = mp.cards().count()
    code = _unique_code()

    mp.open_new_dialog()
    mp.fill_form(code=code, name='取消不应该被保存', fault_type='cancel_test_type')
    mp.cancel()

    # 断言：弹窗关了、数量没变、这张卡没出现过
    expect(mp.dialog).to_have_count(0)
    assert mp.cards().count() == before
    assert mp.card_by_code(code).count() == 0


@allure.feature('故障/预案库')
@allure.story('管理')
@allure.title('编辑已有故障：弹窗回显原值；名称清空提示必填，编码改成别的已有编码提示重复')
@allure.severity(allure.severity_level.CRITICAL)
def test_management_edit_validation(management_page, seeded_fault):
    mp = management_page
    code = seeded_fault['faultCode']
    other_code = mp.card_code(0)        # 拿一个非自己的已有编码当「重复」值

    mp.open_edit_dialog(code)
    # 断言：编辑弹窗标题不同于新建，字段回显的是这条已有数据
    expect(mp.dialog_title).to_have_text('编辑故障')
    assert mp.code_input.input_value() == code
    assert mp.name_input.input_value() == seeded_fault['faultName']

    # 名称清空 → 必填提示
    mp.fill_form(name='')
    mp.save()
    assert any('故障名称' in t for t in mp.helper_texts())
    expect(mp.dialog).to_be_visible()

    # 名称补回去、编码改成别的已有编码 → 重复提示
    mp.fill_form(name='恢复名称再改编码', code=other_code)
    mp.save()
    texts = mp.helper_texts()
    assert any(other_code in t and '已存在' in t for t in texts), texts
    expect(mp.dialog).to_be_visible()

    mp.cancel()
    # 断言：以上都没保存成功，卡片还是原来的名字
    assert mp.card_info(code)['name'] == seeded_fault['faultName']


@allure.feature('故障/预案库')
@allure.story('管理')
@allure.title('编辑已有故障：改字段点取消不生效，点保存才真的改')
@allure.severity(allure.severity_level.CRITICAL)
def test_management_edit_cancel_then_save(management_page, seeded_fault):
    mp = management_page
    code = seeded_fault['faultCode']
    original_name = seeded_fault['faultName']

    # 改名字点取消：卡片内容不变
    mp.open_edit_dialog(code)
    mp.fill_form(name='改了但要取消')
    mp.cancel()
    assert mp.card_info(code)['name'] == original_name

    # 改名字点保存：卡片内容真的变了
    new_name = '改了并且保存了'
    mp.open_edit_dialog(code)
    mp.fill_form(name=new_name)
    mp.save()
    expect(mp.dialog).to_have_count(0)
    assert mp.card_info(code)['name'] == new_name


@allure.feature('故障/预案库')
@allure.story('管理')
@allure.title('废弃：原生确认弹窗，点取消卡片还在，点确定卡片从管理列表消失')
@allure.severity(allure.severity_level.CRITICAL)
def test_management_discard_confirm_flow(management_page, seeded_fault):
    mp = management_page
    code = seeded_fault['faultCode']

    # 点取消：卡片还在
    mp.discard(code, confirm=False)
    expect(mp.card_by_code(code)).to_have_count(1)

    # 点确定：废弃后不再参与定位匹配，管理页也不再展示这条
    mp.discard(code, confirm=True)
    expect(mp.card_by_code(code)).to_have_count(0)


@allure.feature('故障/预案库')
@allure.story('管理')
@allure.title('删除：原生确认弹窗，点取消卡片还在、数量不变，点确定卡片消失、数量 -1')
@allure.severity(allure.severity_level.CRITICAL)
def test_management_delete_confirm_flow(management_page, seeded_fault):
    mp = management_page
    code = seeded_fault['faultCode']
    before = mp.cards().count()

    # 点取消：卡片还在，数量不变
    mp.delete(code, confirm=False)
    expect(mp.card_by_code(code)).to_have_count(1)
    assert mp.cards().count() == before

    # 点确定：永久删除，卡片消失、数量 -1
    mp.delete(code, confirm=True)
    expect(mp.card_by_code(code)).to_have_count(0)
    assert mp.cards().count() == before - 1
