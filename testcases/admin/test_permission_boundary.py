import allure
from playwright.sync_api import expect

from common.utils import api_status, read_yaml
from pages.fault.fault_library_page import FaultLibraryPage
from pages.telemetry.telemetry_page import TelemetryPage

config = read_yaml('config/config.yaml')

# 普通用户（USER 角色）跟管理员（ADMIN）比，权限边界体现在几处：
# - 头像菜单少了「用户管理」「审计日志」「故障管理」三项
# - 故障/预案库模块的子标签少了「管理」
# - 左侧仿真控制面板是只读的（无法启动仿真）
# - 直接改 URL 硬闯 /admin/users、/fault/admin 会被拦，显示无权限提示
# - 后端接口本身也要拦，不能只是前端藏了入口——用普通用户自己的 token 直接打接口验证


@allure.feature('用户管理')
@allure.story('权限边界')
@allure.title('普通用户头像菜单没有「用户管理」「审计日志」「故障管理」')
@allure.severity(allure.severity_level.BLOCKER)
def test_regular_user_avatar_menu_hides_admin_entries(regular_user_session):
    page = regular_user_session
    page.locator('.MuiAvatar-root').click()
    items = page.get_by_role('menuitem').all_inner_texts()
    page.keyboard.press('Escape')

    # 断言：管理员才有的三个入口都不在普通用户的菜单里
    for admin_only in ('用户管理', '审计日志', '故障管理'):
        assert admin_only not in items, f'普通用户菜单里不该有「{admin_only}」：{items}'
    # 断言：「修改密码」「退出」这两个所有人都有的还在
    assert '修改密码' in items and '退出' in items, items


@allure.feature('用户管理')
@allure.story('权限边界')
@allure.title('普通用户的故障/预案库模块子标签里没有「管理」')
@allure.severity(allure.severity_level.CRITICAL)
def test_regular_user_fault_module_hides_management_tab(regular_user_session):
    page = regular_user_session
    FaultLibraryPage(page).open()

    tabs = [t.strip() for t in page.get_by_role('tab').all_inner_texts()]
    # 断言：「管理」不在普通用户能看到的子标签里，其余子标签还在
    assert '管理' not in tabs, f'普通用户不该看到「管理」子标签：{tabs}'
    for name in ('目录', '预案库', '快速定位', '定位历史', '故障注入'):
        assert name in tabs, f'普通用户应该看到「{name}」：{tabs}'


@allure.feature('用户管理')
@allure.story('权限边界')
@allure.title('普通用户的仿真控制面板是只读的，没有「启动仿真循环」按钮')
@allure.severity(allure.severity_level.CRITICAL)
def test_regular_user_telemetry_is_readonly(regular_user_session):
    page = regular_user_session
    tp = TelemetryPage(page).open()

    # 断言：面板上有「只读」提示
    expect(page.get_by_text('只读', exact=False).first).to_be_visible()
    # 断言：仿真循环播放控制整行不渲染；节点列表自己的启动图标不算。
    assert tp.play_button.count() == 0, '普通用户不该有「启动仿真循环」按钮'


@allure.feature('用户管理')
@allure.story('权限边界')
@allure.title('普通用户直接改 URL 访问用户管理页：显示无权限提示')
@allure.severity(allure.severity_level.CRITICAL)
def test_regular_user_blocked_from_user_management_url(regular_user_session):
    page = regular_user_session
    page.goto(config['url'].rstrip('/') + '/zh-CN/admin/users')
    page.wait_for_load_state('networkidle')

    # 断言：显示无权限提示，没有真的看到用户列表
    expect(page.get_by_text('无权限访问用户管理')).to_be_visible()


@allure.feature('用户管理')
@allure.story('权限边界')
@allure.title('普通用户直接改 URL 访问故障管理页：显示无权限提示')
@allure.severity(allure.severity_level.CRITICAL)
def test_regular_user_blocked_from_fault_admin_url(regular_user_session):
    # 只测权限提示本身，不测这个页面的功能内容——/fault/admin 页面另有人在写
    page = regular_user_session
    page.goto(config['url'].rstrip('/') + '/zh-CN/fault/admin')
    page.wait_for_load_state('networkidle')

    expect(page.get_by_text('您没有故障管理的权限')).to_be_visible()


@allure.feature('用户管理')
@allure.story('权限边界')
@allure.title('接口回归：普通用户的 token 直接打「{path}」，后端真的拦（不只是前端藏入口）')
@allure.severity(allure.severity_level.BLOCKER)
def test_regular_user_api_blocked_from_user_list(regular_user_session):
    status = api_status(regular_user_session, '/api/users', method='GET')
    # 断言：不是靠前端藏菜单，后端接口本身也拒绝
    assert status == 403, f'GET /api/users 应该 403，实际 {status}'


@allure.feature('用户管理')
@allure.story('权限边界')
@allure.title('接口回归：普通用户的 token 直接打 POST /api/fault，后端真的拦')
@allure.severity(allure.severity_level.BLOCKER)
def test_regular_user_api_blocked_from_fault_create(regular_user_session):
    body = {
        'faultCode': 'ZZPERM-TEST', 'faultName': '权限测试', 'faultType': 'x',
        'subsystem': 'power', 'severity': 'III', 'status': 'active',
    }
    status = api_status(regular_user_session, '/api/fault', method='POST', body=body)
    assert status == 403, f'POST /api/fault 应该 403，实际 {status}'
