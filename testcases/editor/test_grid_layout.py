from playwright.sync_api import expect
from pages.editor.grid_layout_page import GridLayoutPage


# 左侧组件库分类都可见
def test_component_categories(grid_layout_page):
    for name in GridLayoutPage.COMPONENT_CATEGORIES:
        expect(grid_layout_page.page.get_by_role('button', name=f'Collapse {name}')).to_be_visible()


# 每个分类下组件都可见
def test_component_items(grid_layout_page):
    for category, items in GridLayoutPage.COMPONENT_ITEMS.items():
        for item in items:
            expect(grid_layout_page.page.locator('[data-puck-drawer-item]', has_text=item).first).to_be_visible()