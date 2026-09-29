import uuid

import pytest

from common.utils import read_secrets, read_yaml
from pages.admin.user_management_page import UserManagementPage
from pages.guide.guide_page import GuidePage
from pages.login.login_page import LoginPage

config = read_yaml('config/config.yaml')


# 进入用户管理页面：直接改 URL 进（比每次都点头像菜单快，头像菜单入口本身单独有
# 一条用例覆盖，见 test_user_management_opens_via_avatar_menu）
@pytest.fixture
def user_management_page(home_page):
    home_page.goto(config['url'].rstrip('/') + '/zh-CN/admin/users')
    home_page.wait_for_load_state('networkidle')
    ump = UserManagementPage(home_page)
    ump.rows().first.wait_for(state='visible')
    return ump


# 上一步 → 用接口（不经过「创建用户」表单）直接建一个测试账号，给「编辑 / 重置密码 /
# 禁用 / 删除」这类不是在测新建流程本身、只是需要一个已存在账号当靶子的用例用。
# 用户名带 zztest- 前缀 + 随机后缀，不会跟真实账号撞车。
# 建完得刷新回列表页才能在表格里点到它。teardown 用接口删掉；用例里已经手动删过
# （比如删除用例本身）也不报错。
@pytest.fixture
def seeded_test_user(user_management_page):
    ump = user_management_page
    username = f'zztest-{uuid.uuid4().hex[:8]}'
    created = ump.api_create(username=username, display_name='自动化测试账号')

    ump.page.reload(wait_until='networkidle')
    ump.rows().first.wait_for(state='visible')

    yield created
    ump.api_delete(created['id'])


# 建一个测试账号（默认 forcePwdChange=true），只建号不登录——给「首次登录强制改密」
# 这类用例自己控制登录节奏用（不像 regular_user_session/admin_role_session 那样直接
# 把改密流程走完）。用完接口删。
@pytest.fixture
def force_change_account(user_management_page):
    ump = user_management_page
    username = f'zzforcepwd-{uuid.uuid4().hex[:8]}'
    initial_password = 'Init12345'
    created = ump.api_create(username=username, display_name='强改密测试', password=initial_password)
    yield username, initial_password, created
    ump.api_delete(created['id'])


# 建一个一次性测试账号，在完全独立的浏览器 context 里登录它。仅供会修改账号本身的
# 破坏性用例使用（例如管理员自我降级）；不能拿固定 admin/user 做这种测试。
# 密码框有 3 个是因为背后登录表单自己的密码框也还在 DOM 里（被改密弹窗盖住），要
# 限定在弹窗（role=dialog）范围内填，不然会填错到登录表单自己的密码框上。
def _new_role_session(ump, browser, role, prefix, display_name):
    username = f'{prefix}-{uuid.uuid4().hex[:8]}'
    initial_password = 'Init12345'
    created = ump.api_create(
        username=username, display_name=display_name, password=initial_password, role=role)

    ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
    user_page = ctx.new_page()
    user_page.goto(config['url'])
    user_page.wait_for_load_state('networkidle')
    login = LoginPage(user_page)
    login.login(username, initial_password)
    login.complete_force_change('RoleTest123456')
    GuidePage(user_page).complete()

    return ctx, user_page, created


# 给「权限边界」用例建立固定普通用户会话。222 的 secrets.yaml 已配置完成改密的
# user 账号；这里直接接口登录并写入 token，不重复建号、强制改密和删号。
@pytest.fixture
def regular_user_session(browser):
    account = read_secrets()['accounts']['user']
    ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
    user_page = ctx.new_page()
    response = user_page.request.post(
        config['url'].rstrip('/') + '/api/auth/login',
        data={'username': account['username'], 'password': account['password']},
    )
    body = response.json() if response.ok else {}
    data = body.get('data') or {}
    token = data.get('token')
    assert token, f'固定普通用户接口登录失败：HTTP {response.status}'
    assert not data.get('forcePwdChange'), '固定普通用户仍处于待改密状态'

    user_page.goto(
        config['url'].rstrip('/') + '/zh-CN/login', wait_until='domcontentloaded')
    user_page.evaluate(
        "token => localStorage.setItem('sarsat_token', token)", token)
    user_page.goto(config['url'], wait_until='domcontentloaded')
    GuidePage(user_page).complete()

    yield user_page
    ctx.close()


# 给「自我删除 / 自我改权限保护」这类用例当一个「已登录、自己就是管理员」的会话用——
# 测的是这个账号自己能不能删自己、能不能把自己降级，不是别的账号操作它。
@pytest.fixture
def admin_role_session(user_management_page, browser):
    ump = user_management_page
    ctx, user_page, created = _new_role_session(ump, browser, 'ADMIN', 'zzselfadmin', '自我操作测试账号')
    yield user_page, created
    ctx.close()
    ump.api_delete(created['id'])
