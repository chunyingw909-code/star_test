import allure
from playwright.sync_api import expect


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-文本组件')
@allure.title('拖拽文本后画布出现组件，默认显示标题')
@allure.severity(allure.severity_level.BLOCKER)
def test_text_default(grid_text_page):
    expect(grid_text_page.canvas_widgets()).to_have_count(1)
    expect(grid_text_page.canvas_widgets().first).to_contain_text('标题')


# ==================== 属性面板 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-文本组件')
@allure.title('点击组件，右侧属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_select_shows_properties(grid_text_page):
    # 右侧断言
    expect(grid_text_page.prop_content).to_have_value('标题')
    expect(grid_text_page.prop_font_size).to_have_value('24')
    expect(grid_text_page.prop_color).to_have_value('#ffffff')
    # 画布断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')


@allure.feature('界面编辑器')
@allure.story('栅格布局-文本组件')
@allure.title('点击空白区域，右侧切换回Page属性')
@allure.severity(allure.severity_level.NORMAL)
def test_text_click_blank_shows_page(grid_text_page):
    grid_text_page.click_canvas_blank()
    expect(grid_text_page.page_props_marker).to_be_visible()


# ==================== 内容修改 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-文本组件')
@allure.title('修改内容为"卫星遥测监控大屏"')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_modify_content(grid_text_page):
    grid_text_page.prop_content.fill('卫星遥测监控大屏')
    # 右侧断言
    expect(grid_text_page.prop_content).to_have_value('卫星遥测监控大屏')
    # 画布断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(grid_text_page.canvas_widgets().first).to_contain_text('卫星遥测监控大屏')


@allure.feature('界面编辑器')
@allure.story('栅格布局-文本组件')
@allure.title('清空内容，画布上不显示文字')
@allure.severity(allure.severity_level.NORMAL)
def test_text_clear_content(grid_text_page):
    grid_text_page.prop_content.fill('')
    # 右侧断言
    expect(grid_text_page.prop_content).to_have_value('')
    # 画布断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(grid_text_page.canvas_widgets().first).not_to_contain_text('标题')


# ==================== 颜色修改 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-文本组件')
@allure.title('修改颜色为红色 #E74C3C')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_modify_color(grid_text_page):
    grid_text_page.prop_color.fill('#E74C3C')
    # 右侧断言
    expect(grid_text_page.prop_color).to_have_value('#E74C3C')
    # 画布断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('color', 'rgb(231, 76, 60)')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('font-weight', '700')


@allure.feature('界面编辑器')
@allure.story('栅格布局-文本组件')
@allure.title('颜色恢复为白色 #ffffff')
@allure.severity(allure.severity_level.NORMAL)
def test_text_color_recover(grid_text_page):
    grid_text_page.prop_color.fill('#E74C3C')
    grid_text_page.prop_color.fill('#ffffff')
    # 右侧断言
    expect(grid_text_page.prop_color).to_have_value('#ffffff')
    # 画布断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('font-weight', '700')


# ==================== 字号修改 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-文本组件')
@allure.title('字号调大为48')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_increase_font_size(grid_text_page):
    grid_text_page.prop_font_size.fill('48')
    # 右侧断言
    expect(grid_text_page.prop_font_size).to_have_value('48')
    # 画布断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '48px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')


@allure.feature('界面编辑器')
@allure.story('栅格布局-文本组件')
@allure.title('字号调小为8')
@allure.severity(allure.severity_level.NORMAL)
def test_text_decrease_font_size(grid_text_page):
    grid_text_page.prop_font_size.fill('8')
    # 右侧断言
    expect(grid_text_page.prop_font_size).to_have_value('8')
    # 画布断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '8px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')


@allure.feature('界面编辑器')
@allure.story('栅格布局-文本组件')
@allure.title('字号从48恢复为24')
@allure.severity(allure.severity_level.NORMAL)
def test_text_font_size_recover(grid_text_page):
    grid_text_page.prop_font_size.fill('48')
    grid_text_page.prop_font_size.fill('24')
    # 右侧断言
    expect(grid_text_page.prop_font_size).to_have_value('24')
    # 画布断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')


# ==================== 单位修改 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-文本组件')
@allure.title('设置单位为"V"')
@allure.severity(allure.severity_level.NORMAL)
def test_text_set_unit(grid_text_page):
    grid_text_page.prop_unit.fill('V')
    # 右侧断言
    expect(grid_text_page.prop_unit).to_have_value('V')
    # 画布断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(grid_text_page.canvas_widgets().first).to_contain_text('V')


@allure.feature('界面编辑器')
@allure.story('栅格布局-文本组件')
@allure.title('清空单位')
@allure.severity(allure.severity_level.NORMAL)
def test_text_unit_clear(grid_text_page):
    grid_text_page.prop_unit.fill('V')
    grid_text_page.prop_unit.fill('')
    # 右侧断言
    expect(grid_text_page.prop_unit).to_have_value('')
    # 画布断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(grid_text_page.canvas_widgets().first).not_to_contain_text('V')


# ==================== 对齐方式 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-文本组件')
@allure.title('切换对齐方式为居中')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_align_center(grid_text_page):
    grid_text_page.prop_align.select_option(label='居中')
    # 右侧断言
    expect(grid_text_page.prop_align).to_have_value('{"value":"center"}')
    # 画布断言：父容器使用 flex + justify-content: center
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    parent_div = text_el.locator('xpath=..')
    expect(parent_div).to_have_css('justify-content', 'center')
    # 基础样式不变
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')


@allure.feature('界面编辑器')
@allure.story('栅格布局-文本组件')
@allure.title('切换对齐方式为右')
@allure.severity(allure.severity_level.NORMAL)
def test_text_align_right(grid_text_page):
    grid_text_page.prop_align.select_option(label='右')
    # 右侧断言
    expect(grid_text_page.prop_align).to_have_value('{"value":"right"}')
    # 画布断言：父容器使用 flex + justify-content: flex-end
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    parent_div = text_el.locator('xpath=..')
    expect(parent_div).to_have_css('justify-content', 'flex-end')
    # 基础样式不变
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')


# ==================== 字重 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-文本组件')
@allure.title('切换字重为正常 (400)')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_weight_normal(grid_text_page):
    grid_text_page.prop_weight.select_option(label='正常')
    # 右侧断言
    expect(grid_text_page.prop_weight).to_have_value('{"value":"400"}')
    # 画布断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-weight', '400')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')


@allure.feature('界面编辑器')
@allure.story('栅格布局-文本组件')
@allure.title('切换字重为粗体 (700)')
@allure.severity(allure.severity_level.NORMAL)
def test_text_weight_bold(grid_text_page):
    grid_text_page.prop_weight.select_option(label='粗体')
    # 右侧断言
    expect(grid_text_page.prop_weight).to_have_value('{"value":"700"}')
    # 画布断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-weight', '700')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')


# ==================== 绑定模式 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-文本组件')
@allure.title('切换绑定模式为静态')
@allure.severity(allure.severity_level.NORMAL)
def test_text_binding_mode_static(grid_text_page):
    grid_text_page.prop_binding_mode.select_option(label='静态')
    # 右侧断言
    expect(grid_text_page.prop_binding_mode).to_have_value('{"value":"static"}')
    # 画布断言（基础样式不变）
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')


@allure.feature('界面编辑器')
@allure.story('栅格布局-文本组件')
@allure.title('切换绑定模式为动态')
@allure.severity(allure.severity_level.NORMAL)
def test_text_binding_mode_dynamic(grid_text_page):
    grid_text_page.prop_binding_mode.select_option(label='动态')
    # 右侧断言
    expect(grid_text_page.prop_binding_mode).to_have_value('{"value":"dynamic"}')
    # 画布断言（基础样式不变）
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')


# ==================== 复制与删除 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-文本组件')
@allure.title('复制文本组件，画布出现两个相同组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_duplicate(grid_text_page):
    grid_text_page.duplicate_widget()
    # 右侧断言（复制后新组件被选中，属性不变）
    expect(grid_text_page.prop_content).to_have_value('标题')
    expect(grid_text_page.prop_font_size).to_have_value('24')
    expect(grid_text_page.prop_color).to_have_value('#ffffff')
    # 数量断言
    expect(grid_text_page.canvas_widgets()).to_have_count(2)
    # 画布断言：两个组件均为默认样式
    first_p = grid_text_page.canvas_widgets().nth(0).locator('p')
    second_p = grid_text_page.canvas_widgets().nth(1).locator('p')
    expect(first_p).to_have_css('font-size', '24px')
    expect(first_p).to_have_css('color', 'rgb(255, 255, 255)')
    expect(first_p).to_have_css('font-weight', '700')
    expect(second_p).to_have_css('font-size', '24px')
    expect(second_p).to_have_css('color', 'rgb(255, 255, 255)')
    expect(second_p).to_have_css('font-weight', '700')
    expect(grid_text_page.canvas_widgets().nth(0)).to_contain_text('标题')
    expect(grid_text_page.canvas_widgets().nth(1)).to_contain_text('标题')


@allure.feature('界面编辑器')
@allure.story('栅格布局-文本组件')
@allure.title('删除文本组件，画布无组件，右侧切换为Page属性')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_delete(grid_text_page):
    grid_text_page.delete_widget()
    # 右侧断言（删除后无组件，切换为Page属性）
    expect(grid_text_page.page_props_marker).to_be_visible()
    # 数量断言
    expect(grid_text_page.canvas_widgets()).to_have_count(0)


# ==================== 组合修改 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-文本组件')
@allure.title('组合修改内容、颜色、字号与对齐方式')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_combined(grid_text_page):
    grid_text_page.prop_content.fill('卫星遥测监控大屏')
    grid_text_page.prop_color.fill('#E74C3C')
    grid_text_page.prop_font_size.fill('48')
    grid_text_page.prop_align.select_option(label='居中')
    # 右侧断言
    expect(grid_text_page.prop_content).to_have_value('卫星遥测监控大屏')
    expect(grid_text_page.prop_color).to_have_value('#E74C3C')
    expect(grid_text_page.prop_font_size).to_have_value('48')
    expect(grid_text_page.prop_align).to_have_value('{"value":"center"}')
    # 画布断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('color', 'rgb(231, 76, 60)')
    expect(text_el).to_have_css('font-size', '48px')
    parent_div = text_el.locator('xpath=..')
    expect(parent_div).to_have_css('justify-content', 'center')
    expect(grid_text_page.canvas_widgets().first).to_contain_text('卫星遥测监控大屏')