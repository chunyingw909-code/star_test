import allure
from playwright.sync_api import expect


@allure.feature('界面编辑器')
@allure.story('栅格布局-下拉框组件')
@allure.title('拖拽下拉框后画布出现组件，默认标签为"下拉框"')
@allure.severity(allure.severity_level.BLOCKER)
def test_dropdown_default(grid_dropdown_page):
    # 画布断言
    expect(grid_dropdown_page.canvas_widgets()).to_have_count(1)
    expect(grid_dropdown_page.canvas_widgets().first).to_contain_text('下拉框')


@allure.feature('界面编辑器')
@allure.story('栅格布局-下拉框组件')
@allure.title('点击组件，右侧属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_dropdown_select_shows_properties(grid_dropdown_page):
    # 右侧断言
    expect(grid_dropdown_page.prop_label).to_have_value('下拉框')
    expect(grid_dropdown_page.prop_options).to_have_value('选项一, 选项二, 选项三')
    expect(grid_dropdown_page.prop_default_value).to_have_value('')
    expect(grid_dropdown_page.prop_api_url).to_have_value('')
    expect(grid_dropdown_page.prop_field_name).to_have_value('')


@allure.feature('界面编辑器')
@allure.story('栅格布局-下拉框组件')
@allure.title('点击空白区域，右侧切换回Page属性')
@allure.severity(allure.severity_level.NORMAL)
def test_dropdown_click_blank_shows_page(grid_dropdown_page):
    grid_dropdown_page.click_canvas_blank()
    expect(grid_dropdown_page.page.get_by_title('布局列数')).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('栅格布局-下拉框组件')
@allure.title('修改标签为"国家选择"')
@allure.severity(allure.severity_level.CRITICAL)
def test_dropdown_modify_label(grid_dropdown_page):
    grid_dropdown_page.prop_label.fill('国家选择')
    # 右侧断言
    expect(grid_dropdown_page.prop_label).to_have_value('国家选择')
    # 画布断言
    expect(grid_dropdown_page.widget_label_text()).to_have_text('国家选择')


@allure.feature('界面编辑器')
@allure.story('栅格布局-下拉框组件')
@allure.title('清空标签')
@allure.severity(allure.severity_level.NORMAL)
def test_dropdown_clear_label(grid_dropdown_page):
    grid_dropdown_page.prop_label.fill('')
    # 右侧断言
    expect(grid_dropdown_page.prop_label).to_have_value('')
    # 画布断言
    expect(grid_dropdown_page.canvas_widgets().first).not_to_contain_text('下拉框')


@allure.feature('界面编辑器')
@allure.story('栅格布局-下拉框组件')
@allure.title('标签恢复为"下拉框"')
@allure.severity(allure.severity_level.NORMAL)
def test_dropdown_label_recover(grid_dropdown_page):
    grid_dropdown_page.prop_label.fill('国家选择')
    grid_dropdown_page.prop_label.fill('下拉框')
    # 右侧断言
    expect(grid_dropdown_page.prop_label).to_have_value('下拉框')
    # 画布断言
    expect(grid_dropdown_page.widget_label_text()).to_have_text('下拉框')


@allure.feature('界面编辑器')
@allure.story('栅格布局-下拉框组件')
@allure.title('修改选项为"选项A, 选项B"')
@allure.severity(allure.severity_level.CRITICAL)
def test_dropdown_modify_options(grid_dropdown_page):
    grid_dropdown_page.prop_options.fill('选项A, 选项B')
    # 右侧断言
    expect(grid_dropdown_page.prop_options).to_have_value('选项A, 选项B')


@allure.feature('界面编辑器')
@allure.story('栅格布局-下拉框组件')
@allure.title('选项恢复为默认三个')
@allure.severity(allure.severity_level.NORMAL)
def test_dropdown_options_recover(grid_dropdown_page):
    grid_dropdown_page.prop_options.fill('选项A, 选项B')
    grid_dropdown_page.prop_options.fill('选项一, 选项二, 选项三')
    # 右侧断言
    expect(grid_dropdown_page.prop_options).to_have_value('选项一, 选项二, 选项三')


@allure.feature('界面编辑器')
@allure.story('栅格布局-下拉框组件')
@allure.title('输入API地址和字段名')
@allure.severity(allure.severity_level.CRITICAL)
def test_dropdown_data_binding(grid_dropdown_page):
    grid_dropdown_page.prop_api_url.fill('abc')
    grid_dropdown_page.prop_field_name.fill('xyz')
    # 右侧断言
    expect(grid_dropdown_page.prop_api_url).to_have_value('abc')
    expect(grid_dropdown_page.prop_field_name).to_have_value('xyz')


@allure.feature('界面编辑器')
@allure.story('栅格布局-下拉框组件')
@allure.title('清空API地址和字段名')
@allure.severity(allure.severity_level.NORMAL)
def test_dropdown_data_binding_clear(grid_dropdown_page):
    grid_dropdown_page.prop_api_url.fill('abc')
    grid_dropdown_page.prop_field_name.fill('xyz')
    grid_dropdown_page.prop_api_url.fill('')
    grid_dropdown_page.prop_field_name.fill('')
    # 右侧断言
    expect(grid_dropdown_page.prop_api_url).to_have_value('')
    expect(grid_dropdown_page.prop_field_name).to_have_value('')


@allure.feature('界面编辑器')
@allure.story('栅格布局-下拉框组件')
@allure.title('复制下拉框组件，画布出现两个相同组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_dropdown_duplicate(grid_dropdown_page):
    grid_dropdown_page.duplicate_button.dispatch_event('click')
    # 右侧断言（复制后新组件被选中，属性不变）
    expect(grid_dropdown_page.prop_label).to_have_value('下拉框')
    expect(grid_dropdown_page.prop_options).to_have_value('选项一, 选项二, 选项三')
    # 数量断言
    expect(grid_dropdown_page.canvas_widgets()).to_have_count(2)
    # 画布断言
    expect(grid_dropdown_page.canvas_widgets().nth(0)).to_contain_text('下拉框')
    expect(grid_dropdown_page.canvas_widgets().nth(1)).to_contain_text('下拉框')


@allure.feature('界面编辑器')
@allure.story('栅格布局-下拉框组件')
@allure.title('删除下拉框组件，画布无组件，右侧切换为Page属性')
@allure.severity(allure.severity_level.CRITICAL)
def test_dropdown_delete(grid_dropdown_page):
    grid_dropdown_page.delete_button.dispatch_event('click')
    # 右侧断言（删除后无组件，切换为Page属性）
    expect(grid_dropdown_page.page.get_by_title('布局列数')).to_be_visible()
    # 数量断言
    expect(grid_dropdown_page.canvas_widgets()).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('栅格布局-下拉框组件')
@allure.title('组合修改标签与选项')
@allure.severity(allure.severity_level.CRITICAL)
def test_dropdown_combined(grid_dropdown_page):
    grid_dropdown_page.prop_label.fill('国家选择')
    grid_dropdown_page.prop_options.fill('选项A, 选项B')
    # 右侧断言
    expect(grid_dropdown_page.prop_label).to_have_value('国家选择')
    expect(grid_dropdown_page.prop_options).to_have_value('选项A, 选项B')
    # 画布断言
    expect(grid_dropdown_page.widget_label_text()).to_have_text('国家选择')
