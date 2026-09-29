"""仪表盘组件。

所有修改都同时断言右侧属性和 ECharts gauge 正在渲染的明确状态；
不使用“像素前后不一样”作为通过条件。
"""
import allure
from playwright.sync_api import expect

from testcases.editor.common_style_cases import CommonStyleCases


DEFAULT_BANDS = [
    (0.8, '#2FC25B'),
    (0.9, '#F4D03F'),
    (1.0, '#E74C3C'),
]


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('添加仪表盘后画布出现组件，默认量程 0–100 V')
@allure.severity(allure.severity_level.BLOCKER)
def test_gauge_add(free_gauge_page):
    gp = free_gauge_page
    expect(gp.canvas_widgets()).to_have_count(1)
    # 用户看到的 Range 文案
    r = gp.range_text()
    assert (r['min'], r['max'], r['unit']) == ('0', '100', 'V'), f'默认量程/单位不对：{r}'
    # 仪表盘实际画的是默认标题、当前值、量程、单位和三段颜色
    assert gp.gauge_state() == {
        'title': '母线电压',
        'value': 72.5,
        'range': (0.0, 100.0),
        'detail': '{value} V',
        'bands': DEFAULT_BANDS,
    }


@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('点击组件，属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_defaults(free_gauge_page):
    gp = free_gauge_page
    gp.click_widget()
    # 右侧断言
    expect(gp.prop_panel).to_be_visible()
    expect(gp.prop_title).to_have_value('母线电压')
    expect(gp.prop_min).to_have_value('0')
    expect(gp.prop_max).to_have_value('100')
    expect(gp.prop_value).to_have_value('72.5')
    expect(gp.prop_unit).to_have_value('V')
    expect(gp.prop_thresholds).to_have_value('80,90')
    expect(gp.prop_size).to_have_value('240')


@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('点击画布空白区域，属性面板隐藏')
@allure.severity(allure.severity_level.NORMAL)
def test_gauge_panel_hides(free_gauge_page):
    gp = free_gauge_page
    gp.click_widget()
    expect(gp.prop_panel).to_be_visible()
    gp.click_canvas_blank()
    expect(gp.prop_panel).to_be_hidden()


# ==================== 标题 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('修改标题为“供电电压监控”，仪表盘显示这个标题')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_title(free_gauge_page):
    gp = free_gauge_page
    gp.click_widget()
    gp.prop_title.fill('供电电压监控')
    expect(gp.prop_title).to_have_value('供电电压监控')
    gp.wait_gauge('title', '供电电压监控')


# ==================== 单位 / 量程 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('修改单位为 kW，Range 那行同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_unit(free_gauge_page):
    gp = free_gauge_page
    gp.click_widget()
    gp.prop_unit.fill('kW')
    # 右侧断言
    expect(gp.prop_unit).to_have_value('kW')
    assert gp.range_text()['unit'] == 'kW', f"Range 里单位没变：{gp.range_text()}"
    gp.wait_gauge('detail', '{value} kW')

    gp.prop_unit.fill('V')
    assert gp.range_text()['unit'] == 'V'
    gp.wait_gauge('detail', '{value} V')


@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('修改量程为 10–50，Range 那行同步；恢复 0–100')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_range(free_gauge_page):
    gp = free_gauge_page
    gp.click_widget()
    gp.prop_min.fill('10')
    gp.prop_max.fill('50')
    # 右侧断言
    expect(gp.prop_min).to_have_value('10')
    expect(gp.prop_max).to_have_value('50')
    # 画布断言
    r = gp.range_text()
    assert (r['min'], r['max']) == ('10', '50'), f'Range 里量程没变：{r}'
    gp.wait_gauge('range', (10.0, 50.0))

    gp.prop_min.fill('0')
    gp.prop_max.fill('100')
    r = gp.range_text()
    assert (r['min'], r['max']) == ('0', '100')
    gp.wait_gauge('range', (0.0, 100.0))


@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('当前值改为 42，仪表盘显示值和指针数据都是 42')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_value(free_gauge_page):
    gp = free_gauge_page
    gp.click_widget()
    gp.prop_value.fill('42')

    expect(gp.prop_value).to_have_value('42')
    gp.wait_gauge('value', 42.0)


# ==================== 实时遥测 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('绑定母线电压实时遥测后，仪表盘显示真实的 20–40V 工程值')
@allure.severity(allure.severity_level.BLOCKER)
def test_gauge_realtime_telemetry(free_gauge_realtime):
    gp = free_gauge_realtime
    gp.click_widget()

    binding = gp.bind_realtime('母线电压（V） · power')

    assert binding['item'] == '母线电压（V） · power'
    value = gp.wait_live_value()
    state = gp.gauge_state()
    assert state['title'] == '母线电压'
    assert state['detail'] == '{value} V'
    assert 20 <= value <= 40, f'母线电压应是 20–40V 的实时工程值，实际 {value}V'
    assert value != 72.5, '绑定后不应继续显示仪表盘演示值 72.5V'


@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('警告/危险阈值改为 30,40，仪表盘色段边界变为 30%/40%')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_thresholds(free_gauge_page):
    gp = free_gauge_page
    gp.click_widget()
    gp.prop_thresholds.fill('30,40')

    expect(gp.prop_thresholds).to_have_value('30,40')
    gp.wait_gauge('bands', [
        (0.3, '#2FC25B'),
        (0.4, '#F4D03F'),
        (1.0, '#E74C3C'),
    ])


# ==================== 尺寸 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('尺寸改为 400，仪表盘精确变为 400×280；恢复 240×168')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_size(free_gauge_page):
    gp = free_gauge_page
    gp.click_widget()
    assert gp.chart_size() == (240, 168)

    gp.prop_size.fill('400')
    expect(gp.prop_size).to_have_value('400')
    assert gp.chart_size() == (400, 280)

    gp.prop_size.fill('240')
    assert gp.chart_size() == (240, 168)


# ==================== 删除 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('删除仪表盘组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_delete(free_gauge_page):
    gp = free_gauge_page
    expect(gp.canvas_widgets()).to_have_count(1)
    gp.delete_widget()
    expect(gp.canvas_widgets()).to_have_count(0)


# ==================== 组合修改 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('同时修改单位、量程、尺寸')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_combined(free_gauge_page):
    gp = free_gauge_page
    gp.click_widget()
    gp.prop_unit.fill('kW')
    gp.prop_min.fill('20')
    gp.prop_max.fill('80')
    gp.prop_size.fill('300')

    # 右侧断言
    expect(gp.prop_unit).to_have_value('kW')
    expect(gp.prop_min).to_have_value('20')
    expect(gp.prop_max).to_have_value('80')
    expect(gp.prop_size).to_have_value('300')
    # 画布断言
    r = gp.range_text()
    assert (r['min'], r['max'], r['unit']) == ('20', '80', 'kW'), f'Range 不对：{r}'
    gp.wait_gauge('range', (20.0, 80.0))
    gp.wait_gauge('detail', '{value} kW')
    assert gp.chart_size() == (300, 210)


# ==================== 通用样式（共用用例集）====================

class TestGaugeCommonStyle(CommonStyleCases):
    widget_fixture = 'free_gauge_page'
    story = '自由布局-仪表盘组件'
