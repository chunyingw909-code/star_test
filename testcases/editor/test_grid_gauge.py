from playwright.sync_api import expect


# ==================== 默认状态 ====================

# 拖拽仪表盘后画布出现组件，底部显示默认量程
def test_gauge_default(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    expect(grid_gauge_page.canvas_widgets()).to_have_count(1)
    expect(grid_gauge_page.gauge_caption()).to_contain_text('Range')
    assert_screenshot(canvas, 'grid_gauge_default.png')


# 点击组件，右侧属性面板显示默认值
def test_gauge_select_shows_properties(grid_gauge_page):
    expect(grid_gauge_page.prop_title).to_have_value('母线电压')
    expect(grid_gauge_page.prop_min).to_have_value('0')
    expect(grid_gauge_page.prop_max).to_have_value('100')
    expect(grid_gauge_page.prop_value).to_have_value('72.5')
    expect(grid_gauge_page.prop_unit).to_have_value('V')
    expect(grid_gauge_page.prop_thresholds).to_have_value('80,90')
    expect(grid_gauge_page.prop_size).to_have_value('240')
    expect(grid_gauge_page.prop_data_source).to_have_value('')
    expect(grid_gauge_page.prop_field_path).to_have_value('')
    # CSS断言
    chart = grid_gauge_page.gauge_chart()
    expect(chart).to_have_css('width', '240px')


# 点击空白，右侧切回Page属性
def test_gauge_click_blank_shows_page(grid_gauge_page):
    grid_gauge_page.click_canvas_blank()
    expect(grid_gauge_page.page.get_by_title('布局列数')).to_be_visible()


# ==================== 标题 ====================

# 修改标题为"供电电压"
def test_gauge_modify_title(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    grid_gauge_page.prop_title.fill('供电电压')
    # 右侧断言
    expect(grid_gauge_page.prop_title).to_have_value('供电电压')
    # CSS断言（尺寸不变）
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(canvas, 'grid_gauge_title_supply_voltage.png')


# 清空标题
def test_gauge_clear_title(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    grid_gauge_page.prop_title.fill('')
    # 右侧断言
    expect(grid_gauge_page.prop_title).to_have_value('')
    # CSS断言
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(canvas, 'grid_gauge_title_empty.png')


# ==================== 最小值 / 最大值 ====================

# 修改量程为 0-50
def test_gauge_range_0_50(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    grid_gauge_page.prop_min.fill('0')
    grid_gauge_page.prop_max.fill('50')
    # 右侧断言
    expect(grid_gauge_page.prop_min).to_have_value('0')
    expect(grid_gauge_page.prop_max).to_have_value('50')
    # CSS断言：caption 应反映新量程
    expect(grid_gauge_page.gauge_caption()).to_contain_text('0')
    expect(grid_gauge_page.gauge_caption()).to_contain_text('50')
    assert_screenshot(canvas, 'grid_gauge_range_0_50.png')


# 量程恢复 0-100
def test_gauge_range_recover(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    grid_gauge_page.prop_min.fill('0')
    grid_gauge_page.prop_max.fill('50')
    grid_gauge_page.prop_min.fill('0')
    grid_gauge_page.prop_max.fill('100')
    # 右侧断言
    expect(grid_gauge_page.prop_min).to_have_value('0')
    expect(grid_gauge_page.prop_max).to_have_value('100')
    # CSS断言
    expect(grid_gauge_page.gauge_caption()).to_contain_text('100')
    assert_screenshot(canvas, 'grid_gauge_range_recover.png')


# ==================== 当前值 ====================

# 当前值改为 25
def test_gauge_value_25(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    grid_gauge_page.prop_value.fill('25')
    # 右侧断言
    expect(grid_gauge_page.prop_value).to_have_value('25')
    # CSS断言（尺寸不变）
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(canvas, 'grid_gauge_value_25.png')


# 当前值改为 0（最小边界）
def test_gauge_value_zero(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    grid_gauge_page.prop_value.fill('0')
    # 右侧断言
    expect(grid_gauge_page.prop_value).to_have_value('0')
    # CSS断言
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(canvas, 'grid_gauge_value_zero.png')


# 当前值改为 100（最大边界）
def test_gauge_value_max(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    grid_gauge_page.prop_value.fill('100')
    # 右侧断言
    expect(grid_gauge_page.prop_value).to_have_value('100')
    # CSS断言
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(canvas, 'grid_gauge_value_max.png')


# 当前值恢复 72.5
def test_gauge_value_recover(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    grid_gauge_page.prop_value.fill('25')
    grid_gauge_page.prop_value.fill('72.5')
    # 右侧断言
    expect(grid_gauge_page.prop_value).to_have_value('72.5')
    # CSS断言
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(canvas, 'grid_gauge_value_recover.png')


# ==================== 单位 ====================

# 单位改为 kW
def test_gauge_unit_kw(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    grid_gauge_page.prop_unit.fill('kW')
    # 右侧断言
    expect(grid_gauge_page.prop_unit).to_have_value('kW')
    # CSS断言：caption 应包含 kW
    expect(grid_gauge_page.gauge_caption()).to_contain_text('kW')
    assert_screenshot(canvas, 'grid_gauge_unit_kw.png')


# 清空单位
def test_gauge_unit_clear(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    grid_gauge_page.prop_unit.fill('')
    # 右侧断言
    expect(grid_gauge_page.prop_unit).to_have_value('')
    # CSS断言：caption 不应再包含 V
    expect(grid_gauge_page.gauge_caption()).to_contain_text('Range: 0–100')
    expect(grid_gauge_page.gauge_caption()).not_to_contain_text('Range: 0–100 V')
    assert_screenshot(canvas, 'grid_gauge_unit_empty.png')


# 单位恢复 V
def test_gauge_unit_recover(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    grid_gauge_page.prop_unit.fill('kW')
    grid_gauge_page.prop_unit.fill('V')
    # 右侧断言
    expect(grid_gauge_page.prop_unit).to_have_value('V')
    # CSS断言
    expect(grid_gauge_page.gauge_caption()).to_contain_text('V')
    assert_screenshot(canvas, 'grid_gauge_unit_recover.png')


# ==================== 阈值 ====================

# 阈值改为 20,35
def test_gauge_thresholds_20_35(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    grid_gauge_page.prop_thresholds.fill('20,35')
    # 右侧断言
    expect(grid_gauge_page.prop_thresholds).to_have_value('20,35')
    # CSS断言（颜色分区变化由截图验证，尺寸不变）
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(canvas, 'grid_gauge_thresholds_20_35.png')


# 阈值恢复 80,90
def test_gauge_thresholds_recover(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    grid_gauge_page.prop_thresholds.fill('20,35')
    grid_gauge_page.prop_thresholds.fill('80,90')
    # 右侧断言
    expect(grid_gauge_page.prop_thresholds).to_have_value('80,90')
    # CSS断言
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(canvas, 'grid_gauge_thresholds_recover.png')


# 清空阈值
def test_gauge_thresholds_clear(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    grid_gauge_page.prop_thresholds.fill('')
    # 右侧断言
    expect(grid_gauge_page.prop_thresholds).to_have_value('')
    # CSS断言
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(canvas, 'grid_gauge_thresholds_empty.png')

# ==================== 尺寸 ====================

# 尺寸改为 400
def test_gauge_size_400(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    grid_gauge_page.prop_size.fill('400')
    # 右侧断言
    expect(grid_gauge_page.prop_size).to_have_value('400')
    # CSS断言：echarts 容器宽度应变为 400px
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '400px')
    assert_screenshot(canvas, 'grid_gauge_size_400.png')


# 尺寸改为最小值 120
def test_gauge_size_120(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    grid_gauge_page.prop_size.fill('120')
    # 右侧断言
    expect(grid_gauge_page.prop_size).to_have_value('120')
    # CSS断言
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '120px')
    assert_screenshot(canvas, 'grid_gauge_size_120.png')


# 尺寸恢复 240
def test_gauge_size_recover(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    grid_gauge_page.prop_size.fill('400')
    grid_gauge_page.prop_size.fill('240')
    # 右侧断言
    expect(grid_gauge_page.prop_size).to_have_value('240')
    # CSS断言
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(canvas, 'grid_gauge_size_recover.png')


# ==================== 数据绑定 ====================

# 输入卫星 ID 和字段路径
def test_gauge_data_binding(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    grid_gauge_page.prop_data_source.fill('SAT-01')
    grid_gauge_page.prop_field_path.fill('bus.voltage')
    # 右侧断言
    expect(grid_gauge_page.prop_data_source).to_have_value('SAT-01')
    expect(grid_gauge_page.prop_field_path).to_have_value('bus.voltage')
    # CSS断言（绑定数据不改变尺寸）
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(canvas, 'grid_gauge_data_binding.png')


# 清空卫星 ID 和字段路径
def test_gauge_data_binding_clear(grid_gauge_page):
    grid_gauge_page.prop_data_source.fill('SAT-01')
    grid_gauge_page.prop_field_path.fill('bus.voltage')
    grid_gauge_page.prop_data_source.fill('')
    grid_gauge_page.prop_field_path.fill('')
    # 右侧断言
    expect(grid_gauge_page.prop_data_source).to_have_value('')
    expect(grid_gauge_page.prop_field_path).to_have_value('')


# ==================== 刷新模式 ====================

# 切换刷新模式为轮询
def test_gauge_refresh_mode_poll(grid_gauge_page):
    grid_gauge_page.prop_refresh_mode.select_option(label='轮询')
    # 右侧断言
    expect(grid_gauge_page.prop_refresh_mode).to_have_value('{"value":"poll"}')


# 切换刷新模式为手动
def test_gauge_refresh_mode_manual(grid_gauge_page):
    grid_gauge_page.prop_refresh_mode.select_option(label='手动')
    # 右侧断言
    expect(grid_gauge_page.prop_refresh_mode).to_have_value('{"value":"manual"}')


# 切换刷新模式恢复推送
def test_gauge_refresh_mode_push(grid_gauge_page):
    grid_gauge_page.prop_refresh_mode.select_option(label='手动')
    grid_gauge_page.prop_refresh_mode.select_option(label='推送')
    # 右侧断言
    expect(grid_gauge_page.prop_refresh_mode).to_have_value('{"value":"push"}')


# ==================== 出错时 ====================

# 切换出错时为显示上次
def test_gauge_error_fallback_show_last(grid_gauge_page):
    grid_gauge_page.prop_error_fallback.select_option(label='显示上次')
    expect(grid_gauge_page.prop_error_fallback).to_have_value('{"value":"showLast"}')


# 切换出错时为隐藏
def test_gauge_error_fallback_hide(grid_gauge_page):
    grid_gauge_page.prop_error_fallback.select_option(label='隐藏')
    expect(grid_gauge_page.prop_error_fallback).to_have_value('{"value":"hide"}')


# 切换出错时恢复显示空
def test_gauge_error_fallback_recover(grid_gauge_page):
    grid_gauge_page.prop_error_fallback.select_option(label='隐藏')
    grid_gauge_page.prop_error_fallback.select_option(label='显示空')
    expect(grid_gauge_page.prop_error_fallback).to_have_value('{"value":"showEmpty"}')


# ==================== 点击事件 ====================

# 点击事件设为弹窗提示
def test_gauge_click_action_alert(grid_gauge_page):
    grid_gauge_page.prop_click_action.select_option(label='弹窗提示')
    expect(grid_gauge_page.prop_click_action).to_have_value('{"value":"alert"}')


# 点击事件设为跳转 URL 并填写目标
def test_gauge_click_action_navigate(grid_gauge_page):
    grid_gauge_page.prop_click_action.select_option(label='跳转 URL')
    grid_gauge_page.prop_click_target.fill('https://example.com')
    expect(grid_gauge_page.prop_click_action).to_have_value('{"value":"navigate"}')
    expect(grid_gauge_page.prop_click_target).to_have_value('https://example.com')


# 点击事件恢复无
def test_gauge_click_action_none(grid_gauge_page):
    grid_gauge_page.prop_click_action.select_option(label='弹窗提示')
    grid_gauge_page.prop_click_action.select_option(label='无')
    expect(grid_gauge_page.prop_click_action).to_have_value('{"value":""}')


# ==================== 阈值触发 ====================

# 阈值触发设为弹窗提示并填消息
def test_gauge_threshold_action_alert(grid_gauge_page):
    grid_gauge_page.prop_threshold_action.select_option(label='弹窗提示')
    grid_gauge_page.prop_threshold_target.fill('电压超限')
    expect(grid_gauge_page.prop_threshold_action).to_have_value('{"value":"alert"}')
    expect(grid_gauge_page.prop_threshold_target).to_have_value('电压超限')


# 阈值触发设为刷新数据
def test_gauge_threshold_action_refresh(grid_gauge_page):
    grid_gauge_page.prop_threshold_action.select_option(label='刷新数据')
    expect(grid_gauge_page.prop_threshold_action).to_have_value('{"value":"refresh"}')


# ==================== 复制 / 删除 ====================

# 复制仪表盘组件
def test_gauge_duplicate(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    grid_gauge_page.duplicate_button.dispatch_event('click')
    # 数量断言
    expect(grid_gauge_page.canvas_widgets()).to_have_count(2)
    # 右侧断言（复制后新组件被选中，属性不变）
    expect(grid_gauge_page.prop_title).to_have_value('母线电压')
    expect(grid_gauge_page.prop_min).to_have_value('0')
    expect(grid_gauge_page.prop_max).to_have_value('100')
    expect(grid_gauge_page.prop_value).to_have_value('72.5')
    expect(grid_gauge_page.prop_unit).to_have_value('V')
    # CSS断言：两个组件都有 echarts
    expect(grid_gauge_page.gauge_chart(0)).to_have_css('width', '240px')
    expect(grid_gauge_page.gauge_chart(1)).to_have_css('width', '240px')
    assert_screenshot(canvas, 'grid_gauge_duplicate.png')


# 删除仪表盘组件
def test_gauge_delete(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    grid_gauge_page.delete_button.dispatch_event('click')
    # 右侧断言（删除后切回Page属性）
    expect(grid_gauge_page.page.get_by_title('布局列数')).to_be_visible()
    # 数量断言
    expect(grid_gauge_page.canvas_widgets()).to_have_count(0)
    assert_screenshot(canvas, 'grid_gauge_delete.png')


# ==================== 组合修改 ====================

# 同时修改标题+量程+单位，验证联动
def test_gauge_combined_title_range_unit(grid_gauge_page, assert_screenshot):
    canvas = grid_gauge_page.page.locator('#puck-canvas-root')
    grid_gauge_page.prop_title.fill('供电电压')
    grid_gauge_page.prop_min.fill('0')
    grid_gauge_page.prop_max.fill('50')
    grid_gauge_page.prop_unit.fill('kW')
    # 右侧断言
    expect(grid_gauge_page.prop_title).to_have_value('供电电压')
    expect(grid_gauge_page.prop_min).to_have_value('0')
    expect(grid_gauge_page.prop_max).to_have_value('50')
    expect(grid_gauge_page.prop_unit).to_have_value('kW')
    # CSS断言：caption 应反映改动
    expect(grid_gauge_page.gauge_caption()).to_contain_text('50')
    expect(grid_gauge_page.gauge_caption()).to_contain_text('kW')
    # 尺寸不变
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')
    assert_screenshot(canvas, 'grid_gauge_combined_title_range_unit.png')