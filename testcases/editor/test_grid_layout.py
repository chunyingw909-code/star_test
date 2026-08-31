import allure
import pytest
from playwright.sync_api import expect

from pages.editor.widget_catalog import WIDGETS, CATEGORIES
from pages.editor.editor_page import EditorPage


@allure.feature('界面编辑器')
@allure.story('栅格布局-组件库')
@allure.title('左侧组件库分类可见：{category}')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('category', CATEGORIES)
def test_component_category_visible(grid_layout_page, category):
    expect(grid_layout_page.category_header(category)).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('栅格布局-组件库')
@allure.title('左侧组件库逐项核对：{spec[label]} / {spec[type]}')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('spec', WIDGETS, ids=[w['type'] for w in WIDGETS])
def test_component_item_visible(grid_layout_page, spec):
    item = grid_layout_page.drawer_item(spec['type'])
    expect(item).to_be_visible()
    expect(item).to_contain_text(spec['label'])


@allure.feature('界面编辑器')
@allure.story('栅格布局-组件库')
@allure.title('左侧组件库的组件集合与组件清单完全一致')
@allure.severity(allure.severity_level.CRITICAL)
def test_component_items_exact(grid_layout_page):
    actual = grid_layout_page.drawer_item_types()
    expected = [w['type'] for w in WIDGETS]
    assert sorted(actual) == sorted(expected), (
        f'多出={sorted(set(actual) - set(expected))} 缺少={sorted(set(expected) - set(actual))}'
    )


# ==================== 视图 / 面板 / 撤销（Puck 编辑器）====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-视图与面板')
@allure.title('UI可视 ↔ <>JSON 自由切换')
@allure.severity(allure.severity_level.CRITICAL)
def test_json_toggle_switches_view(grid_layout_page):
    gp = grid_layout_page
    assert gp.active_view() == 'ui'
    gp.switch_to_json()
    assert gp.active_view() == 'json'
    expect(gp.json_editor.first).to_be_visible()
    gp.switch_to_ui()
    assert gp.active_view() == 'ui'
    expect(gp.canvas).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('栅格布局-视图与面板')
@allure.title('<>JSON 展示画布 JSON（root + widgets）')
@allure.severity(allure.severity_level.CRITICAL)
def test_json_shows_layout_json(grid_text_page):
    grid_text_page.prop_content.fill('GRID-JSON-A')
    grid_text_page.switch_to_json()
    txt = grid_text_page.json_text()
    assert '"root"' in txt and '"widgets"' in txt, txt[:200]
    assert 'TextWidget' in txt
    assert 'GRID-JSON-A' in txt          # 属性面板的改动会体现在 JSON 里


@allure.feature('界面编辑器')
@allure.story('栅格布局-视图与面板')
@allure.title('[现状] 栅格布局在 JSON 里改内容、切回 UI，画布不同步')
@allure.severity(allure.severity_level.NORMAL)
def test_json_edit_does_not_sync_back(grid_text_page):
    # ⚠️ 现状记录（非期望）：自由布局在 <>JSON 里改内容、切回 UI 可视，画布会同步；
    # 栅格布局改了 JSON 再切回 UI，画布内容不变（改动没生效）。又一处自由/栅格不一致。
    # TODO(bug) 期望：应与自由布局一致 —— 切回 UI 后画布显示 GRID-JSON-B。
    page = grid_text_page.page
    grid_text_page.prop_content.fill('GRID-JSON-A')
    expect(page.get_by_text('GRID-JSON-A')).to_be_visible()

    grid_text_page.switch_to_json()
    txt = grid_text_page.json_text()
    grid_text_page.set_json(txt.replace('GRID-JSON-A', 'GRID-JSON-B'))
    grid_text_page.switch_to_ui()

    # 现状：画布还是 A，没变成 B
    expect(page.get_by_text('GRID-JSON-A')).to_be_visible()
    expect(page.get_by_text('GRID-JSON-B')).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('栅格布局-视图与面板')
@allure.title('隐藏 / 显示左侧组件库')
@allure.severity(allure.severity_level.NORMAL)
def test_toggle_left_sidebar(grid_layout_page):
    gp = grid_layout_page
    assert gp.left_sidebar_visible()
    gp.toggle_left_sidebar_button.click()
    gp.page.wait_for_timeout(400)
    assert not gp.left_sidebar_visible()
    gp.toggle_left_sidebar_button.click()
    gp.page.wait_for_timeout(400)
    assert gp.left_sidebar_visible()


@allure.feature('界面编辑器')
@allure.story('栅格布局-视图与面板')
@allure.title('隐藏 / 显示右侧属性面板')
@allure.severity(allure.severity_level.NORMAL)
def test_toggle_right_sidebar(grid_text_page):
    gp = grid_text_page
    assert gp.right_sidebar_visible()
    gp.toggle_right_sidebar_button.click()
    gp.page.wait_for_timeout(400)
    assert not gp.right_sidebar_visible()
    gp.toggle_right_sidebar_button.click()
    gp.page.wait_for_timeout(400)
    assert gp.right_sidebar_visible()


@allure.feature('界面编辑器')
@allure.story('栅格布局-视图与面板')
@allure.title('撤销 / 重做：撤销移除刚拖入的组件，重做恢复')
@allure.severity(allure.severity_level.CRITICAL)
def test_undo_redo(grid_text_page):
    expect(grid_text_page.canvas_widgets()).to_have_count(1)
    grid_text_page.undo()
    expect(grid_text_page.canvas_widgets()).to_have_count(0)
    grid_text_page.redo()
    expect(grid_text_page.canvas_widgets()).to_have_count(1)


# ==================== 保存（Publish）====================
# 栅格布局的「保存」= Puck MenuBar 里的 Publish。

@allure.feature('界面编辑器')
@allure.story('栅格布局-保存')
@allure.title('填布局名称后 Publish，提示"保存成功"')
@allure.severity(allure.severity_level.CRITICAL)
def test_publish_succeeds(grid_text_saved_cleanup):
    gp = grid_text_saved_cleanup
    gp.save_layout('AUTOTEST-GRID-SAVE')
    expect(gp.page.get_by_role('alert').filter(has_text='保存成功')).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('栅格布局-保存')
@allure.title('Publish 后刷新页面，组件仍在（自动回到栅格布局）')
@allure.severity(allure.severity_level.CRITICAL)
def test_publish_persists_after_reload(grid_text_saved_cleanup):
    gp = grid_text_saved_cleanup
    ed = EditorPage(gp.page)
    gp.prop_content.fill('GRID-PERSIST-A')
    gp.save_layout('AUTOTEST-GRID-SAVE')
    expect(gp.page.get_by_role('alert').filter(has_text='保存成功')).to_be_visible()

    ed.reload_editor(layout='grid')
    expect(gp.page.get_by_text('GRID-PERSIST-A')).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('栅格布局-保存')
@allure.title('首次 Publish 前，未保存的编辑刷新即丢')
@allure.severity(allure.severity_level.CRITICAL)
def test_unsaved_lost_before_first_publish(grid_text_page):
    # 还没 Publish 过 → 后端没有对应 page 记录 → 编辑不会被自动保存，刷新即丢。
    gp = grid_text_page
    ed = EditorPage(gp.page)
    gp.prop_content.fill('GRID-UNSAVED-A')
    expect(gp.page.get_by_text('GRID-UNSAVED-A')).to_be_visible()

    ed.reload_editor(layout='grid')
    expect(gp.page.get_by_text('GRID-UNSAVED-A')).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('栅格布局-保存')
@allure.title('首次 Publish 之后，后续编辑会防抖自动保存（无需再点 Publish）')
@allure.severity(allure.severity_level.NORMAL)
def test_grid_autosaves_edits_after_publish(grid_text_saved_cleanup):
    # 首次 Publish 建立 page 记录后，应用对后续每次编辑做防抖自动保存
    # （抓到 PUT /api/pages/<id>，约数秒延迟），不需要再点 Publish。
    # 自由布局也是同样的行为（首次「保存」后自动保存），两种布局一致。
    # 用户手动操作时的自然停顿刚好等到自动保存，所以"加组件不保存、刷新后还在"。
    gp = grid_text_saved_cleanup
    ed = EditorPage(gp.page)

    # 先 Publish 一次，建立 page 记录
    gp.prop_content.fill('AUTOSAVE-A')
    gp.save_layout('AUTOTEST-GRID-SAVE')
    expect(gp.page.get_by_role('alert').filter(has_text='保存成功')).to_be_visible()

    # 再加一个组件，不点 Publish，等防抖自动保存落库
    gp.drag_to_canvas('GaugeWidget')
    expect(gp.canvas_widgets()).to_have_count(2)
    gp.page.wait_for_timeout(8000)

    ed.reload_editor(layout='grid')
    # 没点 Publish 的第 2 个组件也被自动保存下来了
    expect(gp.canvas_widgets()).to_have_count(2)


@allure.feature('界面编辑器')
@allure.story('栅格布局-保存')
@allure.title('Publish 后「新建」+确定，刷新页面组件也不再出现')
@allure.severity(allure.severity_level.NORMAL)
def test_new_removes_saved_layout(grid_text_saved_cleanup):
    gp = grid_text_saved_cleanup
    ed = EditorPage(gp.page)
    gp.prop_content.fill('GRID-NEWRM-A')
    gp.save_layout('AUTOTEST-GRID-SAVE')
    expect(gp.page.get_by_role('alert').filter(has_text='保存成功')).to_be_visible()

    ed.click_new_and_confirm()
    ed.reload_editor(layout='grid')
    expect(gp.page.get_by_text('GRID-NEWRM-A')).to_have_count(0)
