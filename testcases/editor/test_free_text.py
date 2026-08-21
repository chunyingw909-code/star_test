from playwright.sync_api import expect


# 验证组件默认状态 标题
def test_text_default(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(free_text_page.canvas_widgets()).to_have_count(1)
    expect(free_text_page.canvas_widgets().first).to_contain_text('标题')
    # 右侧断言
    expect(free_text_page.prop_content).to_have_value('标题')
    expect(free_text_page.prop_font_size).to_have_value('24')
    expect(free_text_page.prop_color).to_have_value('#ffffff')
    # CSS断言
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_default.png')


# 初始内容字号颜色
def test_text_select_shows_properties(free_text_page):
    free_text_page.click_widget()
    expect(free_text_page.prop_panel).to_be_visible()
    expect(free_text_page.prop_content).to_have_value('标题')
    expect(free_text_page.prop_font_size).to_have_value('24')
    expect(free_text_page.prop_color).to_have_value('#ffffff')
    # CSS断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')


# 点空白区域 属性面板消失
def test_text_click_blank_hides_properties(free_text_page):
    free_text_page.click_widget()
    expect(free_text_page.prop_panel).to_be_visible()
    free_text_page.click_canvas_blank()
    expect(free_text_page.prop_panel).to_be_hidden()


# 改内容里面的字
def test_text_modify_content(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_content.fill('卫星遥测监控大屏')
    # 右侧断言
    expect(free_text_page.prop_content).to_have_value('卫星遥测监控大屏')
    # CSS断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    expect(free_text_page.canvas_widgets().first).to_contain_text('卫星遥测监控大屏')
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_modify_content.png')


# 改颜色
def test_text_modify_color(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_color.fill('#E74C3C')
    # 右侧断言
    expect(free_text_page.prop_color).to_have_value('#E74C3C')
    # CSS断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('color', 'rgb(231, 76, 60)')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('font-weight', '700')
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_color_red.png')


# 删除组件
def test_text_delete(free_text_page):
    expect(free_text_page.canvas_widgets()).to_have_count(1)
    free_text_page.delete_widget()
    expect(free_text_page.canvas_widgets()).to_have_count(0)


# 清空内容，画布上不显示文字
def test_text_clear_content(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_content.fill('')
    # 右侧断言
    expect(free_text_page.prop_content).to_have_value('')
    # CSS断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    expect(free_text_page.canvas_widgets().first).not_to_contain_text('标题')
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_clear_content.png')


# 字号调大
def test_text_increase_font_size(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_font_size.fill('48')
    # 右侧断言
    expect(free_text_page.prop_font_size).to_have_value('48')
    # CSS断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '48px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_font_size_48.png')


# 字号调小
def test_text_decrease_font_size(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_font_size.fill('8')
    # 右侧断言
    expect(free_text_page.prop_font_size).to_have_value('8')
    # CSS断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '8px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_font_size_8.png')


# 输入单位
def test_text_set_unit(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_unit.fill('V')
    # 右侧断言
    expect(free_text_page.prop_unit).to_have_value('V')
    # CSS断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    expect(free_text_page.canvas_widgets().first).to_contain_text('V')
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_unit_v.png')


# 切换对齐方式为居中
def test_text_align_center(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_align.click()
    free_text_page.page.get_by_role('option', name='居中').click()
    # 右侧断言
    expect(free_text_page.prop_align).to_have_text('居中')
    # CSS断言（对齐效果由截图验证，这里检查字号和颜色不变）
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_align_center.png')


# 切换对齐为右
def test_text_align_right(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_align.click()
    free_text_page.page.get_by_role('option', name='右').click()
    # 右侧断言
    expect(free_text_page.prop_align).to_have_text('右')
    # CSS断言（对齐效果由截图验证，这里检查字号和颜色不变）
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_align_right.png')


# 切换粗细为正常
def test_text_weight_normal(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_weight.click()
    free_text_page.page.get_by_role('option', name='正常').click()
    # 右侧断言
    expect(free_text_page.prop_weight).to_have_text('正常')
    # CSS断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-weight', '400')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_weight_normal.png')


# 切换粗细为粗体
def test_text_weight_bold(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_weight.click()
    free_text_page.page.get_by_role('option', name='粗体').click()
    # 右侧断言
    expect(free_text_page.prop_weight).to_have_text('粗体')
    # CSS断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-weight', '700')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_weight_bold.png')


# ==================== 新增补充测试（对齐 grid） ====================

# 清空内容后重新输入"母线电压"
def test_text_content_recover(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_content.fill('母线电压')
    # 右侧断言
    expect(free_text_page.prop_content).to_have_value('母线电压')
    # CSS断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    expect(free_text_page.canvas_widgets().first).to_contain_text('母线电压')
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_content_recover.png')


# 字号调大48后再调回24
def test_text_font_size_recover(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_font_size.fill('48')
    free_text_page.prop_font_size.fill('24')
    # 右侧断言
    expect(free_text_page.prop_font_size).to_have_value('24')
    # CSS断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_font_size_recover.png')


# 颜色改为红色后再恢复白色
def test_text_color_recover(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_color.fill('#E74C3C')
    free_text_page.prop_color.fill('#ffffff')
    # 右侧断言
    expect(free_text_page.prop_color).to_have_value('#ffffff')
    # CSS断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('font-weight', '700')
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_color_recover.png')


# 颜色改为浅蓝色 #4fc3f7
def test_text_color_light_blue(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_color.fill('#4fc3f7')
    # 右侧断言
    expect(free_text_page.prop_color).to_have_value('#4fc3f7')
    # CSS断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('color', 'rgb(79, 195, 247)')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('font-weight', '700')
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_color_light_blue.png')


# 字重切换为中等 (500)
def test_text_weight_medium(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_weight.click()
    free_text_page.page.get_by_role('option', name='中等').click()
    # 右侧断言
    expect(free_text_page.prop_weight).to_have_text('中等')
    # CSS断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-weight', '500')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_weight_medium.png')


# 输入单位后再清空
def test_text_unit_clear(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_unit.fill('V')
    free_text_page.prop_unit.fill('')
    # 右侧断言
    expect(free_text_page.prop_unit).to_have_value('')
    # CSS断言
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    # 验证单位消失（即文本不含'V'）
    expect(free_text_page.canvas_widgets().first).not_to_contain_text('V')
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_unit_clear.png')


# 绑定模式切换为静态
def test_text_binding_mode_static(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_binding_mode.click()
    free_text_page.page.get_by_role('option', name='静态').click()
    # 右侧断言
    expect(free_text_page.prop_binding_mode).to_have_text('静态')
    # CSS断言（绑定模式不改变样式）
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_binding_static.png')


# 绑定模式切换为动态
def test_text_binding_mode_dynamic(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_binding_mode.click()
    free_text_page.page.get_by_role('option', name='动态').click()
    # 右侧断言
    expect(free_text_page.prop_binding_mode).to_have_text('动态')
    # CSS断言（绑定模式不改变样式）
    text_el = free_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    assert_screenshot(free_text_page.canvas_widgets().first, 'free_text_binding_dynamic.png')