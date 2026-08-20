from playwright.sync_api import expect


# 拖拽文本后画布出现组件，默认显示标题
def test_text_default(grid_text_page, assert_screenshot):
    expect(grid_text_page.canvas_widgets()).to_have_count(1)
    expect(grid_text_page.canvas_widgets().first).to_contain_text('标题')
    assert_screenshot(grid_text_page.canvas_widgets().first, 'grid_text_default.png')


# 点击组件，右侧属性面板显示默认值
def test_text_select_shows_properties(grid_text_page):
    grid_text_page.click_widget()
    expect(grid_text_page.prop_content).to_have_value('标题')
    expect(grid_text_page.prop_font_size).to_have_value('24')
    expect(grid_text_page.prop_color).to_have_value('#ffffff')


# 改内容
def test_text_modify_content(grid_text_page, assert_screenshot):
    grid_text_page.click_widget()
    grid_text_page.prop_content.fill('卫星遥测监控大屏')
    expect(grid_text_page.prop_content).to_have_value('卫星遥测监控大屏')
    expect(grid_text_page.canvas_widgets().first).to_contain_text('卫星遥测监控大屏')
    assert_screenshot(grid_text_page.canvas_widgets().first, 'grid_text_modify_content.png')


# 清空内容
def test_text_clear_content(grid_text_page, assert_screenshot):
    grid_text_page.click_widget()
    grid_text_page.prop_content.fill('')
    expect(grid_text_page.prop_content).to_have_value('')
    expect(grid_text_page.canvas_widgets().first).not_to_contain_text('标题')
    assert_screenshot(grid_text_page.canvas_widgets().first, 'grid_text_clear_content.png')


# 字号调大
def test_text_increase_font_size(grid_text_page, assert_screenshot):
    grid_text_page.click_widget()
    grid_text_page.prop_font_size.fill('48')
    expect(grid_text_page.prop_font_size).to_have_value('48')
    assert_screenshot(grid_text_page.canvas_widgets().first, 'grid_text_font_size_48.png')


# 字号调小
def test_text_decrease_font_size(grid_text_page, assert_screenshot):
    grid_text_page.click_widget()
    grid_text_page.prop_font_size.fill('8')
    expect(grid_text_page.prop_font_size).to_have_value('8')
    assert_screenshot(grid_text_page.canvas_widgets().first, 'grid_text_font_size_8.png')


# 修改颜色
def test_text_modify_color(grid_text_page, assert_screenshot):
    grid_text_page.click_widget()
    grid_text_page.prop_color.fill('#E74C3C')
    expect(grid_text_page.prop_color).to_have_value('#E74C3C')
    assert_screenshot(grid_text_page.canvas_widgets().first, 'grid_text_color_red.png')


# 输入单位
def test_text_set_unit(grid_text_page, assert_screenshot):
    grid_text_page.click_widget()
    grid_text_page.prop_unit.fill('V')
    expect(grid_text_page.prop_unit).to_have_value('V')
    assert_screenshot(grid_text_page.canvas_widgets().first, 'grid_text_unit_v.png')


# 切换对齐为居中
def test_text_align_center(grid_text_page, assert_screenshot):
    grid_text_page.click_widget()
    grid_text_page.prop_align.select_option(label='居中')
    assert_screenshot(grid_text_page.canvas_widgets().first, 'grid_text_align_center.png')


# 切换对齐为右
def test_text_align_right(grid_text_page, assert_screenshot):
    grid_text_page.click_widget()
    grid_text_page.prop_align.select_option(label='右')
    assert_screenshot(grid_text_page.canvas_widgets().first, 'grid_text_align_right.png')


# 切换粗细为正常
def test_text_weight_normal(grid_text_page, assert_screenshot):
    grid_text_page.click_widget()
    grid_text_page.prop_weight.select_option(label='正常')
    assert_screenshot(grid_text_page.canvas_widgets().first, 'grid_text_weight_normal.png')


# 切换粗细为粗体
def test_text_weight_bold(grid_text_page, assert_screenshot):
    grid_text_page.click_widget()
    grid_text_page.prop_weight.select_option(label='粗体')
    assert_screenshot(grid_text_page.canvas_widgets().first, 'grid_text_weight_bold.png')

# 点击空白，右侧切换回Page属性
def test_text_click_blank_shows_page(grid_text_page):
    grid_text_page.click_canvas_blank()
    expect(grid_text_page.page.locator('h2', has_text='Page')).to_be_visible()