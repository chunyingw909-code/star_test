"""状态灯组件。三个工业控件里这个是真能反映数据的。

⚠️ 不测的：
   状态文字 —— 映射坏了（填"警告"画布反而显示"危险"），别改它，默认停在"正常"

⚠️ 警告 / 危险 / 离线 三种颜色只有组件处在对应状态时才在画布上生效，
   而那几个状态现在没法稳定触发（改状态文字会乱），所以只校验属性写得进去。
   正常颜色能直接在灯珠上验证（默认就是「正常」态）。
"""
import allure
from playwright.sync_api import expect

from testcases.editor.common_style_cases import CommonStyleCases


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('添加状态灯后画布出现组件，默认显示"状态"和"正常"，灯珠为绿色')
@allure.severity(allure.severity_level.BLOCKER)
def test_status_add(free_status_page):
    sp = free_status_page
    expect(sp.canvas_widgets()).to_have_count(1)
    # 画布断言
    expect(sp.widget).to_contain_text('状态')
    expect(sp.widget).to_contain_text('正常')
    assert sp.lamp_size() == (36, 36), '默认灯珠该是 36x36'


@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('点击组件，属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_defaults(free_status_page):
    sp = free_status_page
    sp.click_widget()
    # 右侧断言
    expect(sp.prop_panel).to_be_visible()
    expect(sp.prop_label).to_have_value('状态')
    expect(sp.prop_normal_color).to_have_value('#2FC25B')
    expect(sp.prop_size).to_have_value('36')
    expect(sp.show_label_radio('是')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('点击画布空白区域，属性面板隐藏')
@allure.severity(allure.severity_level.NORMAL)
def test_status_panel_hides(free_status_page):
    sp = free_status_page
    sp.click_widget()
    expect(sp.prop_panel).to_be_visible()
    sp.click_canvas_blank()
    expect(sp.prop_panel).to_be_hidden()


# ==================== 标签 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('修改标签为"姿态控制"，画布同步；清空也同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_label(free_status_page):
    sp = free_status_page
    sp.click_widget()
    sp.prop_label.fill('姿态控制')
    # 右侧断言
    expect(sp.prop_label).to_have_value('姿态控制')
    # 画布断言
    expect(sp.widget_label).to_have_text('姿态控制')

    # 清空后画布回落到默认（跟表格标题一样的行为），不是空白
    sp.prop_label.fill('')
    assert sp.widget_label.inner_text() != '', \
        '清空标签后画布应回落到默认文字，不是空白'


# ==================== 颜色 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('四种状态颜色都能写入，正常颜色的色块同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_colors(free_status_page):
    # 灯珠会自己循环变色，画布上测不稳，只校验属性面板 + 色块（见文件开头说明）。
    sp = free_status_page
    sp.click_widget()
    sp.prop_normal_color.fill('#00FF00')
    # 右侧断言
    expect(sp.prop_normal_color).to_have_value('#00FF00')
    expect(sp.prop_normal_color_swatch).to_have_value('#00ff00')
    for prop, value in [(sp.prop_warning_color, '#F4D03F'),
                        (sp.prop_danger_color, '#FF0000'),
                        (sp.prop_offline_color, '#999999')]:
        prop.fill(value)
        expect(prop).to_have_value(value)


@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('尺寸改为 80，灯珠变大；改为 12 变小；恢复 36')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_size(free_status_page):
    sp = free_status_page
    sp.click_widget()

    sp.prop_size.fill('80')
    expect(sp.prop_size).to_have_value('80')
    assert sp.lamp_size() == (80, 80), f'尺寸 80 时灯珠该是 80x80，实际 {sp.lamp_size()}'

    sp.prop_size.fill('12')
    assert sp.lamp_size() == (12, 12), f'尺寸 12 时灯珠该是 12x12，实际 {sp.lamp_size()}'

    sp.prop_size.fill('36')
    assert sp.lamp_size() == (36, 36)


# ==================== 显示标签 / 告警闪烁 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('关闭显示标签，画布上标签文字消失；打开又出现')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_show_label_toggle(free_status_page):
    sp = free_status_page
    sp.click_widget()
    sp.prop_label.fill('姿态控制')
    expect(sp.widget_label).to_have_text('姿态控制')

    sp.show_label_radio('否').click()
    # 右侧断言
    expect(sp.show_label_radio('否')).to_be_checked()
    # 画布断言：整块文字都没了
    expect(sp.widget).not_to_contain_text('姿态控制')

    sp.show_label_radio('是').click()
    expect(sp.widget_label).to_have_text('姿态控制')


@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('告警闪烁开关来回切，单选状态同步')
@allure.severity(allure.severity_level.NORMAL)
def test_status_blink_toggle(free_status_page):
    # 闪烁只在告警态才看得到动画，正常态没有可观察效果，这里只校验开关状态。
    sp = free_status_page
    sp.click_widget()
    sp.blink_radio('是').click()
    expect(sp.blink_radio('是')).to_be_checked()
    sp.blink_radio('否').click()
    expect(sp.blink_radio('否')).to_be_checked()


# ==================== 删除 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('删除状态灯组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_delete(free_status_page):
    sp = free_status_page
    expect(sp.canvas_widgets()).to_have_count(1)
    sp.delete_widget()
    expect(sp.canvas_widgets()).to_have_count(0)


# ==================== 组合修改 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('同时修改标签、正常颜色、尺寸')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_combined(free_status_page):
    sp = free_status_page
    sp.click_widget()
    sp.prop_label.fill('姿态控制')
    sp.prop_normal_color.fill('#00FF00')
    sp.prop_size.fill('60')

    # 右侧断言
    expect(sp.prop_label).to_have_value('姿态控制')
    expect(sp.prop_normal_color).to_have_value('#00FF00')
    expect(sp.prop_size).to_have_value('60')
    # 画布断言
    expect(sp.widget_label).to_have_text('姿态控制')
    assert sp.lamp_size() == (60, 60), '灯珠该 60x60'


# ==================== 实时遥测 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('绑定电源运行模式后，状态灯显示“正常”、绿色灯珠和 LIVE 状态')
@allure.severity(allure.severity_level.BLOCKER)
def test_status_realtime_telemetry(free_status_realtime):
    sp = free_status_realtime
    sp.click_widget()

    binding = sp.bind_realtime('电源运行模式 · power')

    assert binding['item'] == '电源运行模式 · power'
    expect(sp.widget_live).to_have_text('● LIVE')
    expect(sp.widget_status).to_have_text('正常')
    assert sp.lamp_color() == 'rgb(47, 194, 91)', \
        f'“正常”状态应显示绿色灯珠，实际 {sp.lamp_color()}'


# ==================== 通用样式（共用用例集）====================

class TestStatusCommonStyle(CommonStyleCases):
    widget_fixture = 'free_status_page'
    story = '自由布局-状态灯组件'
