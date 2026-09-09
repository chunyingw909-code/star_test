import pytest

from pages.telemetry.telemetry_page import TelemetryPage


# 进入卫星遥测模块（顶部导航 → 「卫星遥测」，等「仿真控制」面板出现）。
# teardown：把仿真停掉 + 重置，避免上一个用例的仿真状态 / 速度档污染下一个。
@pytest.fixture
def telemetry_page(home_page):
    tp = TelemetryPage(home_page).open()
    yield tp
    tp.teardown_sim()


# 已启动仿真的卫星遥测页：进模块 → 点▶ → 等顶部 T 开始走（确认真的跑起来了）。
# 给「暂停 / 停止 / 快照 / 断点 / 曲线在动」这类必须仿真运行的用例用。
@pytest.fixture
def running_sim(telemetry_page):
    telemetry_page.start_sim()
    telemetry_page.wait_sim_time_advances()
    return telemetry_page
