import allure
from playwright.sync_api import expect


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('添加输入框后画布出现组件')
@allure.severity(allure.severity_level.BLOCKER)
def test_input_default(free_input_page):
    # 数量断言
    expect(free_input_page.canvas_widgets()).to_have_count(1)
    # 画布断言
    expect(free_input_page.canvas_widgets().first).to_contain_text('输入框')


@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('点击组件，属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_input_select_shows_properties(free_input_page):
    free_input_page.click_widget()
    expect(free_input_page.prop_panel).to_be_visible()
    # 右侧断言
    expect(free_input_page.prop_label).to_have_value('输入框')
    expect(free_input_page.prop_placeholder).to_have_value('请输入...')
    expect(free_input_page.prop_default_value).to_have_value('')
    expect(free_input_page.prop_rows).to_have_value('1')
    expect(free_input_page.prop_api_url).to_have_value('')
    expect(free_input_page.prop_field_name).to_have_value('')
    expect(free_input_page.multiline_radio('否')).to_be_checked()
    # CSS断言
    expect(free_input_page.widget_input()).to_have_css('font-size', '12px')
    expect(free_input_page.widget_input()).to_have_attribute('placeholder', '请输入...')


@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('点击空白区域，属性面板消失')
@allure.severity(allure.severity_level.NORMAL)
def test_input_click_blank_hides_properties(free_input_page):
    free_input_page.click_widget()
    expect(free_input_page.prop_panel).to_be_visible()
    free_input_page.click_canvas_blank()
    expect(free_input_page.prop_panel).to_be_hidden()


# ==================== 标签 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('修改标签为"搜索框"')
@allure.severity(allure.severity_level.CRITICAL)
def test_input_modify_label(free_input_page):
    free_input_page.click_widget()
    free_input_page.prop_label.fill('搜索框')
    # 右侧断言
    expect(free_input_page.prop_label).to_have_value('搜索框')
    # 画布断言
    expect(free_input_page.widget_label_text()).to_have_text('搜索框')


@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('清空标签')
@allure.severity(allure.severity_level.NORMAL)
def test_input_clear_label(free_input_page):
    free_input_page.click_widget()
    free_input_page.prop_label.fill('')
    # 右侧断言
    expect(free_input_page.prop_label).to_have_value('')
    # 画布断言
    expect(free_input_page.canvas_widgets().first).not_to_contain_text('输入框')


@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('标签恢复为"输入框"')
@allure.severity(allure.severity_level.NORMAL)
def test_input_label_recover(free_input_page):
    free_input_page.click_widget()
    free_input_page.prop_label.fill('搜索框')
    free_input_page.prop_label.fill('输入框')
    # 右侧断言
    expect(free_input_page.prop_label).to_have_value('输入框')
    # 画布断言
    expect(free_input_page.widget_label_text()).to_have_text('输入框')


# ==================== 占位提示 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('修改占位提示为"请输入关键词"')
@allure.severity(allure.severity_level.CRITICAL)
def test_input_modify_placeholder(free_input_page):
    free_input_page.click_widget()
    free_input_page.prop_placeholder.fill('请输入关键词')
    # 右侧断言
    expect(free_input_page.prop_placeholder).to_have_value('请输入关键词')
    # CSS断言
    expect(free_input_page.widget_input()).to_have_attribute('placeholder', '请输入关键词')


@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('清空占位提示')
@allure.severity(allure.severity_level.NORMAL)
def test_input_clear_placeholder(free_input_page):
    free_input_page.click_widget()
    free_input_page.prop_placeholder.fill('')
    # 右侧断言
    expect(free_input_page.prop_placeholder).to_have_value('')
    # CSS断言
    expect(free_input_page.widget_input()).to_have_attribute('placeholder', '')


@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('占位提示恢复为"请输入..."')
@allure.severity(allure.severity_level.NORMAL)
def test_input_placeholder_recover(free_input_page):
    free_input_page.click_widget()
    free_input_page.prop_placeholder.fill('请输入关键词')
    free_input_page.prop_placeholder.fill('请输入...')
    # 右侧断言
    expect(free_input_page.prop_placeholder).to_have_value('请输入...')
    # CSS断言
    expect(free_input_page.widget_input()).to_have_attribute('placeholder', '请输入...')


# ==================== 默认值 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('设置默认值"hello"')
@allure.severity(allure.severity_level.CRITICAL)
def test_input_set_default_value(free_input_page):
    free_input_page.click_widget()
    free_input_page.prop_default_value.fill('hello')
    # 右侧断言
    expect(free_input_page.prop_default_value).to_have_value('hello')


@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('清空默认值')
@allure.severity(allure.severity_level.NORMAL)
def test_input_clear_default_value(free_input_page):
    free_input_page.click_widget()
    free_input_page.prop_default_value.fill('hello')
    free_input_page.prop_default_value.fill('')
    # 右侧断言
    expect(free_input_page.prop_default_value).to_have_value('')


# ==================== 多行 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('切换多行为"是"，input变为textarea')
@allure.severity(allure.severity_level.CRITICAL)
def test_input_multiline_yes(free_input_page):
    free_input_page.click_widget()
    free_input_page.multiline_radio('是').check()
    # 右侧断言
    expect(free_input_page.multiline_radio('是')).to_be_checked()
    # CSS断言：变为textarea
    expect(free_input_page.widget_textarea()).to_be_visible()
    expect(free_input_page.widget_textarea()).to_have_css('font-size', '12px')


@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('多行从"是"恢复为"否"，textarea变回input')
@allure.severity(allure.severity_level.NORMAL)
def test_input_multiline_recover(free_input_page):
    free_input_page.click_widget()
    free_input_page.multiline_radio('是').check()
    free_input_page.multiline_radio('否').check()
    # 右侧断言
    expect(free_input_page.multiline_radio('否')).to_be_checked()
    # CSS断言：变回input
    expect(free_input_page.widget_input()).to_be_visible()
    expect(free_input_page.widget_input()).to_have_css('font-size', '12px')


# ==================== 行数 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('行数改为5')
@allure.severity(allure.severity_level.NORMAL)
def test_input_rows_5(free_input_page):
    free_input_page.click_widget()
    free_input_page.multiline_radio('是').check()
    free_input_page.prop_rows.fill('5')
    # 右侧断言
    expect(free_input_page.prop_rows).to_have_value('5')
    # CSS断言
    expect(free_input_page.widget_textarea()).to_have_attribute('rows', '5')
    expect(free_input_page.widget_textarea()).to_have_css('font-size', '12px')


@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('行数改为10')
@allure.severity(allure.severity_level.NORMAL)
def test_input_rows_max(free_input_page):
    free_input_page.click_widget()
    free_input_page.multiline_radio('是').check()
    free_input_page.prop_rows.fill('10')
    # 右侧断言
    expect(free_input_page.prop_rows).to_have_value('10')
    # CSS断言
    expect(free_input_page.widget_textarea()).to_have_attribute('rows', '10')


@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('行数恢复为1')
@allure.severity(allure.severity_level.NORMAL)
def test_input_rows_recover(free_input_page):
    free_input_page.click_widget()
    free_input_page.multiline_radio('是').check()
    free_input_page.prop_rows.fill('5')
    free_input_page.prop_rows.fill('1')
    # 右侧断言
    expect(free_input_page.prop_rows).to_have_value('1')
    # CSS断言
    expect(free_input_page.widget_textarea()).to_have_attribute('rows', '1')


# ==================== 数据绑定 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('输入API地址和字段名')
@allure.severity(allure.severity_level.CRITICAL)
def test_input_data_binding(free_input_page):
    free_input_page.click_widget()
    free_input_page.prop_api_url.fill('abc')
    free_input_page.prop_field_name.fill('xyz')
    # 右侧断言
    expect(free_input_page.prop_api_url).to_have_value('abc')
    expect(free_input_page.prop_field_name).to_have_value('xyz')


@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('清空API地址和字段名')
@allure.severity(allure.severity_level.NORMAL)
def test_input_data_binding_clear(free_input_page):
    free_input_page.click_widget()
    free_input_page.prop_api_url.fill('abc')
    free_input_page.prop_field_name.fill('xyz')
    free_input_page.prop_api_url.fill('')
    free_input_page.prop_field_name.fill('')
    # 右侧断言
    expect(free_input_page.prop_api_url).to_have_value('')
    expect(free_input_page.prop_field_name).to_have_value('')


# ==================== 删除 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('删除输入框组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_input_delete(free_input_page):
    expect(free_input_page.canvas_widgets()).to_have_count(1)
    free_input_page.delete_widget()
    expect(free_input_page.canvas_widgets()).to_have_count(0)


# ==================== 组合修改 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('同时修改标签+占位提示+多行+行数')
@allure.severity(allure.severity_level.CRITICAL)
def test_input_combined(free_input_page):
    free_input_page.click_widget()
    free_input_page.prop_label.fill('备注')
    free_input_page.prop_placeholder.fill('请输入备注信息')
    free_input_page.prop_default_value.fill('无')
    free_input_page.multiline_radio('是').check()
    free_input_page.prop_rows.fill('3')
    # 右侧断言
    expect(free_input_page.prop_label).to_have_value('备注')
    expect(free_input_page.prop_placeholder).to_have_value('请输入备注信息')
    expect(free_input_page.prop_default_value).to_have_value('无')
    expect(free_input_page.multiline_radio('是')).to_be_checked()
    expect(free_input_page.prop_rows).to_have_value('3')
    # 画布断言
    expect(free_input_page.canvas_widgets().first).to_contain_text('备注')
    expect(free_input_page.widget_textarea()).to_have_attribute('rows', '3')
    expect(free_input_page.widget_textarea()).to_have_attribute('placeholder', '请输入备注信息')

# ==================== 默认值：预览态验证 ====================
# 编辑态画布上的输入框只是「设计态占位」，改默认值不会立即体现；
# 切到预览态后组件真正挂载，默认值会填进渲染出来的输入框。

@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('设默认值后编辑态画布不变、预览态输入框带出默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_input_default_value_in_preview(free_input_page):
    from pages.editor.editor_page import EditorPage
    free_input_page.click_widget()
    free_input_page.prop_default_value.fill('SAT-01')
    expect(free_input_page.prop_default_value).to_have_value('SAT-01')
    # 编辑态画布输入框仍为空
    expect(free_input_page.widget_input()).to_have_value('')
    # 预览态：渲染出来的输入框带上默认值
    EditorPage(free_input_page.page).enter_preview()
    expect(free_input_page.preview_input()).to_have_value('SAT-01')


@allure.feature('界面编辑器')
@allure.story('自由布局-输入框组件')
@allure.title('多行模式下默认值在预览态填进文本域')
@allure.severity(allure.severity_level.NORMAL)
def test_input_default_value_multiline_in_preview(free_input_page):
    from pages.editor.editor_page import EditorPage
    free_input_page.click_widget()
    free_input_page.multiline_radio('是').check()
    free_input_page.prop_default_value.fill('第一行内容')
    EditorPage(free_input_page.page).enter_preview()
    expect(free_input_page.preview_textarea()).to_have_value('第一行内容')
