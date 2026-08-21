from playwright.sync_api import expect


# ==================== 默认状态 ====================

def test_indicator_default(free_indicator_page, assert_screenshot):
    expect(free_indicator_page.canvas_widgets()).to_have_count(1)
    expect(free_indicator_page.canvas_widgets().first).to_contain_text('CPU 使用率')
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_default.png')


def test_indicator_select_shows_properties(free_indicator_page):
    free_indicator_page.click_widget()
    expect(free_indicator_page.prop_panel).to_be_visible()
    expect(free_indicator_page.prop_label).to_have_value('CPU 使用率')
    expect(free_indicator_page.prop_value).to_have_value('45.2')
    expect(free_indicator_page.prop_unit).to_have_value('%')
    expect(free_indicator_page.prop_warning_threshold).to_have_value('70')
    expect(free_indicator_page.prop_danger_threshold).to_have_value('90')
    expect(free_indicator_page.prop_icon).to_have_text('CPU')
    expect(free_indicator_page.prop_decimal).to_have_value('1')


def test_indicator_click_blank_hides_properties(free_indicator_page):
    free_indicator_page.click_widget()
    expect(free_indicator_page.prop_panel).to_be_visible()
    free_indicator_page.click_canvas_blank()
    expect(free_indicator_page.prop_panel).to_be_hidden()


# ==================== 标签 ====================

def test_indicator_modify_label(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_label.fill('母线电流')
    expect(free_indicator_page.prop_label).to_have_value('母线电流')
    expect(free_indicator_page.canvas_widgets().first).to_contain_text('母线电流')
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_label_current.png')


def test_indicator_clear_label(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_label.fill('')
    expect(free_indicator_page.prop_label).to_have_value('')
    expect(free_indicator_page.canvas_widgets().first).not_to_contain_text('CPU 使用率')
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_label_empty.png')


# ==================== 数值 ====================

def test_indicator_modify_value(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_value.fill('88.5')
    expect(free_indicator_page.prop_value).to_have_value('88.5')
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_value_88_5.png')


def test_indicator_value_zero(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_value.fill('0')
    expect(free_indicator_page.prop_value).to_have_value('0')
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_value_zero.png')


def test_indicator_value_recover(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_value.fill('88.5')
    free_indicator_page.prop_value.fill('45.2')
    expect(free_indicator_page.prop_value).to_have_value('45.2')
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_value_recover.png')


# ==================== 单位 ====================

def test_indicator_modify_unit(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_unit.fill('A')
    expect(free_indicator_page.prop_unit).to_have_value('A')
    expect(free_indicator_page.canvas_widgets().first).to_contain_text('A')
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_unit_a.png')


def test_indicator_unit_clear(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_unit.fill('')
    expect(free_indicator_page.prop_unit).to_have_value('')
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_unit_empty.png')


def test_indicator_unit_recover(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_unit.fill('A')
    free_indicator_page.prop_unit.fill('%')
    expect(free_indicator_page.prop_unit).to_have_value('%')
    expect(free_indicator_page.canvas_widgets().first).to_contain_text('%')
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_unit_recover.png')


# ==================== 警告阈值 / 危险阈值 ====================

def test_indicator_warning_threshold(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_warning_threshold.fill('70')
    free_indicator_page.prop_danger_threshold.fill('90')
    free_indicator_page.prop_value.fill('88.5')
    expect(free_indicator_page.prop_warning_threshold).to_have_value('70')
    expect(free_indicator_page.prop_danger_threshold).to_have_value('90')
    expect(free_indicator_page.prop_value).to_have_value('88.5')
    # 数值88.5 >= 警告70 且 < 危险90，卡片应变为警告态
    # 把截图目标从 canvas_widgets().first 改成整个 canvas
    canvas = free_indicator_page.page.locator('.react-grid-layout')
    assert_screenshot(canvas, 'free_indicator_warning_state.png')


def test_indicator_danger_threshold(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_warning_threshold.fill('70')
    free_indicator_page.prop_danger_threshold.fill('90')
    free_indicator_page.prop_value.fill('95')
    expect(free_indicator_page.prop_value).to_have_value('95')
    # 数值95 >= 危险90，卡片应变为危险态
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_danger_state.png')


def test_indicator_normal_state(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_warning_threshold.fill('70')
    free_indicator_page.prop_danger_threshold.fill('90')
    free_indicator_page.prop_value.fill('50')
    expect(free_indicator_page.prop_value).to_have_value('50')
    # 数值50 < 警告70，卡片应为正常态
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_normal_state.png')


# ==================== 图标 ====================

def test_indicator_icon_change(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_icon.click()
    free_indicator_page.page.get_by_role('option', name='温度').click()
    expect(free_indicator_page.prop_icon).to_have_text('温度')
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_icon_temp.png')


def test_indicator_icon_recover(free_indicator_page):
    free_indicator_page.click_widget()
    free_indicator_page.prop_icon.click()
    free_indicator_page.page.get_by_role('option', name='温度').click()
    free_indicator_page.prop_icon.click()
    free_indicator_page.page.get_by_role('option', name='CPU').click()
    expect(free_indicator_page.prop_icon).to_have_text('CPU')


# ==================== 小数位 ====================

def test_indicator_decimal_0(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_decimal.fill('0')
    expect(free_indicator_page.prop_decimal).to_have_value('0')
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_decimal_0.png')


def test_indicator_decimal_3(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_decimal.fill('3')
    expect(free_indicator_page.prop_decimal).to_have_value('3')
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_decimal_3.png')


# ==================== 显示状态 ====================

def test_indicator_hide_status(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.show_status_radio('否').check()
    expect(free_indicator_page.show_status_radio('否')).to_be_checked()
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_hide_status.png')


def test_indicator_show_status_recover(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.show_status_radio('否').check()
    free_indicator_page.show_status_radio('是').check()
    expect(free_indicator_page.show_status_radio('是')).to_be_checked()
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_show_status_recover.png')


# ==================== 数据绑定 ====================

def test_indicator_data_binding(free_indicator_page):
    free_indicator_page.click_widget()
    free_indicator_page.prop_data_source.fill('SAT-01')
    free_indicator_page.prop_field_path.fill('cpu.usage')
    expect(free_indicator_page.prop_data_source).to_have_value('SAT-01')
    expect(free_indicator_page.prop_field_path).to_have_value('cpu.usage')


# ==================== 阈值触发事件 ====================

def test_indicator_threshold_action_alert(free_indicator_page):
    free_indicator_page.click_widget()
    free_indicator_page.prop_threshold_action.click()
    free_indicator_page.page.get_by_role('option', name='弹窗提示').click()
    free_indicator_page.prop_threshold_target.fill('CPU超限')
    expect(free_indicator_page.prop_threshold_action).to_have_text('弹窗提示')
    expect(free_indicator_page.prop_threshold_target).to_have_value('CPU超限')


# ==================== 删除 ====================

def test_indicator_delete(free_indicator_page):
    expect(free_indicator_page.canvas_widgets()).to_have_count(1)
    free_indicator_page.delete_widget()
    expect(free_indicator_page.canvas_widgets()).to_have_count(0)


# ==================== 组合修改 ====================

def test_indicator_combined(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_label.fill('母线电流')
    free_indicator_page.prop_value.fill('88.5')
    free_indicator_page.prop_unit.fill('A')
    free_indicator_page.prop_warning_threshold.fill('70')
    free_indicator_page.prop_danger_threshold.fill('90')
    expect(free_indicator_page.prop_label).to_have_value('母线电流')
    expect(free_indicator_page.prop_value).to_have_value('88.5')
    expect(free_indicator_page.prop_unit).to_have_value('A')
    expect(free_indicator_page.canvas_widgets().first).to_contain_text('母线电流')
    expect(free_indicator_page.canvas_widgets().first).to_contain_text('A')
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_combined.png')