import allure
from playwright.sync_api import expect

from common.utils import api_fetch, read_yaml
from pages.admin.user_management_page import UserManagementPage

config = read_yaml('config/config.yaml')

# 管理员对自己账号做操作时的两种实测行为：
# - 删除自己：后端拦住（400），不是靠前端藏按钮——UI 上删除按钮照样能点、原生确认框
#   照样弹，只是提交后账号并没有真的消失。
# - 把自己的角色从管理员降成普通用户：后端允许，这是管理员自愿放弃权限，不是提权类
#   风险，如实记录当前行为，不当成问题处理。


@allure.feature('用户管理')
@allure.story('自我操作保护')
@allure.title('管理员删除自己：弹出「不能删除自己」提示，账号仍然存在（后端拒绝）')
@allure.severity(allure.severity_level.BLOCKER)
def test_admin_cannot_delete_self(admin_role_session):
    page, created = admin_role_session
    username = created['username']
    page.goto(config['url'].rstrip('/') + '/zh-CN/admin/users')
    page.wait_for_load_state('networkidle')
    ump = UserManagementPage(page)
    ump.rows().first.wait_for(state='visible')

    ump.delete(username, confirm=True)

    # 断言：页面弹出「不能删除自己」的提示
    expect(ump.page_alert).to_contain_text('不能删除自己')
    # 断言：账号还在——后端没真的执行删除
    expect(ump.row_by_username(username)).to_have_count(1)
    # 断言：接口层面响应体也是同样的拒绝原因
    resp = api_fetch(page, f"/api/users/{created['id']}", method='DELETE')
    assert resp['code'] == 400 and resp['message'] == '不能删除自己', resp


@allure.feature('用户管理')
@allure.story('自我操作保护')
@allure.title('管理员把自己的角色改成普通用户：允许（自愿放弃权限，不是提权）')
@allure.severity(allure.severity_level.NORMAL)
def test_admin_can_demote_self(admin_role_session):
    page, created = admin_role_session
    username = created['username']
    page.goto(config['url'].rstrip('/') + '/zh-CN/admin/users')
    page.wait_for_load_state('networkidle')
    ump = UserManagementPage(page)
    ump.rows().first.wait_for(state='visible')

    ump.open_edit_dialog(username)
    ump.fill_edit_form(role='用户')
    ump.save()

    # 断言：降级成功，弹窗关闭、角色列变成「用户」
    expect(ump.dialog).to_have_count(0)
    assert ump.row_info(username)['role'] == '用户'
