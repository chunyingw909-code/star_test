from playwright.sync_api import expect

# 验证组件默认状态 标题
def test_text_default(free_text_page,assert_screenshot):
    expect(free_text_page.canvas_widgets()).to_have_count(1)
    expect(free_text_page.canvas_widgets().first).to_contain_text('标题')
    assert_screenshot(free_text_page.canvas_widgets().first, 'text_default.png')

# 初始内容字号颜色
def test_text_select_shows_properties(free_text_page):
    free_text_page.click_widget()
    expect(free_text_page.prop_panel).to_be_visible()
    expect(free_text_page.prop_content).to_have_value('标题')
    expect(free_text_page.prop_font_size).to_have_value('24')
    expect(free_text_page.prop_color).to_have_value('#ffffff')

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
    expect(free_text_page.canvas_widgets().first).to_contain_text('卫星遥测监控大屏')   #左
    expect(free_text_page.prop_content).to_have_value('卫星遥测监控大屏')  #右
    assert_screenshot(free_text_page.canvas_widgets().first, 'text_modify_content.png')


# 改颜色
def test_text_modify_color(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_color.fill('#E74C3C')
    expect(free_text_page.prop_color).to_have_value('#E74C3C')
    assert_screenshot(free_text_page.canvas_widgets().first, 'text_color_red.png')


# 删除组件
def test_text_delete(free_text_page):
    expect(free_text_page.canvas_widgets()).to_have_count(1)
    free_text_page.delete_widget()
    expect(free_text_page.canvas_widgets()).to_have_count(0)

# 清空内容，画布上不显示文字
def test_text_clear_content(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_content.fill('')
    expect(free_text_page.prop_content).to_have_value('')
    expect(free_text_page.canvas_widgets().first).not_to_contain_text('标题')
    assert_screenshot(free_text_page.canvas_widgets().first, 'text_clear_content.png')


# 字号调大
def test_text_increase_font_size(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_font_size.fill('48')
    expect(free_text_page.prop_font_size).to_have_value('48')
    assert_screenshot(free_text_page.canvas_widgets().first, 'text_font_size_48.png')

# 字号调小
def test_text_decrease_font_size(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_font_size.fill('8')
    expect(free_text_page.prop_font_size).to_have_value('8')
    assert_screenshot(free_text_page.canvas_widgets().first, 'text_font_size_8.png')


# 输入单位
def test_text_set_unit(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_unit.fill('V')
    expect(free_text_page.canvas_widgets().first).to_contain_text('V')
    expect(free_text_page.prop_unit).to_have_value('V')
    assert_screenshot(free_text_page.canvas_widgets().first, 'text_unit_v.png')

# 切换对齐方式为居中
def test_text_align_center(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_align.click()
    free_text_page.page.get_by_role('option', name='居中').click()
    expect(free_text_page.prop_align).to_have_text('居中')
    assert_screenshot(free_text_page.canvas_widgets().first, 'text_align_center.png')


# 切换对齐为右
def test_text_align_right(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_align.click()
    free_text_page.page.get_by_role('option', name='右').click()
    expect(free_text_page.prop_align).to_have_text('右')
    assert_screenshot(free_text_page.canvas_widgets().first, 'text_align_right.png')


# 切换粗细为正常
def test_text_weight_normal(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_weight.click()
    free_text_page.page.get_by_role('option', name='正常').click()
    expect(free_text_page.prop_weight).to_have_text('正常')
    assert_screenshot(free_text_page.canvas_widgets().first, 'text_weight_normal.png')


# 切换粗细为粗体
def test_text_weight_bold(free_text_page, assert_screenshot):
    free_text_page.click_widget()
    free_text_page.prop_weight.click()
    free_text_page.page.get_by_role('option', name='粗体').click()
    expect(free_text_page.prop_weight).to_have_text('粗体')
    assert_screenshot(free_text_page.canvas_widgets().first, 'text_weight_bold.png')

