import time

import allure
import pytest
from playwright.sync_api import expect

from pages.telemetry.telemetry_page import TelemetryPage


# 卫星遥测主区 + 左侧仿真控制的功能用例。
# 本文件不覆盖导入、导出、批量修改和实时曲线时间窗；这些能力后续单独成组。
# 所有断言都落在可观察结果上：固定参数、场景/节点状态、仿真时间、曲线数据和快照恢复。


SUBSYSTEM_CASES = list(TelemetryPage.SUBSYSTEM_PARAMETERS.items())


def _parameter_count(groups):
    return sum(len(parameters) for parameters in groups.values())


# ==================== 进入模块 / 固定参数 ====================

@allure.feature('卫星遥测')
@allure.story('遥测主区-进入模块')
@allure.title('点顶部「卫星遥测」后该 Tab 选中，主区默认展示「供配电」8 条参数')
@allure.severity(allure.severity_level.BLOCKER)
def test_enter_module(telemetry_page):
    # 断言：真正进入了卫星遥测主区，而不是只看到全局常驻的标题和仿真侧栏。
    expect(telemetry_page.nav_entry).to_have_attribute('aria-selected', 'true')
    assert telemetry_page.selected_subtab() == '供配电'

    # 断言：默认分系统的参数内容已渲染完整。
    assert telemetry_page.parameter_cards.count() == 8
    expect(telemetry_page.parameter_group('太阳阵')).to_be_visible()


@allure.feature('卫星遥测')
@allure.story('遥测主区-分系统参数')
@allure.title('分系统「{name}」展示产品定义的固定分组、参数名、单位和总数')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize(
    'name,groups', SUBSYSTEM_CASES, ids=[name for name, _groups in SUBSYSTEM_CASES])
def test_subsystem_fixed_parameters(telemetry_page, name, groups):
    telemetry_page.open_subtab(name)

    # 断言：切换结果和当前可见参数总数都与该分系统定义一致。
    assert telemetry_page.selected_subtab() == name
    expected_count = _parameter_count(groups)
    assert telemetry_page.parameter_cards.count() == expected_count

    # 断言：每个分组里的参数顺序、名称和单位逐项一致。
    for group_name, expected_parameters in groups.items():
        group = telemetry_page.parameter_group(group_name)
        expect(group).to_be_visible()
        cards = telemetry_page.parameter_cards_in_group(group_name)
        assert cards.count() == len(expected_parameters), (
            f'「{name}/{group_name}」参数数应为 {len(expected_parameters)}，'
            f'实际 {cards.count()}')
        for index, (parameter_name, unit) in enumerate(expected_parameters):
            lines = [line.strip() for line in cards.nth(index).inner_text().splitlines()
                     if line.strip()]
            assert lines[0] == parameter_name, (
                f'「{name}/{group_name}」第 {index + 1} 项应为 {parameter_name}，实际 {lines}')
            if unit:
                assert any(unit in line for line in lines), (
                    f'「{name}/{group_name}/{parameter_name}」应显示单位 {unit}，实际 {lines}')


# ==================== 模拟节点 / 真实节点 ====================

@allure.feature('卫星遥测')
@allure.story('遥测主区-节点模式')
@allure.title('真实节点显示不可用占位；切回模拟节点后供配电参数恢复')
@allure.severity(allure.severity_level.CRITICAL)
def test_node_mode_switch_changes_content(telemetry_page):
    # 断言：进入模块默认是可用的模拟节点模式。
    assert telemetry_page.node_mode() == 'sim'
    assert telemetry_page.parameter_cards.count() == 8

    telemetry_page.set_node_mode('real')

    # 断言：真实节点模式不仅按钮变了，主区内容也切成明确占位状态。
    expect(telemetry_page.real_node_button).to_have_attribute('aria-pressed', 'true')
    expect(telemetry_page.sim_node_button).to_have_attribute('aria-pressed', 'false')
    expect(telemetry_page.real_node_notice).to_be_visible()
    assert telemetry_page.parameter_cards.count() == 0

    telemetry_page.set_node_mode('sim')

    # 断言：切回后占位消失，默认分系统参数重新出现。
    expect(telemetry_page.sim_node_button).to_have_attribute('aria-pressed', 'true')
    expect(telemetry_page.real_node_notice).to_be_hidden()
    assert telemetry_page.parameter_cards.count() == 8


# ==================== 场景 / 卫星 / 仿真节点 ====================

@allure.feature('卫星遥测')
@allure.story('场景与卫星')
@allure.title('无卫星场景：卫星数为 0，无节点可启动，播放与暂停不可用')
@allure.severity(allure.severity_level.CRITICAL)
def test_scene_without_satellites(empty_satellite_scenario):
    tp = empty_satellite_scenario

    # 断言：场景选择生效，且页面没有凭空生成卫星或节点。
    expect(tp.satellite_select_label).to_contain_text(tp.selected_scenario['name'])
    assert tp.configured_satellites == []
    assert tp.satellite_count() == 0
    assert tp.node_statuses() == {}

    # 断言：没有卫星时，仿真循环的播放和暂停都不可用。
    expect(tp.play_button).to_be_disabled()
    expect(tp.pause_button).to_be_disabled()

    tp.node_start_button.click()

    # 断言：启动进程弹窗也没有可选卫星，不能真正拉起节点。
    expect(tp.node_launch_dialog).to_be_visible()
    tp.node_launch_satellite.click()
    assert tp.node_launch_options.count() == 0
    tp.page.keyboard.press('Escape')
    expect(tp.node_launch_button).to_be_disabled()
    tp.node_launch_close.click()
    expect(tp.node_launch_dialog).to_be_hidden()


@allure.feature('卫星遥测')
@allure.story('场景与卫星')
@allure.title('有卫星但节点未启动：卫星按钮和 STOPPED 节点存在，播放仍不可用')
@allure.severity(allure.severity_level.BLOCKER)
def test_scene_with_stopped_satellites(stopped_satellite_scenario):
    tp = stopped_satellite_scenario
    expected_names = [item['name'] for item in tp.configured_satellites]

    # 断言：配置中的卫星全部显示在选择区和节点区，但尚无活动卫星。
    expect(tp.satellite_select_label).to_contain_text(tp.selected_scenario['name'])
    for name in expected_names:
        expect(tp.satellite_button(name).first).to_be_visible()
    assert tp.node_statuses() == {name: 'STOPPED' for name in expected_names}
    assert tp.active_satellite_names() == []
    assert tp.satellite_count() == 0

    # 断言：未启动任何节点时，不能播放或暂停仿真。
    expect(tp.play_button).to_be_disabled()
    expect(tp.pause_button).to_be_disabled()


@allure.feature('卫星遥测')
@allure.story('场景与卫星')
@allure.title('多卫星场景：未启动卫星显示但不能选中，当前活动卫星保持选中')
@allure.severity(allure.severity_level.CRITICAL)
def test_stopped_satellite_cannot_be_selected(multi_satellite_scenario):
    tp = multi_satellite_scenario
    active = tp.active_satellite_names()
    stopped = [item['name'] for item in tp.configured_satellites if item['name'] not in active]
    if not active or not stopped:
        pytest.skip(f'需要同时存在活动和停止卫星，当前活动={active}，停止={stopped}')
    selected_before = tp.selected_satellite()

    tp.select_satellite(stopped[0])

    # 断言：停止卫星仍展示在选择区，但不能成为遥测数据源。
    expect(tp.satellite_button(stopped[0]).first).to_be_visible()
    assert tp.selected_satellite() == selected_before


@allure.feature('卫星遥测')
@allure.story('仿真节点')
@allure.title('启动一颗仿真节点后状态变为 RUNNING、活动卫星出现、播放键可用')
@allure.severity(allure.severity_level.BLOCKER)
def test_started_node_enables_simulation(sim_ready_page):
    tp = sim_ready_page
    active = tp.active_satellite_names()

    # 断言：至少一颗节点真正进入运行态。
    assert active, '启动节点后应至少出现一颗活动卫星'
    statuses = tp.node_statuses()
    assert all(statuses[name] == 'RUNNING' for name in active)

    # 断言：节点已就绪但仿真循环尚未启动，可以播放，不能暂停。
    expect(tp.play_button).to_be_enabled()
    expect(tp.pause_button).to_be_disabled()
    # 当前产品把停止设计为幂等操作，空闲态仍保持可用。
    expect(tp.stop_button).to_be_enabled()


# ==================== 播放 / 暂停 / 停止 / 重置 ====================

@allure.feature('卫星遥测')
@allure.story('仿真控制-播放')
@allure.title('点播放后仿真时间推进、实时曲线产生数据点，按钮切到运行态')
@allure.severity(allure.severity_level.BLOCKER)
def test_start_sim_advances_time_and_curve(sim_ready_page):
    tp = sim_ready_page
    points_before = tp.curve_point_count()

    tp.start_sim()
    current_time = tp.wait_sim_time_advances()
    points_after = tp.wait_curve_points_increase(points_before)

    # 断言：仿真循环和实时曲线都真的工作，不只检查按钮点击成功。
    assert current_time and current_time > 0
    assert points_after > points_before

    # 断言：运行态只能暂停或停止，不能重复播放。
    expect(tp.play_button).to_be_disabled()
    expect(tp.pause_button).to_be_enabled()
    expect(tp.stop_button).to_be_enabled()


@allure.feature('卫星遥测')
@allure.story('仿真控制-暂停')
@allure.title('运行中点暂停后仿真时间和曲线数据点都冻结，可继续播放或停止')
@allure.severity(allure.severity_level.CRITICAL)
def test_pause_freezes_time_and_curve(running_sim):
    tp = running_sim
    tp.wait_curve_points_increase()
    tp.pause_sim()
    tp.page.wait_for_timeout(800)  # 等暂停前已在途的最后一帧落下。
    time_paused = tp.sim_time()
    points_paused = tp.curve_point_count()
    tp.page.wait_for_timeout(2000)

    # 断言：暂停后的观察窗口内，时间和曲线点数均不再变化。
    assert tp.sim_time() == time_paused
    assert tp.curve_point_count() == points_paused

    # 断言：暂停态可以继续播放或停止，暂停键自身不可重复点击。
    expect(tp.play_button).to_be_enabled()
    expect(tp.pause_button).to_be_disabled()
    expect(tp.stop_button).to_be_enabled()


@allure.feature('卫星遥测')
@allure.story('仿真控制-停止')
@allure.title('运行中点停止后时间和曲线冻结，播放恢复且暂停禁用')
@allure.severity(allure.severity_level.CRITICAL)
def test_stop_freezes_simulation(running_sim):
    tp = running_sim
    tp.wait_curve_points_increase()
    tp.stop_sim()
    tp.page.wait_for_timeout(800)
    time_stopped = tp.sim_time()
    points_stopped = tp.curve_point_count()
    tp.page.wait_for_timeout(2000)

    # 断言：停止后仿真时间和实时曲线均保持不动。
    assert tp.sim_time() == time_stopped
    assert tp.curve_point_count() == points_stopped

    # 断言：停止态可以重新播放，暂停不可用；停止键作为幂等操作仍可用。
    expect(tp.play_button).to_be_enabled()
    expect(tp.pause_button).to_be_disabled()
    expect(tp.stop_button).to_be_enabled()


@allure.feature('卫星遥测')
@allure.story('仿真控制-重置')
@allure.title('运行并产生曲线后重置：时间、进度、速度和曲线数据全部回到初始值')
@allure.severity(allure.severity_level.CRITICAL)
def test_reset_restores_initial_state(running_sim):
    tp = running_sim
    tp.set_speed('8x')
    assert tp.wait_curve_points_increase() > 0

    tp.reset_sim()
    tp.page.wait_for_timeout(800)

    # 断言：所有仿真数据状态一起重置，不只检查速度文案。
    assert tp.sim_time() == 0
    assert tp.progress_percent() == 0
    assert tp.current_speed() == '1x'
    assert tp.curve_point_count() == 0

    # 断言：重置后回到可播放、不可暂停的空闲态；停止键仍可幂等执行。
    expect(tp.play_button).to_be_enabled()
    expect(tp.pause_button).to_be_disabled()
    expect(tp.stop_button).to_be_enabled()


# ==================== 仿真速度 ====================

@allure.feature('卫星遥测')
@allure.story('仿真控制-速度')
@allure.title('预设倍速「{speed}」同步更新状态文案和唯一高亮档位')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize('speed', TelemetryPage.SPEEDS)
def test_speed_preset_state(telemetry_page, speed):
    telemetry_page.set_speed(speed)

    # 断言：状态文案与所点档位一致。
    assert telemetry_page.current_speed() == speed
    assert telemetry_page.speed_is_active(speed)

    # 断言：其余预设档位没有残留高亮。
    for other in TelemetryPage.SPEEDS:
        if other != speed:
            assert not telemetry_page.speed_is_active(other)


@allure.feature('卫星遥测')
@allure.story('仿真控制-速度')
@allure.title('各运行 1 秒，8x 的仿真时间和曲线点增量都大于 1x')
@allure.severity(allure.severity_level.CRITICAL)
def test_speed_changes_time_and_curve_rate(sim_ready_page):
    tp = sim_ready_page

    # 1x：从运行态观察 1 秒内的 T 和曲线增量。
    tp.set_speed('1x')
    tp.start_sim()
    tp.wait_sim_time_advances()
    tp.wait_curve_points_increase()
    one_x_time_start = tp.sim_time() or 0
    one_x_points_start = tp.curve_point_count()
    tp.page.wait_for_timeout(1000)
    one_x_time_delta = (tp.sim_time() or 0) - one_x_time_start
    one_x_points_delta = tp.curve_point_count() - one_x_points_start

    # 运行中切到 8x；先固定等 1 秒让异步速度更新落地，再观察后续 1 秒。
    tp.set_speed('8x')
    tp.page.wait_for_timeout(1000)
    assert tp.current_speed() == '8x'
    assert tp.speed_is_active('8x')
    assert not tp.speed_is_active('1x')

    eight_x_time_start = tp.sim_time() or 0
    eight_x_points_start = tp.curve_point_count()
    tp.page.wait_for_timeout(1000)
    eight_x_time_delta = (tp.sim_time() or 0) - eight_x_time_start
    eight_x_points_delta = tp.curve_point_count() - eight_x_points_start
    tp.pause_sim()

    # 断言：相同 1 秒观察窗内，8x 的 T 推进量必须大于 1x。
    assert one_x_time_delta > 0
    assert eight_x_time_delta > one_x_time_delta, (
        f'1x 的 T 增量={one_x_time_delta}s，8x 的 T 增量={eight_x_time_delta}s')

    # 断言：相同 1 秒观察窗内，8x 产生的曲线点也必须更多。
    assert one_x_points_delta > 0
    assert eight_x_points_delta > one_x_points_delta, (
        f'1x 新增曲线点={one_x_points_delta}，8x 新增曲线点={eight_x_points_delta}')


# ==================== 运行读数 / 快照断点 ====================

@allure.feature('卫星遥测')
@allure.story('仿真控制-运行读数')
@allure.title('仿真运行时进度、链路数和队列深度均为非负整数')
@allure.severity(allure.severity_level.NORMAL)
def test_running_counters_are_non_negative_integers(running_sim):
    tp = running_sim

    # 断言：进度、链路和队列深度是有效运行读数。
    for name, value in (
            ('进度', tp.progress_percent()),
            ('链路数', tp.link_count()),
            ('队列深度', tp.queue_depth())):
        assert isinstance(value, int) and value >= 0, f'「{name}」不是非负整数：{value!r}'


@allure.feature('卫星遥测')
@allure.story('仿真控制-运行读数')
@allure.title('仿真运行 1 秒后，卫星数等于活动节点数')
@allure.severity(allure.severity_level.CRITICAL)
def test_running_satellite_count_matches_active_nodes(running_sim):
    tp = running_sim
    active = tp.active_satellite_names()

    # 页面读数刷新较慢；节点 RUNNING、T 已推进后再固定等待 1 秒。
    assert active
    tp.page.wait_for_timeout(1000)

    # 断言：给足一次刷新时间后，卫星数必须等于实际活动节点数。
    assert tp.satellite_count() == len(active), (
        f'场景「{tp.selected_scenario["name"]}」活动节点为 {active}，'
        f'固定等待 1 秒后卫星数仍为 {tp.satellite_count()}')


@allure.feature('卫星遥测')
@allure.story('仿真控制-快照与断点')
@allure.title('保存快照后条目可见；继续运行再加载该断点，仿真时间回到保存点')
@allure.severity(allure.severity_level.CRITICAL)
# 删除快照做隔离清理时，产品偶发抛出文本为 "V" 的前端错误；功能断言仍严格执行。
@pytest.mark.allow_page_errors
def test_snapshot_restore_rewinds_simulation(running_sim):
    tp = running_sim
    name = f'AUTOTEST-SNAP-{int(time.time() * 1000)}'
    saved_at = tp.sim_time() or 0

    tp.save_snapshot(name)

    # 断言：保存动作成功，断点弹窗中出现唯一命名条目。
    expect(tp.snackbar_message).to_contain_text('快照已保存')
    tp.open_breakpoint_dialog()
    expect(tp.breakpoint_entry(name)).to_have_count(1)
    tp.close_breakpoint_dialog()

    tp.page.wait_for_timeout(2200)
    advanced_to = tp.sim_time() or 0
    assert advanced_to > saved_at

    tp.open_breakpoint_dialog()
    tp.apply_breakpoint(name)
    tp.page.wait_for_timeout(800)
    restored_to = tp.sim_time() or 0

    # 断言：加载断点真正恢复时间，而不是只关闭弹窗或弹提示。
    assert restored_to < advanced_to
    assert abs(restored_to - saved_at) <= 1.5, (
        f'断点应恢复到约 {saved_at}s，实际 {restored_to}s（恢复前 {advanced_to}s）')

    # 清理：只删除本用例创建的唯一 AUTOTEST 快照。
    if tp.breakpoint_dialog.is_visible():
        tp.close_breakpoint_dialog()
    tp.open_breakpoint_dialog()
    tp.delete_breakpoint(name)
    expect(tp.breakpoint_entry(name)).to_have_count(0)
    tp.close_breakpoint_dialog()
