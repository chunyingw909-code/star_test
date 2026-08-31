import allure
import pytest
from playwright.sync_api import expect

from pages.editor.editor_page import EditorPage

RES_KEYS = list(EditorPage.RESOLUTIONS)   # ['fullhd', 'hd', 'tablet']


# ==================== 屏幕分辨率 ====================

@allure.feature('界面编辑器')
@allure.story('屏幕分辨率')
@allure.title('默认分辨率是 fullhd')
@allure.severity(allure.severity_level.CRITICAL)
def test_default_resolution_is_fullhd(free_layout_page):
    ed = EditorPage(free_layout_page.page)
    expect(ed.resolution_button('fullhd')).to_have_attribute('aria-pressed', 'true')


@allure.feature('界面编辑器')
@allure.story('屏幕分辨率')
@allure.title('切换分辨率：按钮状态互斥 + 画布宽度对应')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('key', RES_KEYS)
def test_set_resolution(free_layout_page, key):
    ed = EditorPage(free_layout_page.page)
    ed.set_resolution(key)
    expect(ed.resolution_button(key)).to_have_attribute('aria-pressed', 'true')
    for other in RES_KEYS:
        if other != key:
            expect(ed.resolution_button(other)).to_have_attribute('aria-pressed', 'false')
    assert abs(ed.canvas_width() - EditorPage.RESOLUTIONS[key]) <= 2, \
        f'{key} 期望画布宽 {EditorPage.RESOLUTIONS[key]}，实际 {ed.canvas_width()}'


@allure.feature('界面编辑器')
@allure.story('屏幕分辨率')
@allure.title('分辨率在布局切换后保持')
@allure.severity(allure.severity_level.NORMAL)
def test_resolution_persists_across_layout_switch(free_layout_page):
    ed = EditorPage(free_layout_page.page)
    ed.set_resolution('tablet')
    ed.switch_to_grid()
    ed.switch_to_free()
    expect(ed.resolution_button('tablet')).to_have_attribute('aria-pressed', 'true')
    assert abs(ed.canvas_width() - EditorPage.RESOLUTIONS['tablet']) <= 2


@allure.feature('界面编辑器')
@allure.story('屏幕分辨率')
@allure.title('分辨率在预览往返后保持')
@allure.severity(allure.severity_level.NORMAL)
def test_resolution_persists_across_preview(free_text_page):
    # 用带一个文本组件的画布：enter/exit_preview 依赖编辑壳里的组件挂载/卸载
    ed = EditorPage(free_text_page.page)
    ed.set_resolution('hd')
    ed.enter_preview()
    ed.exit_preview()
    expect(ed.resolution_button('hd')).to_have_attribute('aria-pressed', 'true')
    assert abs(ed.canvas_width() - EditorPage.RESOLUTIONS['hd']) <= 2


# ==================== 主题 ====================

@allure.feature('界面编辑器')
@allure.story('主题')
@allure.title('主题切换按钮 title 往返翻转（默认深色）')
@allure.severity(allure.severity_level.CRITICAL)
def test_theme_toggle_flips_button(free_layout_page):
    ed = EditorPage(free_layout_page.page)
    assert ed.current_theme() == 'dark'          # 默认深色
    ed.theme_toggle.click()
    expect(ed.theme_toggle).to_have_attribute('title', '切换至深色主题')
    ed.theme_toggle.click()
    expect(ed.theme_toggle).to_have_attribute('title', '切换至浅色主题')


@allure.feature('界面编辑器')
@allure.story('主题')
@allure.title('主题选择在布局切换后保持')
@allure.severity(allure.severity_level.NORMAL)
def test_theme_persists_across_layout_switch(free_layout_page):
    ed = EditorPage(free_layout_page.page)
    ed.theme_toggle.click()
    title_after = ed.theme_toggle_title()
    ed.switch_to_grid()
    ed.switch_to_free()
    expect(ed.theme_toggle).to_have_attribute('title', title_after)


@allure.feature('界面编辑器')
@allure.story('主题')
@allure.title('[现状] 切换主题在编辑器里没有可见效果')
@allure.severity(allure.severity_level.NORMAL)
def test_theme_has_no_visible_effect_yet(free_layout_page):
    # ⚠️ 现状记录（非期望）：编辑器里点主题切换，除了按钮自己的 title，
    # DOM 上没有任何变化 —— body 背景色不变、没有 [data-theme]、没有主题 class，
    # 进预览也一样。疑似缺陷。
    # TODO(bug) 期望：切换后画布/预览应有明暗变化。开发修复后改这里的断言。
    ed = EditorPage(free_layout_page.page)
    page = ed.page
    bg_before = page.evaluate("() => getComputedStyle(document.body).backgroundColor")

    ed.theme_toggle.click()
    page.wait_for_timeout(600)

    bg_after = page.evaluate("() => getComputedStyle(document.body).backgroundColor")
    assert bg_before == bg_after, f'现状应无变化，但 body 背景 {bg_before} → {bg_after}'
    expect(page.locator('[data-theme]')).to_have_count(0)
