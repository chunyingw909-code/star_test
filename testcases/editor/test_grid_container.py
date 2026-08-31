import allure
from playwright.sync_api import expect


@allure.feature('界面编辑器')
@allure.story('栅格布局-容器组件')
@allure.title('拖拽容器后画布出现组件，自带嵌套投放区')
@allure.severity(allure.severity_level.BLOCKER)
def test_container_default(grid_container_page):
    cp = grid_container_page
    expect(cp.canvas_widgets()).to_have_count(1)
    expect(cp.canvas_widgets().first).to_contain_text('容器')
    expect(cp.nested_dropzone()).to_have_count(1)


@allure.feature('界面编辑器')
@allure.story('栅格布局-容器组件')
@allure.title('点击容器，右侧属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_select_shows_properties(grid_container_page):
    cp = grid_container_page
    expect(cp.prop_col_span).to_have_value('4')
    expect(cp.prop_title).to_have_value('容器')
    expect(cp.prop_columns).to_have_value('4')
    expect(cp.prop_gap).to_have_value('8')
    expect(cp.prop_padding).to_have_value('8')
    expect(cp.prop_min_height).to_have_value('150')
    assert cp.widget_grid_columns() == 4


@allure.feature('界面编辑器')
@allure.story('栅格布局-容器组件')
@allure.title('修改列数为 3，内部 grid 变成 3 列')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_columns_3(grid_container_page):
    cp = grid_container_page
    cp.prop_columns.fill('3')
    expect(cp.prop_columns).to_have_value('3')
    assert cp.widget_grid_columns() == 3


@allure.feature('界面编辑器')
@allure.story('栅格布局-容器组件')
@allure.title('修改间距为 24px，内部 grid 的 gap 同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_gap_24(grid_container_page):
    cp = grid_container_page
    cp.prop_gap.fill('24')
    expect(cp.prop_gap).to_have_value('24')
    expect(cp.widget_grid()).to_have_css('gap', '24px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-容器组件')
@allure.title('修改标题为"指标区"，画布标签同步')
@allure.severity(allure.severity_level.NORMAL)
def test_container_modify_title(grid_container_page):
    cp = grid_container_page
    cp.prop_title.fill('指标区')
    expect(cp.prop_title).to_have_value('指标区')
    expect(cp.canvas_widgets().first).to_contain_text('指标区')


@allure.feature('界面编辑器')
@allure.story('栅格布局-容器组件')
@allure.title('修改最小高度为 300')
@allure.severity(allure.severity_level.NORMAL)
def test_container_min_height(grid_container_page):
    cp = grid_container_page
    cp.prop_min_height.fill('300')
    expect(cp.prop_min_height).to_have_value('300')


@allure.feature('界面编辑器')
@allure.story('栅格布局-容器组件')
@allure.title('往容器里拖一个文本组件，落在容器的嵌套投放区内')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_nested_drop(grid_container_page):
    cp = grid_container_page
    cp.drag_into_container('TextWidget')
    # 根投放区仍只有 1 个直接子组件（那个容器）
    root_direct = cp.page.locator(
        '[data-testid="dropzone:root:default-zone"] > [data-puck-component]')
    expect(root_direct).to_have_count(1)
    # 文本组件落在了容器的 :children 投放区里
    nested = cp.nested_dropzone().locator('[data-puck-component]')
    expect(nested).to_have_count(1)
    expect(nested.first).to_contain_text('标题')


@allure.feature('界面编辑器')
@allure.story('栅格布局-容器组件')
@allure.title('复制容器组件，画布出现两个')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_duplicate(grid_container_page):
    cp = grid_container_page
    cp.duplicate_widget()
    expect(cp.canvas_widgets()).to_have_count(2)


@allure.feature('界面编辑器')
@allure.story('栅格布局-容器组件')
@allure.title('删除容器组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_delete(grid_container_page):
    cp = grid_container_page
    cp.delete_widget()
    expect(cp.canvas_widgets()).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('栅格布局-容器组件')
@allure.title('组合修改跨列数、标题、列数、间距')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_combined(grid_container_page):
    cp = grid_container_page
    cp.prop_col_span.fill('8')
    cp.prop_title.fill('分系统状态区')
    cp.prop_columns.fill('2')
    cp.prop_gap.fill('16')
    expect(cp.prop_col_span).to_have_value('8')
    expect(cp.prop_title).to_have_value('分系统状态区')
    expect(cp.prop_columns).to_have_value('2')
    expect(cp.prop_gap).to_have_value('16')
    expect(cp.canvas_widgets().first).to_contain_text('分系统状态区')
    assert cp.widget_grid_columns() == 2
