import allure
from playwright.sync_api import expect


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-占位组件')
@allure.title('添加占位后画布出现组件')
@allure.severity(allure.severity_level.BLOCKER)
def test_spacer_default(free_spacer_page):
    expect(free_spacer_page.canvas_widgets()).to_have_count(1)


@allure.feature('界面编辑器')
@allure.story('自由布局-占位组件')
@allure.title('点击组件，属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_spacer_select_shows_properties(free_spacer_page):
    free_spacer_page.click_widget()
    expect(free_spacer_page.prop_panel).to_be_visible()
    # 右侧断言
    expect(free_spacer_page.prop_columns).to_have_value('1')
    expect(free_spacer_page.prop_height).to_have_value('20')
    # 画布断言：占位盒 min-height
    expect(free_spacer_page.widget_spacer_box()).to_have_css('min-height', '20px')


@allure.feature('界面编辑器')
@allure.story('自由布局-占位组件')
@allure.title('点击画布空白区域，属性面板隐藏')
@allure.severity(allure.severity_level.NORMAL)
def test_spacer_click_blank_hides_properties(free_spacer_page):
    free_spacer_page.click_widget()
    expect(free_spacer_page.prop_panel).to_be_visible()
    free_spacer_page.click_canvas_blank()
    expect(free_spacer_page.prop_panel).to_be_hidden()


# ==================== 高度 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-占位组件')
@allure.title('高度改为 120，占位盒 min-height 同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_spacer_modify_height(free_spacer_page):
    free_spacer_page.click_widget()
    free_spacer_page.prop_height.fill('120')
    # 右侧断言
    expect(free_spacer_page.prop_height).to_have_value('120')
    # 画布断言
    expect(free_spacer_page.widget_spacer_box()).to_have_css('min-height', '120px')


@allure.feature('界面编辑器')
@allure.story('自由布局-占位组件')
@allure.title('高度恢复为 20')
@allure.severity(allure.severity_level.NORMAL)
def test_spacer_height_recover(free_spacer_page):
    free_spacer_page.click_widget()
    free_spacer_page.prop_height.fill('120')
    free_spacer_page.prop_height.fill('20')
    # 右侧断言
    expect(free_spacer_page.prop_height).to_have_value('20')
    # 画布断言
    expect(free_spacer_page.widget_spacer_box()).to_have_css('min-height', '20px')


# ==================== 占位列数 ====================
# 自由布局下占位列数没有可观察的画布效果，只校验属性往返

@allure.feature('界面编辑器')
@allure.story('自由布局-占位组件')
@allure.title('占位列数改为 4')
@allure.severity(allure.severity_level.NORMAL)
def test_spacer_modify_columns(free_spacer_page):
    free_spacer_page.click_widget()
    free_spacer_page.prop_columns.fill('4')
    expect(free_spacer_page.prop_columns).to_have_value('4')


@allure.feature('界面编辑器')
@allure.story('自由布局-占位组件')
@allure.title('占位列数恢复为 1')
@allure.severity(allure.severity_level.NORMAL)
def test_spacer_columns_recover(free_spacer_page):
    free_spacer_page.click_widget()
    free_spacer_page.prop_columns.fill('4')
    free_spacer_page.prop_columns.fill('1')
    expect(free_spacer_page.prop_columns).to_have_value('1')


# ==================== 删除 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-占位组件')
@allure.title('删除占位组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_spacer_delete(free_spacer_page):
    expect(free_spacer_page.canvas_widgets()).to_have_count(1)
    free_spacer_page.delete_widget()
    expect(free_spacer_page.canvas_widgets()).to_have_count(0)
