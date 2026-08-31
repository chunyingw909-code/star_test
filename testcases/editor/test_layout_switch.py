import allure
from playwright.sync_api import expect

from pages.editor.editor_page import EditorPage


# 切换用例直接复用 free_layout_page 的入口（编辑态 / 编辑管理 / 默认自由布局），
# 再用 EditorPage 包一层拿工具栏按钮 —— 与 grid_fixtures 里的惯用法一致。


@allure.feature('界面编辑器')
@allure.story('布局切换')
@allure.title('进入编辑器默认是自由布局')
@allure.severity(allure.severity_level.CRITICAL)
def test_default_layout_is_free(free_layout_page):
    ed = EditorPage(free_layout_page.page)
    assert ed.current_layout() == 'free'
    expect(ed.page.locator(EditorPage.CANVAS_FREE)).to_be_visible()
    expect(ed.page.locator(EditorPage.CANVAS_GRID)).to_have_count(0)
    expect(ed.free_layout_button).to_have_attribute('aria-pressed', 'true')
    expect(ed.grid_layout_button).to_have_attribute('aria-pressed', 'false')


@allure.feature('界面编辑器')
@allure.story('布局切换')
@allure.title('切到栅格布局：画布元素替换、按钮状态互斥')
@allure.severity(allure.severity_level.CRITICAL)
def test_switch_to_grid(free_layout_page):
    ed = EditorPage(free_layout_page.page)
    ed.switch_to_grid()
    assert ed.current_layout() == 'grid'
    expect(ed.page.locator(EditorPage.CANVAS_GRID)).to_be_visible()
    expect(ed.page.locator(EditorPage.CANVAS_FREE)).to_have_count(0)
    expect(ed.grid_layout_button).to_have_attribute('aria-pressed', 'true')
    expect(ed.free_layout_button).to_have_attribute('aria-pressed', 'false')


@allure.feature('界面编辑器')
@allure.story('布局切换')
@allure.title('栅格切回自由：画布与按钮状态复原')
@allure.severity(allure.severity_level.CRITICAL)
def test_switch_back_to_free(free_layout_page):
    ed = EditorPage(free_layout_page.page)
    ed.switch_to_grid()
    ed.switch_to_free()
    assert ed.current_layout() == 'free'
    expect(ed.page.locator(EditorPage.CANVAS_FREE)).to_be_visible()
    expect(ed.page.locator(EditorPage.CANVAS_GRID)).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('布局切换')
@allure.title('切到栅格布局弹出提示 Snackbar')
@allure.severity(allure.severity_level.NORMAL)
def test_switch_to_grid_shows_toast(free_layout_page):
    ed = EditorPage(free_layout_page.page)
    ed.switch_to_grid()
    expect(ed.switch_toast.filter(has_text='已切换到栅格布局')).to_be_visible()
    expect(ed.switch_toast.filter(has_text='两种模式共享同一数据源')).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('布局切换')
@allure.title('切回自由布局弹出提示 Snackbar')
@allure.severity(allure.severity_level.NORMAL)
def test_switch_to_free_shows_toast(free_layout_page):
    ed = EditorPage(free_layout_page.page)
    ed.switch_to_grid()
    ed.switch_to_free()
    expect(ed.switch_toast.filter(has_text='已切换到自由布局')).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('布局切换')
@allure.title('切换布局只弹 Snackbar，不弹阻塞式确认框')
@allure.severity(allure.severity_level.NORMAL)
def test_switch_no_confirm_dialog(free_layout_page):
    ed = EditorPage(free_layout_page.page)
    ed.switch_to_grid()
    expect(ed.page.get_by_role('dialog')).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('布局切换')
@allure.title('自由布局搭好的组件，切到栅格布局后仍在（共享同一数据源）')
@allure.severity(allure.severity_level.CRITICAL)
def test_widget_survives_free_to_grid(free_text_page):
    free_text_page.click_widget()
    free_text_page.prop_content.fill('LSW-KEEP-marker')
    expect(free_text_page.page.get_by_text('LSW-KEEP-marker')).to_be_visible()

    EditorPage(free_text_page.page).switch_to_grid()
    expect(free_text_page.page.get_by_text('LSW-KEEP-marker')).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('布局切换')
@allure.title('自由→栅格→自由 来回切，组件与内容不丢')
@allure.severity(allure.severity_level.CRITICAL)
def test_widget_survives_roundtrip(free_text_page):
    free_text_page.click_widget()
    free_text_page.prop_content.fill('LSW-ROUNDTRIP')

    ed = EditorPage(free_text_page.page)
    ed.switch_to_grid()
    ed.switch_to_free()

    expect(free_text_page.page.get_by_text('LSW-ROUNDTRIP')).to_be_visible()
    expect(ed.all_widgets()).to_have_count(1)
