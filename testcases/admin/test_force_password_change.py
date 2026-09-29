import allure
from playwright.sync_api import expect

from common.utils import read_yaml
from pages.login.login_page import LoginPage

config = read_yaml('config/config.yaml')

# 新建账号默认 forcePwdChange=true：首次登录成功后不会直接进主页，而是在登录页原地
# 弹一个「首次登录，请设置新密码」弹窗（URL 仍是 /login，不是登录失败）。
# 用独立的 browser context 走这个流程，不影响 user_management_page 用的管理员会话
# （那个会话后面 fixture teardown 还要用来接口删测试账号）。


@allure.feature('登录')
@allure.story('首次登录强制改密')
@allure.title('首次登录成功后弹「设置新密码」，标题正确，密码框都在')
@allure.severity(allure.severity_level.CRITICAL)
def test_force_change_dialog_appears(force_change_account, browser):
    username, initial_password, _created = force_change_account
    ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
    page = ctx.new_page()
    page.goto(config['url'])
    page.wait_for_load_state('networkidle')
    login = LoginPage(page)
    login.login(username, initial_password)

    # 断言：弹出改密弹窗，还停在 /login（这不算登录失败）
    expect(login.force_change_dialog).to_be_visible()
    expect(login.new_password_input).to_be_visible()
    expect(login.confirm_password_input).to_be_visible()
    assert '/login' in page.url

    ctx.close()


@allure.feature('登录')
@allure.story('首次登录强制改密')
@allure.title('两次新密码不一致：提示「两次输入的新密码不一致」，弹窗不关')
@allure.severity(allure.severity_level.NORMAL)
def test_force_change_password_mismatch(force_change_account, browser):
    username, initial_password, _created = force_change_account
    ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
    page = ctx.new_page()
    page.goto(config['url'])
    page.wait_for_load_state('networkidle')
    login = LoginPage(page)
    login.login(username, initial_password)

    login.new_password_input.fill('ValidPass123')
    login.confirm_password_input.fill('DifferentPass123')
    login.confirm_change_button.click()

    expect(login.force_change_error).to_have_text('两次输入的新密码不一致')
    expect(login.force_change_dialog).to_be_visible()

    ctx.close()


@allure.feature('登录')
@allure.story('首次登录强制改密')
@allure.title('新密码「{label}」：提示密码格式不对，弹窗不关')
@allure.severity(allure.severity_level.NORMAL)
def test_force_change_weak_password(force_change_account, browser):
    username, initial_password, _created = force_change_account
    ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
    page = ctx.new_page()
    page.goto(config['url'])
    page.wait_for_load_state('networkidle')
    login = LoginPage(page)
    login.login(username, initial_password)

    login.complete_force_change('weak')

    expect(login.force_change_error).to_have_text('密码至少 8 位，且需包含字母和数字')
    expect(login.force_change_dialog).to_be_visible()

    ctx.close()


@allure.feature('登录')
@allure.story('首次登录强制改密')
@allure.title('设置合法新密码后：进入主页；旧密码不能再登录，新密码能登录')
@allure.severity(allure.severity_level.BLOCKER)
def test_force_change_success_then_password_swapped(force_change_account, browser):
    username, initial_password, _created = force_change_account
    new_password = 'ForcePwd123456'

    ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
    page = ctx.new_page()
    page.goto(config['url'])
    page.wait_for_load_state('networkidle')
    login = LoginPage(page)
    login.login(username, initial_password)
    login.complete_force_change(new_password)

    # 断言：改密成功，弹窗关了、离开了登录页
    expect(login.force_change_dialog).to_have_count(0)
    assert '/login' not in page.url
    ctx.close()

    # 断言：旧密码不能再登录
    ctx_old = browser.new_context(viewport={'width': 1440, 'height': 900})
    page_old = ctx_old.new_page()
    page_old.goto(config['url'])
    page_old.wait_for_load_state('networkidle')
    login_old = LoginPage(page_old)
    login_old.login(username, initial_password)
    assert '/login' in page_old.url, '旧密码不应该还能登录'
    expect(login_old.error_alert).to_have_text('登录失败，请检查用户名和密码')
    ctx_old.close()

    # 断言：新密码能登录
    ctx_new = browser.new_context(viewport={'width': 1440, 'height': 900})
    page_new = ctx_new.new_page()
    page_new.goto(config['url'])
    page_new.wait_for_load_state('networkidle')
    login_new = LoginPage(page_new)
    login_new.login(username, new_password)
    assert '/login' not in page_new.url, '新密码应该能登录成功'
    ctx_new.close()
