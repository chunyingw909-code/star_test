import uuid

import allure
import pytest
from playwright.sync_api import expect

from pages.admin.user_management_page import UserManagementPage


def _unique_username():
    return f'zztest-{uuid.uuid4().hex[:8]}'


# 用户管理页：跟故障管理页面同一套设计——除了「创建用户」这条本身测的就是新建流程走
# UI，其余要用到「已存在账号」的用例都用 seeded_test_user（接口建）当靶子，接口清理。


@allure.feature('用户管理')
@allure.story('入口')
@allure.title('点头像、菜单里点「用户管理」，进到用户管理页面')
@allure.severity(allure.severity_level.BLOCKER)
def test_user_management_opens_via_avatar_menu(home_page):
    ump = UserManagementPage(home_page)
    ump.open_via_avatar_menu()

    # 断言：进到了用户管理页面（标题 + 表格都在）
    expect(ump.heading).to_be_visible()
    expect(ump.rows().first).to_be_visible()


@allure.feature('用户管理')
@allure.story('列表')
@allure.title('列表里能看到已存在的 admin 账号，角色是管理员')
@allure.severity(allure.severity_level.CRITICAL)
def test_user_management_lists_admin(user_management_page):
    ump = user_management_page
    info = ump.row_info('admin')

    # 断言：admin 这一行角色是「管理员」、状态是「启用」
    assert info['role'] == '管理员', info
    assert info['status'] == '启用', info


@allure.feature('用户管理')
@allure.story('列表')
@allure.title('角色 / 状态 筛选下拉的选项固定')
@allure.severity(allure.severity_level.NORMAL)
def test_user_management_filter_options(user_management_page):
    ump = user_management_page

    # 断言：角色筛选 =「全部」+ 用户/管理员
    assert ump.role_options() == ['全部'] + list(UserManagementPage.ROLES)
    # 断言：状态筛选 =「全部」+ 启用/禁用
    assert ump.status_options() == ['全部'] + list(UserManagementPage.STATUSES)


@allure.feature('用户管理')
@allure.story('创建')
@allure.title('「创建用户」直接点保存：用户名和初始密码必填的提示都出现')
@allure.severity(allure.severity_level.CRITICAL)
def test_user_management_new_requires_fields(user_management_page):
    ump = user_management_page
    ump.open_create_dialog()

    ump.save()

    # 断言：提示用户名和初始密码必填，弹窗还开着（没真的提交）
    assert '用户名和初始密码必填' in (ump.error_text() or ''), ump.error_text()
    expect(ump.dialog).to_be_visible()

    ump.close_dialog()


@allure.feature('用户管理')
@allure.story('创建')
@allure.title('「创建用户」填一个已存在的用户名：提示用户名已存在，弹窗不关')
@allure.severity(allure.severity_level.CRITICAL)
def test_user_management_new_duplicate_username(user_management_page):
    ump = user_management_page
    ump.open_create_dialog()
    ump.fill_create_form(username='admin', display_name='重复用户名测试', password='Test1234')

    ump.save()

    # 断言：提示用户名已存在，弹窗没关
    assert '用户名已存在' in (ump.error_text() or ''), ump.error_text()
    expect(ump.dialog).to_be_visible()

    ump.close_dialog()


@allure.feature('用户管理')
@allure.story('创建')
@allure.title('初始密码「{label}」：提示密码格式不对，弹窗不关')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize('label,password', [
    ('太短', 'Ab1'),
    ('没数字', 'nodigitpw'),
    ('没字母', '12345678'),
])
def test_user_management_new_weak_password(user_management_page, label, password):
    ump = user_management_page
    ump.open_create_dialog()
    ump.fill_create_form(username=_unique_username(), display_name='弱密码测试', password=password)

    ump.save()

    # 断言：提示密码至少 8 位且需包含字母和数字，弹窗没关
    assert '密码至少 8 位' in (ump.error_text() or ''), ump.error_text()
    expect(ump.dialog).to_be_visible()

    ump.close_dialog()


@allure.feature('用户管理')
@allure.story('创建')
@allure.title('创建用户（角色={role}）：保存后列表里出现这一行，内容和所填一致')
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.parametrize('role', UserManagementPage.ROLES)
def test_user_management_create_user(user_management_page, role):
    ump = user_management_page
    username = _unique_username()
    display_name = f'自动化新建-{role}'

    ump.open_create_dialog()
    ump.fill_create_form(username=username, display_name=display_name, password='Test1234', role=role)
    created_id = ump.save_and_get_created_id()
    expect(ump.dialog).to_have_count(0)

    ump.page.reload(wait_until='networkidle')
    ump.rows().first.wait_for(state='visible')

    # 断言：新账号内容（显示名/角色）和刚填的一致，且首次登录待改密
    info = ump.row_info(username)
    assert info['display_name'] == display_name
    assert info['role'] == role
    assert info['pending_pwd_change'] is True

    ump.api_delete(created_id)  # 清理：这条是走 UI 新建流程本身产生的测试数据


@allure.feature('用户管理')
@allure.story('创建')
@allure.title('创建用户填了内容后按 Escape：不会保存，列表里不出现这一行')
@allure.severity(allure.severity_level.CRITICAL)
def test_user_management_new_cancel_discards(user_management_page):
    ump = user_management_page
    username = _unique_username()

    ump.open_create_dialog()
    ump.fill_create_form(username=username, display_name='取消不应该被保存', password='Test1234')
    ump.close_dialog()

    # 断言：弹窗关了、这个用户名没出现过
    expect(ump.dialog).to_have_count(0)
    assert ump.row_by_username(username).count() == 0


@allure.feature('用户管理')
@allure.story('编辑')
@allure.title('编辑已有账号：弹窗回显原值，用户名不能改')
@allure.severity(allure.severity_level.CRITICAL)
def test_user_management_edit_shows_current_values(seeded_test_user, user_management_page):
    ump = user_management_page
    username = seeded_test_user['username']

    ump.open_edit_dialog(username)

    # 断言：编辑弹窗标题带用户名，用户名字段回显且不可编辑，显示名回显
    expect(ump.dialog_title).to_contain_text(username)
    assert ump.username_input.input_value() == username
    expect(ump.username_input).to_be_disabled()
    assert ump.display_name_input.input_value() == seeded_test_user['displayName']

    ump.close_dialog()


@allure.feature('用户管理')
@allure.story('编辑')
@allure.title('编辑改字段点取消不生效，重新打开改了点保存才真的改')
@allure.severity(allure.severity_level.CRITICAL)
def test_user_management_edit_cancel_then_save(seeded_test_user, user_management_page):
    ump = user_management_page
    username = seeded_test_user['username']

    # 改显示名按 Escape：内容不变
    ump.open_edit_dialog(username)
    ump.fill_edit_form(display_name='改了但要取消')
    ump.close_dialog()
    assert ump.row_info(username)['display_name'] == seeded_test_user['displayName']

    # 改显示名 + 角色点保存：真的改了
    ump.open_edit_dialog(username)
    ump.fill_edit_form(display_name='改了并且保存了', role='管理员')
    ump.save()
    expect(ump.dialog).to_have_count(0)

    info = ump.row_info(username)
    assert info['display_name'] == '改了并且保存了'
    assert info['role'] == '管理员'


@allure.feature('用户管理')
@allure.story('重置密码')
@allure.title('重置密码填弱密码：提示密码格式不对，弹窗不关')
@allure.severity(allure.severity_level.NORMAL)
def test_user_management_reset_password_weak(seeded_test_user, user_management_page):
    ump = user_management_page
    ump.open_reset_password_dialog(seeded_test_user['username'])

    ump.confirm_reset('short')

    assert '密码至少 8 位' in (ump.error_text() or ''), ump.error_text()
    expect(ump.dialog).to_be_visible()

    ump.close_dialog()


@allure.feature('用户管理')
@allure.story('重置密码')
@allure.title('重置密码成功：弹窗关闭，这个账号变回「待改密」')
@allure.severity(allure.severity_level.CRITICAL)
def test_user_management_reset_password_success(seeded_test_user, user_management_page):
    ump = user_management_page
    username = seeded_test_user['username']

    ump.open_reset_password_dialog(username)
    ump.confirm_reset('NewPass1234')
    expect(ump.dialog).to_have_count(0)

    # 断言：重置后这个账号下次登录要改密
    ump.page.reload(wait_until='networkidle')
    ump.rows().first.wait_for(state='visible')
    assert ump.row_info(username)['pending_pwd_change'] is True


@allure.feature('用户管理')
@allure.story('启停')
@allure.title('禁用/启用瞬间生效，没有二次确认弹窗')
@allure.severity(allure.severity_level.CRITICAL)
def test_user_management_toggle_status(seeded_test_user, user_management_page):
    ump = user_management_page
    username = seeded_test_user['username']
    assert ump.row_info(username)['status'] == '启用'

    ump.toggle_status(username)
    # 断言：没有原生 confirm、没有 MUI 弹窗，直接变成「禁用」
    expect(ump.dialog).to_have_count(0)
    assert ump.row_info(username)['status'] == '禁用'

    ump.toggle_status(username)
    assert ump.row_info(username)['status'] == '启用'


@allure.feature('用户管理')
@allure.story('删除')
@allure.title('删除：原生确认弹窗，点取消账号还在，点确定账号消失')
@allure.severity(allure.severity_level.CRITICAL)
def test_user_management_delete_confirm_flow(seeded_test_user, user_management_page):
    ump = user_management_page
    username = seeded_test_user['username']

    # 点取消：账号还在
    ump.delete(username, confirm=False)
    expect(ump.row_by_username(username)).to_have_count(1)

    # 点确定：永久删除，账号消失
    ump.delete(username, confirm=True)
    expect(ump.row_by_username(username)).to_have_count(0)
