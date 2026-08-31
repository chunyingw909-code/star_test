import allure
from playwright.sync_api import expect


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-下拉框组件')
@allure.title('添加下拉框后画布出现组件，默认标签为"下拉框"')
@allure.severity(allure.severity_level.BLOCKER)
def test_dropdown_default(free_dropdown_page):
    # 画布断言
    expect(free_dropdown_page.canvas_widgets()).to_have_count(1)
    expect(free_dropdown_page.canvas_widgets().first).to_contain_text('下拉框')


@allure.feature('界面编辑器')
@allure.story('自由布局-下拉框组件')
@allure.title('点击组件，属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_dropdown_select_shows_properties(free_dropdown_page):
    free_dropdown_page.click_widget()
    expect(free_dropdown_page.prop_panel).to_be_visible()
    # 右侧断言
    expect(free_dropdown_page.prop_label).to_have_value('下拉框')
    expect(free_dropdown_page.prop_options).to_have_value('选项一, 选项二, 选项三')
    expect(free_dropdown_page.prop_default_value).to_have_value('')
    expect(free_dropdown_page.prop_api_url).to_have_value('')
    expect(free_dropdown_page.prop_field_name).to_have_value('')


@allure.feature('界面编辑器')
@allure.story('自由布局-下拉框组件')
@allure.title('点击画布空白区域，属性面板隐藏')
@allure.severity(allure.severity_level.NORMAL)
def test_dropdown_click_blank_hides_properties(free_dropdown_page):
    free_dropdown_page.click_widget()
    expect(free_dropdown_page.prop_panel).to_be_visible()
    free_dropdown_page.click_canvas_blank()
    expect(free_dropdown_page.prop_panel).to_be_hidden()


# ==================== 标签 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-下拉框组件')
@allure.title('修改标签为"国家选择"')
@allure.severity(allure.severity_level.CRITICAL)
def test_dropdown_modify_label(free_dropdown_page):
    free_dropdown_page.click_widget()
    free_dropdown_page.prop_label.fill('国家选择')
    # 右侧断言
    expect(free_dropdown_page.prop_label).to_have_value('国家选择')
    # 画布断言
    expect(free_dropdown_page.widget_label_text()).to_have_text('国家选择')


@allure.feature('界面编辑器')
@allure.story('自由布局-下拉框组件')
@allure.title('清空标签')
@allure.severity(allure.severity_level.NORMAL)
def test_dropdown_clear_label(free_dropdown_page):
    free_dropdown_page.click_widget()
    free_dropdown_page.prop_label.fill('')
    # 右侧断言
    expect(free_dropdown_page.prop_label).to_have_value('')
    # 画布断言
    expect(free_dropdown_page.canvas_widgets().first).not_to_contain_text('下拉框')


@allure.feature('界面编辑器')
@allure.story('自由布局-下拉框组件')
@allure.title('标签恢复为"下拉框"')
@allure.severity(allure.severity_level.NORMAL)
def test_dropdown_label_recover(free_dropdown_page):
    free_dropdown_page.click_widget()
    free_dropdown_page.prop_label.fill('国家选择')
    free_dropdown_page.prop_label.fill('下拉框')
    # 右侧断言
    expect(free_dropdown_page.prop_label).to_have_value('下拉框')
    # 画布断言
    expect(free_dropdown_page.widget_label_text()).to_have_text('下拉框')


# ==================== 选项 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-下拉框组件')
@allure.title('修改选项为"选项A, 选项B"')
@allure.severity(allure.severity_level.CRITICAL)
def test_dropdown_modify_options(free_dropdown_page):
    free_dropdown_page.click_widget()
    free_dropdown_page.prop_options.fill('选项A, 选项B')
    # 右侧断言
    expect(free_dropdown_page.prop_options).to_have_value('选项A, 选项B')


@allure.feature('界面编辑器')
@allure.story('自由布局-下拉框组件')
@allure.title('选项恢复为默认三个')
@allure.severity(allure.severity_level.NORMAL)
def test_dropdown_options_recover(free_dropdown_page):
    free_dropdown_page.click_widget()
    free_dropdown_page.prop_options.fill('选项A, 选项B')
    free_dropdown_page.prop_options.fill('选项一, 选项二, 选项三')
    # 右侧断言
    expect(free_dropdown_page.prop_options).to_have_value('选项一, 选项二, 选项三')


# ==================== 数据绑定 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-下拉框组件')
@allure.title('输入API地址和字段名')
@allure.severity(allure.severity_level.CRITICAL)
def test_dropdown_data_binding(free_dropdown_page):
    free_dropdown_page.click_widget()
    free_dropdown_page.prop_api_url.fill('abc')
    free_dropdown_page.prop_field_name.fill('xyz')
    # 右侧断言
    expect(free_dropdown_page.prop_api_url).to_have_value('abc')
    expect(free_dropdown_page.prop_field_name).to_have_value('xyz')


@allure.feature('界面编辑器')
@allure.story('自由布局-下拉框组件')
@allure.title('清空API地址和字段名')
@allure.severity(allure.severity_level.NORMAL)
def test_dropdown_data_binding_clear(free_dropdown_page):
    free_dropdown_page.click_widget()
    free_dropdown_page.prop_api_url.fill('abc')
    free_dropdown_page.prop_field_name.fill('xyz')
    free_dropdown_page.prop_api_url.fill('')
    free_dropdown_page.prop_field_name.fill('')
    # 右侧断言
    expect(free_dropdown_page.prop_api_url).to_have_value('')
    expect(free_dropdown_page.prop_field_name).to_have_value('')


# ==================== 删除 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-下拉框组件')
@allure.title('删除下拉框组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_dropdown_delete(free_dropdown_page):
    expect(free_dropdown_page.canvas_widgets()).to_have_count(1)
    free_dropdown_page.delete_widget()
    expect(free_dropdown_page.canvas_widgets()).to_have_count(0)


# ==================== 组合修改 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-下拉框组件')
@allure.title('组合修改标签与选项')
@allure.severity(allure.severity_level.CRITICAL)
def test_dropdown_combined(free_dropdown_page):
    free_dropdown_page.click_widget()
    free_dropdown_page.prop_label.fill('国家选择')
    free_dropdown_page.prop_options.fill('选项A, 选项B')
    # 右侧断言
    expect(free_dropdown_page.prop_label).to_have_value('国家选择')
    expect(free_dropdown_page.prop_options).to_have_value('选项A, 选项B')
    # 画布断言
    expect(free_dropdown_page.widget_label_text()).to_have_text('国家选择')


# ==================== 默认值：预览态验证 ====================
# 编辑态画布下拉框不体现默认值，预览态挂载后默认选中项才出现。

@allure.feature('界面编辑器')
@allure.story('自由布局-下拉框组件')
@allure.title('设默认值后编辑态画布不选中、预览态下拉框默认选中该项')
@allure.severity(allure.severity_level.CRITICAL)
def test_dropdown_default_value_in_preview(free_dropdown_page):
    from pages.editor.editor_page import EditorPage
    free_dropdown_page.click_widget()
    free_dropdown_page.prop_options.fill('选项一, 选项二, 选项三')
    free_dropdown_page.prop_default_value.fill('选项二')
    expect(free_dropdown_page.prop_default_value).to_have_value('选项二')
    # 编辑态画布下拉框没有选中项
    expect(free_dropdown_page.widget_select()).not_to_contain_text('选项二')
    # 预览态：下拉框默认选中「选项二」
    EditorPage(free_dropdown_page.page).enter_preview()
    expect(free_dropdown_page.preview_select()).to_have_text('选项二')


@allure.feature('界面编辑器')
@allure.story('自由布局-下拉框组件')
@allure.title('默认值不在选项列表里时，预览态不选中任何项')
@allure.severity(allure.severity_level.NORMAL)
def test_dropdown_default_value_not_in_options(free_dropdown_page):
    from pages.editor.editor_page import EditorPage
    free_dropdown_page.click_widget()
    free_dropdown_page.prop_options.fill('选项一, 选项二')
    free_dropdown_page.prop_default_value.fill('不存在的项')
    EditorPage(free_dropdown_page.page).enter_preview()
    expect(free_dropdown_page.preview_select()).not_to_contain_text('不存在的项')
