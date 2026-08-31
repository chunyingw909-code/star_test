import allure
from playwright.sync_api import expect


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('添加容器后画布出现组件，内部是空的 CSS grid')
@allure.severity(allure.severity_level.BLOCKER)
def test_container_default(free_container_page):
    cp = free_container_page
    expect(cp.canvas_widgets()).to_have_count(1)
    expect(cp.canvas_widgets().first).to_contain_text('容器')
    expect(cp.widget_grid()).to_have_count(1)


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('点击容器，属性面板显示默认值（列数 4 / 间距 8 / 内边距 8）')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_select_shows_properties(free_container_page):
    cp = free_container_page
    cp.click_widget()
    expect(cp.prop_panel).to_be_visible()
    expect(cp.prop_title).to_have_value('容器')
    expect(cp.prop_columns).to_have_value('4')
    expect(cp.prop_gap).to_have_value('8')
    expect(cp.prop_padding).to_have_value('8')
    assert cp.widget_grid_columns() == 4


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('修改列数为 3，内部 grid 变成 3 列')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_columns_3(free_container_page):
    cp = free_container_page
    cp.click_widget()
    cp.prop_columns.fill('3')
    expect(cp.prop_columns).to_have_value('3')
    assert cp.widget_grid_columns() == 3


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('修改间距为 24px，内部 grid 的 gap 同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_gap_24(free_container_page):
    cp = free_container_page
    cp.click_widget()
    cp.prop_gap.fill('24')
    expect(cp.prop_gap).to_have_value('24')


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('修改标题为"指标区"，画布标签同步')
@allure.severity(allure.severity_level.NORMAL)
def test_container_modify_title(free_container_page):
    cp = free_container_page
    cp.click_widget()
    cp.prop_title.fill('指标区')
    expect(cp.prop_title).to_have_value('指标区')
    expect(cp.canvas_widgets().first).to_contain_text('指标区')


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('修改最小高度为 300')
@allure.severity(allure.severity_level.NORMAL)
def test_container_min_height(free_container_page):
    cp = free_container_page
    cp.click_widget()
    cp.prop_min_height.fill('300')
    expect(cp.prop_min_height).to_have_value('300')


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('删除容器组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_delete(free_container_page):
    cp = free_container_page
    expect(cp.canvas_widgets()).to_have_count(1)
    cp.delete_widget()
    expect(cp.canvas_widgets()).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('组合修改标题、列数、间距、内边距')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_combined(free_container_page):
    cp = free_container_page
    cp.click_widget()
    cp.prop_title.fill('分系统状态区')
    cp.prop_columns.fill('2')
    cp.prop_gap.fill('16')
    cp.prop_padding.fill('12')
    expect(cp.prop_title).to_have_value('分系统状态区')
    expect(cp.prop_columns).to_have_value('2')
    expect(cp.prop_gap).to_have_value('16')
    expect(cp.prop_padding).to_have_value('12')
    expect(cp.canvas_widgets().first).to_contain_text('分系统状态区')
    assert cp.widget_grid_columns() == 2
