"""仪表盘组件。

⚠️ 只有【标题 / 单位 / 最小值 / 最大值 / 尺寸】在画布上看得出来，其余是摆设：
   当前值、阈值(警告,危险) —— 只影响 echarts 内部绘制，暂不测
等能连上真实数据再补。

标题画在 echarts canvas 里读不到文字，用像素指纹判断它变没变。
"""
import allure
from playwright.sync_api import expect

from common.canvas_pixels import assert_changed
from testcases.editor.common_style_cases import CommonStyleCases


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('添加仪表盘后画布出现组件，默认量程 0–100 V')
@allure.severity(allure.severity_level.BLOCKER)
def test_gauge_add(free_gauge_page):
    gp = free_gauge_page
    expect(gp.canvas_widgets()).to_have_count(1)
    # 画布断言：Range 那行
    r = gp.range_text()
    assert (r['min'], r['max'], r['unit']) == ('0', '100', 'V'), f'默认量程/单位不对：{r}'


@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('点击组件，属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_defaults(free_gauge_page):
    gp = free_gauge_page
    gp.click_widget()
    # 右侧断言
    expect(gp.prop_panel).to_be_visible()
    expect(gp.prop_min).to_have_value('0')
    expect(gp.prop_max).to_have_value('100')
    expect(gp.prop_unit).to_have_value('V')
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
@allure.title('修改标题，echarts 画布跟着重绘')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_title(free_gauge_page):
    gp = free_gauge_page
    gp.click_widget()
    from common.canvas_pixels import fingerprint
    before = fingerprint(gp.widget_canvas)

    gp.prop_title.fill('供电电压监控')
    after = fingerprint(gp.widget_canvas)
    # 右侧断言
    expect(gp.prop_title).to_have_value('供电电压监控')
    # 画布断言：标题画在 canvas 里，像素变了
    assert_changed(before, after, '改标题')


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
    # 画布断言
    assert gp.range_text()['unit'] == 'kW', f"Range 里单位没变：{gp.range_text()}"

    gp.prop_unit.fill('V')
    assert gp.range_text()['unit'] == 'V'


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

    gp.prop_min.fill('0')
    gp.prop_max.fill('100')
    r = gp.range_text()
    assert (r['min'], r['max']) == ('0', '100')


# ==================== 尺寸 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-仪表盘组件')
@allure.title('尺寸改为 400，echarts 那块变大；恢复 240')
@allure.severity(allure.severity_level.CRITICAL)
def test_gauge_size(free_gauge_page):
    gp = free_gauge_page
    gp.click_widget()
    w0, h0 = gp.chart_size()

    gp.prop_size.fill('400')
    # 右侧断言
    expect(gp.prop_size).to_have_value('400')
    # 画布断言：echarts 那块比原来大
    w1, h1 = gp.chart_size()
    assert w1 > w0 and h1 > h0, f'尺寸设 400，echarts 该变大：{w0}x{h0} -> {w1}x{h1}'

    gp.prop_size.fill('240')
    w2, h2 = gp.chart_size()
    assert (w2, h2) == (w0, h0), f'尺寸恢复 240，echarts 该回到原大小：{w2}x{h2} vs {w0}x{h0}'


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


# ==================== 通用样式（共用用例集）====================

class TestGaugeCommonStyle(CommonStyleCases):
    widget_fixture = 'free_gauge_page'
    story = '自由布局-仪表盘组件'
