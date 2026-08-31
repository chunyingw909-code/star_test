import allure
from playwright.sync_api import expect

from pages.editor.editor_page import EditorPage


# 「新建」点击后弹浏览器原生 confirm（不是 MUI 弹框，get_by_role('dialog') 找不到），
# 用 page.on/once('dialog', ...) 处理：accept() = 确定，dismiss() = 取消。
#
# 本文件只管「新建对当前画布的影响」（清空 / 不清空）。
# 「新建对已保存布局的影响」（刷新后也不再出现）在 test_free_layout.py /
# test_grid_layout.py 的「保存」story 里（test_new_removes_saved_layout）。


@allure.feature('界面编辑器')
@allure.story('新建')
@allure.title('点「新建」弹出浏览器原生确认框，文案正确')
@allure.severity(allure.severity_level.CRITICAL)
def test_new_pops_native_confirm(free_text_page):
    page = free_text_page.page
    ed = EditorPage(page)

    seen = {}
    page.once('dialog', lambda d: (seen.update(type=d.type, message=d.message), d.dismiss()))
    ed.new_button.click()
    page.wait_for_timeout(500)

    assert seen.get('type') == 'confirm'
    assert seen.get('message') == EditorPage.NEW_CONFIRM_MESSAGE


@allure.feature('界面编辑器')
@allure.story('新建')
@allure.title('原生确认框点「取消」，画布内容不变')
@allure.severity(allure.severity_level.CRITICAL)
def test_new_cancel_keeps_canvas(free_text_page):
    page = free_text_page.page
    ed = EditorPage(page)
    free_text_page.click_widget()
    free_text_page.prop_content.fill('NEW-KEEP')
    expect(page.get_by_text('NEW-KEEP')).to_be_visible()

    ed.click_new_and_cancel()
    page.wait_for_timeout(800)

    expect(page.get_by_text('NEW-KEEP')).to_be_visible()
    expect(ed.all_widgets()).to_have_count(1)


@allure.feature('界面编辑器')
@allure.story('新建')
@allure.title('原生确认框点「确定」，画布被清空')
@allure.severity(allure.severity_level.CRITICAL)
def test_new_confirm_clears_canvas(free_text_page):
    page = free_text_page.page
    ed = EditorPage(page)
    free_text_page.click_widget()
    free_text_page.prop_content.fill('NEW-CLEAR')
    expect(page.get_by_text('NEW-CLEAR')).to_be_visible()

    ed.click_new_and_confirm()
    expect(ed.all_widgets()).to_have_count(0)
    expect(page.get_by_text('NEW-CLEAR')).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('新建')
@allure.title('对着模板铺好的画布点「新建」+确定，同样清空')
@allure.severity(allure.severity_level.NORMAL)
def test_new_confirm_clears_template(free_layout_page):
    from pages.editor.template_page import TemplateDialog
    page = free_layout_page.page
    ed = EditorPage(page)
    TemplateDialog(page).open().apply('综合遥测总览大屏')
    expect(page.get_by_text('卫星星座综合遥测大屏')).to_be_visible()

    ed.click_new_and_confirm()
    expect(ed.all_widgets()).to_have_count(0)
    expect(page.get_by_text('卫星星座综合遥测大屏')).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('新建')
@allure.title('[现状] 栅格布局下「新建」弹出确认框，但点确定并不清空画布')
@allure.severity(allure.severity_level.NORMAL)
def test_new_in_grid_confirm_does_not_clear(grid_text_page):
    # ⚠️ 现状记录（非期望）：栅格布局下「新建」按钮在、点击也会弹出同样文案的
    # 原生 confirm，但点「确定」后画布组件**没有被清空**（自由布局会清空）。
    # 又一处自由/栅格不一致。
    # TODO(bug) 期望：应与自由布局一致 —— 点确定后 all_widgets() 归 0。
    page = grid_text_page.page
    ed = EditorPage(page)
    expect(ed.new_button).to_be_visible()
    expect(ed.all_widgets()).to_have_count(1)

    seen = {}
    page.once('dialog', lambda d: (seen.update(type=d.type, message=d.message), d.accept()))
    ed.new_button.click()
    page.wait_for_timeout(2000)

    # 确认框本身正常
    assert seen.get('type') == 'confirm'
    assert seen.get('message') == EditorPage.NEW_CONFIRM_MESSAGE
    # 现状：画布没清空
    expect(ed.all_widgets()).to_have_count(1)
