import allure
from playwright.sync_api import expect


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('拖拽仪表盘后画布出现组件，底部显示默认量程')
@allure.severity(allure.severity_level.BLOCKER)
def test_gauge_default(grid_gauge_page):
    # 画布断言
    expect(grid_gauge_page.canvas_widgets()).to_have_count(1)
    expect(grid_gauge_page.gauge_caption()).to_contain_text('Range')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('点击组件，右侧属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_select_shows_properties(grid_gauge_page):
    # 右侧断言
    expect(grid_gauge_page.prop_title).to_have_value('母线电压')
    expect(grid_gauge_page.prop_min).to_have_value('0')
    expect(grid_gauge_page.prop_max).to_have_value('100')
    expect(grid_gauge_page.prop_value).to_have_value('72.5')
    expect(grid_gauge_page.prop_unit).to_have_value('V')
    expect(grid_gauge_page.prop_thresholds).to_have_value('80,90')
    expect(grid_gauge_page.prop_size).to_have_value('240')
    expect(grid_gauge_page.prop_data_source).to_have_value('')
    expect(grid_gauge_page.prop_field_path).to_have_value('')
    # 画布断言
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('点击空白，右侧切回Page属性')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_click_blank_shows_page(grid_gauge_page):
    grid_gauge_page.click_canvas_blank()
    expect(grid_gauge_page.page.get_by_title('布局列数')).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('修改标题为"供电电压"')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_modify_title(grid_gauge_page):
    grid_gauge_page.prop_title.fill('供电电压')
    # 右侧断言
    expect(grid_gauge_page.prop_title).to_have_value('供电电压')
    # 画布断言（尺寸不变）
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('清空标题')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_clear_title(grid_gauge_page):
    grid_gauge_page.prop_title.fill('')
    # 右侧断言
    expect(grid_gauge_page.prop_title).to_have_value('')
    # 画布断言
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('修改量程为 0-50')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_range_0_50(grid_gauge_page):
    grid_gauge_page.prop_min.fill('0')
    grid_gauge_page.prop_max.fill('50')
    # 右侧断言
    expect(grid_gauge_page.prop_min).to_have_value('0')
    expect(grid_gauge_page.prop_max).to_have_value('50')
    # 画布断言：caption 应反映新量程
    expect(grid_gauge_page.gauge_caption()).to_contain_text('0')
    expect(grid_gauge_page.gauge_caption()).to_contain_text('50')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('量程恢复 0-100')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_range_recover(grid_gauge_page):
    grid_gauge_page.prop_min.fill('0')
    grid_gauge_page.prop_max.fill('50')
    grid_gauge_page.prop_min.fill('0')
    grid_gauge_page.prop_max.fill('100')
    # 右侧断言
    expect(grid_gauge_page.prop_min).to_have_value('0')
    expect(grid_gauge_page.prop_max).to_have_value('100')
    # 画布断言
    expect(grid_gauge_page.gauge_caption()).to_contain_text('100')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('当前值改为 25')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_value_25(grid_gauge_page):
    grid_gauge_page.prop_value.fill('25')
    # 右侧断言
    expect(grid_gauge_page.prop_value).to_have_value('25')
    # 画布断言（尺寸不变）
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('当前值改为 0（最小边界）')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_value_zero(grid_gauge_page):
    grid_gauge_page.prop_value.fill('0')
    # 右侧断言
    expect(grid_gauge_page.prop_value).to_have_value('0')
    # 画布断言
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('当前值改为 100（最大边界）')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_value_max(grid_gauge_page):
    grid_gauge_page.prop_value.fill('100')
    # 右侧断言
    expect(grid_gauge_page.prop_value).to_have_value('100')
    # 画布断言
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('当前值恢复 72.5')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_value_recover(grid_gauge_page):
    grid_gauge_page.prop_value.fill('25')
    grid_gauge_page.prop_value.fill('72.5')
    # 右侧断言
    expect(grid_gauge_page.prop_value).to_have_value('72.5')
    # 画布断言
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('单位改为 kW')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_unit_kw(grid_gauge_page):
    grid_gauge_page.prop_unit.fill('kW')
    # 右侧断言
    expect(grid_gauge_page.prop_unit).to_have_value('kW')
    # 画布断言：caption 应包含 kW
    expect(grid_gauge_page.gauge_caption()).to_contain_text('kW')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('清空单位')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_unit_clear(grid_gauge_page):
    grid_gauge_page.prop_unit.fill('')
    # 右侧断言
    expect(grid_gauge_page.prop_unit).to_have_value('')
    # 画布断言：caption 不应再包含 V
    expect(grid_gauge_page.gauge_caption()).to_contain_text('Range: 0–100')
    expect(grid_gauge_page.gauge_caption()).not_to_contain_text('Range: 0–100 V')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('单位恢复 V')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_unit_recover(grid_gauge_page):
    grid_gauge_page.prop_unit.fill('kW')
    grid_gauge_page.prop_unit.fill('V')
    # 右侧断言
    expect(grid_gauge_page.prop_unit).to_have_value('V')
    # 画布断言
    expect(grid_gauge_page.gauge_caption()).to_contain_text('V')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('阈值改为 20,35')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_thresholds_20_35(grid_gauge_page):
    grid_gauge_page.prop_thresholds.fill('20,35')
    # 右侧断言
    expect(grid_gauge_page.prop_thresholds).to_have_value('20,35')
    # 画布断言（颜色分区变化不做像素校验，只确认尺寸不变）
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('阈值恢复 80,90')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_thresholds_recover(grid_gauge_page):
    grid_gauge_page.prop_thresholds.fill('20,35')
    grid_gauge_page.prop_thresholds.fill('80,90')
    # 右侧断言
    expect(grid_gauge_page.prop_thresholds).to_have_value('80,90')
    # 画布断言
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('清空阈值')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_thresholds_clear(grid_gauge_page):
    grid_gauge_page.prop_thresholds.fill('')
    # 右侧断言
    expect(grid_gauge_page.prop_thresholds).to_have_value('')
    # 画布断言
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('尺寸改为 400')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_size_400(grid_gauge_page):
    grid_gauge_page.prop_size.fill('400')
    # 右侧断言
    expect(grid_gauge_page.prop_size).to_have_value('400')
    # 画布断言：echarts 容器宽度应变为 400px
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '400px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('尺寸改为最小值 120')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_size_120(grid_gauge_page):
    grid_gauge_page.prop_size.fill('120')
    # 右侧断言
    expect(grid_gauge_page.prop_size).to_have_value('120')
    # 画布断言
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '120px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('尺寸恢复 240')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_size_recover(grid_gauge_page):
    grid_gauge_page.prop_size.fill('400')
    grid_gauge_page.prop_size.fill('240')
    # 右侧断言
    expect(grid_gauge_page.prop_size).to_have_value('240')
    # 画布断言
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('输入卫星 ID 和字段路径')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_data_binding(grid_gauge_page):
    grid_gauge_page.prop_data_source.fill('SAT-01')
    grid_gauge_page.prop_field_path.fill('bus.voltage')
    # 右侧断言
    expect(grid_gauge_page.prop_data_source).to_have_value('SAT-01')
    expect(grid_gauge_page.prop_field_path).to_have_value('bus.voltage')
    # 画布断言（绑定数据不改变尺寸）
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('清空卫星 ID 和字段路径')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_data_binding_clear(grid_gauge_page):
    grid_gauge_page.prop_data_source.fill('SAT-01')
    grid_gauge_page.prop_field_path.fill('bus.voltage')
    grid_gauge_page.prop_data_source.fill('')
    grid_gauge_page.prop_field_path.fill('')
    # 右侧断言
    expect(grid_gauge_page.prop_data_source).to_have_value('')
    expect(grid_gauge_page.prop_field_path).to_have_value('')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('复制仪表盘组件，画布出现两个相同组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_duplicate(grid_gauge_page):
    grid_gauge_page.duplicate_button.dispatch_event('click')
    # 数量断言
    expect(grid_gauge_page.canvas_widgets()).to_have_count(2)
    # 右侧断言（复制后新组件被选中，属性不变）
    expect(grid_gauge_page.prop_title).to_have_value('母线电压')
    expect(grid_gauge_page.prop_min).to_have_value('0')
    expect(grid_gauge_page.prop_max).to_have_value('100')
    expect(grid_gauge_page.prop_value).to_have_value('72.5')
    expect(grid_gauge_page.prop_unit).to_have_value('V')
    # 画布断言：两个组件都有 echarts
    expect(grid_gauge_page.gauge_chart(0)).to_have_css('width', '240px')
    expect(grid_gauge_page.gauge_chart(1)).to_have_css('width', '240px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('删除仪表盘组件，画布无组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_delete(grid_gauge_page):
    grid_gauge_page.delete_button.dispatch_event('click')
    # 右侧断言（删除后切回Page属性）
    expect(grid_gauge_page.page.get_by_title('布局列数')).to_be_visible()
    # 数量断言
    expect(grid_gauge_page.canvas_widgets()).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('栅格布局-仪表盘组件')
@allure.title('同时修改标题+量程+单位，验证联动')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_combined_title_range_unit(grid_gauge_page):
    grid_gauge_page.prop_title.fill('供电电压')
    grid_gauge_page.prop_min.fill('0')
    grid_gauge_page.prop_max.fill('50')
    grid_gauge_page.prop_unit.fill('kW')
    # 右侧断言
    expect(grid_gauge_page.prop_title).to_have_value('供电电压')
    expect(grid_gauge_page.prop_min).to_have_value('0')
    expect(grid_gauge_page.prop_max).to_have_value('50')
    expect(grid_gauge_page.prop_unit).to_have_value('kW')
    # 画布断言：caption 应反映改动，尺寸不变
    expect(grid_gauge_page.gauge_caption()).to_contain_text('50')
    expect(grid_gauge_page.gauge_caption()).to_contain_text('kW')
    expect(grid_gauge_page.gauge_chart()).to_have_css('width', '240px')
