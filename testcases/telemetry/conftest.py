import pytest

from pages.telemetry.telemetry_page import TelemetryPage


# 进入卫星遥测模块（顶部导航 → 「卫星遥测」，等「仿真控制」面板出现）。
# teardown：把仿真停掉 + 重置，避免上一个用例的仿真状态 / 速度档污染下一个。
@pytest.fixture
def telemetry_page(home_page):
    tp = TelemetryPage(home_page).open()
    yield tp
    tp.teardown_sim()


# 动态选择一条配置了卫星的场景。场景发现走只读接口，选择走应用自己的
# sarsat_last_scenario localStorage 键，不依赖右侧抽屉 DOM。
@pytest.fixture
def satellite_scenario(telemetry_page):
    scenario = telemetry_page.select_first_scenario_with_satellites()
    assert scenario, '当前没有任何配置了卫星的场景'
    assert telemetry_page.configured_satellites
    return telemetry_page


# 未配置卫星场景 Fix
# 只接受正式接口中真实存在的无卫星场景，不 mock、不修改有卫星业务场景。
# 当前环境没有时明确跳过；待产品支持真实空场景后，这条用例会自动开始执行。
@pytest.fixture
def empty_satellite_scenario(telemetry_page):
    scenario = telemetry_page.find_scenario_without_satellites()
    if scenario is None:
        count = len(telemetry_page.scenario_inventory())
        pytest.skip(
            f'当前 {count} 个场景都被后端配置了卫星，没有真实无卫星场景')
    telemetry_page.select_scenario(scenario)
    return telemetry_page


# 多卫星配置场景 Fix
# 不启动额外节点，用于验证活动/停止卫星在选择区的差异。
@pytest.fixture
def multi_satellite_scenario(telemetry_page):
    scenario = telemetry_page.find_scenario_with_satellites(min_count=2)
    if scenario is None:
        pytest.skip('当前没有配置至少 2 颗卫星的场景')
    telemetry_page.select_scenario(scenario)
    return telemetry_page


# 节点未启动 Fix
# 遍历 222 的真实有卫星场景，选择一条当前没有运行节点的场景；不停止共享节点，
# 也不因为当前选中的某个场景正在运行就跳过整条用例。
@pytest.fixture
def stopped_satellite_scenario(telemetry_page):
    candidates = [
        scenario for scenario in telemetry_page.scenario_inventory()
        if scenario['satellites']
    ]
    candidates.sort(key=lambda item: item['template'])
    checked = {}
    for scenario in candidates:
        telemetry_page.select_scenario(scenario)
        active = telemetry_page.active_satellite_names()
        checked[scenario['name']] = active
        if not active:
            return telemetry_page
    pytest.fail(f'222 所有有卫星场景都已有运行节点，无法验证停止态：{checked}')


# 已启动仿真节点、活动卫星已出现的页面。节点进程是整组仿真测试的共享昂贵前置；
# 缺少时只启动一颗，结束时仅停止/重置仿真循环，不在每条用例之间反复冷启动节点。
@pytest.fixture
def sim_ready_page(satellite_scenario):
    satellite_scenario.ensure_one_active_node()
    try:
        yield satellite_scenario
    finally:
        satellite_scenario.teardown_sim()


# 已启动仿真的卫星遥测页：选有卫星场景 → 启动节点 → 点▶ → 等顶部 T 开始走。
# 给「暂停 / 停止 / 快照 / 断点 / 曲线在动」这类必须仿真运行的用例用。
@pytest.fixture
def running_sim(sim_ready_page):
    sim_ready_page.start_sim()
    sim_ready_page.wait_sim_time_advances()
    return sim_ready_page
