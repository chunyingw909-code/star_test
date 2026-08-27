import allure
from playwright.sync_api import expect


@allure.feature('界面编辑器')
@allure.story('自由布局-组件库')
@allure.title('点击"添加组件"后弹出的窗口列表')
@allure.severity(allure.severity_level.CRITICAL)
def test_add_component_menu(free_layout_page):
    free_layout_page.add_component_button.click()
    expect(free_layout_page.menu).to_be_visible()
    items = free_layout_page.menu.get_by_role('menuitem')
    expect(items).to_have_count(12)
    for name in free_layout_page.COMPONENT_NAMES:
        expect(free_layout_page.component_item(name)).to_be_visible()   #每一项都对应