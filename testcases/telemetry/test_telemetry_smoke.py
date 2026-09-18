import allure
import pytest
from playwright.sync_api import expect

from pages.telemetry.telemetry_page import TelemetryPage


# 卫星遥测「点了有没有反应」冒烟：只验证控件点击后有可观察的响应
# （子标签选中态切换 / 速度档文案变化 / 节点模式切换 / 操作弹 Snackbar），
# 不验证遥测数值。有副作用的 启动 / 保存快照 / 加载断点 不在此覆盖。


# ==================== 进入模块 ====================

@allure.feature('卫星遥测')
@allure.story('冒烟')
@allure.title('点顶部「卫星遥测」进入模块，显示「星座数字验证系统」与「仿真控制」面板')
@allure.severity(allure.severity_level.BLOCKER)
def test_telemetry_entry(telemetry_page):
    expect(telemetry_page.title).to_be_visible()
    expect(telemetry_page.sim_control_heading).to_be_visible()
    # 默认停在第一个分系统子标签「供配电」
    assert telemetry_page.selected_subtab() == '供配电'


# ==================== 分系统子标签 ====================

@allure.feature('卫星遥测')
@allure.story('冒烟')
@allure.title('点分系统子标签「{name}」→ 它被选中，其余取消选中')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('name', TelemetryPage.SUBTABS)
def test_telemetry_subtab_switch(telemetry_page, name):
    telemetry_page.open_subtab(name)
    expect(telemetry_page.subtab(name)).to_have_attribute('aria-selected', 'true')
    assert telemetry_page.selected_subtab() == name
    # 其余子标签均未选中
    for other in TelemetryPage.SUBTABS:
        if other != name:
            expect(telemetry_page.subtab(other)).to_have_attribute('aria-selected', 'false')


@allure.feature('卫星遥测')
@allure.story('冒烟')
@allure.title('子标签来回切换：供配电 → 设备接口 → 供配电，选中态跟手')
@allure.severity(allure.severity_level.NORMAL)
def test_telemetry_subtab_roundtrip(telemetry_page):
    telemetry_page.open_subtab('设备接口')
    assert telemetry_page.selected_subtab() == '设备接口'
    telemetry_page.open_subtab('供配电')
    assert telemetry_page.selected_subtab() == '供配电'


# ==================== 仿真速度档 ====================

@allure.feature('卫星遥测')
@allure.story('冒烟')
@allure.title('点速度档「{speed}」→「速度: {speed}」文案更新，该档变为当前档')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('speed', TelemetryPage.SPEEDS)
def test_telemetry_speed_select(telemetry_page, speed):
    telemetry_page.set_speed(speed)
    expect(telemetry_page.speed_label).to_contain_text(f'速度: {speed}')
    assert telemetry_page.current_speed() == speed
    assert telemetry_page.speed_is_active(speed)


@allure.feature('卫星遥测')
@allure.story('冒烟')
@allure.title('速度档改为 16x 再调回 1x，文案与高亮同步')
@allure.severity(allure.severity_level.NORMAL)
def test_telemetry_speed_roundtrip(telemetry_page):
    telemetry_page.set_speed('16x')
    assert telemetry_page.current_speed() == '16x'
    telemetry_page.set_speed('1x')
    assert telemetry_page.current_speed() == '1x'
    assert telemetry_page.speed_is_active('1x')
    assert not telemetry_page.speed_is_active('16x')


# ==================== 仿真节点模式 ====================

@allure.feature('卫星遥测')
@allure.story('冒烟')
@allure.title('点「真实节点」→ 它被按下、「模拟节点」弹起；点回「模拟节点」复原')
@allure.severity(allure.severity_level.CRITICAL)
def test_telemetry_node_mode_toggle(telemetry_page):
    # 默认「模拟节点」
    assert telemetry_page.node_mode() == 'sim'

    telemetry_page.set_node_mode('real')
    expect(telemetry_page.real_node_button).to_have_attribute('aria-pressed', 'true')
    expect(telemetry_page.sim_node_button).to_have_attribute('aria-pressed', 'false')
    assert telemetry_page.node_mode() == 'real'

    telemetry_page.set_node_mode('sim')
    expect(telemetry_page.sim_node_button).to_have_attribute('aria-pressed', 'true')
    expect(telemetry_page.real_node_button).to_have_attribute('aria-pressed', 'false')


# ==================== 重置 / 应用 ====================

@allure.feature('卫星遥测')
@allure.story('冒烟')
@allure.title('切到 4x 后点「重置」，速度、时间和进度恢复初始值')
@allure.severity(allure.severity_level.NORMAL)
def test_telemetry_reset_responds(telemetry_page):
    telemetry_page.set_speed('4x')
    assert telemetry_page.current_speed() == '4x'
    telemetry_page.reset_button.click()
    expect(telemetry_page.speed_label).to_contain_text('1x')
    assert telemetry_page.speed_is_active('1x')
    assert (telemetry_page.sim_time() or 0) == 0
    assert (telemetry_page.progress_percent() or 0) == 0
    expect(telemetry_page.sim_control_heading).to_be_visible()


@allure.feature('卫星遥测')
@allure.story('冒烟')
@allure.title('改速度档后点「应用」有响应（弹出提示，不报错不白屏）')
@allure.severity(allure.severity_level.NORMAL)
def test_telemetry_apply_responds(telemetry_page):
    telemetry_page.set_speed('4x')
    telemetry_page.apply_button.click()
    expect(telemetry_page.snackbar).to_be_visible()
    expect(telemetry_page.sim_control_heading).to_be_visible()
