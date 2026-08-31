import allure
from playwright.sync_api import expect

from pages.editor.editor_page import EditorPage


# ==================== 编辑 / 预览 切换 ====================

@allure.feature('界面编辑器')
@allure.story('预览')
@allure.title('点击"预览"后切到预览态，点"编辑"切回编辑态（toggle 状态互斥）')
@allure.severity(allure.severity_level.CRITICAL)
def test_preview_toggle_button_state(grid_layout_page):
    ed = EditorPage(grid_layout_page.page)
    # 初始：编辑态
    expect(ed.edit_button).to_have_attribute('aria-pressed', 'true')
    expect(ed.preview_button).to_have_attribute('aria-pressed', 'false')
    # 切预览
    ed.preview_button.click()
    expect(ed.preview_button).to_have_attribute('aria-pressed', 'true')
    expect(ed.edit_button).to_have_attribute('aria-pressed', 'false')
    # 切回编辑
    ed.edit_button.click()
    expect(ed.edit_button).to_have_attribute('aria-pressed', 'true')
    expect(ed.preview_button).to_have_attribute('aria-pressed', 'false')


@allure.feature('界面编辑器')
@allure.story('预览')
@allure.title('预览态下编辑器结构（左侧组件库 / 右侧属性面板 / 画布拖放区）全部隐藏')
@allure.severity(allure.severity_level.CRITICAL)
def test_preview_hides_editor_chrome(grid_layout_page):
    ed = EditorPage(grid_layout_page.page)
    # 编辑态：这些都在
    expect(ed.left_drawer_items.first).to_be_visible()
    expect(grid_layout_page.canvas).to_be_visible()

    ed.preview_button.click()

    # 预览态：编辑器结构全没了
    expect(ed.left_drawer_items).to_have_count(0)
    expect(ed.right_property_panel).to_have_count(0)
    expect(grid_layout_page.canvas).to_have_count(0)
    expect(ed.puck_components).to_have_count(0)


# ==================== 预览渲染内容 ====================

@allure.feature('界面编辑器')
@allure.story('预览')
@allure.title('编辑态搭好的组件，预览态仍然渲染出来')
@allure.severity(allure.severity_level.CRITICAL)
def test_preview_renders_widget_content(grid_text_page):
    grid_text_page.prop_content.fill('卫星遥测监控大屏')
    expect(grid_text_page.canvas_widgets().first).to_contain_text('卫星遥测监控大屏')

    ed = EditorPage(grid_text_page.page)
    ed.preview_button.click()

    # 预览里没有 puck 编辑壳，但组件内容照常渲染
    expect(ed.puck_components).to_have_count(0)
    expect(grid_text_page.page.get_by_text('卫星遥测监控大屏')).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('预览')
@allure.title('预览态下点击组件不会弹出属性面板（只读渲染）')
@allure.severity(allure.severity_level.NORMAL)
def test_preview_is_read_only(grid_text_page):
    grid_text_page.prop_content.fill('只读渲染测试')
    ed = EditorPage(grid_text_page.page)
    ed.preview_button.click()

    grid_text_page.page.get_by_text('只读渲染测试').first.click()
    expect(ed.right_property_panel).to_have_count(0)


# ==================== 切回编辑 ====================

@allure.feature('界面编辑器')
@allure.story('预览')
@allure.title('预览后切回编辑，组件库恢复、已搭组件与内容保留')
@allure.severity(allure.severity_level.CRITICAL)
def test_preview_back_to_edit_restores(grid_text_page):
    grid_text_page.prop_content.fill('保留内容测试')
    ed = EditorPage(grid_text_page.page)

    ed.preview_button.click()
    expect(ed.puck_components).to_have_count(0)

    ed.edit_button.click()
    # 组件库回来、组件还在、内容没丢
    expect(ed.left_drawer_items.first).to_be_visible()
    expect(grid_text_page.canvas_widgets()).to_have_count(1)
    expect(grid_text_page.canvas_widgets().first).to_contain_text('保留内容测试')


# ==================== 交互事件（现状：不触发）====================

@allure.feature('界面编辑器')
@allure.story('预览')
@allure.title('[现状] 组件配了「点击事件=弹窗提示」，预览态点它没有任何弹窗')
@allure.severity(allure.severity_level.NORMAL)
def test_interaction_event_does_not_fire_in_preview(grid_chart_page):
    # ⚠️ 现状记录：右侧属性面板配 点击事件=弹窗提示 + 点击目标文案，
    # 进预览态点该组件 —— 没有原生 confirm、没有 MUI 弹框、没有 snackbar、
    # 找不到那段文案。交互事件（点击/双击/阈值/悬停/定时 → 弹窗/跳转/刷新/联动）
    # 目前跑不通；配套的「流程」编排器节点也无法配置。整套交互功能未完成。
    # TODO(bug) 期望：预览/发布态点组件应按配置弹窗/跳转/刷新/联动。
    page = grid_chart_page.page
    dialogs = []
    page.on('dialog', lambda d: (dialogs.append(d.message), d.dismiss()))

    grid_chart_page.event_select('点击事件').select_option(label='弹窗提示')
    grid_chart_page.prop_click_target.fill('IEV-ALERT-TEXT')

    ed = EditorPage(page)
    ed.enter_preview()
    page.get_by_text('真实数据图表').first.click(force=True)
    page.wait_for_timeout(1000)

    assert dialogs == [], f'现状应无原生弹窗，实际 {dialogs}'
    expect(page.get_by_role('alert').filter(has_text='IEV-ALERT-TEXT')).to_have_count(0)
    expect(page.get_by_text('IEV-ALERT-TEXT')).to_have_count(0)
