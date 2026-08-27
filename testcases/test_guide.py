import allure
from playwright.sync_api import expect
from pages.guide.guide_page import GuidePage


@allure.feature('系统初始化引导')
@allure.story('首次初始化向导')
@allure.title('完成三步初始化向导流程')
@allure.severity(allure.severity_level.BLOCKER)
def test_guide_three_steps(open_page):
    guide = GuidePage(open_page)

    # 第1步：核心节点配置
    expect(guide.step_title()).to_have_text('系统首次初始化向导')
    expect(guide.active_step_label()).to_have_text('核心节点配置')
    expect(guide.prev_button).to_be_disabled()
    expect(guide.next_button).to_be_enabled()

    guide.next_button.click()

    # 第2步：数据库连接
    expect(guide.active_step_label()).to_have_text('数据库连接')
    expect(guide.prev_button).to_be_enabled()

    guide.next_button.click()

    # 第3步：工作空间初始化
    expect(guide.active_step_label()).to_have_text('工作空间初始化')

    # 完成
    guide.finish_button.click()
    expect(guide.dialog).to_be_hidden()