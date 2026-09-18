import time

import pytest

from pages.scenario.scenario_drawer_page import ScenarioDrawerPage


# ==================== 场景 Tab - 基础抽屉 Fix ====================
# 打开主页右侧抽屉并固定在「场景」Tab，供列表、搜索和入口类用例复用。
@pytest.fixture
def scenario_drawer_page(home_page):
    return ScenarioDrawerPage(home_page).open()


# ==================== 场景 Tab - 场景切换 Fix ====================
# 每条切换用例从“正常运行模式”开始，避免浏览器残留的上次场景影响弹窗文案。
@pytest.fixture
def scenario_switch_page(scenario_drawer_page):
    scenario_drawer_page.set_current_scenario('正常运行模式')
    return scenario_drawer_page


# ==================== 场景 Tab - 快速创建/删除 Fix ====================
# 为写路径生成唯一名称；无论用例在哪一步失败，teardown 都会清理已创建的临时场景。
@pytest.fixture
def scenario_create_case(scenario_drawer_page):
    name = f'AUTOTEST-SCENE-{int(time.time() * 1000)}'
    yield scenario_drawer_page, name
    scenario_drawer_page.delete_scenario_if_present(name)
