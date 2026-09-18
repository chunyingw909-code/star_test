"""画布 —— 组件在画布上的集体行为，跟具体是哪个组件无关。

这里管：
  - 「添加组件」菜单里的项和内置组件清单一致
  - 可视视图 ↔ <>JSON 视图 互切；在 JSON 里改内容 / 改 root 配置，切回画布跟着变

不归这里的：
  - 单个组件自己的属性怎么改 → 各组件自己的测试文件（test_free_文本.py 之类）
  - 整份布局的新建 / 保存 / 模板 / 发布 / 版本 → test_layout_manage.py
  - 编辑预览切换 / 分辨率 / 主题 → test_display.py

还没覆盖（后续补在本文件）：组件拖动、缩放、删除、多个组件共存。
"""
import allure
from playwright.sync_api import expect

from pages.editor.widget_catalog import ACTIVE_LABELS


# ==================== 「添加组件」菜单 ====================
# ACTIVE_LABELS 是 pages/editor/widget_catalog.py 里当前开放的 8 个组件清单。
# 一条用例就够：点开菜单，把菜单里的项和这份清单做「完全一致」比对。
# 这一条同时管住了三件事：数量对不对、每个该有的在不在、有没有多出来的。

@allure.feature('界面编辑器')
@allure.story('画布-添加组件菜单')
@allure.title('"添加组件"菜单里的项和当前开放组件清单完全一致（8 个）')
@allure.severity(allure.severity_level.CRITICAL)
def test_add_component_menu_matches_catalog(free_layout_page):
    free_layout_page.add_component_button.click()
    expect(free_layout_page.menu).to_be_visible()

    # add_menu_labels() 读的是菜单里每一项的显示名（每项文本是「显示名\n分类」，取第一行）
    actual = sorted(free_layout_page.add_menu_labels())
    expected = sorted(ACTIVE_LABELS)
    # 断言消息把「多出的」「缺的」分开列，失败时一眼看出差在哪
    assert actual == expected, (
        f'菜单和组件清单对不上：'
        f'多出={sorted(set(actual) - set(expected))} '
        f'缺少={sorted(set(expected) - set(actual))}'
    )


# ==================== UI可视 / <>JSON 视图 ====================

@allure.feature('界面编辑器')
@allure.story('画布-JSON视图')
@allure.title('UI可视 ↔ <>JSON 自由切换，激活态互斥')
@allure.severity(allure.severity_level.CRITICAL)
def test_json_toggle_switches_view(free_layout_page):
    # 编辑器上方一对按钮「UI可视 / <>JSON」，点哪个哪个激活、两者互斥。
    # active_view() 以「JSON 编辑框可不可见」来判断当前在哪个视图。
    fp = free_layout_page
    assert fp.active_view() == 'ui'    # 一进来是 UI 视图
    fp.switch_to_json()
    assert fp.active_view() == 'json'
    expect(fp.json_editor.first).to_be_visible()
    fp.switch_to_ui()
    assert fp.active_view() == 'ui'
    expect(fp.canvas).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('画布-JSON视图')
@allure.title('<>JSON 模式展示画布的布局 JSON（root + widgets）')
@allure.severity(allure.severity_level.CRITICAL)
def test_json_shows_layout_json(free_text_page):
    # 切到 JSON 视图，编辑框里就是当前画布的布局 JSON：
    #   root    —— 画布本身的配置（列数 / 行高 / 间距）
    #   widgets —— 画布上每个组件（这里放了个文本组件，所以能搜到 TextWidget）
    free_text_page.switch_to_json()
    txt = free_text_page.json_text()
    assert '"root"' in txt, txt[:200]
    assert '"widgets"' in txt
    assert 'TextWidget' in txt


@allure.feature('界面编辑器')
@allure.story('画布-JSON视图')
@allure.title('在 JSON 里改内容，切回 UI 画布同步更新')
@allure.severity(allure.severity_level.CRITICAL)
def test_json_edit_syncs_to_canvas(free_text_page):
    # 在 JSON 里把文本内容 A 改成 B，切回 UI，画布上的字应跟着变成 B。
    # 验证「JSON 编辑 -> 画布」这条方向是通的。
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
@allure.story('画布-JSON视图')
@allure.title('在 JSON 里改 root 配置，切回 UI 说明文字同步')
@allure.severity(allure.severity_level.NORMAL)
def test_json_edit_root_updates_caption(free_text_page):
    # 在 JSON 里改 root 的 cols（列数）和 gap（间距），切回 UI，
    # 画布上方那行「自由布局（GridStack）· N 列 / 行高 / 间距 Npx」说明应同步。
    fp = free_text_page
    fp.switch_to_json()
    txt = fp.json_text()
    new = txt.replace('"cols": 12', '"cols": 6').replace('"gap": 8', '"gap": 24')
    assert new != txt, '预期 JSON 里有 "cols": 12 / "gap": 8'
    fp.set_json(new)
    fp.switch_to_ui()
    expect(fp.gridstack_caption).to_contain_text('6 列')
    expect(fp.gridstack_caption).to_contain_text('间距 24px')
