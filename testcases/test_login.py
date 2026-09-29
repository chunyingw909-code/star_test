import allure
import pytest
from playwright.sync_api import expect

from common.utils import read_secrets

# 登录页：185 这类没有登录态的环境用例直接 skip，其余断言都不写死具体环境。
# 提示统一走同一个 MuiAlert（error_alert）：留空是本地拦截的「请输入用户名和密码」，
# 账号/密码错了是统一的「登录失败，请检查用户名和密码」（不区分具体错在哪）。
# 固定 admin/user 已完成首次改密；首次改密行为由 admin/test_force_password_change.py
# 使用一次性账号单独覆盖，登录页基础用例不会修改固定账号密码。


@pytest.fixture(autouse=True)
def _skip_without_login(login_screen):
    if '/login' not in login_screen.page.url:
        pytest.skip('当前环境没有登录页（未启用登录态）')


@allure.feature('登录')
@allure.story('登录页')
@allure.title('登录页表单元素都在：用户名/密码输入框、登录按钮')
@allure.severity(allure.severity_level.BLOCKER)
def test_login_page_renders(login_screen):
    l = login_screen
    # 断言：标题、两个输入框、登录按钮都可见
    expect(l.page.get_by_text('账号登录')).to_be_visible()
    expect(l.username_input).to_be_visible()
    expect(l.password_input).to_be_visible()
    expect(l.login_button).to_be_visible()
    # 断言：登录按钮初始不是禁用的（留空也能点，校验在点击时做）
    expect(l.login_button).to_be_enabled()


@allure.feature('登录')
@allure.story('登录页')
@allure.title('用户名密码都留空点登录：提示「请输入用户名和密码」，不发请求，停在登录页')
@allure.severity(allure.severity_level.CRITICAL)
def test_login_empty_submit(login_screen):
    l = login_screen
    fired = []
    l.page.on('request', lambda r: fired.append(r.url) if '/api/auth/login' in r.url else None)

    l.login_button.click()
    l.page.wait_for_timeout(500)

    # 断言：本地拦截提示，没有真的打登录接口
    expect(l.error_alert).to_have_text('请输入用户名和密码')
    assert not fired, f'留空提交不应该发登录请求：{fired}'
    # 断言：还停在登录页
    assert '/login' in l.page.url


@allure.feature('登录')
@allure.story('登录页')
@allure.title('只填「{label}」点登录：同样提示「请输入用户名和密码」，不发请求')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize('label,fill', [
    ('用户名', lambda l: l.username_input.fill('admin')),
    ('密码', lambda l: l.password_input.fill('admin123')),
])
def test_login_partial_fill(login_screen, label, fill):
    l = login_screen
    fired = []
    l.page.on('request', lambda r: fired.append(r.url) if '/api/auth/login' in r.url else None)

    fill(l)
    l.login_button.click()
    l.page.wait_for_timeout(500)

    expect(l.error_alert).to_have_text('请输入用户名和密码')
    assert not fired, f'只填一项不应该发登录请求：{fired}'


@allure.feature('登录')
@allure.story('登录页')
@allure.title('账号密码错误：统一提示「{title}」，真的发了登录请求但没登进去')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('title,username,password', [
    ('用户名不存在', 'no_such_user_zzz', 'whatever123'),
    ('密码错误', 'admin', 'wrong_password_zzz'),
])
def test_login_invalid_credentials(login_screen, title, username, password):
    l = login_screen
    with l.page.expect_request(
            lambda r: '/api/auth/login' in r.url and r.method == 'POST') as req_info:
        l.login(username, password)

    # 断言：真的打了登录接口——业务失败包在响应体里（HTTP 状态仍是 200），
    # 断言 code != 200 而不是看 HTTP 状态
    body = req_info.value.response().json()
    assert body['code'] != 200, f'账号密码错误不应该返回业务成功：{body}'
    # 断言：错误提示统一，不泄露具体是「用户名不存在」还是「密码错误」
    expect(l.error_alert).to_have_text('登录失败，请检查用户名和密码')
    # 断言：还停在登录页
    assert '/login' in l.page.url


@allure.feature('登录')
@allure.story('登录页')
@allure.title('超长用户名/密码：输入框不限制长度，提交后按普通的登录失败处理，不崩')
@allure.severity(allure.severity_level.NORMAL)
def test_login_overlong_input(login_screen):
    l = login_screen
    long_str = 'a' * 300

    l.login(long_str, long_str)

    # 断言：输入框原样接受了超长内容（没有前端 maxlength 截断）
    assert len(l.username_input.input_value()) == 300
    # 断言：跟普通的账号密码错误走同一条提示，页面没有崩/白屏
    expect(l.error_alert).to_have_text('登录失败，请检查用户名和密码')


@allure.feature('登录')
@allure.story('登录页')
@allure.title('密码框回车等价于点「登录」')
@allure.severity(allure.severity_level.NORMAL)
def test_login_enter_key_submits(login_screen):
    l = login_screen
    admin = read_secrets()['accounts']['admin']

    l.username_input.fill(admin['username'])
    l.password_input.fill(admin['password'])
    l.password_input.press('Enter')
    l.wait_result()

    # 断言：回车触发了登录，已经离开登录页
    assert '/login' not in l.page.url


@allure.feature('登录')
@allure.story('登录页')
@allure.title('管理员账号密码正确：登录成功跳主页，本地存下 token')
@allure.severity(allure.severity_level.BLOCKER)
def test_login_success(login_screen):
    l = login_screen
    admin = read_secrets()['accounts']['admin']

    l.login(admin['username'], admin['password'])

    # 断言：跳出登录页
    assert '/login' not in l.page.url, f'登录成功后应该离开登录页，实际 {l.page.url}'
    # 断言：token 落进了 localStorage（后续接口鉴权靠它，见 common.utils.api_fetch）
    token = l.page.evaluate("() => localStorage.getItem('sarsat_token')")
    assert token, '登录成功后 localStorage 里应该有 sarsat_token'
