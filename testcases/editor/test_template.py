import allure
import pytest
from playwright.sync_api import expect

from pages.editor.editor_page import EditorPage
from pages.editor.template_page import TemplateDialog

TPL_NAMES = list(TemplateDialog.TEMPLATES)


def _select_template_text_widget(page):
    """点中模板里那个（唯一带 <p> 的）文本组件，直到右侧出现「内容」框。
    模板在自由布局下会被包进容器，最外层组件也"含 p"，所以逐个试。
    """
    candidates = page.locator('.react-grid-item, [data-puck-component]').filter(has=page.locator('p'))
    for i in range(candidates.count()):
        candidates.nth(i).click(force=True)
        page.wait_for_timeout(400)
        content = page.get_by_label('内容')
        if content.count() and content.first.is_visible():
            return
    raise AssertionError('模板里没找到可编辑的文本组件')


# ==================== 弹框本身 ====================

@allure.feature('界面编辑器')
@allure.story('模板')
@allure.title('点「模板」打开「选择页面模板」弹框：3 个模板 + 保存当前 + 取消')
@allure.severity(allure.severity_level.CRITICAL)
def test_template_dialog_opens(free_layout_page):
    td = TemplateDialog(free_layout_page.page).open()
    expect(td.title).to_be_visible()
    expect(td.save_current_button).to_be_visible()
    expect(td.cancel_button).to_be_visible()
    for name in TPL_NAMES:
        expect(td.card(name)).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('模板')
@allure.title('模板弹框逐一核对：{name}')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('name', TPL_NAMES)
def test_template_dialog_lists_all(free_layout_page, name):
    td = TemplateDialog(free_layout_page.page).open()
    expect(td.card(name)).to_have_count(1)


@allure.feature('界面编辑器')
@allure.story('模板')
@allure.title('点「取消」关闭弹框，画布不变')
@allure.severity(allure.severity_level.NORMAL)
def test_template_cancel(free_text_page):
    free_text_page.click_widget()
    free_text_page.prop_content.fill('TPL-CANCEL')
    td = TemplateDialog(free_text_page.page).open()
    td.cancel()
    expect(td.page.get_by_role('dialog')).to_have_count(0)
    expect(free_text_page.page.get_by_text('TPL-CANCEL')).to_be_visible()


# ==================== 应用模板 ====================

@allure.feature('界面编辑器')
@allure.story('模板')
@allure.title('应用模板后画布铺上对应内容：{name}')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('name, marker', list(TemplateDialog.TEMPLATES.items()))
def test_apply_template(free_layout_page, name, marker):
    page = free_layout_page.page
    ed = EditorPage(page)
    TemplateDialog(page).open().apply(name)
    expect(page.get_by_text(marker).first).to_be_visible()
    expect(ed.all_widgets().first).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('模板')
@allure.title('应用模板会覆盖画布上原有的组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_apply_template_overwrites_existing(free_text_page):
    page = free_text_page.page
    free_text_page.click_widget()
    free_text_page.prop_content.fill('TPL-OVERWRITE')
    expect(page.get_by_text('TPL-OVERWRITE')).to_be_visible()

    TemplateDialog(page).open().apply('综合遥测总览大屏')
    expect(page.get_by_text('TPL-OVERWRITE')).to_have_count(0)
    expect(page.get_by_text('卫星星座综合遥测大屏')).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('模板')
@allure.title('画布有内容时应用模板，点卡片即生效，无二次确认弹框')
@allure.severity(allure.severity_level.NORMAL)
def test_apply_template_no_confirm_dialog(free_text_page):
    page = free_text_page.page
    free_text_page.click_widget()
    free_text_page.prop_content.fill('TPL-X')

    td = TemplateDialog(page).open()
    td.card('综合遥测总览大屏').click()
    expect(page.get_by_role('dialog')).to_have_count(0)
    expect(page.get_by_text('卫星星座综合遥测大屏')).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('模板')
@allure.title('切换到另一个模板会完全替换，不叠加')
@allure.severity(allure.severity_level.CRITICAL)
def test_switch_template_replaces(free_layout_page):
    page = free_layout_page.page
    td = TemplateDialog(page)
    td.open().apply('综合遥测总览大屏')
    expect(page.get_by_text('卫星星座综合遥测大屏')).to_be_visible()

    td.open().apply('紧凑型场景配置表单')
    expect(page.get_by_text('新建数字验证仿真任务')).to_be_visible()
    expect(page.get_by_text('卫星星座综合遥测大屏')).to_have_count(0)


# ==================== 模板内容 ====================

@allure.feature('界面编辑器')
@allure.story('模板')
@allure.title('"故障研判与应急面板"标题为红色 rgb(231, 76, 60)')
@allure.severity(allure.severity_level.NORMAL)
def test_template2_title_is_red(free_layout_page):
    page = free_layout_page.page
    TemplateDialog(page).open().apply('故障研判与应急面板')
    title_p = page.locator('p').filter(has_text='实时告警与研判分析').first
    expect(title_p).to_have_css('color', 'rgb(231, 76, 60)')


@allure.feature('界面编辑器')
@allure.story('模板')
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


@allure.feature('界面编辑器')
@allure.story('模板')
@allure.title('同一模板在自由 ↔ 栅格切换后，渲染内容与样式一致')
@allure.severity(allure.severity_level.CRITICAL)
def test_template_survives_layout_switch(free_layout_page):
    page = free_layout_page.page
    ed = EditorPage(page)
    TemplateDialog(page).open().apply('综合遥测总览大屏')

    def assert_template_present():
        for t in ['卫星星座综合遥测大屏', '核心指标', '分系统状态']:
            expect(page.get_by_text(t).first).to_be_visible()
        # 标题 p 颜色两种布局下应一致
        expect(page.locator('p').filter(has_text='卫星星座综合遥测大屏').first) \
            .to_have_css('color', 'rgb(79, 195, 247)')

    assert_template_present()
    ed.switch_to_grid()
    assert_template_present()          # 顶层组件个数会不同（4 vs 16），只比内容/样式
    ed.switch_to_free()
    assert_template_present()


# ==================== 布局无关 ====================

@allure.feature('界面编辑器')
@allure.story('模板')
@allure.title('栅格布局下同样能打开并应用模板')
@allure.severity(allure.severity_level.NORMAL)
def test_template_available_in_grid(grid_layout_page):
    page = grid_layout_page.page
    ed = EditorPage(page)
    expect(ed.template_button).to_be_visible()

    td = TemplateDialog(page).open()
    expect(td.title).to_be_visible()
    td.apply('紧凑型场景配置表单')
    expect(page.get_by_text('新建数字验证仿真任务')).to_be_visible()
