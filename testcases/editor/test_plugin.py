import allure
import pytest
from playwright.sync_api import expect

from pages.editor.plugin_page import PluginManager
from pages.editor.widget_catalog import WIDGETS


# ==================== Plugin Manager 对话框本身 ====================

@allure.feature('界面编辑器')
@allure.story('插件')
@allure.title('点击"插件"打开 Plugin Manager，默认 12 / 12 启用')
@allure.severity(allure.severity_level.CRITICAL)
def test_plugin_manager_opens(plugin_manager):
    expect(plugin_manager.dialog).to_be_visible()
    expect(plugin_manager.title).to_be_visible()
    expect(plugin_manager.description).to_be_visible()
    expect(plugin_manager.enabled_count).to_have_text('12 / 12 enabled')
    expect(plugin_manager.rows()).to_have_count(len(WIDGETS))
    expect(plugin_manager.close_button).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('插件')
@allure.title('Plugin Manager 逐行核对：显示名 / Type / 分类')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('spec', WIDGETS, ids=[w['type'] for w in WIDGETS])
def test_plugin_manager_lists_widget(plugin_manager, spec):
    row = plugin_manager.row(spec['type'])
    expect(row).to_have_count(1)
    expect(row).to_contain_text(spec['label'])
    expect(row).to_contain_text(spec['type'])
    expect(row).to_contain_text(spec['category'])


@allure.feature('界面编辑器')
@allure.story('插件')
@allure.title('Plugin Manager 表格里的组件集合与组件清单完全一致')
@allure.severity(allure.severity_level.CRITICAL)
def test_plugin_manager_widget_set_exact(plugin_manager):
    actual = [t.strip() for t in plugin_manager.row_types()]
    expected = [w['type'] for w in WIDGETS]
    assert sorted(actual) == sorted(expected), (
        f'多出={sorted(set(actual) - set(expected))} 缺少={sorted(set(expected) - set(actual))}'
    )


@allure.feature('界面编辑器')
@allure.story('插件')
@allure.title('禁用某组件后计数变 11 / 12，重新启用回到 12 / 12')
@allure.severity(allure.severity_level.CRITICAL)
def test_plugin_toggle_updates_count(plugin_manager):
    plugin_manager.set_enabled('SpacerWidget', False)
    expect(plugin_manager.enabled_count).to_have_text('11 / 12 enabled')
    expect(plugin_manager.checkbox('SpacerWidget')).not_to_be_checked()

    plugin_manager.set_enabled('SpacerWidget', True)
    expect(plugin_manager.enabled_count).to_have_text('12 / 12 enabled')
    expect(plugin_manager.checkbox('SpacerWidget')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('插件')
@allure.title('点击 CLOSE 关闭 Plugin Manager')
@allure.severity(allure.severity_level.NORMAL)
def test_plugin_manager_close(plugin_manager):
    plugin_manager.close()
    expect(plugin_manager.dialog).to_be_hidden()


# ==================== 禁用插件对画布上已放置组件的影响 ====================
# plugin_with_chart 返回 (PluginManager, FreeChartPage)：画布已放一个图表 + 打开的弹框，
# teardown 会把所有插件开关复位成启用。

@allure.feature('界面编辑器')
@allure.story('插件')
@allure.title('禁用图表插件后，计数变 11/12，画布上的图表被标记"组件已禁用"')
@allure.severity(allure.severity_level.CRITICAL)
def test_plugin_disable_marks_placed_widget(plugin_with_chart):
    pm, chart = plugin_with_chart
    pm.set_enabled('ChartWidget', False)
    expect(pm.enabled_count).to_have_text('11 / 12 enabled')
    pm.close()
    expect(chart.widget_disabled_badge()).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('插件')
@allure.title('禁用插件后点击该组件，右侧属性面板变成锁定提示、不再显示属性')
@allure.severity(allure.severity_level.CRITICAL)
def test_plugin_disabled_widget_property_panel_locked(plugin_with_chart):
    pm, chart = plugin_with_chart
    pm.set_enabled('ChartWidget', False)
    pm.close()
    chart.click_widget()
    expect(chart.disabled_panel_notice).to_be_visible()
    # 正常属性控件消失
    expect(chart.prop_title).to_have_count(0)
    expect(chart.prop_chart_type).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('插件')
@allure.title('禁用插件后，该组件从"添加组件"菜单里消失')
@allure.severity(allure.severity_level.CRITICAL)
def test_plugin_disable_removes_from_component_library(plugin_with_chart):
    pm, chart = plugin_with_chart
    pm.set_enabled('ChartWidget', False)
    pm.close()
    chart.add_component_button.click()
    expect(chart.component_item('图表')).to_have_count(0)
    expect(chart.component_item('表格')).to_have_count(1)
    chart.close_add_menu()


@allure.feature('界面编辑器')
@allure.story('插件')
@allure.title('重新启用插件后，画布组件恢复正常、属性面板回来')
@allure.severity(allure.severity_level.CRITICAL)
def test_plugin_reenable_restores_widget(plugin_with_chart):
    pm, chart = plugin_with_chart
    pm.set_enabled('ChartWidget', False)
    pm.close()
    expect(chart.widget_disabled_badge()).to_be_visible()

    pm.open()
    pm.set_enabled('ChartWidget', True)
    expect(pm.enabled_count).to_have_text('12 / 12 enabled')
    pm.close()

    expect(chart.widget_disabled_badge()).to_have_count(0)
    chart.click_widget()
    expect(chart.prop_title).to_have_value('真实数据图表')


@allure.feature('界面编辑器')
@allure.story('插件')
@allure.title('禁用其它组件的插件，不影响画布上的图表')
@allure.severity(allure.severity_level.NORMAL)
def test_plugin_disable_other_does_not_affect_chart(plugin_with_chart):
    pm, chart = plugin_with_chart
    pm.set_enabled('TableWidget', False)
    pm.close()
    expect(chart.widget_disabled_badge()).to_have_count(0)
    chart.click_widget()
    expect(chart.prop_title).to_have_value('真实数据图表')
