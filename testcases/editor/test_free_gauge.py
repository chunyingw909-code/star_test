from playwright.sync_api import expect


# ==================== 默认状态 ====================

# 添加仪表盘后画布出现组件
def test_gauge_default(free_gauge_page, assert_screenshot):
    expect(free_gauge_page.canvas_widgets()).to_have_count(1)
    expect(free_gauge_page.gauge_caption()).to_contain_text('Range')
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_default.png')


# 点击组件，属性面板显示默认值
def test_gauge_select_shows_properties(free_gauge_page):
    free_gauge_page.click_widget()
    expect(free_gauge_page.prop_panel).to_be_visible()
    # 右侧断言
    expect(free_gauge_page.prop_title).to_have_value('母线电压')
    expect(free_gauge_page.prop_min).to_have_value('0')
    expect(free_gauge_page.prop_max).to_have_value('100')
    expect(free_gauge_page.prop_value).to_have_value('72.5')
    expect(free_gauge_page.prop_unit).to_have_value('V')
    expect(free_gauge_page.prop_thresholds).to_have_value('80,90')
    expect(free_gauge_page.prop_size).to_have_value('240')
    expect(free_gauge_page.prop_data_source).to_have_value('')
    expect(free_gauge_page.prop_field_path).to_have_value('')
    # CSS断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')


# 点空白区域，属性面板消失
def test_gauge_click_blank_hides_properties(free_gauge_page):
    free_gauge_page.click_widget()
    expect(free_gauge_page.prop_panel).to_be_visible()
    free_gauge_page.click_canvas_blank()
    expect(free_gauge_page.prop_panel).to_be_hidden()


# ==================== 标题 ====================

# 修改标题为"供电电压"
def test_gauge_modify_title(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_title.fill('供电电压')
    # 右侧断言
    expect(free_gauge_page.prop_title).to_have_value('供电电压')
    # CSS断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_title_supply_voltage.png')


# 清空标题
def test_gauge_clear_title(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_title.fill('')
    # 右侧断言
    expect(free_gauge_page.prop_title).to_have_value('')
    # CSS断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_title_empty.png')


# ==================== 最小值 / 最大值 ====================

# 修改量程为 0-50
def test_gauge_range_0_50(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_min.fill('0')
    free_gauge_page.prop_max.fill('50')
    # 右侧断言
    expect(free_gauge_page.prop_min).to_have_value('0')
    expect(free_gauge_page.prop_max).to_have_value('50')
    # CSS断言
    expect(free_gauge_page.gauge_caption()).to_contain_text('0')
    expect(free_gauge_page.gauge_caption()).to_contain_text('50')
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_range_0_50.png')


# 量程恢复 0-100
def test_gauge_range_recover(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_min.fill('0')
    free_gauge_page.prop_max.fill('50')
    free_gauge_page.prop_min.fill('0')
    free_gauge_page.prop_max.fill('100')
    # 右侧断言
    expect(free_gauge_page.prop_min).to_have_value('0')
    expect(free_gauge_page.prop_max).to_have_value('100')
    # CSS断言
    expect(free_gauge_page.gauge_caption()).to_contain_text('100')
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_range_recover.png')


# ==================== 当前值 ====================

# 当前值改为 25
def test_gauge_value_25(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_value.fill('25')
    # 右侧断言
    expect(free_gauge_page.prop_value).to_have_value('25')
    # CSS断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_value_25.png')


# 当前值改为 0
def test_gauge_value_zero(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_value.fill('0')
    # 右侧断言
    expect(free_gauge_page.prop_value).to_have_value('0')
    # CSS断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_value_zero.png')


# 当前值改为 100
def test_gauge_value_max(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_value.fill('100')
    # 右侧断言
    expect(free_gauge_page.prop_value).to_have_value('100')
    # CSS断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_value_max.png')


# 当前值恢复 72.5
def test_gauge_value_recover(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_value.fill('25')
    free_gauge_page.prop_value.fill('72.5')
    # 右侧断言
    expect(free_gauge_page.prop_value).to_have_value('72.5')
    # CSS断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_value_recover.png')


# ==================== 单位 ====================

# 单位改为 kW
def test_gauge_unit_kw(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_unit.fill('kW')
    # 右侧断言
    expect(free_gauge_page.prop_unit).to_have_value('kW')
    # CSS断言
    expect(free_gauge_page.gauge_caption()).to_contain_text('kW')
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_unit_kw.png')


# 清空单位
def test_gauge_unit_clear(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_unit.fill('')
    # 右侧断言
    expect(free_gauge_page.prop_unit).to_have_value('')
    # CSS断言
    expect(free_gauge_page.gauge_caption()).to_contain_text('Range: 0–100')
    expect(free_gauge_page.gauge_caption()).not_to_contain_text('Range: 0–100 V')
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_unit_empty.png')


# 单位恢复 V
def test_gauge_unit_recover(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_unit.fill('kW')
    free_gauge_page.prop_unit.fill('V')
    # 右侧断言
    expect(free_gauge_page.prop_unit).to_have_value('V')
    # CSS断言
    expect(free_gauge_page.gauge_caption()).to_contain_text('V')
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_unit_recover.png')


# ==================== 阈值 ====================

# 阈值改为 20,35
def test_gauge_thresholds_20_35(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_thresholds.fill('20,35')
    # 右侧断言
    expect(free_gauge_page.prop_thresholds).to_have_value('20,35')
    # CSS断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_thresholds_20_35.png')


# 阈值恢复 80,90
def test_gauge_thresholds_recover(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_thresholds.fill('20,35')
    free_gauge_page.prop_thresholds.fill('80,90')
    # 右侧断言
    expect(free_gauge_page.prop_thresholds).to_have_value('80,90')
    # CSS断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_thresholds_recover.png')


# 清空阈值
def test_gauge_thresholds_clear(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_thresholds.fill('')
    # 右侧断言
    expect(free_gauge_page.prop_thresholds).to_have_value('')
    # CSS断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_thresholds_empty.png')


# ==================== 尺寸 ====================

# 尺寸改为 400
def test_gauge_size_400(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_size.fill('400')
    # 右侧断言
    expect(free_gauge_page.prop_size).to_have_value('400')
    # CSS断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '400px')
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_size_400.png')


# 尺寸改为最小值 120
def test_gauge_size_120(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_size.fill('120')
    # 右侧断言
    expect(free_gauge_page.prop_size).to_have_value('120')
    # CSS断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '120px')
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_size_120.png')


# 尺寸恢复 240
def test_gauge_size_recover(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_size.fill('400')
    free_gauge_page.prop_size.fill('240')
    # 右侧断言
    expect(free_gauge_page.prop_size).to_have_value('240')
    # CSS断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_size_recover.png')


# ==================== 数据绑定 ====================

# 输入卫星 ID 和字段路径
def test_gauge_data_binding(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_data_source.fill('SAT-01')
    free_gauge_page.prop_field_path.fill('bus.voltage')
    # 右侧断言
    expect(free_gauge_page.prop_data_source).to_have_value('SAT-01')
    expect(free_gauge_page.prop_field_path).to_have_value('bus.voltage')
    # CSS断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_data_binding.png')


# 清空卫星 ID 和字段路径
def test_gauge_data_binding_clear(free_gauge_page):
    free_gauge_page.click_widget()
    free_gauge_page.prop_data_source.fill('SAT-01')
    free_gauge_page.prop_field_path.fill('bus.voltage')
    free_gauge_page.prop_data_source.fill('')
    free_gauge_page.prop_field_path.fill('')
    # 右侧断言
    expect(free_gauge_page.prop_data_source).to_have_value('')
    expect(free_gauge_page.prop_field_path).to_have_value('')


# ==================== 刷新模式（MUI Select） ====================

# 切换刷新模式为轮询
def test_gauge_refresh_mode_poll(free_gauge_page):
    free_gauge_page.click_widget()
    free_gauge_page.prop_refresh_mode.click()
    free_gauge_page.page.get_by_role('option', name='轮询').click()
    # 右侧断言
    expect(free_gauge_page.prop_refresh_mode).to_have_text('轮询')


# 切换刷新模式为手动
def test_gauge_refresh_mode_manual(free_gauge_page):
    free_gauge_page.click_widget()
    free_gauge_page.prop_refresh_mode.click()
    free_gauge_page.page.get_by_role('option', name='手动').click()
    # 右侧断言
    expect(free_gauge_page.prop_refresh_mode).to_have_text('手动')


# 切换刷新模式恢复推送
def test_gauge_refresh_mode_push(free_gauge_page):
    free_gauge_page.click_widget()
    free_gauge_page.prop_refresh_mode.click()
    free_gauge_page.page.get_by_role('option', name='手动').click()
    free_gauge_page.prop_refresh_mode.click()
    free_gauge_page.page.get_by_role('option', name='推送').click()
    # 右侧断言
    expect(free_gauge_page.prop_refresh_mode).to_have_text('推送')


# ==================== 出错时 ====================

# 切换出错时为显示上次
def test_gauge_error_fallback_show_last(free_gauge_page):
    free_gauge_page.click_widget()
    free_gauge_page.prop_error_fallback.click()
    free_gauge_page.page.get_by_role('option', name='显示上次').click()
    expect(free_gauge_page.prop_error_fallback).to_have_text('显示上次')


# 切换出错时为隐藏
def test_gauge_error_fallback_hide(free_gauge_page):
    free_gauge_page.click_widget()
    free_gauge_page.prop_error_fallback.click()
    free_gauge_page.page.get_by_role('option', name='隐藏').click()
    expect(free_gauge_page.prop_error_fallback).to_have_text('隐藏')


# 切换出错时恢复显示空
def test_gauge_error_fallback_recover(free_gauge_page):
    free_gauge_page.click_widget()
    free_gauge_page.prop_error_fallback.click()
    free_gauge_page.page.get_by_role('option', name='隐藏').click()
    free_gauge_page.prop_error_fallback.click()
    free_gauge_page.page.get_by_role('option', name='显示空').click()
    expect(free_gauge_page.prop_error_fallback).to_have_text('显示空')

# ==================== 点击事件 ====================

# 点击事件设为弹窗提示
def test_gauge_click_action_alert(free_gauge_page):
    free_gauge_page.click_widget()
    free_gauge_page.prop_click_action.click()
    free_gauge_page.page.get_by_role('option', name='弹窗提示').click()
    expect(free_gauge_page.prop_click_action).to_have_text('弹窗提示')


# 点击事件设为跳转 URL 并填写目标
def test_gauge_click_action_navigate(free_gauge_page):
    free_gauge_page.click_widget()
    free_gauge_page.prop_click_action.click()
    free_gauge_page.page.get_by_role('option', name='跳转 URL').click()
    free_gauge_page.prop_click_target.fill('https://example.com')
    expect(free_gauge_page.prop_click_action).to_have_text('跳转 URL')
    expect(free_gauge_page.prop_click_target).to_have_value('https://example.com')


# 点击事件恢复无
def test_gauge_click_action_none(free_gauge_page):
    free_gauge_page.click_widget()
    free_gauge_page.prop_click_action.click()
    free_gauge_page.page.get_by_role('option', name='弹窗提示').click()
    free_gauge_page.prop_click_action.click()
    free_gauge_page.page.get_by_role('option', name='无').click()
    expect(free_gauge_page.prop_click_action).not_to_have_text('弹窗提示')


# ==================== 阈值触发 ====================

# 阈值触发设为弹窗提示并填消息
def test_gauge_threshold_action_alert(free_gauge_page):
    free_gauge_page.click_widget()
    free_gauge_page.prop_threshold_action.click()
    free_gauge_page.page.get_by_role('option', name='弹窗提示').click()
    free_gauge_page.prop_threshold_target.fill('电压超限')
    expect(free_gauge_page.prop_threshold_action).to_have_text('弹窗提示')
    expect(free_gauge_page.prop_threshold_target).to_have_value('电压超限')


# 阈值触发设为刷新数据
def test_gauge_threshold_action_refresh(free_gauge_page):
    free_gauge_page.click_widget()
    free_gauge_page.prop_threshold_action.click()
    free_gauge_page.page.get_by_role('option', name='刷新数据').click()
    expect(free_gauge_page.prop_threshold_action).to_have_text('刷新数据')


# ==================== 删除 ====================

# 删除仪表盘
def test_gauge_delete(free_gauge_page):
    expect(free_gauge_page.canvas_widgets()).to_have_count(1)
    free_gauge_page.delete_widget()
    expect(free_gauge_page.canvas_widgets()).to_have_count(0)


# ==================== 组合修改 ====================

# 同时修改标题+量程+单位
def test_gauge_combined_title_range_unit(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_title.fill('供电电压')
    free_gauge_page.prop_min.fill('0')
    free_gauge_page.prop_max.fill('50')
    free_gauge_page.prop_unit.fill('kW')
    # 右侧断言
    expect(free_gauge_page.prop_title).to_have_value('供电电压')
    expect(free_gauge_page.prop_min).to_have_value('0')
    expect(free_gauge_page.prop_max).to_have_value('50')
    expect(free_gauge_page.prop_unit).to_have_value('kW')
    # CSS断言
    expect(free_gauge_page.gauge_caption()).to_contain_text('50')
    expect(free_gauge_page.gauge_caption()).to_contain_text('kW')
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_combined_title_range_unit.png')