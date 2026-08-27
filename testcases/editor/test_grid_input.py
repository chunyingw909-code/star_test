import allure
from playwright.sync_api import expect


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('拖拽输入框后画布出现组件')
@allure.severity(allure.severity_level.BLOCKER)
def test_input_default(grid_input_page):
    # 数量断言
    expect(grid_input_page.canvas_widgets()).to_have_count(1)
    # 画布断言
    expect(grid_input_page.canvas_widgets().first).to_contain_text('输入框')


@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('点击组件，属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_input_select_shows_properties(grid_input_page):
    # 右侧断言
    expect(grid_input_page.prop_label).to_have_value('输入框')
    expect(grid_input_page.prop_placeholder).to_have_value('请输入...')
    expect(grid_input_page.prop_default_value).to_have_value('')
    expect(grid_input_page.prop_rows).to_have_value('1')
    expect(grid_input_page.prop_api_url).to_have_value('')
    expect(grid_input_page.prop_field_name).to_have_value('')
    expect(grid_input_page.multiline_radio('否')).to_be_checked()
    # 画布断言
    expect(grid_input_page.widget_input()).to_have_css('font-size', '12px')
    expect(grid_input_page.widget_input()).to_have_attribute('placeholder', '请输入...')


@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('点击空白，右侧切换回Page属性')
@allure.severity(allure.severity_level.NORMAL)
def test_input_click_blank_shows_page(grid_input_page):
    grid_input_page.click_canvas_blank()
    expect(grid_input_page.page.get_by_title('布局列数')).to_be_visible()


# ==================== 跨列数 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('跨列数改为2')
@allure.severity(allure.severity_level.CRITICAL)
def test_input_col_span_2(grid_input_page):
    grid_input_page.prop_col_span.fill('2')
    # 右侧断言
    expect(grid_input_page.prop_col_span).to_have_value('2')
    # 画布断言
    widget = grid_input_page.canvas_widgets().first
    expect(widget).to_have_css('grid-column', 'span 2')


@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('跨列数改为4')
@allure.severity(allure.severity_level.NORMAL)
def test_input_col_span_4(grid_input_page):
    grid_input_page.prop_col_span.fill('4')
    # 右侧断言
    expect(grid_input_page.prop_col_span).to_have_value('4')
    # 画布断言
    widget = grid_input_page.canvas_widgets().first
    expect(widget).to_have_css('grid-column', 'span 4')


# ==================== 标签 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('修改标签为"搜索框"')
@allure.severity(allure.severity_level.CRITICAL)
def test_input_modify_label(grid_input_page):
    grid_input_page.prop_label.fill('搜索框')
    # 右侧断言
    expect(grid_input_page.prop_label).to_have_value('搜索框')
    # 画布断言
    expect(grid_input_page.widget_label_text()).to_have_text('搜索框')


@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('清空标签')
@allure.severity(allure.severity_level.NORMAL)
def test_input_clear_label(grid_input_page):
    grid_input_page.prop_label.fill('')
    # 右侧断言
    expect(grid_input_page.prop_label).to_have_value('')
    # 画布断言
    expect(grid_input_page.canvas_widgets().first).not_to_contain_text('输入框')


@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('标签恢复为"输入框"')
@allure.severity(allure.severity_level.NORMAL)
def test_input_label_recover(grid_input_page):
    grid_input_page.prop_label.fill('搜索框')
    grid_input_page.prop_label.fill('输入框')
    # 右侧断言
    expect(grid_input_page.prop_label).to_have_value('输入框')
    # 画布断言
    expect(grid_input_page.widget_label_text()).to_have_text('输入框')


# ==================== 占位提示 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('修改占位提示为"请输入关键词"')
@allure.severity(allure.severity_level.CRITICAL)
def test_input_modify_placeholder(grid_input_page):
    grid_input_page.prop_placeholder.fill('请输入关键词')
    # 右侧断言
    expect(grid_input_page.prop_placeholder).to_have_value('请输入关键词')
    # 画布断言
    expect(grid_input_page.widget_input()).to_have_attribute('placeholder', '请输入关键词')


@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('清空占位提示')
@allure.severity(allure.severity_level.NORMAL)
def test_input_clear_placeholder(grid_input_page):
    grid_input_page.prop_placeholder.fill('')
    # 右侧断言
    expect(grid_input_page.prop_placeholder).to_have_value('')
    # 画布断言
    expect(grid_input_page.widget_input()).to_have_attribute('placeholder', '')


@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('占位提示恢复为"请输入..."')
@allure.severity(allure.severity_level.NORMAL)
def test_input_placeholder_recover(grid_input_page):
    grid_input_page.prop_placeholder.fill('请输入关键词')
    grid_input_page.prop_placeholder.fill('请输入...')
    # 右侧断言
    expect(grid_input_page.prop_placeholder).to_have_value('请输入...')
    # 画布断言
    expect(grid_input_page.widget_input()).to_have_attribute('placeholder', '请输入...')


# ==================== 默认值 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('设置默认值"hello"')
@allure.severity(allure.severity_level.CRITICAL)
def test_input_set_default_value(grid_input_page):
    grid_input_page.prop_default_value.fill('hello')
    # 右侧断言
    expect(grid_input_page.prop_default_value).to_have_value('hello')


@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('清空默认值')
@allure.severity(allure.severity_level.NORMAL)
def test_input_clear_default_value(grid_input_page):
    grid_input_page.prop_default_value.fill('hello')
    grid_input_page.prop_default_value.fill('')
    # 右侧断言
    expect(grid_input_page.prop_default_value).to_have_value('')


# ==================== 多行 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('切换多行为"是"，input变为textarea')
@allure.severity(allure.severity_level.CRITICAL)
def test_input_multiline_yes(grid_input_page):
    grid_input_page.multiline_label('是').click()
    # 右侧断言
    expect(grid_input_page.multiline_radio('是')).to_be_checked()
    # 画布断言
    expect(grid_input_page.widget_textarea()).to_be_visible()
    expect(grid_input_page.widget_textarea()).to_have_css('font-size', '12px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('多行从"是"恢复为"否"，textarea变回input')
@allure.severity(allure.severity_level.NORMAL)
def test_input_multiline_recover(grid_input_page):
    grid_input_page.multiline_label('是').click()
    grid_input_page.multiline_label('否').click()
    # 右侧断言
    expect(grid_input_page.multiline_radio('否')).to_be_checked()
    # 画布断言
    expect(grid_input_page.widget_input()).to_be_visible()
    expect(grid_input_page.widget_input()).to_have_css('font-size', '12px')


# ==================== 行数 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('行数改为5')
@allure.severity(allure.severity_level.NORMAL)
def test_input_rows_5(grid_input_page):
    grid_input_page.multiline_label('是').click()
    grid_input_page.prop_rows.fill('5')
    # 右侧断言
    expect(grid_input_page.prop_rows).to_have_value('5')
    # 画布断言
    expect(grid_input_page.widget_textarea()).to_have_attribute('rows', '5')
    expect(grid_input_page.widget_textarea()).to_have_css('font-size', '12px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('行数改为10')
@allure.severity(allure.severity_level.NORMAL)
def test_input_rows_10(grid_input_page):
    grid_input_page.multiline_label('是').click()
    grid_input_page.prop_rows.fill('10')
    # 右侧断言
    expect(grid_input_page.prop_rows).to_have_value('10')
    # 画布断言
    expect(grid_input_page.widget_textarea()).to_have_attribute('rows', '10')


@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('行数恢复为1')
@allure.severity(allure.severity_level.NORMAL)
def test_input_rows_recover(grid_input_page):
    grid_input_page.multiline_label('是').click()
    grid_input_page.prop_rows.fill('5')
    grid_input_page.prop_rows.fill('1')
    # 右侧断言
    expect(grid_input_page.prop_rows).to_have_value('1')
    # 画布断言
    expect(grid_input_page.widget_textarea()).to_have_attribute('rows', '1')


# ==================== 数据绑定 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('输入API地址和字段名')
@allure.severity(allure.severity_level.CRITICAL)
def test_input_data_binding(grid_input_page):
    grid_input_page.prop_api_url.fill('abc')
    grid_input_page.prop_field_name.fill('xyz')
    # 右侧断言
    expect(grid_input_page.prop_api_url).to_have_value('abc')
    expect(grid_input_page.prop_field_name).to_have_value('xyz')


@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('清空API地址和字段名')
@allure.severity(allure.severity_level.NORMAL)
def test_input_data_binding_clear(grid_input_page):
    grid_input_page.prop_api_url.fill('abc')
    grid_input_page.prop_field_name.fill('xyz')
    grid_input_page.prop_api_url.fill('')
    grid_input_page.prop_field_name.fill('')
    # 右侧断言
    expect(grid_input_page.prop_api_url).to_have_value('')
    expect(grid_input_page.prop_field_name).to_have_value('')


# ==================== 复制 / 删除 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('复制输入框组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_input_duplicate(grid_input_page):
    grid_input_page.duplicate_button.dispatch_event('click')
    # 数量断言
    expect(grid_input_page.canvas_widgets()).to_have_count(2)
    # 右侧断言
    expect(grid_input_page.prop_label).to_have_value('输入框')
    expect(grid_input_page.prop_placeholder).to_have_value('请输入...')
    # 画布断言
    expect(grid_input_page.canvas_widgets().nth(0)).to_contain_text('输入框')
    expect(grid_input_page.canvas_widgets().nth(1)).to_contain_text('输入框')


@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('删除输入框组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_input_delete(grid_input_page):
    grid_input_page.delete_button.dispatch_event('click')
    # 右侧断言
    expect(grid_input_page.page.get_by_title('布局列数')).to_be_visible()
    # 数量断言
    expect(grid_input_page.canvas_widgets()).to_have_count(0)


# ==================== 组合修改 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-输入框组件')
@allure.title('同时修改跨列数+标签+占位提示+多行+行数')
@allure.severity(allure.severity_level.CRITICAL)
def test_input_combined(grid_input_page):
    grid_input_page.prop_col_span.fill('4')
    grid_input_page.prop_label.fill('备注')
    grid_input_page.prop_placeholder.fill('请输入备注信息')
    grid_input_page.prop_default_value.fill('无')
    grid_input_page.multiline_label('是').click()
    grid_input_page.prop_rows.fill('3')
    # 右侧断言
    expect(grid_input_page.prop_col_span).to_have_value('4')
    expect(grid_input_page.prop_label).to_have_value('备注')
    expect(grid_input_page.prop_placeholder).to_have_value('请输入备注信息')
    expect(grid_input_page.prop_default_value).to_have_value('无')
    expect(grid_input_page.multiline_radio('是')).to_be_checked()
    expect(grid_input_page.prop_rows).to_have_value('3')
    # 画布断言
    expect(grid_input_page.canvas_widgets().first).to_contain_text('备注')
    expect(grid_input_page.widget_textarea()).to_have_attribute('rows', '3')
    expect(grid_input_page.widget_textarea()).to_have_attribute('placeholder', '请输入备注信息')
    expect(grid_input_page.canvas_widgets().first).to_have_css('grid-column', 'span 4')
