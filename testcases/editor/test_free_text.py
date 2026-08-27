import allure
from playwright.sync_api import expect


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('添加文本组件后画布出现组件，默认标题为"标题"')
@allure.severity(allure.severity_level.BLOCKER)
def test_text_default(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    # 画布断言
    expect(free_text_page.canvas_widgets()).to_have_count(1)
    expect(free_text_page.canvas_widgets().first).to_contain_text('标题')
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_default.png')


# ==================== 属性面板 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('点击组件，属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_select_shows_properties(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    expect(free_text_page.prop_panel).to_be_visible()
    # 右侧断言
    expect(free_text_page.prop_content).to_have_value('标题')
    expect(free_text_page.prop_font_size).to_have_value('24')
    expect(free_text_page.prop_color).to_have_value('#ffffff')
    # 画布断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_select_shows_properties.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('点击画布空白区域，属性面板隐藏')
@allure.severity(allure.severity_level.NORMAL)
def test_text_click_blank_hides_properties(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    expect(free_text_page.prop_panel).to_be_visible()
    free_text_page.click_canvas_blank()
    expect(free_text_page.prop_panel).to_be_hidden()
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_click_blank_hides_properties.png')


# ==================== 内容修改 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('修改内容为"卫星遥测监控大屏"')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_modify_content(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_content.fill('卫星遥测监控大屏')
    # 右侧断言
    expect(free_text_page.prop_content).to_have_value('卫星遥测监控大屏')
    # 画布断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    expect(free_text_page.canvas_widgets().first).to_contain_text('卫星遥测监控大屏')
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_modify_content.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('清空内容，画布上不显示文字')
@allure.severity(allure.severity_level.NORMAL)
def test_text_clear_content(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_content.fill('')
    # 右侧断言
    expect(free_text_page.prop_content).to_have_value('')
    # 画布断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    expect(free_text_page.canvas_widgets().first).not_to_contain_text('标题')
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_clear_content.png')


# ==================== 颜色修改 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('修改颜色为红色 #E74C3C')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_modify_color(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_color.fill('#E74C3C')
    # 右侧断言
    expect(free_text_page.prop_color).to_have_value('#E74C3C')
    # 画布断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('color', 'rgb(231, 76, 60)')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('font-weight', '700')
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_color_red.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('修改颜色为浅蓝色 #4fc3f7')
@allure.severity(allure.severity_level.NORMAL)
def test_text_color_light_blue(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_color.fill('#4fc3f7')
    # 右侧断言
    expect(free_text_page.prop_color).to_have_value('#4fc3f7')
    # 画布断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('color', 'rgb(79, 195, 247)')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('font-weight', '700')
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_color_light_blue.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('颜色恢复为白色 #ffffff')
@allure.severity(allure.severity_level.NORMAL)
def test_text_color_recover(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_color.fill('#E74C3C')
    free_text_page.prop_color.fill('#ffffff')
    # 右侧断言
    expect(free_text_page.prop_color).to_have_value('#ffffff')
    # 画布断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('font-weight', '700')
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_color_recover.png')


# ==================== 字号修改 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('字号调大为48')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_increase_font_size(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_font_size.fill('48')
    # 右侧断言
    expect(free_text_page.prop_font_size).to_have_value('48')
    # 画布断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '48px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_font_size_48.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('字号调小为8')
@allure.severity(allure.severity_level.NORMAL)
def test_text_decrease_font_size(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_font_size.fill('8')
    # 右侧断言
    expect(free_text_page.prop_font_size).to_have_value('8')
    # 画布断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '8px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_font_size_8.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('字号从48恢复为24')
@allure.severity(allure.severity_level.NORMAL)
def test_text_font_size_recover(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_font_size.fill('48')
    free_text_page.prop_font_size.fill('24')
    # 右侧断言
    expect(free_text_page.prop_font_size).to_have_value('24')
    # 画布断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_font_size_recover.png')


# ==================== 单位修改 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('设置单位为"V"')
@allure.severity(allure.severity_level.NORMAL)
def test_text_set_unit(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_unit.fill('V')
    # 右侧断言
    expect(free_text_page.prop_unit).to_have_value('V')
    # 画布断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    expect(free_text_page.canvas_widgets().first).to_contain_text('V')
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_unit_v.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('清空单位')
@allure.severity(allure.severity_level.NORMAL)
def test_text_unit_clear(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_unit.fill('V')
    free_text_page.prop_unit.fill('')
    # 右侧断言
    expect(free_text_page.prop_unit).to_have_value('')
    # 画布断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    expect(free_text_page.canvas_widgets().first).not_to_contain_text('V')
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_unit_clear.png')


# ==================== 对齐方式 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('切换对齐方式为居中')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_align_center(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_align.click()
    free_text_page.page.get_by_role('option', name='居中').click()
    # 右侧断言
    expect(free_text_page.prop_align).to_have_text('居中')
    # 画布断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_align_center.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('切换对齐方式为右')
@allure.severity(allure.severity_level.NORMAL)
def test_text_align_right(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_align.click()
    free_text_page.page.get_by_role('option', name='右').click()
    # 右侧断言
    expect(free_text_page.prop_align).to_have_text('右')
    # 画布断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_align_right.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('对齐方式从右恢复为左（默认）')
@allure.severity(allure.severity_level.NORMAL)
def test_text_align_left_recover(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    # 先改为右
    free_text_page.prop_align.click()
    free_text_page.page.get_by_role('option', name='右').click()
    expect(free_text_page.prop_align).to_have_text('右')
    # 再改回左
    free_text_page.prop_align.click()
    free_text_page.page.get_by_role('option', name='左').click()
    expect(free_text_page.prop_align).to_have_text('左')
    # 画布断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_align_left_recover.png')


# ==================== 字重 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('切换字重为正常 (400)')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_weight_normal(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_weight.click()
    free_text_page.page.get_by_role('option', name='正常').click()
    # 右侧断言
    expect(free_text_page.prop_weight).to_have_text('正常')
    # 画布断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-weight', '400')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_weight_normal.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('切换字重为粗体 (700)')
@allure.severity(allure.severity_level.NORMAL)
def test_text_weight_bold(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_weight.click()
    free_text_page.page.get_by_role('option', name='粗体').click()
    # 右侧断言
    expect(free_text_page.prop_weight).to_have_text('粗体')
    # 画布断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-weight', '700')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_weight_bold.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('切换字重为中等 (500)')
@allure.severity(allure.severity_level.NORMAL)
def test_text_weight_medium(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_weight.click()
    free_text_page.page.get_by_role('option', name='中等').click()
    # 右侧断言
    expect(free_text_page.prop_weight).to_have_text('中等')
    # 画布断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-weight', '500')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_weight_medium.png')


# ==================== 绑定模式 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('切换绑定模式为静态')
@allure.severity(allure.severity_level.NORMAL)
def test_text_binding_mode_static(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_binding_mode.click()
    free_text_page.page.get_by_role('option', name='静态').click()
    # 右侧断言
    expect(free_text_page.prop_binding_mode).to_have_text('静态')
    # 画布断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_binding_static.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('切换绑定模式为动态')
@allure.severity(allure.severity_level.NORMAL)
def test_text_binding_mode_dynamic(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_binding_mode.click()
    free_text_page.page.get_by_role('option', name='动态').click()
    # 右侧断言
    expect(free_text_page.prop_binding_mode).to_have_text('动态')
    # 画布断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_binding_dynamic.png')


# ==================== 删除 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('删除文本组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_delete(free_text_page):
    expect(free_text_page.canvas_widgets()).to_have_count(1)
    free_text_page.delete_widget()
    expect(free_text_page.canvas_widgets()).to_have_count(0)


# ==================== 组合修改 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('同时修改内容、颜色、字号、单位、对齐、字重')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_combined(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    # 修改多个属性
    free_text_page.prop_content.fill('综合测试文本')
    free_text_page.prop_color.fill('#4fc3f7')  # 浅蓝
    free_text_page.prop_font_size.fill('36')
    free_text_page.prop_unit.fill('kW')
    # 对齐方式改为居中
    free_text_page.prop_align.click()
    free_text_page.page.get_by_role('option', name='居中').click()
    # 字重改为粗体
    free_text_page.prop_weight.click()
    free_text_page.page.get_by_role('option', name='粗体').click()
    # 右侧断言
    expect(free_text_page.prop_content).to_have_value('综合测试文本')
    expect(free_text_page.prop_color).to_have_value('#4fc3f7')
    expect(free_text_page.prop_font_size).to_have_value('36')
    expect(free_text_page.prop_unit).to_have_value('kW')
    expect(free_text_page.prop_align).to_have_text('居中')
    expect(free_text_page.prop_weight).to_have_text('粗体')
    # 画布断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '36px')
    expect(text_el).to_have_css('color', 'rgb(79, 195, 247)')
    expect(text_el).to_have_css('font-weight', '700')
    expect(free_text_page.canvas_widgets().first).to_contain_text('综合测试文本')
    expect(free_text_page.canvas_widgets().first).to_contain_text('kW')
    # 截图断言
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_combined.png')