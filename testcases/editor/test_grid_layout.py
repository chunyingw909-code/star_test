import allure
from playwright.sync_api import expect
from pages.editor.grid_layout_page import GridLayoutPage


@allure.feature('界面编辑器')
@allure.story('栅格布局-组件库')
@allure.title('左侧组件库分类都可见')
@allure.severity(allure.severity_level.CRITICAL)
def test_component_categories(grid_layout_page):
    for name in GridLayoutPage.COMPONENT_CATEGORIES:
        expect(grid_layout_page.page.locator(f'button[title="Collapse {name}"]')).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('栅格布局-组件库')
@allure.title('每个分类下组件都可见')
@allure.severity(allure.severity_level.CRITICAL)
def test_component_items(grid_layout_page):
    for category, items in GridLayoutPage.COMPONENT_ITEMS.items():
        for item in items:
            expect(grid_layout_page.page.locator('[data-puck-drawer-item]', has_text=item).first).to_be_visible()
