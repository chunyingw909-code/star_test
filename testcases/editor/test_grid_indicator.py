from playwright.sync_api import expect


# ==================== 默认状态 ====================

def test_indicator_default(grid_indicator_page, assert_screenshot):
    canvas = grid_indicator_page.page.locator('#puck-canvas-root')
    expect(grid_indicator_page.canvas_widgets()).to_have_count(1)
    expect(grid_indicator_page.canvas_widgets().first).to_contain_text('CPU 使用率')
    assert_screenshot(canvas, 'grid_indicator_default.png')


def test_indicator_select_shows_properties(grid_indicator_page):
    expect(grid_indicator_page.prop_label).to_have_value('CPU 使用率')
    expect(grid_indicator_page.prop_value).to_have_value('45.2')
    expect(grid_indicator_page.prop_unit).to_have_value('%')
    expect(grid_indicator_page.prop_warning_threshold).to_have_value('70')
    expect(grid_indicator_page.prop_danger_threshold).to_have_value('90')
    expect(grid_indicator_page.prop_icon).to_have_value('{"value":"cpu"}')
    expect(grid_indicator_page.prop_decimal).to_have_value('1')


def test_indicator_click_blank_shows_page(grid_indicator_page):
    grid_indicator_page.click_canvas_blank()
    expect(grid_indicator_page.page.get_by_title('布局列数')).to_be_visible()


# ==================== 标签 ====================

def test_indicator_modify_label(grid_indicator_page, assert_screenshot):
    canvas = grid_indicator_page.page.locator('#puck-canvas-root')
    grid_indicator_page.prop_label.fill('母线电流')
    expect(grid_indicator_page.prop_label).to_have_value('母线电流')
    expect(grid_indicator_page.canvas_widgets().first).to_contain_text('母线电流')
    assert_screenshot(canvas, 'grid_indicator_label_current.png')


def test_indicator_clear_label(grid_indicator_page, assert_screenshot):
    canvas = grid_indicator_page.page.locator('#puck-canvas-root')
    grid_indicator_page.prop_label.fill('')
    expect(grid_indicator_page.prop_label).to_have_value('')
    expect(grid_indicator_page.canvas_widgets().first).not_to_contain_text('CPU 使用率')
    assert_screenshot(canvas, 'grid_indicator_label_empty.png')


def test_indicator_label_recover(grid_indicator_page):
    grid_indicator_page.prop_label.fill('母线电流')
    grid_indicator_page.prop_label.fill('CPU 使用率')
    expect(grid_indicator_page.prop_label).to_have_value('CPU 使用率')
    expect(grid_indicator_page.canvas_widgets().first).to_contain_text('CPU 使用率')


# ==================== 数值 ====================

def test_indicator_modify_value(grid_indicator_page):
    grid_indicator_page.prop_value.fill('88.5')
    expect(grid_indicator_page.prop_value).to_have_value('88.5')


def test_indicator_value_zero(grid_indicator_page):
    grid_indicator_page.prop_value.fill('0')
    expect(grid_indicator_page.prop_value).to_have_value('0')


def test_indicator_value_recover(grid_indicator_page):
    grid_indicator_page.prop_value.fill('88.5')
    grid_indicator_page.prop_value.fill('45.2')
    expect(grid_indicator_page.prop_value).to_have_value('45.2')


# ==================== 单位 ====================

def test_indicator_modify_unit(grid_indicator_page, assert_screenshot):
    canvas = grid_indicator_page.page.locator('#puck-canvas-root')
    grid_indicator_page.prop_unit.fill('A')
    expect(grid_indicator_page.prop_unit).to_have_value('A')
    expect(grid_indicator_page.canvas_widgets().first).to_contain_text('A')
    assert_screenshot(canvas, 'grid_indicator_unit_a.png')


def test_indicator_unit_clear(grid_indicator_page):
    grid_indicator_page.prop_unit.fill('')
    expect(grid_indicator_page.prop_unit).to_have_value('')


def test_indicator_unit_recover(grid_indicator_page):
    grid_indicator_page.prop_unit.fill('A')
    grid_indicator_page.prop_unit.fill('%')
    expect(grid_indicator_page.prop_unit).to_have_value('%')
    expect(grid_indicator_page.canvas_widgets().first).to_contain_text('%')


# ==================== 警告阈值 / 危险阈值 ====================

def test_indicator_warning_threshold(grid_indicator_page):
    grid_indicator_page.prop_warning_threshold.fill('70')
    grid_indicator_page.prop_danger_threshold.fill('90')
    grid_indicator_page.prop_value.fill('88.5')
    expect(grid_indicator_page.prop_warning_threshold).to_have_value('70')
    expect(grid_indicator_page.prop_danger_threshold).to_have_value('90')
    expect(grid_indicator_page.prop_value).to_have_value('88.5')


def test_indicator_danger_threshold(grid_indicator_page):
    grid_indicator_page.prop_warning_threshold.fill('70')
    grid_indicator_page.prop_danger_threshold.fill('90')
    grid_indicator_page.prop_value.fill('95')
    expect(grid_indicator_page.prop_value).to_have_value('95')


def test_indicator_normal_state(grid_indicator_page):
    grid_indicator_page.prop_warning_threshold.fill('70')
    grid_indicator_page.prop_danger_threshold.fill('90')
    grid_indicator_page.prop_value.fill('50')
    expect(grid_indicator_page.prop_value).to_have_value('50')


# ==================== 图标 ====================

def test_indicator_icon_memory(grid_indicator_page):
    grid_indicator_page.prop_icon.select_option(label='内存')
    expect(grid_indicator_page.prop_icon).to_have_value('{"value":"memory"}')


def test_indicator_icon_network(grid_indicator_page):
    grid_indicator_page.prop_icon.select_option(label='网络')
    expect(grid_indicator_page.prop_icon).to_have_value('{"value":"network"}')


def test_indicator_icon_temp(grid_indicator_page):
    grid_indicator_page.prop_icon.select_option(label='温度')
    expect(grid_indicator_page.prop_icon).to_have_value('{"value":"temp"}')


def test_indicator_icon_speed(grid_indicator_page):
    grid_indicator_page.prop_icon.select_option(label='速度')
    expect(grid_indicator_page.prop_icon).to_have_value('{"value":"speed"}')


def test_indicator_icon_recover(grid_indicator_page):
    grid_indicator_page.prop_icon.select_option(label='温度')
    grid_indicator_page.prop_icon.select_option(label='CPU')
    expect(grid_indicator_page.prop_icon).to_have_value('{"value":"cpu"}')


# ==================== 小数位 ====================

def test_indicator_decimal_0(grid_indicator_page):
    grid_indicator_page.prop_decimal.fill('0')
    expect(grid_indicator_page.prop_decimal).to_have_value('0')


def test_indicator_decimal_3(grid_indicator_page):
    grid_indicator_page.prop_decimal.fill('3')
    expect(grid_indicator_page.prop_decimal).to_have_value('3')


def test_indicator_decimal_recover(grid_indicator_page):
    grid_indicator_page.prop_decimal.fill('0')
    grid_indicator_page.prop_decimal.fill('1')
    expect(grid_indicator_page.prop_decimal).to_have_value('1')


# ==================== 显示状态 ====================

def test_indicator_hide_status(grid_indicator_page):
    grid_indicator_page.show_status_label('否').click()
    expect(grid_indicator_page.show_status_radio('否')).to_be_checked()


def test_indicator_show_status_recover(grid_indicator_page):
    grid_indicator_page.show_status_label('否').click()
    grid_indicator_page.show_status_label('是').click()
    expect(grid_indicator_page.show_status_radio('是')).to_be_checked()


# ==================== 刷新模式 ====================

def test_indicator_refresh_mode_poll(grid_indicator_page):
    grid_indicator_page.prop_refresh_mode.select_option(label='轮询')
    expect(grid_indicator_page.prop_refresh_mode).to_have_value('{"value":"poll"}')


def test_indicator_refresh_mode_manual(grid_indicator_page):
    grid_indicator_page.prop_refresh_mode.select_option(label='手动')
    expect(grid_indicator_page.prop_refresh_mode).to_have_value('{"value":"manual"}')


def test_indicator_refresh_mode_push(grid_indicator_page):
    grid_indicator_page.prop_refresh_mode.select_option(label='手动')
    grid_indicator_page.prop_refresh_mode.select_option(label='推送')
    expect(grid_indicator_page.prop_refresh_mode).to_have_value('{"value":"push"}')


# ==================== 出错时 ====================

def test_indicator_error_fallback_show_last(grid_indicator_page):
    grid_indicator_page.prop_error_fallback.select_option(label='显示上次')
    expect(grid_indicator_page.prop_error_fallback).to_have_value('{"value":"showLast"}')


def test_indicator_error_fallback_hide(grid_indicator_page):
    grid_indicator_page.prop_error_fallback.select_option(label='隐藏')
    expect(grid_indicator_page.prop_error_fallback).to_have_value('{"value":"hide"}')


def test_indicator_error_fallback_recover(grid_indicator_page):
    grid_indicator_page.prop_error_fallback.select_option(label='隐藏')
    grid_indicator_page.prop_error_fallback.select_option(label='显示空')
    expect(grid_indicator_page.prop_error_fallback).to_have_value('{"value":"showEmpty"}')


# ==================== 点击事件 ====================

def test_indicator_click_action_alert(grid_indicator_page):
    grid_indicator_page.prop_click_action.select_option(label='弹窗提示')
    expect(grid_indicator_page.prop_click_action).to_have_value('{"value":"alert"}')


def test_indicator_click_action_navigate(grid_indicator_page):
    grid_indicator_page.prop_click_action.select_option(label='跳转 URL')
    grid_indicator_page.prop_click_target.fill('https://example.com')
    expect(grid_indicator_page.prop_click_action).to_have_value('{"value":"navigate"}')
    expect(grid_indicator_page.prop_click_target).to_have_value('https://example.com')


def test_indicator_click_action_none(grid_indicator_page):
    grid_indicator_page.prop_click_action.select_option(label='弹窗提示')
    grid_indicator_page.prop_click_action.select_option(label='无')
    expect(grid_indicator_page.prop_click_action).to_have_value('{"value":""}')


# ==================== 阈值触发 ====================

def test_indicator_threshold_action_alert(grid_indicator_page):
    grid_indicator_page.prop_threshold_action.select_option(label='弹窗提示')
    grid_indicator_page.prop_threshold_target.fill('CPU超限')
    expect(grid_indicator_page.prop_threshold_action).to_have_value('{"value":"alert"}')
    expect(grid_indicator_page.prop_threshold_target).to_have_value('CPU超限')


def test_indicator_threshold_action_refresh(grid_indicator_page):
    grid_indicator_page.prop_threshold_action.select_option(label='刷新数据')
    expect(grid_indicator_page.prop_threshold_action).to_have_value('{"value":"refresh"}')


# ==================== 数据绑定 ====================

def test_indicator_data_binding(grid_indicator_page):
    grid_indicator_page.prop_data_source.fill('SAT-01')
    grid_indicator_page.prop_field_path.fill('cpu.usage')
    expect(grid_indicator_page.prop_data_source).to_have_value('SAT-01')
    expect(grid_indicator_page.prop_field_path).to_have_value('cpu.usage')


def test_indicator_data_binding_clear(grid_indicator_page):
    grid_indicator_page.prop_data_source.fill('SAT-01')
    grid_indicator_page.prop_field_path.fill('cpu.usage')
    grid_indicator_page.prop_data_source.fill('')
    grid_indicator_page.prop_field_path.fill('')
    expect(grid_indicator_page.prop_data_source).to_have_value('')
    expect(grid_indicator_page.prop_field_path).to_have_value('')


# ==================== 复制 / 删除 ====================

def test_indicator_duplicate(grid_indicator_page, assert_screenshot):
    canvas = grid_indicator_page.page.locator('#puck-canvas-root')
    grid_indicator_page.duplicate_button.dispatch_event('click')
    expect(grid_indicator_page.canvas_widgets()).to_have_count(2)
    expect(grid_indicator_page.prop_label).to_have_value('CPU 使用率')
    expect(grid_indicator_page.prop_unit).to_have_value('%')
    assert_screenshot(canvas, 'grid_indicator_duplicate.png')


def test_indicator_delete(grid_indicator_page, assert_screenshot):
    canvas = grid_indicator_page.page.locator('#puck-canvas-root')
    grid_indicator_page.delete_button.dispatch_event('click')
    expect(grid_indicator_page.page.get_by_title('布局列数')).to_be_visible()
    expect(grid_indicator_page.canvas_widgets()).to_have_count(0)
    assert_screenshot(canvas, 'grid_indicator_delete.png')


# ==================== 组合修改 ====================

def test_indicator_combined(grid_indicator_page):
    grid_indicator_page.prop_label.fill('母线电流')
    grid_indicator_page.prop_value.fill('88.5')
    grid_indicator_page.prop_unit.fill('A')
    grid_indicator_page.prop_warning_threshold.fill('70')
    grid_indicator_page.prop_danger_threshold.fill('90')
    expect(grid_indicator_page.prop_label).to_have_value('母线电流')
    expect(grid_indicator_page.prop_value).to_have_value('88.5')
    expect(grid_indicator_page.prop_unit).to_have_value('A')
    expect(grid_indicator_page.canvas_widgets().first).to_contain_text('母线电流')
    expect(grid_indicator_page.canvas_widgets().first).to_contain_text('A')