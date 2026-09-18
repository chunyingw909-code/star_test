"""布局管理 —— 对「整份布局」的存和取。

这里管：
  - 新建：清空画布（浏览器原生确认框）
  - 保存：布局名称 + 保存、刷新后还在
  - 模板：打开弹框、套用、覆盖、替换、模板里的组件可编辑、保存当前为模板
  - 发布：发布看板（开发 / 预发布 / 生产）
  - 版本管理：右抽屉「编辑管理 / 版本管理」两个 tab

模板放这里，是因为套模板本质就是「把一份现成的布局读进画布」，
跟新建（清空）、保存（写出去）是同一件事的正反面。

不归这里的：
  - 组件在画布上的行为、JSON 视图 → test_canvas.py
  - 编辑预览切换 / 分辨率 / 主题 → test_display.py
  - 插件开关 → test_plugin.py
"""
import allure
import pytest
from playwright.sync_api import expect

from pages.editor.editor_page import EditorPage
from pages.editor.template_page import TemplateDialog

TPL_NAMES = list(TemplateDialog.TEMPLATES)


def _select_template_text_widget(page):
    """逐个点击模板文本及其祖先，直到右侧出现「内容」框。

    模板组件可能嵌在容器内，事件绑定在文本外层而不是 <p> 本身。
    """
    candidates = page.locator('.react-grid-item p')
    for i in range(candidates.count()):
        target = candidates.nth(i)
        for _ in range(6):
            target.click(force=True)
            page.wait_for_timeout(250)
            content = page.get_by_label('内容')
            if content.count() and content.first.is_visible():
                return
            target = target.locator('xpath=..')
    raise AssertionError('模板里没找到可编辑的文本组件')


# ==================== 新建 ====================
# 「新建」点击后弹浏览器原生 confirm（不是 MUI 弹框，get_by_role('dialog') 找不到），
# 用 page.on/once('dialog', ...) 处理：accept() = 确定，dismiss() = 取消。

@allure.feature('界面编辑器')
@allure.story('布局管理-新建')
@allure.title('点「新建」弹出浏览器原生确认框，文案正确')
@allure.severity(allure.severity_level.CRITICAL)
def test_new_pops_native_confirm(free_text_page):
    page = free_text_page.page
    ed = free_text_page.editor

    seen = {}
    page.once('dialog', lambda d: (seen.update(type=d.type, message=d.message), d.dismiss()))
    ed.new_button.click()
    page.wait_for_timeout(500)

    assert seen.get('type') == 'confirm'
    assert seen.get('message') == EditorPage.NEW_CONFIRM_MESSAGE


@allure.feature('界面编辑器')
@allure.story('布局管理-新建')
@allure.title('原生确认框点「取消」，画布内容不变')
@allure.severity(allure.severity_level.CRITICAL)
def test_new_cancel_keeps_canvas(free_text_page):
    page = free_text_page.page
    ed = free_text_page.editor
    free_text_page.click_widget()
    free_text_page.prop_content.fill('NEW-KEEP')
    expect(page.get_by_text('NEW-KEEP')).to_be_visible()

    ed.click_new_and_cancel()
    page.wait_for_timeout(800)

    expect(page.get_by_text('NEW-KEEP')).to_be_visible()
    expect(ed.all_widgets()).to_have_count(1)


@allure.feature('界面编辑器')
@allure.story('布局管理-新建')
@allure.title('原生确认框点「确定」，画布被清空')
@allure.severity(allure.severity_level.CRITICAL)
def test_new_confirm_clears_canvas(free_text_page):
    page = free_text_page.page
    ed = free_text_page.editor
    free_text_page.click_widget()
    free_text_page.prop_content.fill('NEW-CLEAR')
    expect(page.get_by_text('NEW-CLEAR')).to_be_visible()

    ed.click_new_and_confirm()
    expect(ed.all_widgets()).to_have_count(0)
    expect(page.get_by_text('NEW-CLEAR')).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('布局管理-新建')
@allure.title('对着模板铺好的画布点「新建」+确定，同样清空')
@allure.severity(allure.severity_level.NORMAL)
def test_new_confirm_clears_template(free_layout_page):
    page = free_layout_page.page
    ed = free_layout_page.editor
    TemplateDialog(page).open().apply('综合遥测总览大屏')
    marker = TemplateDialog.TEMPLATES['综合遥测总览大屏']
    expect(page.get_by_text(marker)).to_be_visible()

    ed.click_new_and_confirm()
    expect(ed.all_widgets()).to_have_count(0)
    expect(page.get_by_text(marker)).to_have_count(0)


# ==================== 保存 ====================

@allure.feature('界面编辑器')
@allure.story('布局管理-保存')
@allure.title('未填布局名称直接保存，提示"请输入布局名称"，画布不变')
@allure.severity(allure.severity_level.CRITICAL)
def test_save_without_name_shows_hint(free_text_page):
    fp = free_text_page
    fp.save_button.first.click()
    expect(fp.page.get_by_role('alert').filter(has_text='请输入布局名称')).to_be_visible()
    expect(fp.canvas_widgets()).to_have_count(1)


@allure.feature('界面编辑器')
@allure.story('布局管理-保存')
@allure.title('填布局名称后保存，提示"保存成功"')
@allure.severity(allure.severity_level.CRITICAL)
def test_save_with_name_succeeds(free_text_saved_cleanup):
    tp = free_text_saved_cleanup
    tp.save_layout('AUTOTEST-SAVE')
    expect(tp.page.get_by_role('alert').filter(has_text='保存成功')).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('布局管理-保存')
@allure.title('保存后刷新页面，组件仍在')
@allure.severity(allure.severity_level.CRITICAL)
def test_save_persists_after_reload(free_text_saved_cleanup):
    tp = free_text_saved_cleanup
    ed = tp.editor
    tp.click_widget()
    tp.prop_content.fill('PERSIST-A')
    tp.save_layout('AUTOTEST-SAVE')
    expect(tp.page.get_by_role('alert').filter(has_text='保存成功')).to_be_visible()

    ed.reload_editor()
    expect(tp.page.get_by_text('PERSIST-A')).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('布局管理-保存')
@allure.title('首次「保存」前，未保存的编辑刷新即丢')
@allure.severity(allure.severity_level.CRITICAL)
def test_unsaved_lost_before_first_save(free_text_page):
    # 还没「保存」过 → 后端没有对应 page 记录 → 编辑不会被自动保存，刷新即丢。
    tp = free_text_page
    ed = tp.editor
    tp.click_widget()
    tp.prop_content.fill('UNSAVED-A')
    expect(tp.page.get_by_text('UNSAVED-A')).to_be_visible()

    ed.reload_editor()
    expect(tp.page.get_by_text('UNSAVED-A')).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('布局管理-保存')
@allure.title('保存后「新建」只清当前画布，刷新会恢复已保存布局')
@allure.severity(allure.severity_level.NORMAL)
def test_new_keeps_saved_layout(free_text_saved_cleanup):
    tp = free_text_saved_cleanup
    ed = tp.editor
    tp.click_widget()
    tp.prop_content.fill('NEW-REMOVES-A')
    tp.save_layout('AUTOTEST-SAVE')
    expect(tp.page.get_by_role('alert').filter(has_text='保存成功')).to_be_visible()

    ed.click_new_and_confirm()
    expect(ed.all_widgets()).to_have_count(0)

    ed.reload_editor()
    expect(tp.page.get_by_text('NEW-REMOVES-A')).to_be_visible()


# ==================== 模板 · 弹框本身 ====================

@allure.feature('界面编辑器')
@allure.story('布局管理-模板')
@allure.title('点「模板」打开「选择页面模板」弹框：内置模板 + 保存当前 + 取消')
@allure.severity(allure.severity_level.CRITICAL)
def test_template_dialog_opens(free_layout_page):
    td = TemplateDialog(free_layout_page.page).open()
    expect(td.title).to_be_visible()
    expect(td.save_current_button).to_be_visible()
    expect(td.cancel_button).to_be_visible()
    for name in TPL_NAMES:
        expect(td.card(name)).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('布局管理-模板')
@allure.title('模板弹框逐一核对：{name}')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('name', TPL_NAMES)
def test_template_dialog_lists_all(free_layout_page, name):
    td = TemplateDialog(free_layout_page.page).open()
    expect(td.card(name)).to_have_count(1)


@allure.feature('界面编辑器')
@allure.story('布局管理-模板')
@allure.title('点「取消」关闭弹框，画布不变')
@allure.severity(allure.severity_level.NORMAL)
def test_template_cancel(free_text_page):
    free_text_page.click_widget()
    free_text_page.prop_content.fill('TPL-CANCEL')
    td = TemplateDialog(free_text_page.page).open()
    td.cancel()
    expect(td.page.get_by_role('dialog')).to_have_count(0)
    expect(free_text_page.page.get_by_text('TPL-CANCEL')).to_be_visible()


# ==================== 模板 · 保存当前 / 套用 / 删除 ====================
# 「保存当前为模板」弹的是浏览器原生 prompt（不是 MUI 框）：
#   message=「模板名称:」，默认值「新建面板」。
# 自定义模板卡片右上角 CloseIcon 删除时弹原生 confirm「确定删除此模板？」。

CUSTOM_TPL_NAME = 'AUTOTEST-CUSTOM-TPL'
CUSTOM_TPL_MARKER = 'AUTOTEST-CUSTOM-MARKER'


@pytest.fixture
def custom_template_cleanup(free_text_page):
    """保存自定义模板的用例用：teardown 里把残留的自定义模板删掉，避免污染列表。"""
    yield free_text_page
    page = free_text_page.page
    try:
        td = TemplateDialog(page)
        if page.get_by_role('dialog').count() == 0:
            td.open()
        if td.card(CUSTOM_TPL_NAME).count():
            td.click_delete_and_confirm(CUSTOM_TPL_NAME)
            page.wait_for_timeout(800)
        if page.get_by_role('dialog').count():
            td.cancel()
    except Exception as e:
        print(f'[custom_template_cleanup] 清理失败: {e}')


@allure.feature('界面编辑器')
@allure.story('布局管理-模板')
@allure.title('「保存当前为模板」弹原生命名框，点取消不保存')
@allure.severity(allure.severity_level.CRITICAL)
def test_template_save_current_cancel(free_text_page):
    page = free_text_page.page
    free_text_page.click_widget()
    free_text_page.prop_content.fill(CUSTOM_TPL_MARKER)

    seen = {}
    page.once('dialog', lambda d: (
        seen.update(type=d.type, message=d.message, default=d.default_value),
        d.dismiss(),
    ))
    td = TemplateDialog(page).open()
    td.save_current_button.click()
    page.wait_for_timeout(800)

    assert seen.get('type') == 'prompt'
    assert seen.get('message') == TemplateDialog.PROMPT_MESSAGE
    assert seen.get('default') == TemplateDialog.PROMPT_DEFAULT
    expect(td.card(CUSTOM_TPL_NAME)).to_have_count(0)
    expect(td.toast('已保存为模板')).to_have_count(0)
    td.cancel()


@allure.feature('界面编辑器')
@allure.story('布局管理-模板')
@allure.title('「保存当前为模板」确定后提示成功，列表出现该模板，可套用、可删除')
@allure.severity(allure.severity_level.CRITICAL)
def test_template_save_current_button(custom_template_cleanup):
    tp = custom_template_cleanup
    page = tp.page
    tp.click_widget()
    tp.prop_content.fill(CUSTOM_TPL_MARKER)

    # —— 保存 ——
    td = TemplateDialog(page).open()
    td.click_save_current_and_confirm(CUSTOM_TPL_NAME)
    expect(td.toast(f'已保存为模板"{CUSTOM_TPL_NAME}"')).to_be_visible()
    expect(td.card(CUSTOM_TPL_NAME)).to_be_visible()
    expect(td.card(CUSTOM_TPL_NAME)).to_contain_text(TemplateDialog.CUSTOM_CAPTION)

    # —— 套用：先关弹框、清画布，再打开套用刚存的模板 ——
    td.cancel()
    EditorPage(page).click_new_and_confirm()
    expect(EditorPage(page).all_widgets()).to_have_count(0)

    td.open().apply(CUSTOM_TPL_NAME)
    expect(page.get_by_text(CUSTOM_TPL_MARKER)).to_be_visible()

    # —— 删除：取消保留 / 确定移除 ——
    td.open()
    expect(td.card(CUSTOM_TPL_NAME)).to_be_visible()
    td.click_delete_and_cancel(CUSTOM_TPL_NAME)
    page.wait_for_timeout(500)
    expect(td.card(CUSTOM_TPL_NAME)).to_be_visible()

    td.click_delete_and_confirm(CUSTOM_TPL_NAME)
    expect(td.toast('模板已删除')).to_be_visible()
    expect(td.card(CUSTOM_TPL_NAME)).to_have_count(0)
    td.cancel()


# ==================== 模板 · 应用 ====================

@allure.feature('界面编辑器')
@allure.story('布局管理-模板')
@allure.title('应用模板后画布铺上对应内容：{name}')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('name, marker', list(TemplateDialog.TEMPLATES.items()))
def test_apply_template(free_layout_page, name, marker):
    page = free_layout_page.page
    ed = free_layout_page.editor
    TemplateDialog(page).open().apply(name)
    expect(page.get_by_text(marker).first).to_be_visible()
    expect(ed.all_widgets().first).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('布局管理-模板')
@allure.title('应用模板会覆盖画布上原有的组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_apply_template_overwrites_existing(free_text_page):
    page = free_text_page.page
    free_text_page.click_widget()
    free_text_page.prop_content.fill('TPL-OVERWRITE')
    expect(page.get_by_text('TPL-OVERWRITE')).to_be_visible()

    TemplateDialog(page).open().apply('综合遥测总览大屏')
    expect(page.get_by_text('TPL-OVERWRITE')).to_have_count(0)
    expect(page.get_by_text(TemplateDialog.TEMPLATES['综合遥测总览大屏'])).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('布局管理-模板')
@allure.title('切换到另一个模板会完全替换，不叠加')
@allure.severity(allure.severity_level.CRITICAL)
def test_switch_template_replaces(free_layout_page):
    page = free_layout_page.page
    td = TemplateDialog(page)
    td.open().apply('综合遥测总览大屏')
    first_marker = TemplateDialog.TEMPLATES['综合遥测总览大屏']
    second_marker = TemplateDialog.TEMPLATES['故障研判与应急面板']
    expect(page.get_by_text(first_marker)).to_be_visible()

    td.open().apply('故障研判与应急面板')
    expect(page.get_by_text(second_marker)).to_be_visible()
    expect(page.get_by_text(first_marker)).to_have_count(0)


# ==================== 模板 · 内容 ====================

@allure.feature('界面编辑器')
@allure.story('布局管理-模板')
@allure.title('"故障研判与应急面板"标题为红色 rgb(231, 76, 60)')
@allure.severity(allure.severity_level.NORMAL)
def test_template2_title_is_red(free_layout_page):
    page = free_layout_page.page
    TemplateDialog(page).open().apply('故障研判与应急面板')
    title_p = page.locator('p').filter(has_text='实时告警与研判分析').first
    expect(title_p).to_have_css('color', 'rgb(231, 76, 60)')


@allure.feature('界面编辑器')
@allure.story('布局管理-模板')
@allure.title('模板里的组件可编辑：改内容与颜色，画布同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_template_content_is_editable(free_layout_page):
    page = free_layout_page.page
    TemplateDialog(page).open().apply('故障研判与应急面板')

    _select_template_text_widget(page)
    page.get_by_label('内容').first.fill('TPL-EDIT-PROOF')
    page.get_by_label('颜色', exact=True).first.fill('#00ff00')

    edited_p = page.locator('p').filter(has_text='TPL-EDIT-PROOF').first
    expect(edited_p).to_have_text('TPL-EDIT-PROOF')
    expect(edited_p).to_have_css('color', 'rgb(0, 255, 0)')


# ==================== 发布 ====================

@allure.feature('界面编辑器')
@allure.story('布局管理-发布')
@allure.title('点「发布」弹出「发布看板」，三个环境各一行、各有「发布」按钮')
@allure.severity(allure.severity_level.CRITICAL)
def test_publish_dialog_opens(free_layout_page):
    ed = free_layout_page.editor
    ed.open_publish_dialog()
    # 弹窗断言
    for env in ['开发环境', '预发布', '生产环境']:
        expect(ed.publish_dialog).to_contain_text(env)
    expect(ed.publish_dialog).to_contain_text('尚未发布')
    expect(ed.publish_env_buttons).to_have_count(3)
    ed.publish_dialog_close.click()
    expect(ed.publish_dialog).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('布局管理-发布')
@allure.title('没起布局名称就点发布，提示「保存失败，无法发布，请检查布局名称」')
@allure.severity(allure.severity_level.CRITICAL)
def test_publish_without_name_prompts(free_text_page):
    # free_text_page 的画布有组件但没填布局名称、没保存过。
    ed = free_text_page.editor
    ed.open_publish_dialog()
    # 弹窗标题里布局名是空的「」
    expect(ed.publish_dialog).to_contain_text('发布「」')

    ed.publish_to('dev')
    free_text_page.page.wait_for_timeout(1500)
    # 提示报错、没发布出去
    expect(free_text_page.page.get_by_role('alert')
           .filter(has_text='请检查布局名称')).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('布局管理-发布')
@allure.title('填名称并保存后，选「开发环境」发布，提示「已发布到开发环境」')
@allure.severity(allure.severity_level.CRITICAL)
def test_publish_to_dev_succeeds(free_text_saved_cleanup):
    tp = free_text_saved_cleanup
    ed = tp.editor
    tp.save_layout('AUTOTEST-PUBLISH')
    expect(tp.page.get_by_role('alert').filter(has_text='保存成功')).to_be_visible()

    ed.open_publish_dialog()
    # 弹窗标题里带上布局名
    expect(ed.publish_dialog).to_contain_text('发布「AUTOTEST-PUBLISH」')

    ed.publish_to('dev')
    tp.page.wait_for_timeout(2000)
    # 发布成功提示
    expect(tp.page.get_by_role('alert').filter(has_text='已发布到开发环境')).to_be_visible()


# ==================== 版本管理 ====================

@allure.feature('界面编辑器')
@allure.story('布局管理-版本管理')
@allure.title('右抽屉两个 tab：编辑管理 / 版本管理，默认在编辑管理，来回切')
@allure.severity(allure.severity_level.NORMAL)
def test_version_tab_switch(free_layout_page):
    ed = free_layout_page.editor
    expect(ed.edit_manage_tab).to_be_visible()
    expect(ed.version_manage_tab).to_be_visible()
    expect(ed.edit_manage_tab).to_have_attribute('aria-selected', 'true')

    # 切到版本管理：编辑器本体（画布 + 添加组件）被换成版本面板
    ed.version_manage_tab.click()
    expect(ed.version_manage_tab).to_have_attribute('aria-selected', 'true')
    expect(free_layout_page.add_component_button).to_have_count(0)

    # 切回编辑管理：编辑器本体回来
    ed.edit_manage_tab.click()
    expect(ed.edit_manage_tab).to_have_attribute('aria-selected', 'true')
    expect(free_layout_page.canvas).to_be_visible()
    expect(free_layout_page.add_component_button).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('布局管理-版本管理')
@allure.title('版本管理面板有「发布新版本 / 查看全屏 / 回滚编辑」，发布新版本走发布看板')
@allure.severity(allure.severity_level.NORMAL)
def test_version_manage_actions(free_text_saved_cleanup):
    tp = free_text_saved_cleanup
    ed = tp.editor
    tp.save_layout('AUTOTEST-VERSION')
    expect(tp.page.get_by_role('alert').filter(has_text='保存成功')).to_be_visible()

    ed.version_manage_tab.click()
    tp.page.wait_for_timeout(800)
    # 三个动作按钮都在
    expect(ed.publish_new_version_button).to_be_visible()
    expect(ed.view_fullscreen_button).to_be_visible()
    expect(ed.rollback_edit_button).to_be_visible()

    # 「发布新版本」打开的就是发布看板
    ed.publish_new_version_button.click()
    expect(ed.publish_dialog).to_be_visible()
    expect(ed.publish_dialog).to_contain_text('发布「AUTOTEST-VERSION」')
    ed.publish_dialog_close.click()
