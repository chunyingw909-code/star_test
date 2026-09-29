import time

import pytest

from pages.scenario.control_drawer_page import ControlDrawerPage
from pages.scenario.scenario_drawer_page import ScenarioDrawerPage


# ==================== 场景 Tab - 基础抽屉 Fix ====================
# 打开主页右侧抽屉并固定在「场景」Tab，供列表、搜索和入口类用例复用。
@pytest.fixture
def scenario_drawer_page(home_page):
    return ScenarioDrawerPage(home_page).open()


# ==================== 管控 Tab - 基础抽屉 Fix ====================
# 打开主页右侧抽屉并固定在「管控」Tab，供节点管控、指令序列相关用例复用。
@pytest.fixture
def control_drawer_page(home_page):
    return ControlDrawerPage(home_page).open()


# ==================== 场景 Tab - 场景切换 Fix ====================
# 从 /api/scenarios 当前响应中取两条不同场景；不依赖固定名称或数据库 ID。
@pytest.fixture
def scenario_switch_page(scenario_drawer_page):
    scenarios = scenario_drawer_page.scenario_inventory()
    assert len(scenarios) >= 2, f'场景切换至少需要 2 条场景，当前为 {scenarios}'
    source, target = scenarios[-1], scenarios[0]
    scenario_drawer_page.set_current_scenario(source)
    return scenario_drawer_page, source['name'], target['name']


# ==================== 场景 Tab - 快速创建/删除 Fix ====================
# 为写路径生成唯一名称；无论用例在哪一步失败，teardown 都会清理已创建的临时场景。
@pytest.fixture
def scenario_create_case(scenario_drawer_page):
    name = f'AUTOTEST-SCENE-{int(time.time() * 1000)}'
    yield scenario_drawer_page, name
    scenario_drawer_page.delete_scenario_if_present(name)
