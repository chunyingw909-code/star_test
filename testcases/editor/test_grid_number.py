import allure
from playwright.sync_api import expect


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('拖拽数值输入后画布出现组件，默认标签"数值输入"')
@allure.severity(allure.severity_level.BLOCKER)
def test_number_default(grid_number_page):
    expect(grid_number_page.canvas_widgets()).to_have_count(1)
    expect(grid_number_page.canvas_widgets().first).to_contain_text('数值输入')


@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('点击组件，右侧属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_number_select_shows_properties(grid_number_page):
    # 右侧断言
    expect(grid_number_page.prop_col_span).to_have_value('')
    expect(grid_number_page.prop_label).to_have_value('数值输入')
    expect(grid_number_page.prop_default_value).to_have_value('0')
    expect(grid_number_page.prop_min).to_have_value('0')
    expect(grid_number_page.prop_max).to_have_value('9999')
    expect(grid_number_page.prop_step).to_have_value('1')
    expect(grid_number_page.prop_unit).to_have_value('')
    expect(grid_number_page.prop_api_url).to_have_value('')
    expect(grid_number_page.prop_field_name).to_have_value('')
    # 画布断言：输入框的 min/max/step
    expect(grid_number_page.widget_input()).to_have_attribute('min', '0')
    expect(grid_number_page.widget_input()).to_have_attribute('max', '9999')
    expect(grid_number_page.widget_input()).to_have_attribute('step', '1')


@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('点击空白区域，右侧切换回Page属性')
@allure.severity(allure.severity_level.NORMAL)
def test_number_click_blank_shows_page(grid_number_page):
    grid_number_page.click_canvas_blank()
    expect(grid_number_page.page_props_marker).to_be_visible()


# ==================== 跨列数 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('跨列数改为 6')
@allure.severity(allure.severity_level.CRITICAL)
def test_number_col_span_6(grid_number_page):
    grid_number_page.prop_col_span.fill('6')
    # 右侧断言
    expect(grid_number_page.prop_col_span).to_have_value('6')
    # 画布断言
    expect(grid_number_page.canvas_widgets().first).to_have_css('grid-column', 'span 6')


@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('跨列数从 6 改为 4')
@allure.severity(allure.severity_level.NORMAL)
def test_number_col_span_recover(grid_number_page):
    # Puck 数字框设过值后清不回空，只能改成别的数
    grid_number_page.prop_col_span.fill('6')
    grid_number_page.prop_col_span.fill('4')
    # 右侧断言
    expect(grid_number_page.prop_col_span).to_have_value('4')
    # 画布断言
    expect(grid_number_page.canvas_widgets().first).to_have_css('grid-column', 'span 4')


# ==================== 标签 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('修改标签为"电压"')
@allure.severity(allure.severity_level.CRITICAL)
def test_number_modify_label(grid_number_page):
    grid_number_page.prop_label.fill('电压')
    # 右侧断言
    expect(grid_number_page.prop_label).to_have_value('电压')
    # 画布断言
    expect(grid_number_page.widget_label_text()).to_have_text('电压')


@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('清空标签')
@allure.severity(allure.severity_level.NORMAL)
def test_number_clear_label(grid_number_page):
    grid_number_page.prop_label.fill('')
    # 右侧断言
    expect(grid_number_page.prop_label).to_have_value('')
    # 画布断言
    expect(grid_number_page.canvas_widgets().first).not_to_contain_text('数值输入')


@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('标签恢复为"数值输入"')
@allure.severity(allure.severity_level.NORMAL)
def test_number_label_recover(grid_number_page):
    grid_number_page.prop_label.fill('电压')
    grid_number_page.prop_label.fill('数值输入')
    # 右侧断言
    expect(grid_number_page.prop_label).to_have_value('数值输入')
    # 画布断言
    expect(grid_number_page.widget_label_text()).to_have_text('数值输入')


# ==================== 默认值 ====================
# 默认值只在预览/运行时生效，编辑态画布输入框始终显示 0，这里只校验属性往返

@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('设置默认值为 42')
@allure.severity(allure.severity_level.CRITICAL)
def test_number_set_default_value(grid_number_page):
    grid_number_page.prop_default_value.fill('42')
    expect(grid_number_page.prop_default_value).to_have_value('42')


@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('默认值恢复为 0')
@allure.severity(allure.severity_level.NORMAL)
def test_number_default_value_recover(grid_number_page):
    grid_number_page.prop_default_value.fill('42')
    grid_number_page.prop_default_value.fill('0')
    expect(grid_number_page.prop_default_value).to_have_value('0')


# ==================== 最小值 / 最大值 / 步长 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('最小值改为 5，画布输入框 min 属性同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_number_modify_min(grid_number_page):
    grid_number_page.prop_min.fill('5')
    # 右侧断言
    expect(grid_number_page.prop_min).to_have_value('5')
    # 画布断言
    expect(grid_number_page.widget_input()).to_have_attribute('min', '5')


@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('最大值改为 100，画布输入框 max 属性同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_number_modify_max(grid_number_page):
    grid_number_page.prop_max.fill('100')
    # 右侧断言
    expect(grid_number_page.prop_max).to_have_value('100')
    # 画布断言
    expect(grid_number_page.widget_input()).to_have_attribute('max', '100')


@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('步长改为 2，画布输入框 step 属性同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_number_modify_step(grid_number_page):
    grid_number_page.prop_step.fill('2')
    # 右侧断言
    expect(grid_number_page.prop_step).to_have_value('2')
    # 画布断言
    expect(grid_number_page.widget_input()).to_have_attribute('step', '2')


@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('最小值 / 最大值 / 步长恢复为默认')
@allure.severity(allure.severity_level.NORMAL)
def test_number_range_recover(grid_number_page):
    grid_number_page.prop_min.fill('5')
    grid_number_page.prop_max.fill('100')
    grid_number_page.prop_step.fill('2')
    grid_number_page.prop_min.fill('0')
    grid_number_page.prop_max.fill('9999')
    grid_number_page.prop_step.fill('1')
    # 右侧断言
    expect(grid_number_page.prop_min).to_have_value('0')
    expect(grid_number_page.prop_max).to_have_value('9999')
    expect(grid_number_page.prop_step).to_have_value('1')
    # 画布断言
    expect(grid_number_page.widget_input()).to_have_attribute('min', '0')
    expect(grid_number_page.widget_input()).to_have_attribute('max', '9999')
    expect(grid_number_page.widget_input()).to_have_attribute('step', '1')


# ==================== 单位 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('设置单位为"V"')
@allure.severity(allure.severity_level.CRITICAL)
def test_number_set_unit(grid_number_page):
    grid_number_page.prop_unit.fill('V')
    # 右侧断言
    expect(grid_number_page.prop_unit).to_have_value('V')
    # 画布断言
    expect(grid_number_page.canvas_widgets().first).to_contain_text('V')


@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('清空单位')
@allure.severity(allure.severity_level.NORMAL)
def test_number_unit_clear(grid_number_page):
    grid_number_page.prop_unit.fill('V')
    grid_number_page.prop_unit.fill('')
    # 右侧断言
    expect(grid_number_page.prop_unit).to_have_value('')
    # 画布断言
    expect(grid_number_page.canvas_widgets().first).not_to_contain_text('V')


# ==================== 数据绑定 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('输入 API 地址和字段名')
@allure.severity(allure.severity_level.CRITICAL)
def test_number_data_binding(grid_number_page):
    grid_number_page.prop_api_url.fill('http://example.com/api')
    grid_number_page.prop_field_name.fill('voltage')
    # 右侧断言
    expect(grid_number_page.prop_api_url).to_have_value('http://example.com/api')
    expect(grid_number_page.prop_field_name).to_have_value('voltage')


@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('清空 API 地址和字段名')
@allure.severity(allure.severity_level.NORMAL)
def test_number_data_binding_clear(grid_number_page):
    grid_number_page.prop_api_url.fill('http://example.com/api')
    grid_number_page.prop_field_name.fill('voltage')
    grid_number_page.prop_api_url.fill('')
    grid_number_page.prop_field_name.fill('')
    # 右侧断言
    expect(grid_number_page.prop_api_url).to_have_value('')
    expect(grid_number_page.prop_field_name).to_have_value('')


# ==================== 复制 / 删除 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('复制数值输入组件，画布出现两个组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_number_duplicate(grid_number_page):
    grid_number_page.duplicate_widget()
    expect(grid_number_page.canvas_widgets()).to_have_count(2)
    expect(grid_number_page.canvas_widgets().nth(0)).to_contain_text('数值输入')
    expect(grid_number_page.canvas_widgets().nth(1)).to_contain_text('数值输入')


@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('删除数值输入组件，画布无组件，右侧切换为Page属性')
@allure.severity(allure.severity_level.CRITICAL)
def test_number_delete(grid_number_page):
    grid_number_page.delete_widget()
    expect(grid_number_page.page_props_marker).to_be_visible()
    expect(grid_number_page.canvas_widgets()).to_have_count(0)


# ==================== 组合修改 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('组合修改跨列数、标签、范围、步长与单位')
@allure.severity(allure.severity_level.CRITICAL)
def test_number_combined(grid_number_page):
    grid_number_page.prop_col_span.fill('8')
    grid_number_page.prop_label.fill('母线电压')
    grid_number_page.prop_min.fill('10')
    grid_number_page.prop_max.fill('50')
    grid_number_page.prop_step.fill('5')
    grid_number_page.prop_unit.fill('kV')
    # 右侧断言
    expect(grid_number_page.prop_col_span).to_have_value('8')
    expect(grid_number_page.prop_label).to_have_value('母线电压')
    expect(grid_number_page.prop_min).to_have_value('10')
    expect(grid_number_page.prop_max).to_have_value('50')
    expect(grid_number_page.prop_step).to_have_value('5')
    expect(grid_number_page.prop_unit).to_have_value('kV')
    # 画布断言
    expect(grid_number_page.canvas_widgets().first).to_have_css('grid-column', 'span 8')
    expect(grid_number_page.widget_label_text()).to_have_text('母线电压')
    expect(grid_number_page.widget_input()).to_have_attribute('min', '10')
    expect(grid_number_page.widget_input()).to_have_attribute('max', '50')
    expect(grid_number_page.widget_input()).to_have_attribute('step', '5')
    expect(grid_number_page.canvas_widgets().first).to_contain_text('kV')


# ==================== 默认值：预览态验证 ====================
# 编辑态画布数值框始终显示 0，默认值只在预览/运行时生效。

@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('设默认值后编辑态画布仍为 0、预览态数值框带出默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_number_default_value_in_preview(grid_number_page):
    from pages.editor.editor_page import EditorPage
    grid_number_page.prop_default_value.fill('42')
    expect(grid_number_page.prop_default_value).to_have_value('42')
    expect(grid_number_page.widget_input()).to_have_value('0')
    EditorPage(grid_number_page.page).enter_preview()
    expect(grid_number_page.preview_input()).to_have_value('42')


@allure.feature('界面编辑器')
@allure.story('栅格布局-数值输入组件')
@allure.title('预览态数值框仍受 min/max/step 约束')
@allure.severity(allure.severity_level.NORMAL)
def test_number_preview_keeps_constraints(grid_number_page):
    from pages.editor.editor_page import EditorPage
    grid_number_page.prop_default_value.fill('7')
    grid_number_page.prop_min.fill('5')
    grid_number_page.prop_max.fill('100')
    grid_number_page.prop_step.fill('2')
    EditorPage(grid_number_page.page).enter_preview()
    field = grid_number_page.preview_input()
    expect(field).to_have_value('7')
    expect(field).to_have_attribute('min', '5')
    expect(field).to_have_attribute('max', '100')
    expect(field).to_have_attribute('step', '2')
