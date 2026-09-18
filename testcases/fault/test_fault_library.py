import allure
import pytest
import re
from playwright.sync_api import expect

from pages.fault.fault_library_page import FaultLibraryPage


# 故障/预案库「模块外壳」的用例：进入模块、6 个子标签。
# 每个子标签内部的功能各归各的 test 文件（目录 → test_fault_catalog.py，详情 → test_fault_detail.py）。


@allure.feature('故障/预案库')
@allure.story('模块外壳')
@allure.title('从顶部导航进入故障/预案库，模块子标签出现')
@allure.severity(allure.severity_level.BLOCKER)
def test_enter_fault_library(fault_library_page):
    # 断言：「故障/预案库」顶部 Tab 处于选中态
    expect(fault_library_page.nav_entry).to_have_attribute('aria-selected', 'true')
    # 断言：模块子标签「目录」可见
    expect(fault_library_page.breadcrumb).to_be_visible()


@allure.feature('故障/预案库')
@allure.story('模块外壳')
@allure.title('6 个子标签都在：目录 / 预案库 / 快速定位 / 定位历史 / 故障注入 / 管理')
@allure.severity(allure.severity_level.CRITICAL)
def test_six_tabs_present(fault_library_page):
    for name in FaultLibraryPage.TABS:
        # 断言：每个子标签都可见
        expect(fault_library_page.tab(name)).to_be_visible()


@allure.feature('故障/预案库')
@allure.story('模块外壳')
@allure.title('进入模块后默认停在「目录」子标签')
@allure.severity(allure.severity_level.NORMAL)
def test_default_subtab_is_catalog(fault_library_page):
    # 断言：「目录」是默认选中的子标签
    expect(fault_library_page.tab('目录')).to_have_attribute('aria-selected', 'true')
    # 断言：其余子标签都未选中
    for name in FaultLibraryPage.TABS[1:]:
        expect(fault_library_page.tab(name)).to_have_attribute('aria-selected', 'false')


# 逐个子标签独立进入并点击——不在一条用例里连点 6 个：「快速定位」会把路由带到
# /fault/locate，之后再找其它 tab 会失败。每个 tab 用一次全新进入。
@allure.feature('故障/预案库')
@allure.story('模块外壳')
@allure.title('点击子标签「{tab_name}」，页面停留在故障/预案库模块内')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize('tab_name', FaultLibraryPage.TABS)
def test_tab_switchable(fault_library_page, tab_name):
    fault_library_page.open_tab(tab_name)
    # 断言：点子标签后仍停留在故障/预案库模块内（顶部 Tab 仍选中）
    expect(fault_library_page.nav_entry).to_have_attribute('aria-selected', 'true')
    if tab_name == '快速定位':
        # 快速定位会进入独立路由，原来的子 tab 条随之卸载。
        expect(fault_library_page.page).to_have_url(re.compile(r'/fault/locate(?:[/?#]|$)'))
    else:
        expect(fault_library_page.tab(tab_name)).to_have_attribute('aria-selected', 'true')
