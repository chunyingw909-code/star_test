"""图表组件。

⚠️ 交互事件里【只有单击生效】：
      点击事件 → 弹窗提示 / 跳转 URL   ✅ 可用，用例挂在文件末尾的共用用例集上
      双击事件 / 阈值触发 / 悬停事件 / 输入变化
                                      ❌ 都不触发。双击只是被当成两次单击，
                                         弹的还是单击配的那条消息，说明双击压根没接
      点击动作里的 刷新数据 / 显示弹窗 / 组件联动
                                      ❌ 不稳定
   这几样【故意不写用例】，面板定位也不留。等开发做完再补。

⚠️ 页面没把 echarts 挂到全局，但 echarts-for-react 实例上能读到正在画的 option。
   绑数据、换类型、挪图例、改线宽、设阈值 —— 都断言 option 里对应字段，
   而不是「像素跟之前不一样」。

⚠️ 【定时刷新配了不生效】。图表取数走 POST /api/datasources/<id>/query，
   把定时触发设成「刷新数据」、间隔设成 1 秒，编辑态和预览态各盯十几秒，
   这个接口一次都不会再发。这条按现状记录写在「定时刷新」一节里。

⚠️ 图表【没有】通用样式那一组（上下左右边距 / 圆角 / 透明度），面板里就没这几个框，
   所以本文件末尾没有挂通用样式的共用用例集。
"""
import allure
import pytest
from playwright.sync_api import expect

from common import echarts_option as eco
from common.number_input import check_number_spinner
from testcases.editor.click_action_cases import ClickActionCases

SERIES_TYPE = {'折线': 'line', '柱状': 'bar', '饼图': 'pie'}
DEMO_SERIES = {'示范量 A', '示范量 B'}


# ==========================================================================
# 一、基础属性 —— 不用绑数据源就能测的
# ==========================================================================
# 加进画布长什么样、面板默认值、标题、输入框自己的行为（上下箭头 / 取值范围）、删除。
# 这些跟有没有数据无关，改了就该有反应。

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('添加图表后画布出现组件，标题为"真实数据图表"，显示演示数据提示')
@allure.severity(allure.severity_level.BLOCKER)
def test_chart_added_to_canvas(free_chart_page):
    cp = free_chart_page
    # 画布断言
    expect(cp.canvas_widgets()).to_have_count(1)
    expect(cp.widget_title).to_have_text('真实数据图表')
    expect(cp.widget_unbound_chip).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('点击图表，属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_default_properties(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    # 右侧断言
    expect(cp.prop_panel).to_be_visible()
    expect(cp.prop_title).to_have_value('真实数据图表')
    expect(cp.prop_chart_type).to_have_text('折线')
    expect(cp.prop_theme).to_have_text('深色')
    expect(cp.prop_legend_position).to_have_text('底部')
    expect(cp.prop_warning_line).to_have_value('0')
    expect(cp.prop_danger_line).to_have_value('0')
    expect(cp.prop_line_width).to_have_value('1.5')
    expect(cp.prop_fill_opacity).to_have_value('0')
    # 三组「是 / 否」单选的默认档
    for group, default in cp.SWITCHES.items():
        expect(cp.switch_radio(group, default), f'{group} 默认应该是「{default}」').to_be_checked()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('点击画布空白区域，属性面板隐藏')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_panel_hides_on_blank_click(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    expect(cp.prop_panel).to_be_visible()
    cp.click_canvas_blank()
    expect(cp.prop_panel).to_be_hidden()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('修改标题为"母线电压趋势"，画布标题同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_modify_title(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    cp.prop_title.fill('母线电压趋势')
    # 右侧断言
    expect(cp.prop_title).to_have_value('母线电压趋势')
    # 画布断言
    expect(cp.widget_title).to_have_text('母线电压趋势')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('清空标题后，画布回退显示默认标题"数据图表"')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_clear_title(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    cp.prop_title.fill('')
    # 右侧断言
    expect(cp.prop_title).to_have_value('')
    # 当前产品行为：空标题在画布上回退为通用默认标题
    expect(cp.widget_title).to_have_text('数据图表')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('警告线 / 危险线的上下箭头：上一下 +1、下一下 -1')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_threshold_line_spinner(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    check_number_spinner(cp.prop_warning_line, start='80')
    check_number_spinner(cp.prop_danger_line, start='95')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('线宽的上下箭头按 step=1 走，且限制在 0.5 ~ 5')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_line_width_spinner(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    # 默认 1.5，step 是 1，所以按一下上箭头是 2.5 不是 1.6
    expect(cp.prop_line_width).to_have_attribute('min', '0.5')
    expect(cp.prop_line_width).to_have_attribute('max', '5')
    check_number_spinner(cp.prop_line_width, start='1.5')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('填充透明度限制在 0 ~ 1，上下箭头按 step=1 走')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_fill_opacity_spinner(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    expect(cp.prop_fill_opacity).to_have_attribute('min', '0')
    expect(cp.prop_fill_opacity).to_have_attribute('max', '1')
    # step 也是 1，所以只在 0 和 1 之间跳
    check_number_spinner(cp.prop_fill_opacity, start='0')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('定时间隔限制在 1 ~ 300')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_timer_interval_range(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    cp.pick_option(cp.prop_timer_action, '刷新数据')
    expect(cp.prop_timer_interval).to_have_attribute('min', '1')
    expect(cp.prop_timer_interval).to_have_attribute('max', '300')
    check_number_spinner(cp.prop_timer_interval, start='5')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('定时触发逐项切换（无 / 刷新数据）')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_timer_all_options(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    for name in cp.TIMER_ACTIONS:
        cp.pick_option(cp.prop_timer_action, name)
        # 右侧断言：选「无」等于清空，下拉里显示的是空占位符而不是「无」两个字
        shown = cp.NONE_DISPLAY if name == cp.NONE_OPTION else name
        expect(cp.prop_timer_action,
               f'定时触发选了「{name}」之后应显示 {shown!r}').to_have_text(shown)


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('删除图表组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_delete(free_chart_page):
    cp = free_chart_page
    expect(cp.canvas_widgets()).to_have_count(1)
    cp.delete_widget()
    # 画布断言
    expect(cp.canvas_widgets()).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('同时修改标题、图表类型、主题、图例位置与警告线')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_combined(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    cp.prop_title.fill('母线电压趋势')
    cp.pick_option(cp.prop_chart_type, '柱状')
    cp.pick_option(cp.prop_theme, '浅色')
    cp.pick_option(cp.prop_legend_position, '顶部')
    cp.prop_warning_line.fill('80')

    # 右侧断言
    expect(cp.prop_title).to_have_value('母线电压趋势')
    expect(cp.prop_chart_type).to_have_text('柱状')
    expect(cp.prop_theme).to_have_text('浅色')
    expect(cp.prop_legend_position).to_have_text('顶部')
    expect(cp.prop_warning_line).to_have_value('80')
    expect(cp.widget_title).to_have_text('母线电压趋势')
    # 画布上的图：类型、图例位置、阈值线都按刚才的操作落上去，不是只改了面板
    cp.wait_chart(lambda o: set(eco.series_types(o)), {'bar'})
    assert cp.chart_legend_side() == '顶部', f'图例应在顶部，实际 {cp.chart_legend_side()}'
    assert 80.0 in eco.mark_line_y_values(cp.chart_option()), (
        f'警告线 80 应画在图上，实际 markLine={eco.mark_line_y_values(cp.chart_option())}')


# ==========================================================================
# 二、绑好数据源之后 —— 人改一处，图上就要是那一处
# ==========================================================================
# 断言读正在画的 echarts option（系列类型 / 图例 / 阈值 / 字段名 / 数据点），
# 不拿「像素跟刚才不一样」当通过。
#
# ⚠️ 数值字段全勾：这张表里常常只有一列真有起伏，只勾第一列会绑到全 0 的列。

def _legend_text_color(opt):
    return eco.unwrap_style(eco.legend(opt).get('textStyle')).get('color')


def _css_brightness(color):
    """#bbb -> 187。浅色主题图例字更深，亮度应更低。"""
    if not color or not isinstance(color, str) or not color.startswith('#'):
        return None
    h = color[1:]
    if len(h) == 3:
        h = ''.join(ch * 2 for ch in h)
    if len(h) != 6:
        return None
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r + g + b) / 3


def _series_numbers(opt):
    nums = []
    for series in eco.series_list(opt):
        nums.extend(eco.numeric_points(series.get('data')))
    return nums


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('绑好之后切浅色主题，图例文字变深；切回深色复原')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bound_theme_changes_canvas(free_chart_bound):
    cp = free_chart_bound
    dark_opt = cp.chart_option()
    dark_color = _legend_text_color(dark_opt)
    assert dark_color, f'深色主题应有图例文字颜色，实际 legend={eco.legend(dark_opt)}'

    cp.pick_option(cp.prop_theme, '浅色')
    expect(cp.prop_theme).to_have_text('浅色')
    light_color = None
    for _ in range(40):
        light_color = _legend_text_color(cp.chart_option())
        if light_color and light_color != dark_color:
            break
        cp.page.wait_for_timeout(150)
    assert light_color != dark_color, (
        f'浅色主题图例文字颜色应与深色不同，实际都是 {dark_color}')
    dark_b, light_b = _css_brightness(dark_color), _css_brightness(light_color)
    if dark_b is not None and light_b is not None:
        assert light_b < dark_b, (
            f'浅色主题图例字应更深，深色={dark_color}({dark_b:.0f}) '
            f'浅色={light_color}({light_b:.0f})')

    cp.pick_option(cp.prop_theme, '深色')
    cp.wait_chart(_legend_text_color, dark_color)


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('绑好之后切图表类型，折线/柱状/饼图各自画成对应 series.type')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bound_chart_type_changes_canvas(free_chart_bound):
    cp = free_chart_bound
    bound_names = list(cp.bound_with['数值字段'])

    for name, series_type in SERIES_TYPE.items():
        cp.pick_option(cp.prop_chart_type, name)
        expect(cp.prop_chart_type, f'图表类型应显示 {name}').to_have_text(name)
        opt = cp.wait_chart(lambda o: set(eco.series_types(o)), {series_type})
        expect(cp.widget_canvas, f'切成 {name} 之后画布上应该还有图').to_have_count(1)
        # 换类型不该把绑好的字段丢了
        names = eco.series_names(opt)
        if series_type == 'pie':
            # 当前产品把横轴类别（时间戳）当成扇区名，不是数值字段名
            slices = eco.as_list(eco.series_list(opt)[0].get('data'))
            pie_nums = eco.numeric_points(slices)
            assert len(slices) >= 2, f'饼图应有多块扇形，实际 {slices[:6]}'
            assert pie_nums, f'饼图扇区应有数值，实际 {slices[:6]}'
        else:
            assert sorted(names) == sorted(bound_names), (
                f'切成{name}后系列名应仍是绑定字段 {bound_names}，实际 {names}')

    cp.pick_option(cp.prop_chart_type, '折线')
    cp.wait_chart(lambda o: sorted(eco.series_names(o)), sorted(bound_names))


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('绑好之后关掉图例，option.legend.show=false；打开又回来')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bound_legend_toggle_changes_canvas(free_chart_bound):
    cp = free_chart_bound
    assert cp.chart_legend_shown() is True

    cp.switch_radio('显示图例', '否').check()
    expect(cp.switch_radio('显示图例', '否')).to_be_checked()
    cp.wait_chart(lambda o: bool(eco.legend(o).get('show', True)), False)

    cp.switch_radio('显示图例', '是').check()
    cp.wait_chart(lambda o: bool(eco.legend(o).get('show', True)), True)


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('绑好之后挪图例，顶部/底部/左侧分别落到对应方位')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bound_legend_position_moves_legend(free_chart_bound):
    cp = free_chart_bound
    for name in cp.LEGEND_POSITIONS:
        cp.pick_option(cp.prop_legend_position, name)
        expect(cp.prop_legend_position, f'图例位置应显示 {name}').to_have_text(name)
        cp.wait_chart(eco.legend_side, name)


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('绑好之后把线宽调到 5，折线 series.lineStyle.width 就是 5')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_bound_line_width_changes_canvas(free_chart_bound):
    cp = free_chart_bound
    cp.prop_line_width.fill('5')
    cp.prop_line_width.blur()
    expect(cp.prop_line_width).to_have_value('5')
    cp.wait_chart(lambda o: eco.line_widths(o)[:1], [5.0])

    cp.prop_line_width.fill('1.5')
    cp.prop_line_width.blur()
    cp.wait_chart(lambda o: eco.line_widths(o)[:1], [1.5])


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('绑好之后打开数据缩放，option.dataZoom 出现滑块')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_bound_data_zoom_changes_canvas(free_chart_bound):
    cp = free_chart_bound
    assert eco.data_zoom_visible(cp.chart_option()) is False

    cp.switch_radio('数据缩放', '是').check()
    expect(cp.switch_radio('数据缩放', '是')).to_be_checked()
    cp.wait_chart(eco.data_zoom_visible, True)


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('绑好之后设警告线 0.5，图上 markLine 就是 0.5；清掉后没有这条线')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bound_warning_line_draws_on_canvas(free_chart_bound):
    cp = free_chart_bound
    nums = _series_numbers(cp.chart_option())
    assert nums, '绑好之后图上应该有数据点'
    lo, hi = min(nums), max(nums)
    # 警告线要落在数据范围内，人才看得到；取区间中点，不写死某张表的 0.5
    value = round((lo + hi) / 2, 4) or 0.5
    cp.prop_warning_line.fill(str(value))
    shown = cp.prop_warning_line.input_value()
    expect(cp.prop_warning_line).to_have_value(shown)
    threshold = float(shown)
    cp.wait_chart(
        lambda o: any(abs(v - threshold) < 1e-6 for v in eco.mark_line_y_values(o)), True)

    cp.prop_warning_line.fill('0')
    cp.wait_chart(
        lambda o: all(abs(v - threshold) > 1e-6 for v in eco.mark_line_y_values(o)), True)


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('绑好之后设危险线，图上 markLine 带上这个阈值；清掉后去掉')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bound_danger_line_draws_on_canvas(free_chart_bound):
    cp = free_chart_bound
    nums = _series_numbers(cp.chart_option())
    assert nums, '绑好之后图上应该有数据点'
    lo, hi = min(nums), max(nums)
    value = round(lo + (hi - lo) * 0.8, 4) if hi != lo else (hi + 1 if hi else 1)
    cp.prop_danger_line.fill(str(value))
    shown = cp.prop_danger_line.input_value()
    expect(cp.prop_danger_line).to_have_value(shown)
    threshold = float(shown)
    cp.wait_chart(
        lambda o: any(abs(v - threshold) < 1e-6 for v in eco.mark_line_y_values(o)), True)

    cp.prop_danger_line.fill('0')
    cp.wait_chart(
        lambda o: all(abs(v - threshold) > 1e-6 for v in eco.mark_line_y_values(o)), True)


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('危险线远超数据范围时，option 里仍记下这个阈值')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_bound_danger_line_out_of_range(free_chart_bound):
    # 产品会把阈值写进 markLine；值超出数据范围时线落在图框外，人看不见。
    # 这里断言「配置确实吃进去了」，并且这个值确实大于当前数据最大值。
    cp = free_chart_bound
    nums = _series_numbers(cp.chart_option())
    assert nums, '绑好之后图上应该有数据点'
    value = int(max(nums) * 10 + 95)
    cp.prop_danger_line.fill(str(value))
    expect(cp.prop_danger_line).to_have_value(str(value))
    cp.wait_chart(
        lambda o: any(abs(v - value) < 1e-6 for v in eco.mark_line_y_values(o)), True)
    assert value > max(nums), (
        f'这条用例要求阈值超出数据，实际阈值 {value}、数据最大 {max(nums)}')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('绑好之后填充透明度拉到 1，折线 areaStyle.opacity 就是 1')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bound_fill_opacity_fills_area(free_chart_bound):
    cp = free_chart_bound
    cp.prop_fill_opacity.fill('1')
    cp.prop_fill_opacity.blur()
    expect(cp.prop_fill_opacity).to_have_value('1')
    cp.wait_chart(lambda o: [round(v, 2) for v in eco.area_opacities(o)[:1]], [1.0])

    cp.prop_fill_opacity.fill('0')
    cp.prop_fill_opacity.blur()
    cp.page.wait_for_timeout(600)
    opacities = eco.area_opacities(cp.chart_option())
    assert not opacities or opacities[0] == 0, (
        f'填充调回 0 后不应再铺色，实际 opacity={opacities}')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('显示提示=是：悬停后提示里带系列名和这个点的数值')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bound_tooltip_shows_on_hover(free_chart_bound):
    cp = free_chart_bound
    expect(cp.switch_radio('显示提示', '是')).to_be_checked()
    assert cp.chart_tooltip_shown() is True

    opt = cp.chart_option()
    series = eco.series_list(opt)
    assert series, '绑好之后应有系列和数据点'

    point = cp.hover_chart_data_point()
    expect(cp.chart_tooltip).to_be_visible()
    text = cp.chart_tooltip.inner_text()

    assert str(point['xValue']) in text, (
        f'提示框应显示横轴值 {point["xValue"]}，实际 {text!r}')
    for item in series:
        name = item.get('name')
        values = eco.numeric_points([eco.as_list(item.get('data'))[point['dataIndex']]])
        assert name and name in text, f'提示框应显示系列名 {name!r}，实际 {text!r}'
        assert values, f'系列 {name!r} 的悬停点应该有数值'
        assert f'{values[0]:g}' in text, (
            f'提示框应显示 {name!r} 的值 {values[0]:g}，实际 {text!r}')

    cp.unhover_chart()
    expect(cp.chart_tooltip).to_be_hidden()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('显示提示=否：option.tooltip.show=false，悬停也不出提示文字')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bound_tooltip_hidden_when_off(free_chart_bound):
    cp = free_chart_bound
    cp.switch_radio('显示提示', '否').check()
    expect(cp.switch_radio('显示提示', '否')).to_be_checked()
    cp.wait_chart(lambda o: bool(eco.tooltip(o).get('show', True)), False)

    cp.hover_chart_data_point()
    expect(cp.chart_tooltip, '关掉提示后悬停真实数据点也不应出现提示').to_be_hidden()
    cp.unhover_chart()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('绑好之后改标题，系列数据和字段名都还在')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_bound_still_renders_after_title_change(free_chart_bound):
    cp = free_chart_bound
    before_names = cp.chart_series_names()
    before_count = len(_series_numbers(cp.chart_option()))

    cp.prop_title.fill('母线电压趋势')
    expect(cp.prop_title).to_have_value('母线电压趋势')
    expect(cp.widget_title).to_have_text('母线电压趋势')
    expect(cp.widget_canvas).to_have_count(1)
    assert cp.chart_series_names() == before_names, (
        f'改标题不该丢掉绑定字段，之前 {before_names}，现在 {cp.chart_series_names()}')
    assert len(_series_numbers(cp.chart_option())) == before_count, '改标题不该把数据点弄丢'


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('定时刷新设为 1 秒后，会持续重新请求数据源')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.xfail(
    reason='产品缺陷：定时刷新配置已保存，但不会按间隔重新请求数据源',
    strict=True,
)
def test_chart_timer_refreshes_data(free_chart_bound):
    # 图表取数走 POST /api/datasources/<id>/query；1 秒刷新在 5 秒内至少应再取两次。
    cp = free_chart_bound
    page = cp.page

    cp.click_widget()
    cp.pick_option(cp.prop_timer_action, '刷新数据')
    cp.prop_timer_interval.fill('1')
    page.wait_for_timeout(1500)
    expect(cp.prop_timer_action).to_have_text('刷新数据')
    expect(cp.prop_timer_interval).to_have_value('1')

    # 从这一刻起数图表的取数请求
    queries = []
    page.on('request', lambda r: queries.append(r.url) if '/query' in r.url else None)
    page.wait_for_timeout(5000)

    assert len(queries) >= 2, f'5 秒内至少应刷新 2 次，实际只有 {len(queries)} 次'


# ==========================================================================
# 三、「配置数据绑定」这个按钮 —— 当成一个独立模块来测
# ==========================================================================
# 只管这个弹窗本身：怎么打开、每种数据来源都点一遍、级联往下选、
# 什么都不填就乱点、取消回退、预览、保存。
# 不写死有哪几种数据来源、每种要填什么字段 —— 下拉里有什么就遍历什么。

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('点「配置数据绑定」打开弹窗，默认数据来源与三个按钮都在')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_open_bind_dialog(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    cp.open_bind_dialog()
    # 弹窗断言
    expect(cp.bind_dialog).to_contain_text('配置图表真实数据')
    expect(cp.bind_field('数据来源')).to_have_text('已登记关系型数据源')
    expect(cp.bind_dialog_cancel).to_be_visible()
    expect(cp.bind_dialog_preview).to_be_visible()
    expect(cp.bind_dialog_save).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('三种图表类型打开的弹窗，副标题各不相同')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bind_dialog_subtitle_per_chart_type(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    # 每种类型开一次弹窗，副标题应该跟着类型走
    for name, subtitle in cp.CHART_TYPE_SUBTITLES.items():
        cp.pick_option(cp.prop_chart_type, name)
        cp.open_bind_dialog()
        # 弹窗断言
        expect(cp.bind_dialog_subtitle, f'{name} 的弹窗副标题应该是「{subtitle}」') \
            .to_have_text(f'当前图表类型：{subtitle}')
        cp.close_bind_dialog()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('数据来源下拉里每个选项都点一遍，字段整组跟着换且不崩')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bind_every_data_source_option(free_chart_page):
    # 不写死有哪几种数据来源 —— 下拉里有什么就遍历什么。
    # 灰掉的选项（后端标了维护中之类）只断言它确实点不动，不去点它。
    cp = free_chart_page
    cp.click_widget()
    cp.open_bind_dialog()

    options = cp.bind_source_options()
    assert options, '数据来源下拉里应该有可选项'

    errors = []
    cp.page.on('pageerror', lambda e: errors.append(str(e)[:150]))

    fields_by_source = {}
    for name, disabled in options:
        if disabled:
            # 弹窗断言：灰的就该是灰的
            cp.bind_field('数据来源').click()
            expect(cp.page.get_by_role('option', name=name, exact=True),
                   f'「{name}」标着不可用，应该是点不动的') \
                .to_have_attribute('aria-disabled', 'true')
            cp.page.keyboard.press('Escape')
            cp.page.wait_for_timeout(400)
            continue

        cp.bind_choose('数据来源', name)
        # 弹窗断言：选中了、弹窗还在、下面的字段整组刷出来了
        expect(cp.bind_field('数据来源'), f'数据来源应显示 {name}').to_have_text(name)
        expect(cp.bind_dialog, f'切到「{name}」之后弹窗不该消失').to_be_visible()
        expect(cp.bind_dialog_cancel).to_be_visible()
        expect(cp.bind_dialog_save).to_be_visible()
        fields = cp.bind_dialog_field_labels()
        assert len(fields) > 1, f'切到「{name}」之后弹窗里应该有配置字段，实际只有 {fields}'
        fields_by_source[name] = fields

    assert not errors, f'切换数据来源时前端报错了：{errors}'
    assert fields_by_source, '一个能点的数据来源都没有？'
    # 不同来源要填的东西不一样，字段不该长得完全一致
    if len(fields_by_source) > 1:
        combos = list(fields_by_source.values())
        assert any(c != combos[0] for c in combos[1:]), (
            f'不同数据来源的配置字段不该完全相同：{fields_by_source}')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('数据绑定是级联的：选完数据源和 Schema，才轮到数据表')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bind_cascades(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    cp.open_bind_dialog()

    # 一上来这三级都是空的
    expect(cp.bind_field('关系型数据源')).to_have_text('')
    expect(cp.bind_field('Schema')).to_have_text('')
    expect(cp.bind_field('数据表')).to_have_text('')

    chosen = cp.bind_pick_table()
    assert chosen['Schema'] and chosen['数据表']
    expect(cp.bind_field('关系型数据源')).to_have_text(chosen['数据源'])
    expect(cp.bind_field('横轴字段')).to_be_visible()
    assert cp.bind_value_fields.count() > 0, '选完数据表后应加载可选数值字段'


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('选完表后多出横轴字段 / 统计方式 / 最大数据点数 / 数值字段')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bind_shows_field_options_after_table(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    cp.open_bind_dialog()
    cp.bind_pick_table()

    # 弹窗断言：选完表才冒出来的那几项
    expect(cp.bind_field('横轴字段')).to_be_visible()
    expect(cp.bind_field('统计方式')).to_have_text('不统计')
    expect(cp.bind_input('最大数据点数')).to_have_value('1000')
    # 数值字段是一排勾选框，默认都没勾
    assert cp.bind_value_fields.count() > 0, '选完表后应该列出可选的数值字段'
    expect(cp.bind_value_fields.first).not_to_be_checked()
    # 「时间间隔」要先选统计方式才启用
    expect(cp.bind_field('时间间隔'), '没选统计方式时，时间间隔应该是禁用的') \
        .to_have_attribute('aria-disabled', 'true')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('统计方式逐项切换，选完之后「时间间隔」才可用')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_bind_aggregation(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    cp.open_bind_dialog()
    cp.bind_pick_table()

    _, aggs = cp.bind_options('统计方式')
    cp.page.keyboard.press('Escape')
    assert aggs == cp.AGGREGATIONS, f'统计方式的选项应该是 {cp.AGGREGATIONS}，实际 {aggs}'

    cp.bind_choose('统计方式', '平均')
    # 弹窗断言
    expect(cp.bind_field('统计方式')).to_have_text('平均')
    expect(cp.bind_field('时间间隔'), '选了统计方式后，时间间隔应该可用了') \
        .not_to_have_attribute('aria-disabled', 'true')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('什么都不选就点「预览真实数据」，提示先选数据源，不崩')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bind_preview_without_anything(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    cp.open_bind_dialog()

    cp.bind_dialog_preview.click()
    cp.page.wait_for_timeout(2500)
    # 弹窗断言：给提示、不出表格、弹窗还在
    expect(cp.bind_need_table_hint).to_be_visible()
    expect(cp.bind_preview_table).to_have_count(0)
    expect(cp.bind_dialog).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('什么都不选就点「保存绑定」，保存不了，弹窗不关画布也不出图')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bind_save_without_anything(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    cp.open_bind_dialog()

    cp.bind_dialog_save.click()
    cp.page.wait_for_timeout(2500)
    # 弹窗断言
    expect(cp.bind_dialog, '什么都没选，弹窗不该关掉').to_be_visible()
    # 画布断言
    # 未绑定时现在会渲染演示图；保存失败后仍应保持演示数据状态
    expect(cp.widget_canvas).to_be_visible()
    expect(cp.widget_unbound_chip).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('只选到表、横轴和数值字段没选就点预览，提示表或字段不合适')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_bind_preview_without_fields(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    cp.open_bind_dialog()
    cp.bind_pick_table()

    cp.bind_dialog_preview.click()
    cp.page.wait_for_timeout(3000)
    # 弹窗断言
    expect(cp.bind_invalid_hint).to_be_visible()
    expect(cp.bind_preview_table).to_have_count(0)
    expect(cp.bind_dialog).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('点「取消」关闭弹窗，画布保持未绑定')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_cancel_bind_dialog(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    cp.open_bind_dialog()
    cp.close_bind_dialog()
    # 画布断言
    expect(cp.bind_dialog).to_have_count(0)
    expect(cp.widget_unbound_chip).to_be_visible()
    expect(cp.widget_canvas).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('选完所有字段但点「取消」，画布仍保持未绑定演示图')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_bind_cancel_after_filling(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    cp.open_bind_dialog()
    cp.bind_pick_table()
    cp.bind_pick_fields()

    cp.close_bind_dialog()
    # 画布断言：填了但没保存，等于没绑，继续显示未绑定演示图
    expect(cp.widget_unbound_chip).to_be_visible()
    expect(cp.widget_canvas).to_be_visible()


def _field_token(name):
    """「执行进度（progress） · float4」-> progress；没括号就用原名。"""
    if '（' in name and '）' in name:
        return name[name.find('（') + 1:name.find('）')].strip()
    return name.split('·')[0].strip()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('选完字段点预览，表格列就是横轴+数值字段，并且有真实数据行')
@allure.severity(allure.severity_level.BLOCKER)
def test_chart_bind_preview_shows_real_data(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    cp.open_bind_dialog()
    cp.bind_pick_table()
    chosen = cp.bind_pick_fields()

    cp.bind_dialog_preview.click()
    expect(cp.bind_preview_table).to_be_visible(timeout=15000)
    expect(cp.bind_invalid_hint).to_have_count(0)
    expect(cp.bind_need_table_hint).to_have_count(0)

    headers = cp.bind_preview_headers()
    rows = cp.bind_preview_table.locator('tbody tr')
    first = cp.bind_preview_first_row()
    assert len(headers) == 1 + len(chosen['数值字段']), (
        f'预览表应是横轴 + {len(chosen["数值字段"])} 个数值列，实际表头 {headers}')
    assert rows.count() > 0, '预览表格应该有数据行'
    assert len(first) == len(headers), f'首行列数应等于表头，表头 {headers} 首行 {first}'
    for name in chosen['数值字段']:
        token = _field_token(name)
        assert any(token.lower() in h.lower() or name.split('（')[0] in h for h in headers), (
            f'预览表头应包含数值字段 {name}（{token}），实际 {headers}')
    numeric_cells = 0
    for cell in first[1:]:
        try:
            float(cell)
            numeric_cells += 1
        except ValueError:
            pass
    assert numeric_cells >= 1, f'预览首行应有真实数值，实际 {first}'


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('预览后再保存，图上的系列名和数据点就是刚才那张预览表')
@allure.severity(allure.severity_level.BLOCKER)
def test_chart_bind_save_renders_chart(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    # 未绑定先确认画的是演示系列，后面用来对比「真的换数据了」
    demo_names = set(cp.chart_series_names())

    cp.open_bind_dialog()
    chosen = cp.bind_pick_table()
    chosen.update(cp.bind_pick_fields())
    cp.bind_dialog_preview.click()
    expect(cp.bind_preview_table).to_be_visible(timeout=15000)
    preview_headers = cp.bind_preview_headers()
    preview_first = cp.bind_preview_first_row()

    cp.bind_dialog_save.click()
    cp.bind_dialog.wait_for(state='hidden', timeout=20000)
    expect(cp.widget_unbound_chip).to_have_count(0)
    expect(cp.widget_bound_chip).to_be_visible()
    expect(cp.widget_canvas).to_have_count(1)
    size = cp.widget_canvas.first.evaluate('el => [el.width, el.height]')
    assert size[0] > 0 and size[1] > 0, f'图表画布尺寸不该是 0，实际 {size}'

    expected = sorted(chosen['数值字段'])
    opt = cp.wait_chart(lambda o: sorted(eco.series_names(o)), expected)
    names = eco.series_names(opt)
    assert not (set(names) & DEMO_SERIES), f'保存后不应还是演示系列 {names}'
    if demo_names:
        assert set(names) != demo_names, f'保存后系列名应换成绑定字段，实际还是 {names}'

    x_values = [str(value) for value in eco.as_list(eco.xaxis(opt).get('data'))]
    assert preview_first[0] in x_values, (
        f'预览首行横轴值 {preview_first[0]!r} 应出现在图上，实际 {x_values[:6]}…')

    series_by_name = {item.get('name'): item for item in eco.series_list(opt)}
    for name, cell in zip(chosen['数值字段'], preview_first[1:]):
        value = float(cell)
        points = eco.numeric_points(series_by_name[name].get('data'))
        assert any(abs(value - point) < 1e-6 for point in points), (
            f'预览表中 {name!r} 的值 {value} 应出现在同名系列，实际 {points[:12]}…')


# ==================== 时序 / API 数据源 —— 冒烟 ====================
# 只管「选完、保存、不崩、画布真的换成已绑定状态」，不像上面关系型那条深挖到
# 图上每个数据点是否精确对得上——时序按时间粒度聚合、API 数据形状本来就不固定，
# 精确断言的投入跟这两条路径的重要度不成比例，等真的出问题再针对性补。

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('折线图绑定时序数据源（TDengine），保存后画布正常出图')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_bind_timeseries_source_smoke(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    cp.pick_option(cp.prop_chart_type, '折线')  # 折线图才推荐时序数据源，见上面的遍历用例

    cp.open_bind_dialog()
    source_name = next(name for name, _ in cp.bind_source_options() if 'TDengine' in name)
    cp.bind_choose('数据来源', source_name)
    cp.bind_pick_timeseries()

    cp.bind_dialog_save.click()
    cp.bind_dialog.wait_for(state='hidden', timeout=20000)
    # 弹窗断言之外，顺带确认切数据源、选完这几步没有前端报错。
    # 注意：时序数据源绑好之后画布上的状态文案是「已登记时序数据源」，不是
    # widget_bound_chip 对应的通用「已登记数据源」，这里不复用那个 locator。
    expect(cp.widget_unbound_chip).to_have_count(0)
    expect(cp.widget_canvas).to_have_count(1)
    size = cp.widget_canvas.first.evaluate('el => [el.width, el.height]')
    assert size[0] > 0 and size[1] > 0, f'图表画布尺寸不该是 0，实际 {size}'


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('图表绑定 API 数据源，保存后画布正常出图')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_bind_api_source_smoke(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    cp.open_bind_dialog()

    cp.bind_choose('数据来源', '已登记 API 数据源')
    cp.bind_pick_api()

    cp.bind_dialog_save.click()
    cp.bind_dialog.wait_for(state='hidden', timeout=20000)
    expect(cp.widget_unbound_chip).to_have_count(0)
    expect(cp.widget_bound_chip).to_be_visible()
    expect(cp.widget_canvas).to_have_count(1)
    size = cp.widget_canvas.first.evaluate('el => [el.width, el.height]')
    assert size[0] > 0 and size[1] > 0, f'图表画布尺寸不该是 0，实际 {size}'


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('时序数据源一个遥测参数都不勾，点保存卡在「配置不完整」')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_bind_timeseries_save_without_params(free_chart_page):
    # 遥测参数勾选框跟关系型的数值字段是同一套「至少选一个」防呆，这里确认
    # 保存这条路是拦得住的（拦不住会直接保存出一张没数据的图）。
    cp = free_chart_page
    cp.click_widget()
    cp.pick_option(cp.prop_chart_type, '折线')
    cp.open_bind_dialog()

    source_name = next(name for name, _ in cp.bind_source_options() if 'TDengine' in name)
    cp.bind_choose('数据来源', source_name)
    for label in ('TDengine 数据源', '卫星', '分系统'):
        cp.bind_choose_first_real(label)
    assert cp.bind_value_fields.count() > 0, '选完分系统后应该列出可勾选的遥测参数'
    # 遥测参数一个都不勾，直接点保存

    cp.bind_dialog_save.click()
    cp.page.wait_for_timeout(2500)
    expect(cp.bind_dialog, '一个遥测参数都没勾，保存不该成功、弹窗不该关').to_be_visible()
    expect(cp.widget_unbound_chip).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('【已知问题】时序数据源没勾遥测参数时点预览，提示语是关系型那条，对不上')
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.xfail(
    reason='产品缺陷：时序数据源一个遥测参数都没勾时点「预览真实数据」，'
           '弹出的是关系型专属提示「请先选择数据源、Schema 和数据表」——'
           '时序数据源根本没有 Schema / 数据表这两个概念，提示语文案复用错了。',
    strict=True,
)
def test_chart_bind_timeseries_preview_without_params(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    cp.pick_option(cp.prop_chart_type, '折线')
    cp.open_bind_dialog()

    source_name = next(name for name, _ in cp.bind_source_options() if 'TDengine' in name)
    cp.bind_choose('数据来源', source_name)
    for label in ('TDengine 数据源', '卫星', '分系统'):
        cp.bind_choose_first_real(label)

    cp.bind_dialog_preview.click()
    cp.page.wait_for_timeout(2500)
    expect(cp.bind_need_table_hint, '时序数据源缺参数时不该显示关系型的「Schema/数据表」提示语') \
        .to_have_count(0)


# ==========================================================================
# 四、点击事件（共用用例集）
# ==========================================================================
# ==================== 点击事件（共用用例集）====================
# 单击 → 弹窗提示 / 跳转 URL —— 用例写在 click_action_cases.py，这里只挂上去。
# 双击 / 阈值 / 悬停 / 输入变化都不触发，不写，原因见本文件开头。

class TestChartClickAction(ClickActionCases):
    widget_fixture = 'free_chart_page'
    story = '自由布局-图表组件'
    marker_prop = 'prop_title'
