from playwright.sync_api import expect


# ==================== 默认状态 ====================

def test_status_default(free_status_page, assert_screenshot):
    expect(free_status_page.canvas_widgets()).to_have_count(1)
    expect(free_status_page.canvas_widgets().first).to_contain_text('状态')
    expect(free_status_page.canvas_widgets().first).to_contain_text('正常')
    assert_screenshot(free_status_page.canvas_widgets().first, 'free_status_default.png')


def test_status_select_shows_properties(free_status_page):
    free_status_page.click_widget()
    expect(free_status_page.prop_panel).to_be_visible()
    expect(free_status_page.prop_label).to_have_value('状态')
    expect(free_status_page.prop_status_text).to_have_value('正常')
    expect(free_status_page.prop_normal_color).to_have_value('#2FC25B')
    expect(free_status_page.prop_warning_color).to_have_value('#F4D03F')
    expect(free_status_page.prop_danger_color).to_have_value('#E74C3C')
    expect(free_status_page.prop_offline_color).to_have_value('#666')
    expect(free_status_page.prop_size).to_have_value('36')


def test_status_click_blank_hides_properties(free_status_page):
    free_status_page.click_widget()
    expect(free_status_page.prop_panel).to_be_visible()
    free_status_page.click_canvas_blank()
    expect(free_status_page.prop_panel).to_be_hidden()


# ==================== 标签 ====================

def test_status_modify_label(free_status_page, assert_screenshot):
    free_status_page.click_widget()
    free_status_page.prop_label.fill('姿轨控 姿态控制')
    expect(free_status_page.prop_label).to_have_value('姿轨控 姿态控制')
    expect(free_status_page.canvas_widgets().first).to_contain_text('姿轨控 姿态控制')
    assert_screenshot(free_status_page.canvas_widgets().first, 'free_status_label_attitude.png')


def test_status_clear_label(free_status_page, assert_screenshot):
    free_status_page.click_widget()
    free_status_page.prop_label.fill('')
    expect(free_status_page.prop_label).to_have_value('')
    assert_screenshot(free_status_page.canvas_widgets().first, 'free_status_label_empty.png')


# ==================== 状态文字 ====================

def test_status_modify_status_text(free_status_page, assert_screenshot):
    free_status_page.click_widget()
    free_status_page.prop_status_text.fill('警告')
    expect(free_status_page.prop_status_text).to_have_value('警告')
    expect(free_status_page.canvas_widgets().first).to_contain_text('警告')
    assert_screenshot(free_status_page.canvas_widgets().first, 'free_status_text_warning.png')


def test_status_clear_status_text(free_status_page, assert_screenshot):
    free_status_page.click_widget()
    free_status_page.prop_status_text.fill('')
    expect(free_status_page.prop_status_text).to_have_value('')
    expect(free_status_page.canvas_widgets().first).not_to_contain_text('正常')
    assert_screenshot(free_status_page.canvas_widgets().first, 'free_status_text_empty.png')


# ==================== 颜色 ====================

def test_status_normal_color_green(free_status_page, assert_screenshot):
    free_status_page.click_widget()
    free_status_page.prop_normal_color.fill('#2FC25B')
    expect(free_status_page.prop_normal_color).to_have_value('#2FC25B')
    assert_screenshot(free_status_page.canvas_widgets().first, 'free_status_color_green.png')


def test_status_warning_color(free_status_page, assert_screenshot):
    free_status_page.click_widget()
    free_status_page.prop_warning_color.fill('#F4D03F')
    expect(free_status_page.prop_warning_color).to_have_value('#F4D03F')
    assert_screenshot(free_status_page.canvas_widgets().first, 'free_status_warning_color.png')


def test_status_danger_color(free_status_page, assert_screenshot):
    free_status_page.click_widget()
    free_status_page.prop_danger_color.fill('#FF0000')
    expect(free_status_page.prop_danger_color).to_have_value('#FF0000')
    assert_screenshot(free_status_page.canvas_widgets().first, 'free_status_danger_color_red.png')


def test_status_offline_color(free_status_page, assert_screenshot):
    free_status_page.click_widget()
    free_status_page.prop_offline_color.fill('#999999')
    expect(free_status_page.prop_offline_color).to_have_value('#999999')
    assert_screenshot(free_status_page.canvas_widgets().first, 'free_status_offline_color.png')


# ==================== 尺寸 ====================

def test_status_size_80(free_status_page, assert_screenshot):
    free_status_page.click_widget()
    free_status_page.prop_size.fill('80')
    expect(free_status_page.prop_size).to_have_value('80')
    assert_screenshot(free_status_page.canvas_widgets().first, 'free_status_size_80.png')


def test_status_size_recover(free_status_page, assert_screenshot):
    free_status_page.click_widget()
    free_status_page.prop_size.fill('80')
    free_status_page.prop_size.fill('36')
    expect(free_status_page.prop_size).to_have_value('36')
    assert_screenshot(free_status_page.canvas_widgets().first, 'free_status_size_recover.png')


# ==================== 显示标签 ====================

def test_status_hide_label(free_status_page, assert_screenshot):
    free_status_page.click_widget()
    free_status_page.show_label_radio('否').check()
    expect(free_status_page.show_label_radio('否')).to_be_checked()
    assert_screenshot(free_status_page.canvas_widgets().first, 'free_status_hide_label.png')


def test_status_show_label_recover(free_status_page, assert_screenshot):
    free_status_page.click_widget()
    free_status_page.show_label_radio('否').check()
    free_status_page.show_label_radio('是').check()
    expect(free_status_page.show_label_radio('是')).to_be_checked()
    expect(free_status_page.canvas_widgets().first).to_contain_text('状态')
    assert_screenshot(free_status_page.canvas_widgets().first, 'free_status_show_label_recover.png')


# ==================== 告警闪烁 ====================

def test_status_blink_off(free_status_page):
    free_status_page.click_widget()
    free_status_page.blink_radio('否').check()
    expect(free_status_page.blink_radio('否')).to_be_checked()


def test_status_blink_on(free_status_page):
    free_status_page.click_widget()
    free_status_page.blink_radio('否').check()
    free_status_page.blink_radio('是').check()
    expect(free_status_page.blink_radio('是')).to_be_checked()


# ==================== 数据绑定 ====================

def test_status_data_binding(free_status_page):
    free_status_page.click_widget()
    free_status_page.prop_data_source.fill('SAT-01')
    free_status_page.prop_field_path.fill('attitude.status')
    expect(free_status_page.prop_data_source).to_have_value('SAT-01')
    expect(free_status_page.prop_field_path).to_have_value('attitude.status')


# ==================== 删除 ====================

def test_status_delete(free_status_page):
    expect(free_status_page.canvas_widgets()).to_have_count(1)
    free_status_page.delete_widget()
    expect(free_status_page.canvas_widgets()).to_have_count(0)