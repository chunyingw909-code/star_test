"""指示牌组件。

⚠️ 只有【标签 / 单位 / 图标】在画布上看得出来，其余现在都是摆设：
   数值、警告阈值、危险阈值、小数位 —— 画布上数值一直显示 "—"（拿不到数据）
   显示状态                     —— 配套的状态趋势也没做好
   卫星 ID、字段路径             —— 绑遥测数据用的，现在连不上真实数据
等能连上真实数据再补。
"""
import allure
from playwright.sync_api import expect

from testcases.editor.common_style_cases import CommonStyleCases


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('添加指示牌后画布出现组件，默认标签"CPU 使用率"、单位"%"')
@allure.severity(allure.severity_level.BLOCKER)
def test_indicator_add(free_indicator_page):
    ip = free_indicator_page
    expect(ip.canvas_widgets()).to_have_count(1)
    # 画布断言
    expect(ip.widget_label).to_have_text('CPU 使用率')
    expect(ip.widget).to_contain_text('%')


@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('点击组件，属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_defaults(free_indicator_page):
    ip = free_indicator_page
    ip.click_widget()
    # 右侧断言
    expect(ip.prop_panel).to_be_visible()
    expect(ip.prop_label).to_have_value('CPU 使用率')
    expect(ip.prop_unit).to_have_value('%')
    expect(ip.prop_icon).to_have_text('CPU')


@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('点击画布空白区域，属性面板隐藏')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_panel_hides(free_indicator_page):
    ip = free_indicator_page
    ip.click_widget()
    expect(ip.prop_panel).to_be_visible()
    ip.click_canvas_blank()
    expect(ip.prop_panel).to_be_hidden()


# ==================== 标签 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('修改标签为"母线电流"，画布同步；清空也同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_label(free_indicator_page):
    ip = free_indicator_page
    ip.click_widget()
    ip.prop_label.fill('母线电流')
    # 右侧断言
    expect(ip.prop_label).to_have_value('母线电流')
    # 画布断言
    expect(ip.widget_label).to_have_text('母线电流')

    ip.prop_label.fill('')
    expect(ip.widget_label).to_have_text('')


# ==================== 单位 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('修改单位为"A"，画布同步；清空也同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_unit(free_indicator_page):
    ip = free_indicator_page
    ip.click_widget()
    ip.prop_unit.fill('A')
    # 右侧断言
    expect(ip.prop_unit).to_have_value('A')
    # 画布断言
    expect(ip.widget_unit).to_have_text('A')

    ip.prop_unit.fill('')
    expect(ip.widget_unit).to_have_text('')


# ==================== 图标 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('图标逐项切换（CPU / 内存 / 网络 / 速度 / 温度），画布图标跟着换')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_icon_all_options(free_indicator_page):
    ip = free_indicator_page
    ip.click_widget()
    for label, testid in ip.ICONS.items():
        ip.pick_option(ip.prop_icon, label)
        # 右侧断言
        expect(ip.prop_icon, f'图标下拉应显示 {label}').to_have_text(label)
        # 画布断言：只出现这一个图标
        expect(ip.widget_icon(testid), f'图标选 {label} 时画布应出现 {testid}').to_have_count(1)
        for other in (t for t in ip.ICONS.values() if t != testid):
            expect(ip.widget_icon(other),
                   f'图标选 {label} 时不该同时有 {other}').to_have_count(0)


# ==================== 删除 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('删除指示牌组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_delete(free_indicator_page):
    ip = free_indicator_page
    expect(ip.canvas_widgets()).to_have_count(1)
    ip.delete_widget()
    expect(ip.canvas_widgets()).to_have_count(0)


# ==================== 组合修改 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('同时修改标签、单位、图标')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_combined(free_indicator_page):
    ip = free_indicator_page
    ip.click_widget()
    ip.prop_label.fill('母线电流')
    ip.prop_unit.fill('A')
    ip.pick_option(ip.prop_icon, '网络')

    # 右侧断言
    expect(ip.prop_label).to_have_value('母线电流')
    expect(ip.prop_unit).to_have_value('A')
    expect(ip.prop_icon).to_have_text('网络')
    # 画布断言
    expect(ip.widget_label).to_have_text('母线电流')
    expect(ip.widget_unit).to_have_text('A')
    expect(ip.widget_icon('NetworkCheckIcon')).to_have_count(1)


# ==================== 通用样式（共用用例集）====================

class TestIndicatorCommonStyle(CommonStyleCases):
    widget_fixture = 'free_indicator_page'
    story = '自由布局-指示牌组件'
