import re

import allure
import pytest
from playwright.sync_api import expect

from pages.scenario.scenario_definition_page import ScenarioDefinitionPage


# 预案库的独立路由版（/fault/plans，表格版）。列表结构和搜索方式跟内嵌卡片版不一样
# （见 FaultPlanLibraryRoutePage 类注释），所以列表相关用例单独一份；详情页两边共享，
# 详情断言在 test_fault_plan_library.py::test_plan_library_open_detail 里参数化覆盖了，
# 这里不重复。


@allure.feature('故障/预案库')
@allure.story('预案库-路由版')
@allure.title('路由版预案库：列出预案行，每行 预案编号/关联故障/操作步骤摘要/预期效果 都有内容')
@allure.severity(allure.severity_level.CRITICAL)
def test_route_plan_library_has_plans(plan_library_route_page):
    plp = plan_library_route_page
    # 断言：列出至少一行预案
    assert plp.rows().count() > 0
    # 断言：首行三个关键字段都有
    info = plp.row_info(0)
    assert info['plan'] and info['fault_code'] and info['fault_name'], f'行字段缺失：{info}'
    # 断言：操作步骤摘要 / 预期效果 两列也有内容
    assert info['steps_summary'], f'操作步骤摘要为空：{info}'
    assert info['expected'], f'预期效果为空：{info}'


@allure.feature('故障/预案库')
@allure.story('预案库-路由版')
@allure.title('路由版搜索（模糊匹配）：按「{by}」对应的输入框都能搜到对应预案')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('by', ['故障编码', '故障名', '预案名'])
def test_route_plan_library_search(plan_library_route_page, by):
    plp = plan_library_route_page
    target = plp.row_info(0)           # 拿首行的三个字段轮流当搜索词
    kw = {'故障编码': target['fault_code'],
          '故障名': target['fault_name'],
          '预案名': target['plan']}[by]
    search_kwargs = {'故障编码': {'fault_code': kw},
                      '故障名': {'fault_name': kw},
                      '预案名': {'keyword': kw}}[by]

    plp.search(**search_kwargs)
    # 断言：有结果，且能搜到目标预案
    assert plp.rows().count() > 0
    titles = [plp.row_info(i)['plan'] for i in range(plp.rows().count())]
    assert target['plan'] in titles, f'搜「{kw}」没搜到目标预案「{target["plan"]}」，得到：{titles}'
    # 断言：每行结果都与关键字相关（预案名 / 编码 / 故障名 任一含 kw）
    for i in range(plp.rows().count()):
        r = plp.row_info(i)
        assert kw in r['plan'] or kw in r['fault_code'] or kw in r['fault_name'], \
            f'结果行 {r} 与关键字「{kw}」无关'


@allure.feature('故障/预案库')
@allure.story('预案库-路由版')
@allure.title('路由版点「仿真」：带仿真入口的预案行跳到对应的场景定义页')
@allure.severity(allure.severity_level.NORMAL)
def test_route_plan_library_simulate_opens_scenario(plan_library_route_page):
    plp = plan_library_route_page
    # 不是每行都有仿真入口，先找一行有的
    index = next((i for i in range(plp.rows().count())
                  if plp.simulate_buttons.nth(i).count() > 0), None)
    if index is None:
        pytest.skip('当前预案列表没有带仿真入口的行')

    plp.open_simulate(index)
    definition = ScenarioDefinitionPage(plp.page)

    # 断言：URL 跳到带 id 的场景定义页（仿真入口指向已存场景，不是新建）
    expect(plp.page).to_have_url(re.compile(r'/scenarios\?id=[^&]+$'))
    # 断言：场景定义页的标志标题可见
    expect(definition.heading).to_be_visible()
