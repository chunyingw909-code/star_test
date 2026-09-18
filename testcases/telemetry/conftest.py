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


# 已启动仿真节点、活动卫星已出现的页面。播放控制在节点启动前是禁用的。
@pytest.fixture
def sim_ready_page(satellite_scenario):
    satellite_scenario.start_nodes()
    visible = satellite_scenario.wait_active_satellites()
    assert visible, (
        f'场景「{satellite_scenario.selected_scenario["name"]}」配置了卫星，'
        '但启动节点后左侧仍没有活动卫星')
    return satellite_scenario


# 已启动仿真的卫星遥测页：选有卫星场景 → 启动节点 → 点▶ → 等顶部 T 开始走。
# 给「暂停 / 停止 / 快照 / 断点 / 曲线在动」这类必须仿真运行的用例用。
@pytest.fixture
def running_sim(sim_ready_page):
    sim_ready_page.start_sim()
    sim_ready_page.wait_sim_time_advances()
    return sim_ready_page
