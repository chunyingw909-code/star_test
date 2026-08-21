from playwright.sync_api import expect


# ==================== 默认状态 ====================

def test_status_default(grid_status_page, assert_screenshot):
    canvas = grid_status_page.page.locator('#puck-canvas-root')
    expect(grid_status_page.canvas_widgets()).to_have_count(1)
    expect(grid_status_page.canvas_widgets().first).to_contain_text('状态')
    assert_screenshot(canvas, 'grid_status_default.png')


def test_status_select_shows_properties(grid_status_page):
    expect(grid_status_page.prop_label).to_have_value('状态')
    expect(grid_status_page.prop_status_text).to_have_value('正常')
    expect(grid_status_page.prop_normal_color).to_have_value('#2FC25B')
    expect(grid_status_page.prop_warning_color).to_have_value('#F4D03F')
    expect(grid_status_page.prop_danger_color).to_have_value('#E74C3C')
    expect(grid_status_page.prop_offline_color).to_have_value('#666')
    expect(grid_status_page.prop_size).to_have_value('36')


def test_status_click_blank_shows_page(grid_status_page):
    grid_status_page.click_canvas_blank()
    expect(grid_status_page.page.get_by_title('布局列数')).to_be_visible()


# ==================== 标签 ====================

def test_status_modify_label(grid_status_page, assert_screenshot):
    canvas = grid_status_page.page.locator('#puck-canvas-root')
    grid_status_page.prop_label.fill('姿轨控 姿态控制')
    expect(grid_status_page.prop_label).to_have_value('姿轨控 姿态控制')
    expect(grid_status_page.canvas_widgets().first).to_contain_text('姿轨控 姿态控制')
    assert_screenshot(canvas, 'grid_status_label_attitude.png')


def test_status_clear_label(grid_status_page, assert_screenshot):
    canvas = grid_status_page.page.locator('#puck-canvas-root')
    grid_status_page.prop_label.fill('')
    expect(grid_status_page.prop_label).to_have_value('')
    assert_screenshot(canvas, 'grid_status_label_empty.png')


# ==================== 状态文字 ====================

def test_status_modify_status_text(grid_status_page, assert_screenshot):
    canvas = grid_status_page.page.locator('#puck-canvas-root')
    grid_status_page.prop_status_text.fill('警告')
    expect(grid_status_page.prop_status_text).to_have_value('警告')
    expect(grid_status_page.canvas_widgets().first).to_contain_text('警告')
    assert_screenshot(canvas, 'grid_status_text_warning.png')


def test_status_clear_status_text(grid_status_page, assert_screenshot):
    canvas = grid_status_page.page.locator('#puck-canvas-root')
    grid_status_page.prop_status_text.fill('')
    expect(grid_status_page.prop_status_text).to_have_value('')
    assert_screenshot(canvas, 'grid_status_text_empty.png')


def test_status_status_text_recover(grid_status_page, assert_screenshot):
    canvas = grid_status_page.page.locator('#puck-canvas-root')
    grid_status_page.prop_status_text.fill('警告')
    grid_status_page.prop_status_text.fill('异常')
    expect(grid_status_page.prop_status_text).to_have_value('异常')
    expect(grid_status_page.canvas_widgets().first).to_contain_text('异常')
    assert_screenshot(canvas, 'grid_status_text_recover.png')


# ==================== 颜色 ====================

def test_status_normal_color(grid_status_page, assert_screenshot):
    canvas = grid_status_page.page.locator('#puck-canvas-root')
    grid_status_page.prop_normal_color.fill('#2FC25B')
    expect(grid_status_page.prop_normal_color).to_have_value('#2FC25B')
    assert_screenshot(canvas, 'grid_status_color_green.png')


def test_status_warning_color(grid_status_page, assert_screenshot):
    canvas = grid_status_page.page.locator('#puck-canvas-root')
    grid_status_page.prop_warning_color.fill('#F4D03F')
    expect(grid_status_page.prop_warning_color).to_have_value('#F4D03F')
    assert_screenshot(canvas, 'grid_status_warning_color.png')


def test_status_danger_color(grid_status_page, assert_screenshot):
    canvas = grid_status_page.page.locator('#puck-canvas-root')
    grid_status_page.prop_danger_color.fill('#FF0000')
    expect(grid_status_page.prop_danger_color).to_have_value('#FF0000')
    assert_screenshot(canvas, 'grid_status_danger_color.png')


def test_status_offline_color(grid_status_page, assert_screenshot):
    canvas = grid_status_page.page.locator('#puck-canvas-root')
    grid_status_page.prop_offline_color.fill('#999999')
    expect(grid_status_page.prop_offline_color).to_have_value('#999999')
    assert_screenshot(canvas, 'grid_status_offline_color.png')


def test_status_color_recover(grid_status_page, assert_screenshot):
    canvas = grid_status_page.page.locator('#puck-canvas-root')
    grid_status_page.prop_normal_color.fill('#00FF00')
    grid_status_page.prop_normal_color.fill('#2FC25B')
    expect(grid_status_page.prop_normal_color).to_have_value('#2FC25B')
    assert_screenshot(canvas, 'grid_status_color_recover.png')


# ==================== 尺寸 ====================

def test_status_size_80(grid_status_page, assert_screenshot):
    canvas = grid_status_page.page.locator('#puck-canvas-root')
    grid_status_page.prop_size.fill('80')
    expect(grid_status_page.prop_size).to_have_value('80')
    assert_screenshot(canvas, 'grid_status_size_80.png')


def test_status_size_12(grid_status_page, assert_screenshot):
    canvas = grid_status_page.page.locator('#puck-canvas-root')
    grid_status_page.prop_size.fill('12')
    expect(grid_status_page.prop_size).to_have_value('12')
    assert_screenshot(canvas, 'grid_status_size_12.png')


def test_status_size_recover(grid_status_page, assert_screenshot):
    canvas = grid_status_page.page.locator('#puck-canvas-root')
    grid_status_page.prop_size.fill('80')
    grid_status_page.prop_size.fill('36')
    expect(grid_status_page.prop_size).to_have_value('36')
    assert_screenshot(canvas, 'grid_status_size_recover.png')


# ==================== 显示标签 ====================

def test_status_hide_label(grid_status_page, assert_screenshot):
    canvas = grid_status_page.page.locator('#puck-canvas-root')
    grid_status_page.show_label_label('否').click()
    expect(grid_status_page.show_label_radio('否')).to_be_checked()
    assert_screenshot(canvas, 'grid_status_hide_label.png')


def test_status_show_label_recover(grid_status_page, assert_screenshot):
    canvas = grid_status_page.page.locator('#puck-canvas-root')
    grid_status_page.show_label_label('否').click()
    grid_status_page.show_label_label('是').click()
    expect(grid_status_page.show_label_radio('是')).to_be_checked()
    expect(grid_status_page.canvas_widgets().first).to_contain_text('状态')
    assert_screenshot(canvas, 'grid_status_show_label_recover.png')


# ==================== 告警闪烁 ====================

def test_status_blink_off(grid_status_page):
    grid_status_page.blink_label('否').click()
    expect(grid_status_page.blink_radio('否')).to_be_checked()


def test_status_blink_on(grid_status_page):
    grid_status_page.blink_label('否').click()
    grid_status_page.blink_label('是').click()
    expect(grid_status_page.blink_radio('是')).to_be_checked()


# ==================== 刷新模式 ====================

def test_status_refresh_mode_poll(grid_status_page):
    grid_status_page.prop_refresh_mode.select_option(label='轮询')
    expect(grid_status_page.prop_refresh_mode).to_have_value('{"value":"poll"}')


def test_status_refresh_mode_manual(grid_status_page):
    grid_status_page.prop_refresh_mode.select_option(label='手动')
    expect(grid_status_page.prop_refresh_mode).to_have_value('{"value":"manual"}')


def test_status_refresh_mode_push(grid_status_page):
    grid_status_page.prop_refresh_mode.select_option(label='手动')
    grid_status_page.prop_refresh_mode.select_option(label='推送')
    expect(grid_status_page.prop_refresh_mode).to_have_value('{"value":"push"}')


# ==================== 出错时 ====================

def test_status_error_fallback_show_last(grid_status_page):
    grid_status_page.prop_error_fallback.select_option(label='显示上次')
    expect(grid_status_page.prop_error_fallback).to_have_value('{"value":"showLast"}')


def test_status_error_fallback_hide(grid_status_page):
    grid_status_page.prop_error_fallback.select_option(label='隐藏')
    expect(grid_status_page.prop_error_fallback).to_have_value('{"value":"hide"}')


def test_status_error_fallback_recover(grid_status_page):
    grid_status_page.prop_error_fallback.select_option(label='隐藏')
    grid_status_page.prop_error_fallback.select_option(label='显示空')
    expect(grid_status_page.prop_error_fallback).to_have_value('{"value":"showEmpty"}')


# ==================== 点击事件 ====================

def test_status_click_action_alert(grid_status_page):
    grid_status_page.prop_click_action.select_option(label='弹窗提示')
    expect(grid_status_page.prop_click_action).to_have_value('{"value":"alert"}')


def test_status_click_action_navigate(grid_status_page):
    grid_status_page.prop_click_action.select_option(label='跳转 URL')
    grid_status_page.prop_click_target.fill('https://example.com')
    expect(grid_status_page.prop_click_action).to_have_value('{"value":"navigate"}')
    expect(grid_status_page.prop_click_target).to_have_value('https://example.com')


def test_status_click_action_none(grid_status_page):
    grid_status_page.prop_click_action.select_option(label='弹窗提示')
    grid_status_page.prop_click_action.select_option(label='无')
    expect(grid_status_page.prop_click_action).to_have_value('{"value":""}')


# ==================== 数据绑定 ====================

def test_status_data_binding(grid_status_page):
    grid_status_page.prop_data_source.fill('SAT-01')
    grid_status_page.prop_field_path.fill('attitude.status')
    expect(grid_status_page.prop_data_source).to_have_value('SAT-01')
    expect(grid_status_page.prop_field_path).to_have_value('attitude.status')


def test_status_data_binding_clear(grid_status_page):
    grid_status_page.prop_data_source.fill('SAT-01')
    grid_status_page.prop_field_path.fill('attitude.status')
    grid_status_page.prop_data_source.fill('')
    grid_status_page.prop_field_path.fill('')
    expect(grid_status_page.prop_data_source).to_have_value('')
    expect(grid_status_page.prop_field_path).to_have_value('')


# ==================== 复制 / 删除 ====================

def test_status_duplicate(grid_status_page, assert_screenshot):
    canvas = grid_status_page.page.locator('#puck-canvas-root')
    grid_status_page.duplicate_button.dispatch_event('click')
    expect(grid_status_page.canvas_widgets()).to_have_count(2)
    expect(grid_status_page.prop_label).to_have_value('状态')
    expect(grid_status_page.prop_size).to_have_value('36')
    assert_screenshot(canvas, 'grid_status_duplicate.png')


def test_status_delete(grid_status_page, assert_screenshot):
    canvas = grid_status_page.page.locator('#puck-canvas-root')
    grid_status_page.delete_button.dispatch_event('click')
    expect(grid_status_page.page.get_by_title('布局列数')).to_be_visible()
    expect(grid_status_page.canvas_widgets()).to_have_count(0)
    assert_screenshot(canvas, 'grid_status_delete.png')