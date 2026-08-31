import allure
import pytest
from playwright.sync_api import expect

from pages.editor.widget_catalog import LABELS
from pages.editor.editor_page import EditorPage


@allure.feature('界面编辑器')
@allure.story('自由布局-组件库')
@allure.title('"添加组件"菜单项数量与组件清单一致（12 项）')
@allure.severity(allure.severity_level.CRITICAL)
def test_add_component_menu_count(free_layout_page):
    free_layout_page.add_component_button.click()
    expect(free_layout_page.menu).to_be_visible()
    expect(free_layout_page.menu.get_by_role('menuitem')).to_have_count(len(LABELS))


@allure.feature('界面编辑器')
@allure.story('自由布局-组件库')
@allure.title('"添加组件"菜单逐项核对：{label}')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('label', LABELS)
def test_add_component_menu_item(free_layout_page, label):
    free_layout_page.add_component_button.click()
    expect(free_layout_page.component_item(label)).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('自由布局-组件库')
@allure.title('"添加组件"菜单组件集合与清单完全一致')
@allure.severity(allure.severity_level.CRITICAL)
def test_add_component_menu_exact(free_layout_page):
    free_layout_page.add_component_button.click()
    actual = free_layout_page.add_menu_labels()
    assert sorted(actual) == sorted(LABELS), (
        f'多出={sorted(set(actual) - set(LABELS))} 缺少={sorted(set(LABELS) - set(actual))}'
    )

# ==================== UI可视 / <>JSON 视图 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-JSON视图')
@allure.title('UI可视 ↔ <>JSON 自由切换，激活态互斥')
@allure.severity(allure.severity_level.CRITICAL)
def test_json_toggle_switches_view(free_layout_page):
    fp = free_layout_page
    assert fp.active_view() == 'ui'
    fp.switch_to_json()
    assert fp.active_view() == 'json'
    expect(fp.json_editor.first).to_be_visible()
    fp.switch_to_ui()
    assert fp.active_view() == 'ui'
    expect(fp.canvas).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('自由布局-JSON视图')
@allure.title('<>JSON 模式展示画布的布局 JSON（root + widgets）')
@allure.severity(allure.severity_level.CRITICAL)
def test_json_shows_layout_json(free_text_page):
    free_text_page.switch_to_json()
    txt = free_text_page.json_text()
    assert '"root"' in txt, txt[:200]
    assert '"widgets"' in txt
    assert 'TextWidget' in txt


@allure.feature('界面编辑器')
@allure.story('自由布局-JSON视图')
@allure.title('在 JSON 里改内容，切回 UI 画布同步更新')
@allure.severity(allure.severity_level.CRITICAL)
def test_json_edit_syncs_to_canvas(free_text_page):
    page = free_text_page.page
    free_text_page.click_widget()
    free_text_page.prop_content.fill('JSON-SYNC-A')
    expect(page.get_by_text('JSON-SYNC-A')).to_be_visible()

    free_text_page.switch_to_json()
    txt = free_text_page.json_text()
    assert 'JSON-SYNC-A' in txt
    free_text_page.set_json(txt.replace('JSON-SYNC-A', 'JSON-SYNC-B'))
    free_text_page.switch_to_ui()

    expect(page.get_by_text('JSON-SYNC-B')).to_be_visible()
    expect(page.get_by_text('JSON-SYNC-A')).to_have_count(0)
    expect(free_text_page.canvas_widgets()).to_have_count(1)


@allure.feature('界面编辑器')
@allure.story('自由布局-JSON视图')
@allure.title('在 JSON 里改 root 配置，切回 UI 说明文字同步')
@allure.severity(allure.severity_level.NORMAL)
def test_json_edit_root_updates_caption(free_text_page):
    fp = free_text_page
    fp.switch_to_json()
    txt = fp.json_text()
    new = txt.replace('"cols": 12', '"cols": 6').replace('"gap": 8', '"gap": 24')
    assert new != txt, '预期 JSON 里有 "cols": 12 / "gap": 8'
    fp.set_json(new)
    fp.switch_to_ui()
    expect(fp.gridstack_caption).to_contain_text('6 列')
    expect(fp.gridstack_caption).to_contain_text('间距 24px')


# ==================== 保存 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-保存')
@allure.title('未填布局名称直接保存，提示"请输入布局名称"，画布不变')
@allure.severity(allure.severity_level.CRITICAL)
def test_save_without_name_shows_hint(free_text_page):
    fp = free_text_page
    fp.save_button.first.click()
    expect(fp.page.get_by_role('alert').filter(has_text='请输入布局名称')).to_be_visible()
    expect(fp.canvas_widgets()).to_have_count(1)


@allure.feature('界面编辑器')
@allure.story('自由布局-保存')
@allure.title('填布局名称后保存，提示"保存成功"')
@allure.severity(allure.severity_level.CRITICAL)
def test_save_with_name_succeeds(free_text_saved_cleanup):
    tp = free_text_saved_cleanup
    tp.save_layout('AUTOTEST-SAVE')
    expect(tp.page.get_by_role('alert').filter(has_text='保存成功')).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('自由布局-保存')
@allure.title('保存后刷新页面，组件仍在')
@allure.severity(allure.severity_level.CRITICAL)
def test_save_persists_after_reload(free_text_saved_cleanup):
    tp = free_text_saved_cleanup
    ed = EditorPage(tp.page)
    tp.click_widget()
    tp.prop_content.fill('PERSIST-A')
    tp.save_layout('AUTOTEST-SAVE')
    expect(tp.page.get_by_role('alert').filter(has_text='保存成功')).to_be_visible()

    ed.reload_editor()
    expect(tp.page.get_by_text('PERSIST-A')).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('自由布局-保存')
@allure.title('首次「保存」前，未保存的编辑刷新即丢')
@allure.severity(allure.severity_level.CRITICAL)
def test_unsaved_lost_before_first_save(free_text_page):
    # 还没「保存」过 → 后端没有对应 page 记录 → 编辑不会被自动保存，刷新即丢。
    tp = free_text_page
    ed = EditorPage(tp.page)
    tp.click_widget()
    tp.prop_content.fill('UNSAVED-A')
    expect(tp.page.get_by_text('UNSAVED-A')).to_be_visible()

    ed.reload_editor()
    expect(tp.page.get_by_text('UNSAVED-A')).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('自由布局-保存')
@allure.title('首次「保存」之后，后续编辑会防抖自动保存（无需再点保存）')
@allure.severity(allure.severity_level.NORMAL)
def test_autosaves_edits_after_save(free_text_saved_cleanup):
    # 首次「保存」建立 page 记录后，应用对后续每次编辑做防抖自动保存
    # （PUT /api/pages/<id>，约数秒延迟），不需要再点保存。栅格布局同样行为。
    tp = free_text_saved_cleanup
    ed = EditorPage(tp.page)

    tp.click_widget()
    tp.prop_content.fill('AUTOSAVE-A')
    tp.save_layout('AUTOTEST-SAVE')
    expect(tp.page.get_by_role('alert').filter(has_text='保存成功')).to_be_visible()

    # 再加一个组件，不点保存，等防抖自动保存落库
    tp.add_component_button.click()
    tp.component_item('图表').click()
    expect(tp.canvas_widgets()).to_have_count(2)
    tp.page.wait_for_timeout(8000)

    ed.reload_editor()
    expect(tp.canvas_widgets()).to_have_count(2)


@allure.feature('界面编辑器')
@allure.story('自由布局-保存')
@allure.title('保存后「新建」+确定，刷新页面组件也不再出现')
@allure.severity(allure.severity_level.NORMAL)
def test_new_removes_saved_layout(free_text_saved_cleanup):
    tp = free_text_saved_cleanup
    ed = EditorPage(tp.page)
    tp.click_widget()
    tp.prop_content.fill('NEW-REMOVES-A')
    tp.save_layout('AUTOTEST-SAVE')
    expect(tp.page.get_by_role('alert').filter(has_text='保存成功')).to_be_visible()

    ed.click_new_and_confirm()
    expect(ed.all_widgets()).to_have_count(0)

    ed.reload_editor()
    expect(tp.page.get_by_text('NEW-REMOVES-A')).to_have_count(0)
