"""图表组件。

⚠️ 交互事件里【只有单击生效】：
      点击事件 → 弹窗提示 / 跳转 URL   ✅ 可用，用例挂在文件末尾的共用用例集上
      双击事件 / 阈值触发 / 悬停事件 / 输入变化
                                      ❌ 都不触发。双击只是被当成两次单击，
                                         弹的还是单击配的那条消息，说明双击压根没接
      点击动作里的 刷新数据 / 显示弹窗 / 组件联动
                                      ❌ 不稳定
   这几样【故意不写用例】，面板定位也不留。等开发做完再补。

⚠️ 图表【没绑数据源就不出图】，只显示标题 +「未绑定数据源」占位。绑定这条链路
   本文件是真跑通的（见「数据绑定」一节），绑完画布上会出现真正的 echarts 图，
   需要有图才能测的用例用 free_chart_bound 这个 fixture。

⚠️ 页面没把 echarts 挂到全局，读不到图表的 option，但【画布的像素读得到】。
   把画布切成九宫格取「像素指纹」，改属性前后一比，就能断言画布真的变了、
   而且变在对的区域（工具见 common/canvas_pixels.py，实测连采 4 次指纹一模一样）。
   主题、图表类型、显示图例、图例位置、线宽、数据缩放 都是这么断言的。
   警告线 / 危险线 / 填充透明度 / 提示框 也都是这么断言的（提示框要 hover）。

⚠️ 【定时刷新配了不生效】。图表取数走 POST /api/datasources/<id>/query，
   把定时触发设成「刷新数据」、间隔设成 1 秒，编辑态和预览态各盯十几秒，
   这个接口一次都不会再发。这条按现状记录写在「定时刷新」一节里。

⚠️ 图表【没有】通用样式那一组（上下左右边距 / 圆角 / 透明度），面板里就没这几个框，
   所以本文件末尾没有挂通用样式的共用用例集。
"""
import allure
from playwright.sync_api import expect

from common.canvas_pixels import assert_changed, assert_same, region_brightness
from common.number_input import check_number_spinner
from testcases.editor.click_action_cases import ClickActionCases


# ==========================================================================
# 一、基础属性 —— 不用绑数据源就能测的
# ==========================================================================
# 加进画布长什么样、面板默认值、标题、输入框自己的行为（上下箭头 / 取值范围）、删除。
# 这些跟有没有数据无关，改了就该有反应。

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('添加图表后画布出现组件，标题为"真实数据图表"，提示未绑定数据源')
@allure.severity(allure.severity_level.BLOCKER)
def test_chart_added_to_canvas(free_chart_page):
    cp = free_chart_page
    # 画布断言
    expect(cp.canvas_widgets()).to_have_count(1)
    expect(cp.widget_title).to_have_text('真实数据图表')
    expect(cp.widget_unbound_chip).to_be_visible()
    expect(cp.widget_unbound_tip).to_be_visible()


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
@allure.title('清空标题，画布标题也空掉')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_clear_title(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    cp.prop_title.fill('')
    # 右侧断言
    expect(cp.prop_title).to_have_value('')
    # 画布断言
    expect(cp.widget_title).to_have_text('')


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
        expect(cp.prop_timer_action, f'定时触发选了「{name}」之后应显示 {shown!r}')             .to_have_text(shown)


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
    # 画布断言：只有标题看得出来
    expect(cp.widget_title).to_have_text('母线电压趋势')


# ==========================================================================
# 二、绑好数据源之后 —— 改属性，画布上真看得出来
# ==========================================================================
# 图表画在 canvas 上，DOM 里读不出主题 / 图例位置这些，但画布的像素读得到。
# 把画布切成九宫格取指纹，改属性前后一比就知道变没变、变在哪块区域。
# 实测同一状态下连采 4 次指纹一模一样，不会飘。工具见 common/canvas_pixels.py。
#
# ⚠️ 绑定时数值字段要【全勾】，别只勾第一个：这张表三个数值字段里只有一个真有数据，
#    另外两个整列都是 0。只勾第一个的话图上是一条贴着底的直线，警告线 / 危险线 /
#    填充透明度改了都看不出来 —— 那不是功能坏了，是绑错了字段。见 bind_pick_fields。
#
# ⚠️ 阈值线（警告线 / 危险线）要设在数据的取值范围【之内】才画得出来。设成远超范围的
#    值，线落到图框外面，画布上自然看不见 —— 这是正常的，下面有一条用例把它固定住。
#
# ⚠️ 提示框（显示提示）是鼠标悬停才画出来的，静态画面上没有，要 hover 才测得到。

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('绑好之后切换主题，画布真的跟着变，切回来复原')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bound_theme_changes_canvas(free_chart_bound):
    cp = free_chart_bound
    # 不要再 click_widget：点一下图会重画，第一张指纹就成了首帧，对不上后面的稳定态
    dark = cp.canvas_fingerprint()

    cp.pick_option(cp.prop_theme, '浅色')
    light = cp.canvas_fingerprint()
    # 右侧断言
    expect(cp.prop_theme).to_have_text('浅色')
    # 画布断言
    assert_changed(dark, light, '主题切成浅色')

    cp.pick_option(cp.prop_theme, '深色')
    back = cp.canvas_fingerprint()
    # 画布断言：切回深色应该跟一开始一模一样
    assert_same(dark, back, '主题切回深色')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('绑好之后逐项切换图表类型，画布每种都不一样')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bound_chart_type_changes_canvas(free_chart_bound):
    cp = free_chart_bound
    # 不要再 click_widget：点一下图会重画，第一张指纹就成了首帧，对不上后面的稳定态

    prints = {}
    for name in cp.CHART_TYPES:
        cp.pick_option(cp.prop_chart_type, name)
        # 右侧断言
        expect(cp.prop_chart_type, f'图表类型应显示 {name}').to_have_text(name)
        # 画布断言：换完类型图还在
        expect(cp.widget_canvas, f'切成 {name} 之后画布上应该还有图').to_have_count(1)
        prints[name] = cp.canvas_fingerprint()

    # 画布断言：三种类型画出来的东西两两不同
    for a, b in [('折线', '柱状'), ('折线', '饼图'), ('柱状', '饼图')]:
        assert_changed(prints[a], prints[b], f'从{a}换成{b}')
    # 饼图是一圈彩色扇形，颜色种类明显比折线多
    assert prints['饼图']['colors'] > prints['折线']['colors'], (
        f"饼图的颜色应该比折线丰富，实际 饼图={prints['饼图']['colors']} "
        f"折线={prints['折线']['colors']}")


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('绑好之后关掉图例，画布上的图例真的没了，打开又回来')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bound_legend_toggle_changes_canvas(free_chart_bound):
    cp = free_chart_bound
    # 不要再 click_widget：点一下图会重画，第一张指纹就成了首帧，对不上后面的稳定态
    on = cp.canvas_fingerprint()

    cp.switch_radio('显示图例', '否').check()
    off = cp.canvas_fingerprint()
    # 右侧断言
    expect(cp.switch_radio('显示图例', '否')).to_be_checked()
    # 画布断言
    assert_changed(on, off, '关掉图例')

    cp.switch_radio('显示图例', '是').check()
    back = cp.canvas_fingerprint()
    # 画布断言
    assert_same(on, back, '重新打开图例')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('绑好之后挪图例位置，图例真的挪到对应的那一边')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bound_legend_position_moves_legend(free_chart_bound):
    cp = free_chart_bound
    # 不要再 click_widget：点一下图会重画，第一张指纹就成了首帧，对不上后面的稳定态

    # 先关掉图例，拿一张「没有图例」的底图，后面拿各个位置跟它比
    cp.switch_radio('显示图例', '否').check()
    no_legend = cp.canvas_fingerprint()
    cp.switch_radio('显示图例', '是').check()

    # 图例位置 -> 图例应该出现在画布的哪一块区域
    where = {'顶部': 'top', '底部': 'bottom', '左侧': 'left'}
    for name, region in where.items():
        cp.pick_option(cp.prop_legend_position, name)
        fp = cp.canvas_fingerprint()
        # 右侧断言
        expect(cp.prop_legend_position, f'图例位置应显示 {name}').to_have_text(name)
        # 画布断言：那一块区域比没有图例时更亮（图例文字画上去了）
        lit = region_brightness(fp, region)
        dark = region_brightness(no_legend, region)
        assert lit > dark, (
            f'图例放在{name}时，画布{region}区应该比没有图例时更亮，'
            f'实际 {dark:.1f} -> {lit:.1f}')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('绑好之后把线宽调粗，画布上的线真的变粗，调回来复原')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_bound_line_width_changes_canvas(free_chart_bound):
    cp = free_chart_bound
    # 不要再 click_widget：点一下图会重画，第一张指纹就成了首帧，对不上后面的稳定态
    thin = cp.canvas_fingerprint()

    cp.prop_line_width.fill('5')
    thick = cp.canvas_fingerprint()
    # 右侧断言
    expect(cp.prop_line_width).to_have_value('5')
    # 画布断言：线画粗了，落在线上的像素更多，那一块更亮
    assert_changed(thin, thick, '线宽调到 5')
    assert region_brightness(thick, 'bottom') > region_brightness(thin, 'bottom'), (
        '线加粗后画布下半部分应该更亮')

    cp.prop_line_width.fill('1.5')
    back = cp.canvas_fingerprint()
    # 画布断言
    assert_same(thin, back, '线宽调回 1.5')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('绑好之后打开数据缩放，画布底部多出缩放条')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_bound_data_zoom_changes_canvas(free_chart_bound):
    cp = free_chart_bound
    # 不要再 click_widget：点一下图会重画，第一张指纹就成了首帧，对不上后面的稳定态
    off = cp.canvas_fingerprint()

    cp.switch_radio('数据缩放', '是').check()
    on = cp.canvas_fingerprint()
    # 右侧断言
    expect(cp.switch_radio('数据缩放', '是')).to_be_checked()
    # 画布断言：缩放条画在底部，那一块会明显变亮
    assert_changed(off, on, '打开数据缩放')
    assert region_brightness(on, 'bottom') > region_brightness(off, 'bottom'), (
        '打开数据缩放后画布底部应该更亮（多了一条缩放条）')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('绑好之后设警告线，画布上真的多出一条线，清掉复原')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bound_warning_line_draws_on_canvas(free_chart_bound):
    cp = free_chart_bound
    before = cp.canvas_fingerprint()

    # 阈值要落在数据的取值范围里，画出来才看得见
    cp.prop_warning_line.fill('0.5')
    after = cp.canvas_fingerprint()
    # 右侧断言
    expect(cp.prop_warning_line).to_have_value('0.5')
    # 画布断言
    assert_changed(before, after, '警告线设成 0.5')

    cp.prop_warning_line.fill('0')
    back = cp.canvas_fingerprint()
    # 画布断言
    assert_same(before, back, '警告线清回 0')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('绑好之后设危险线，画布上真的多出一条线，清掉复原')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bound_danger_line_draws_on_canvas(free_chart_bound):
    cp = free_chart_bound
    before = cp.canvas_fingerprint()

    cp.prop_danger_line.fill('2')
    after = cp.canvas_fingerprint()
    # 右侧断言
    expect(cp.prop_danger_line).to_have_value('2')
    # 画布断言
    assert_changed(before, after, '危险线设成 2')

    cp.prop_danger_line.fill('0')
    back = cp.canvas_fingerprint()
    # 画布断言
    assert_same(before, back, '危险线清回 0')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('危险线设成远超数据范围的值，线落在图外，画布看不出变化')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_bound_danger_line_out_of_range(free_chart_bound):
    # 这不是缺陷：阈值线画在纵轴对应的位置上，值超出数据范围就落到图框外面去了，
    # 画布上自然看不见。用例把这个边界固定下来，免得以后有人以为是没生效。
    cp = free_chart_bound
    before = cp.canvas_fingerprint()

    cp.prop_danger_line.fill('95')
    after = cp.canvas_fingerprint()
    # 右侧断言：值确实写进去了
    expect(cp.prop_danger_line).to_have_value('95')
    # 画布断言：超出范围，画不出来
    assert_same(before, after, '危险线设成超出数据范围的 95')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('绑好之后把填充透明度拉满，折线下方真的填上颜色，调回复原')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bound_fill_opacity_fills_area(free_chart_bound):
    cp = free_chart_bound
    before = cp.canvas_fingerprint()

    cp.prop_fill_opacity.fill('1')
    after = cp.canvas_fingerprint()
    # 右侧断言
    expect(cp.prop_fill_opacity).to_have_value('1')
    # 画布断言：线下方填上了一大片颜色，整幅平均色会明显变化
    assert_changed(before, after, '填充透明度拉到 1')
    assert region_brightness(after, 'bottom') > region_brightness(before, 'bottom'), \
        '填充之后折线下方应该更亮（填上颜色了）'

    cp.prop_fill_opacity.fill('0')
    back = cp.canvas_fingerprint()
    # 画布断言
    assert_same(before, back, '填充透明度调回 0')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('显示提示=是：鼠标移到图上弹出提示框，移开就消失')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bound_tooltip_shows_on_hover(free_chart_bound):
    # 提示框是悬停才画出来的，静态画面上本来就没有，所以必须真的 hover 才测得到
    cp = free_chart_bound
    expect(cp.switch_radio('显示提示', '是')).to_be_checked()
    idle = cp.canvas_fingerprint()

    cp.hover_chart()
    hovering = cp.canvas_fingerprint()
    # 画布断言：提示框画上去了
    assert_changed(idle, hovering, '鼠标移到图上')

    cp.unhover_chart()
    away = cp.canvas_fingerprint()
    # 画布断言：移开后提示框消失，画布复原
    assert_same(idle, away, '鼠标移开')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('显示提示=否：鼠标移到图上也不弹提示框')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bound_tooltip_hidden_when_off(free_chart_bound):
    cp = free_chart_bound
    cp.switch_radio('显示提示', '否').check()
    # 右侧断言
    expect(cp.switch_radio('显示提示', '否')).to_be_checked()

    idle = cp.canvas_fingerprint()
    cp.hover_chart()
    hovering = cp.canvas_fingerprint()
    # 画布断言：关掉提示后，hover 上去画布纹丝不动
    assert_same(idle, hovering, '关掉提示后鼠标移到图上')
    cp.unhover_chart()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('绑好之后改标题，图还在')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_bound_still_renders_after_title_change(free_chart_bound):
    cp = free_chart_bound
    # 不要再 click_widget：点一下图会重画，第一张指纹就成了首帧，对不上后面的稳定态
    cp.prop_title.fill('母线电压趋势')
    # 右侧断言
    expect(cp.prop_title).to_have_value('母线电压趋势')
    # 画布断言：标题变了，图还在
    expect(cp.widget_title).to_have_text('母线电压趋势')
    expect(cp.widget_canvas).to_have_count(1)


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('[现状] 定时刷新配好了也不会真的定时取数')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_timer_does_not_actually_refresh(free_chart_bound):
    # ⚠️ 现状记录（非期望）：图表取数走 POST /api/datasources/<id>/query。
    # 绑好数据源、把定时触发设成「刷新数据」、间隔设成最小的 1 秒，
    # 编辑态和预览态各盯十几秒，这个接口一次都不会再发 —— 定时刷新没接上，
    # 能选能填，但不刷新。
    # TODO(bug) 期望：每隔 N 秒重新取一次数。开发修好后把下面的 == 0 改成 >= 2。
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
    page.wait_for_timeout(12000)

    assert len(queries) == 0, (
        f'现状是定时刷新不生效，12 秒内不该有取数请求，实际发了 {len(queries)} 次；'
        f'如果开发已经修好，请把这条用例改成断言 >= 2')


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
                   f'「{name}」标着不可用，应该是点不动的')                 .to_have_attribute('aria-disabled', 'true')
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
        assert any(c != combos[0] for c in combos[1:]),             f'不同数据来源的配置字段不该完全相同：{fields_by_source}'


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

    # 一路选到数据表，每一级都真的被填上了
    chosen = cp.bind_pick_table()
    expect(cp.bind_field('关系型数据源')).to_have_text(chosen['数据源'])
    expect(cp.bind_field('Schema')).to_have_text(chosen['Schema'])
    expect(cp.bind_field('数据表')).to_have_text(chosen['数据表'])


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
    expect(cp.widget_canvas, '什么都没选，画布上不该出图').to_have_count(0)
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
    expect(cp.widget_canvas).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('选完所有字段但点「取消」，画布仍然不出图')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_bind_cancel_after_filling(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    cp.open_bind_dialog()
    cp.bind_pick_table()
    cp.bind_pick_fields()

    cp.close_bind_dialog()
    # 画布断言：填了但没保存，等于没绑
    expect(cp.widget_unbound_chip).to_be_visible()
    expect(cp.widget_canvas).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('选完所有字段点「预览真实数据」，弹窗里出真实数据表格')
@allure.severity(allure.severity_level.BLOCKER)
def test_chart_bind_preview_shows_real_data(free_chart_page):
    cp = free_chart_page
    cp.click_widget()
    cp.open_bind_dialog()
    cp.bind_pick_table()
    cp.bind_pick_fields()

    cp.bind_dialog_preview.click()
    cp.page.wait_for_timeout(3500)
    # 弹窗断言：出结果表格，有表头有数据行，两种提示都不该再出现
    expect(cp.bind_preview_table).to_have_count(1)
    assert cp.bind_preview_table.locator('thead th').count() >= 2, '预览表格至少两列（横轴 + 数值）'
    assert cp.bind_preview_table.locator('tbody tr').count() > 0, '预览表格应该有数据行'
    expect(cp.bind_invalid_hint).to_have_count(0)
    expect(cp.bind_need_table_hint).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('保存绑定后弹窗关闭，画布上真的出图')
@allure.severity(allure.severity_level.BLOCKER)
def test_chart_bind_save_renders_chart(free_chart_bound):
    cp = free_chart_bound
    # 画布断言：占位文案没了，换成「已登记数据源」，并且真的画出了一块图
    expect(cp.bind_dialog).to_have_count(0)
    expect(cp.widget_unbound_chip).to_have_count(0)
    expect(cp.widget_unbound_tip).to_have_count(0)
    expect(cp.widget_bound_chip).to_be_visible()
    expect(cp.widget_canvas).to_have_count(1)
    size = cp.widget_canvas.first.evaluate('el => [el.width, el.height]')
    assert size[0] > 0 and size[1] > 0, f'图表画布尺寸不该是 0，实际 {size}'


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
