import allure
from playwright.sync_api import expect


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-占位组件')
@allure.title('拖拽占位后画布出现组件，默认 span 1、高度 20px')
@allure.severity(allure.severity_level.BLOCKER)
def test_spacer_default(grid_spacer_page):
    expect(grid_spacer_page.canvas_widgets()).to_have_count(1)
    expect(grid_spacer_page.canvas_widgets().first).to_have_css('grid-column', 'span 1')
    expect(grid_spacer_page.widget_inner()).to_have_css('height', '20px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-占位组件')
@allure.title('点击组件，右侧属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_spacer_select_shows_properties(grid_spacer_page):
    expect(grid_spacer_page.prop_col_span).to_have_value('')
    expect(grid_spacer_page.prop_columns).to_have_value('1')
    expect(grid_spacer_page.prop_height).to_have_value('20')


@allure.feature('界面编辑器')
@allure.story('栅格布局-占位组件')
@allure.title('点击空白区域，右侧切换回Page属性')
@allure.severity(allure.severity_level.NORMAL)
def test_spacer_click_blank_shows_page(grid_spacer_page):
    grid_spacer_page.click_canvas_blank()
    expect(grid_spacer_page.page_props_marker).to_be_visible()


# ==================== 高度 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-占位组件')
@allure.title('高度改为 120，画布同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_spacer_modify_height(grid_spacer_page):
    grid_spacer_page.prop_height.fill('120')
    # 右侧断言
    expect(grid_spacer_page.prop_height).to_have_value('120')
    # 画布断言
    expect(grid_spacer_page.widget_inner()).to_have_css('height', '120px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-占位组件')
@allure.title('高度恢复为 20')
@allure.severity(allure.severity_level.NORMAL)
def test_spacer_height_recover(grid_spacer_page):
    grid_spacer_page.prop_height.fill('120')
    grid_spacer_page.prop_height.fill('20')
    # 右侧断言
    expect(grid_spacer_page.prop_height).to_have_value('20')
    # 画布断言
    expect(grid_spacer_page.widget_inner()).to_have_css('height', '20px')


# ==================== 占位列数 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-占位组件')
@allure.title('占位列数改为 4，跨占 4 列')
@allure.severity(allure.severity_level.CRITICAL)
def test_spacer_modify_columns(grid_spacer_page):
    grid_spacer_page.prop_columns.fill('4')
    # 右侧断言
    expect(grid_spacer_page.prop_columns).to_have_value('4')
    # 画布断言
    expect(grid_spacer_page.canvas_widgets().first).to_have_css('grid-column', 'span 4')


@allure.feature('界面编辑器')
@allure.story('栅格布局-占位组件')
@allure.title('占位列数恢复为 1')
@allure.severity(allure.severity_level.NORMAL)
def test_spacer_columns_recover(grid_spacer_page):
    grid_spacer_page.prop_columns.fill('4')
    grid_spacer_page.prop_columns.fill('1')
    # 右侧断言
    expect(grid_spacer_page.prop_columns).to_have_value('1')
    # 画布断言
    expect(grid_spacer_page.canvas_widgets().first).to_have_css('grid-column', 'span 1')


# ==================== 跨列数 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-占位组件')
@allure.title('跨列数改为 6，覆盖占位列数')
@allure.severity(allure.severity_level.NORMAL)
def test_spacer_col_span_6(grid_spacer_page):
    grid_spacer_page.prop_col_span.fill('6')
    # 右侧断言
    expect(grid_spacer_page.prop_col_span).to_have_value('6')
    # 画布断言
    expect(grid_spacer_page.canvas_widgets().first).to_have_css('grid-column', 'span 6')


# ==================== 复制 / 删除 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-占位组件')
@allure.title('复制占位组件，画布出现两个组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_spacer_duplicate(grid_spacer_page):
    grid_spacer_page.duplicate_widget()
    expect(grid_spacer_page.canvas_widgets()).to_have_count(2)


@allure.feature('界面编辑器')
@allure.story('栅格布局-占位组件')
@allure.title('删除占位组件，画布无组件，右侧切换为Page属性')
@allure.severity(allure.severity_level.CRITICAL)
def test_spacer_delete(grid_spacer_page):
    grid_spacer_page.delete_widget()
    expect(grid_spacer_page.page_props_marker).to_be_visible()
    expect(grid_spacer_page.canvas_widgets()).to_have_count(0)


# ==================== 组合修改 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-占位组件')
@allure.title('组合修改高度与占位列数')
@allure.severity(allure.severity_level.CRITICAL)
def test_spacer_combined(grid_spacer_page):
    grid_spacer_page.prop_height.fill('80')
    grid_spacer_page.prop_columns.fill('3')
    # 右侧断言
    expect(grid_spacer_page.prop_height).to_have_value('80')
    expect(grid_spacer_page.prop_columns).to_have_value('3')
    # 画布断言
    expect(grid_spacer_page.widget_inner()).to_have_css('height', '80px')
    expect(grid_spacer_page.canvas_widgets().first).to_have_css('grid-column', 'span 3')
