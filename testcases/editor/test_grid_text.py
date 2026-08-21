from playwright.sync_api import expect


# 拖拽文本后画布出现组件，默认显示标题
def test_text_default(grid_text_page, assert_screenshot):
    canvas = grid_text_page.page.locator('#puck-canvas-root')
    expect(grid_text_page.canvas_widgets()).to_have_count(1)
    expect(grid_text_page.canvas_widgets().first).to_contain_text('标题')
    assert_screenshot(canvas, 'grid_text_default.png')


# 点击组件，右侧属性面板显示默认值
def test_text_select_shows_properties(grid_text_page):
    # 右侧断言
    expect(grid_text_page.prop_content).to_have_value('标题')
    expect(grid_text_page.prop_font_size).to_have_value('24')
    expect(grid_text_page.prop_color).to_have_value('#ffffff')
    # CSS断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')


# 改内容
def test_text_modify_content(grid_text_page, assert_screenshot):
    canvas = grid_text_page.page.locator('#puck-canvas-root')
    grid_text_page.prop_content.fill('卫星遥测监控大屏')
    # 右侧断言
    expect(grid_text_page.prop_content).to_have_value('卫星遥测监控大屏')
    # CSS断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(grid_text_page.canvas_widgets().first).to_contain_text('卫星遥测监控大屏')
    assert_screenshot(canvas, 'grid_text_modify_content.png')


# 清空内容
def test_text_clear_content(grid_text_page, assert_screenshot):
    canvas = grid_text_page.page.locator('#puck-canvas-root')
    grid_text_page.prop_content.fill('')
    # 右侧断言
    expect(grid_text_page.prop_content).to_have_value('')
    # CSS断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(grid_text_page.canvas_widgets().first).not_to_contain_text('标题')
    assert_screenshot(canvas, 'grid_text_clear_content.png')


# 字号调大
def test_text_increase_font_size(grid_text_page, assert_screenshot):
    canvas = grid_text_page.page.locator('#puck-canvas-root')
    grid_text_page.prop_font_size.fill('48')
    # 右侧断言
    expect(grid_text_page.prop_font_size).to_have_value('48')
    # CSS断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '48px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    assert_screenshot(canvas, 'grid_text_font_size_48.png')


# 字号调小
def test_text_decrease_font_size(grid_text_page, assert_screenshot):
    canvas = grid_text_page.page.locator('#puck-canvas-root')
    grid_text_page.prop_font_size.fill('8')
    # 右侧断言
    expect(grid_text_page.prop_font_size).to_have_value('8')
    # CSS断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '8px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    assert_screenshot(canvas, 'grid_text_font_size_8.png')


# 修改颜色
def test_text_modify_color(grid_text_page, assert_screenshot):
    canvas = grid_text_page.page.locator('#puck-canvas-root')
    grid_text_page.prop_color.fill('#E74C3C')
    # 右侧断言
    expect(grid_text_page.prop_color).to_have_value('#E74C3C')
    # CSS断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('color', 'rgb(231, 76, 60)')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('font-weight', '700')
    assert_screenshot(canvas, 'grid_text_color_red.png')


# 输入单位
def test_text_set_unit(grid_text_page, assert_screenshot):
    canvas = grid_text_page.page.locator('#puck-canvas-root')
    grid_text_page.prop_unit.fill('V')
    # 右侧断言
    expect(grid_text_page.prop_unit).to_have_value('V')
    # CSS断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(grid_text_page.canvas_widgets().first).to_contain_text('V')
    assert_screenshot(canvas, 'grid_text_unit_v.png')


# 切换对齐为居中
def test_text_align_center(grid_text_page, assert_screenshot):
    canvas = grid_text_page.page.locator('#puck-canvas-root')
    grid_text_page.prop_align.select_option(label='居中')
    # 右侧断言
    expect(grid_text_page.prop_align).to_have_value('{"value":"center"}')
    # CSS断言（对齐效果由截图验证，这里检查字号和颜色不变）
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    assert_screenshot(canvas, 'grid_text_align_center.png')


# 切换对齐为右
def test_text_align_right(grid_text_page, assert_screenshot):
    canvas = grid_text_page.page.locator('#puck-canvas-root')
    grid_text_page.prop_align.select_option(label='右')
    # 右侧断言
    expect(grid_text_page.prop_align).to_have_value('{"value":"right"}')
    # CSS断言（对齐效果由截图验证，这里检查字号和颜色不变）
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    assert_screenshot(canvas, 'grid_text_align_right.png')


# 切换粗细为正常
def test_text_weight_normal(grid_text_page, assert_screenshot):
    canvas = grid_text_page.page.locator('#puck-canvas-root')
    grid_text_page.prop_weight.select_option(label='正常')
    # 右侧断言
    expect(grid_text_page.prop_weight).to_have_value('{"value":"400"}')
    # CSS断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-weight', '400')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    assert_screenshot(canvas, 'grid_text_weight_normal.png')


# 切换粗细为粗体
def test_text_weight_bold(grid_text_page, assert_screenshot):
    canvas = grid_text_page.page.locator('#puck-canvas-root')
    grid_text_page.prop_weight.select_option(label='粗体')
    # 右侧断言
    expect(grid_text_page.prop_weight).to_have_value('{"value":"700"}')
    # CSS断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-weight', '700')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    assert_screenshot(canvas, 'grid_text_weight_bold.png')


# 点击空白，右侧切换回Page属性
def test_text_click_blank_shows_page(grid_text_page):
    grid_text_page.click_canvas_blank()
    expect(grid_text_page.page.get_by_title('布局列数')).to_be_visible()


# 复制文本组件
def test_text_duplicate(grid_text_page, assert_screenshot):
    canvas = grid_text_page.page.locator('#puck-canvas-root')
    grid_text_page.duplicate_button.click()
    # 右侧断言（复制后新组件被选中，属性不变）
    expect(grid_text_page.prop_content).to_have_value('标题')
    expect(grid_text_page.prop_font_size).to_have_value('24')
    expect(grid_text_page.prop_color).to_have_value('#ffffff')
    # 数量断言
    expect(grid_text_page.canvas_widgets()).to_have_count(2)
    # CSS断言：两个组件均为默认样式
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
    assert_screenshot(canvas, 'grid_text_duplicate.png')


# 删除文本组件
def test_text_delete(grid_text_page, assert_screenshot):
    canvas = grid_text_page.page.locator('#puck-canvas-root')
    grid_text_page.delete_button.click()
    # 右侧断言（删除后无组件，切换为Page属性）
    expect(grid_text_page.page.get_by_title('布局列数')).to_be_visible()
    # 数量断言
    expect(grid_text_page.canvas_widgets()).to_have_count(0)
    # 无CSS断言（组件已删）
    assert_screenshot(canvas, 'grid_text_delete.png')


# 字号调大48后再调回24
def test_text_font_size_recover(grid_text_page, assert_screenshot):
    canvas = grid_text_page.page.locator('#puck-canvas-root')
    grid_text_page.prop_font_size.fill('48')
    grid_text_page.prop_font_size.fill('24')
    # 右侧断言
    expect(grid_text_page.prop_font_size).to_have_value('24')
    # CSS断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    assert_screenshot(canvas, 'grid_text_font_size_recover.png')


# 颜色改为红色后再恢复白色
def test_text_color_recover(grid_text_page, assert_screenshot):
    canvas = grid_text_page.page.locator('#puck-canvas-root')
    grid_text_page.prop_color.fill('#E74C3C')
    grid_text_page.prop_color.fill('#ffffff')
    # 右侧断言
    expect(grid_text_page.prop_color).to_have_value('#ffffff')
    # CSS断言
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('font-weight', '700')
    assert_screenshot(canvas, 'grid_text_color_recover.png')


# 输入单位后再清空
def test_text_unit_clear(grid_text_page, assert_screenshot):
    canvas = grid_text_page.page.locator('#puck-canvas-root')
    grid_text_page.prop_unit.fill('V')
    grid_text_page.prop_unit.fill('')
    # 右侧断言
    expect(grid_text_page.prop_unit).to_have_value('')
    # CSS断言（样式不变）
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    # 验证单位消失（即文本不含'V'）
    expect(grid_text_page.canvas_widgets().first).not_to_contain_text('V')
    assert_screenshot(canvas, 'grid_text_unit_clear.png')


# 绑定模式切换为静态
def test_text_binding_mode_static(grid_text_page, assert_screenshot):
    canvas = grid_text_page.page.locator('#puck-canvas-root')
    grid_text_page.prop_binding_mode.select_option(label='静态')
    # 右侧断言
    expect(grid_text_page.prop_binding_mode).to_have_value('{"value":"static"}')
    # CSS断言（绑定模式改变不改变样式，但可检查基础样式不变）
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    assert_screenshot(canvas, 'grid_text_binding_static.png')


# 绑定模式切换为动态
def test_text_binding_mode_dynamic(grid_text_page, assert_screenshot):
    canvas = grid_text_page.page.locator('#puck-canvas-root')
    grid_text_page.prop_binding_mode.select_option(label='动态')
    # 右侧断言
    expect(grid_text_page.prop_binding_mode).to_have_value('{"value":"dynamic"}')
    # CSS断言（基础样式不变）
    text_el = grid_text_page.canvas_widgets().first.locator('p')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    assert_screenshot(canvas, 'grid_text_binding_dynamic.png')