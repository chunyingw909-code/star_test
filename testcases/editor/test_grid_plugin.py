import allure
import pytest
from playwright.sync_api import expect


# =============================================================================
# ⚠️ 现状记录（非期望行为）——— 栅格布局(Puck)未实现「插件禁用态」
#
# 关掉某组件的插件后，栅格布局下：
#   1. 计数正常变 11/12                                （这个是对的）
#   2. 画布上的该组件退化成 Puck 通用兜底串
#      "No configuration for <Type>"，组件内容丢失      （缺陷）
#   3. 没有自由布局那种「组件已禁用」徽标               （缺陷）
#   4. 右侧属性面板没有锁定提示，仍显示可编辑字段        （缺陷）
#   5. 组件库/添加菜单里该组件依然存在
#      —— 与 Plugin Manager 弹框自己的说明
#      "Disabled widgets are hidden from the component library" 矛盾  （缺陷）
#
# 期望：应与自由布局一致（见 test_plugin.py 里 free 版的禁用效果用例）。
# 这些用例锁定当前实际行为，防止再回归；开发修复后需要把断言改成期望值。
# TODO(bug): 已知问题，将向开发提单。
# =============================================================================


@allure.feature('界面编辑器')
@allure.story('插件')
@allure.title('[现状] 栅格布局禁用图表插件：计数变 11/12（唯一正确的部分）')
@allure.severity(allure.severity_level.NORMAL)
def test_grid_plugin_disable_updates_count(plugin_with_grid_chart):
    pm, chart = plugin_with_grid_chart
    pm.set_enabled('ChartWidget', False)
    expect(pm.enabled_count).to_have_text('11 / 12 enabled')
    pm.set_enabled('ChartWidget', True)
    expect(pm.enabled_count).to_have_text('12 / 12 enabled')


@allure.feature('界面编辑器')
@allure.story('插件')
@allure.title('[现状] 栅格布局禁用后，画布组件退化成 "No configuration for ..." 兜底串')
@allure.severity(allure.severity_level.NORMAL)
def test_grid_plugin_disabled_widget_degrades_to_fallback(plugin_with_grid_chart):
    pm, chart = plugin_with_grid_chart
    pm.set_enabled('ChartWidget', False)
    pm.close()
    widget = chart.canvas_widgets().first
    # 现状：Puck 英文兜底串，图表内容丢失
    expect(widget).to_contain_text('No configuration for ChartWidget')
    # 现状：没有自由布局那种「组件已禁用」徽标
    # TODO(bug) 期望：expect(chart.widget_disabled_badge()).to_be_visible()
    expect(chart.widget_disabled_badge()).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('插件')
@allure.title('[现状] 栅格布局禁用后点击该组件，右侧没有锁定提示')
@allure.severity(allure.severity_level.NORMAL)
def test_grid_plugin_no_lock_notice_on_panel(plugin_with_grid_chart):
    pm, chart = plugin_with_grid_chart
    pm.set_enabled('ChartWidget', False)
    pm.close()
    chart.click_widget()
    # 现状：没有 "该组件已禁用（对应插件已关闭），禁止编辑…" 这条提示
    # TODO(bug) 期望：expect(chart.disabled_panel_notice).to_be_visible()
    expect(chart.disabled_panel_notice).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('插件')
@allure.title('[现状] 栅格布局禁用后，该组件仍留在组件库里（与弹框说明矛盾）')
@allure.severity(allure.severity_level.NORMAL)
def test_grid_plugin_still_in_component_library(plugin_with_grid_chart):
    pm, chart = plugin_with_grid_chart
    pm.set_enabled('ChartWidget', False)
    pm.close()
    # 现状：组件库里还能看到被禁用的组件
    # TODO(bug) 期望：expect(chart.drawer_item('ChartWidget')).to_have_count(0)
    expect(chart.drawer_item('ChartWidget')).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('插件')
@allure.title('[现状] 栅格布局重新启用插件后，画布组件恢复正常')
@allure.severity(allure.severity_level.CRITICAL)
def test_grid_plugin_reenable_restores_widget(plugin_with_grid_chart):
    pm, chart = plugin_with_grid_chart
    pm.set_enabled('ChartWidget', False)
    pm.close()
    expect(chart.canvas_widgets().first).to_contain_text('No configuration for ChartWidget')

    pm.open()
    pm.set_enabled('ChartWidget', True)
    expect(pm.enabled_count).to_have_text('12 / 12 enabled')
    pm.close()

    # 恢复方向是好的：兜底串消失、属性面板可用
    expect(chart.canvas_widgets().first).not_to_contain_text('No configuration for')
    chart.click_widget()
    expect(chart.prop_title).to_have_value('真实数据图表')
