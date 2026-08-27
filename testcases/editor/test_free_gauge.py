import allure
from playwright.sync_api import expect


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('添加仪表盘后画布出现组件')
@allure.severity(allure.severity_level.BLOCKER)
def test_gauge_default(free_gauge_page, assert_screenshot):
    # 画布断言
    expect(free_gauge_page.canvas_widgets()).to_have_count(1)
    expect(free_gauge_page.gauge_caption()).to_contain_text('Range')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_default.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('点击组件，属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_select_shows_properties(free_gauge_page, assert_screenshot):
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
    # 画布断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_select_shows_properties.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('点空白区域，属性面板消失')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_click_blank_hides_properties(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    expect(free_gauge_page.prop_panel).to_be_visible()
    free_gauge_page.click_canvas_blank()
    expect(free_gauge_page.prop_panel).to_be_hidden()
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_click_blank_hides_properties.png')


# ==================== 标题 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('修改标题为"供电电压"')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_modify_title(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_title.fill('供电电压')
    # 右侧断言
    expect(free_gauge_page.prop_title).to_have_value('供电电压')
    # 画布断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_title_supply_voltage.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('清空标题')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_clear_title(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_title.fill('')
    # 右侧断言
    expect(free_gauge_page.prop_title).to_have_value('')
    # 画布断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_title_empty.png')


# ==================== 最小值 / 最大值 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('修改量程为 0-50')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_range_0_50(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_min.fill('0')
    free_gauge_page.prop_max.fill('50')
    # 右侧断言
    expect(free_gauge_page.prop_min).to_have_value('0')
    expect(free_gauge_page.prop_max).to_have_value('50')
    # 画布断言
    expect(free_gauge_page.gauge_caption()).to_contain_text('0')
    expect(free_gauge_page.gauge_caption()).to_contain_text('50')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_range_0_50.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('量程恢复 0-100')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_range_recover(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_min.fill('0')
    free_gauge_page.prop_max.fill('50')
    free_gauge_page.prop_min.fill('0')
    free_gauge_page.prop_max.fill('100')
    # 右侧断言
    expect(free_gauge_page.prop_min).to_have_value('0')
    expect(free_gauge_page.prop_max).to_have_value('100')
    # 画布断言
    expect(free_gauge_page.gauge_caption()).to_contain_text('100')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_range_recover.png')


# ==================== 当前值 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('当前值改为 25')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_value_25(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_value.fill('25')
    # 右侧断言
    expect(free_gauge_page.prop_value).to_have_value('25')
    # 画布断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_value_25.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('当前值改为 0（最小边界）')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_value_zero(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_value.fill('0')
    # 右侧断言
    expect(free_gauge_page.prop_value).to_have_value('0')
    # 画布断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_value_zero.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('当前值改为 100（最大边界）')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_value_max(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_value.fill('100')
    # 右侧断言
    expect(free_gauge_page.prop_value).to_have_value('100')
    # 画布断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_value_max.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('当前值恢复 72.5')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_value_recover(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_value.fill('25')
    free_gauge_page.prop_value.fill('72.5')
    # 右侧断言
    expect(free_gauge_page.prop_value).to_have_value('72.5')
    # 画布断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_value_recover.png')


# ==================== 单位 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('单位改为 kW')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_unit_kw(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_unit.fill('kW')
    # 右侧断言
    expect(free_gauge_page.prop_unit).to_have_value('kW')
    # 画布断言
    expect(free_gauge_page.gauge_caption()).to_contain_text('kW')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_unit_kw.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('清空单位')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_unit_clear(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_unit.fill('')
    # 右侧断言
    expect(free_gauge_page.prop_unit).to_have_value('')
    # 画布断言
    expect(free_gauge_page.gauge_caption()).to_contain_text('Range: 0–100')
    expect(free_gauge_page.gauge_caption()).not_to_contain_text('Range: 0–100 V')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_unit_empty.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('单位恢复 V')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_unit_recover(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_unit.fill('kW')
    free_gauge_page.prop_unit.fill('V')
    # 右侧断言
    expect(free_gauge_page.prop_unit).to_have_value('V')
    # 画布断言
    expect(free_gauge_page.gauge_caption()).to_contain_text('V')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_unit_recover.png')


# ==================== 阈值 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('阈值改为 20,35')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_thresholds_20_35(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_thresholds.fill('20,35')
    # 右侧断言
    expect(free_gauge_page.prop_thresholds).to_have_value('20,35')
    # 画布断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_thresholds_20_35.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('阈值恢复 80,90')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_thresholds_recover(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_thresholds.fill('20,35')
    free_gauge_page.prop_thresholds.fill('80,90')
    # 右侧断言
    expect(free_gauge_page.prop_thresholds).to_have_value('80,90')
    # 画布断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_thresholds_recover.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('清空阈值')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_thresholds_clear(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_thresholds.fill('')
    # 右侧断言
    expect(free_gauge_page.prop_thresholds).to_have_value('')
    # 画布断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_thresholds_empty.png')


# ==================== 尺寸 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('尺寸改为 400')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_size_400(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_size.fill('400')
    # 右侧断言
    expect(free_gauge_page.prop_size).to_have_value('400')
    # 画布断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '400px')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_size_400.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('尺寸改为最小值 120')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_size_120(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_size.fill('120')
    # 右侧断言
    expect(free_gauge_page.prop_size).to_have_value('120')
    # 画布断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '120px')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_size_120.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('尺寸恢复 240')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_size_recover(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_size.fill('400')
    free_gauge_page.prop_size.fill('240')
    # 右侧断言
    expect(free_gauge_page.prop_size).to_have_value('240')
    # 画布断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_size_recover.png')


# ==================== 数据绑定 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('输入卫星 ID 和字段路径')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_data_binding(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_data_source.fill('SAT-01')
    free_gauge_page.prop_field_path.fill('bus.voltage')
    # 右侧断言
    expect(free_gauge_page.prop_data_source).to_have_value('SAT-01')
    expect(free_gauge_page.prop_field_path).to_have_value('bus.voltage')
    # 画布断言
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_data_binding.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('清空卫星 ID 和字段路径')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_data_binding_clear(free_gauge_page, assert_screenshot):
    free_gauge_page.click_widget()
    free_gauge_page.prop_data_source.fill('SAT-01')
    free_gauge_page.prop_field_path.fill('bus.voltage')
    free_gauge_page.prop_data_source.fill('')
    free_gauge_page.prop_field_path.fill('')
    # 右侧断言
    expect(free_gauge_page.prop_data_source).to_have_value('')
    expect(free_gauge_page.prop_field_path).to_have_value('')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_data_binding_clear.png')


# ==================== 删除 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('删除仪表盘组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_delete(free_gauge_page):
    expect(free_gauge_page.canvas_widgets()).to_have_count(1)
    free_gauge_page.delete_widget()
    expect(free_gauge_page.canvas_widgets()).to_have_count(0)


# ==================== 组合修改 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('同时修改标题+量程+单位')
@allure.severity(allure.severity_level.CRITICAL)
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
    # 画布断言
    expect(free_gauge_page.gauge_caption()).to_contain_text('50')
    expect(free_gauge_page.gauge_caption()).to_contain_text('kW')
    expect(free_gauge_page.gauge_chart()).to_have_css('width', '240px')
    # 截图断言
    # 等待 ECharts 过渡动画播完，避免截到中间帧
    free_gauge_page.page.wait_for_timeout(1000)
    assert_screenshot(free_gauge_page.canvas_widgets().first, 'free_gauge_combined_title_range_unit.png')
