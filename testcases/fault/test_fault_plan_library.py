import json
import re

import allure
import pytest
from playwright.sync_api import expect

from pages.fault.plan_library_page import FaultPlanLibraryPage
from pages.scenario.scenario_definition_page import ScenarioDefinitionPage


# 「预案库」子标签：处置预案的卡片列表 + 点开的预案详情。
# 点开后不断言 URL（路由后续可能改），只断言详情内容和所点卡片一致。


@allure.feature('故障/预案库')
@allure.story('预案库')
@allure.title('进入预案库，列出预案卡片，卡片带 预案名/关联故障编码/故障名/操作步骤/预期效果')
@allure.severity(allure.severity_level.CRITICAL)
def test_plan_library_has_plans(plan_library_page):
    plp = plan_library_page
    # 断言：列出至少一张预案卡
    assert plp.cards().count() > 0
    # 断言：首张卡片三个关键字段都有
    info = plp.card_info(0)
    assert info['plan'] and info['fault_code'] and info['fault_name'], f'卡片字段缺失：{info}'
    # 断言：卡片上直接展示的操作步骤摘要非空——不用点进详情就能看到
    assert plp.card_steps_summary(0), '卡片上的操作步骤摘要为空'
    # 断言：卡片上直接展示的预期效果非空，且带「预期:」前缀
    expected = plp.card_expected_summary(0)
    assert expected.startswith('预期'), f'卡片预期效果格式不对：{expected!r}'


@allure.feature('故障/预案库')
@allure.story('预案库')
@allure.title('搜索预案（模糊匹配）：按「{by}」都能搜到对应预案')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('by', ['故障编码', '故障名', '预案名'])
def test_plan_library_search(plan_library_page, by):
    plp = plan_library_page
    target = plp.card_info(0)          # 拿首张卡的三个字段轮流当搜索词
    kw = {'故障编码': target['fault_code'],
          '故障名': target['fault_name'],
          '预案名': target['plan']}[by]

    plp.search(kw)
    # 断言：有结果，且能搜到目标预案
    assert plp.cards().count() > 0
    titles = [plp.card_info(i)['plan'] for i in range(plp.cards().count())]
    assert target['plan'] in titles, f'搜「{kw}」没搜到目标预案「{target["plan"]}」，得到：{titles}'
    # 断言：每张结果卡都与关键字相关（预案名 / 编码 / 故障名 任一含 kw）
    for i in range(plp.cards().count()):
        c = plp.card_info(i)
        assert kw in c['plan'] or kw in c['fault_code'] or kw in c['fault_name'], \
            f'结果卡 {c} 与关键字「{kw}」无关'


@allure.feature('故障/预案库')
@allure.story('预案库')
@allure.title('点开一条预案（内嵌卡片 / 路由表格两种入口各跑一遍）：详情页的 预案名 / 关联故障 / 操作步骤 与列表里那条一致')
@allure.severity(allure.severity_level.CRITICAL)
def test_plan_library_open_detail(plan_detail_page):
    d = plan_detail_page
    picked = d.picked           # 进详情前，从列表（卡片或表格）读到的这条数据

    # 断言：详情页预案名 = 列表里那条的预案名
    assert d.detail_plan_name() == picked['plan'], \
        f'详情预案名 {d.detail_plan_name()!r} != 列表 {picked["plan"]!r}'
    # 断言：详情页「关联故障」行同时带上该故障的编码和名称
    linked = d.linked_fault_text()
    assert picked['fault_code'] in linked and picked['fault_name'] in linked, \
        f'关联故障行「{linked}」缺编码/名称：{picked}'
    # 断言：有「操作步骤」区块且至少一步
    expect(d.steps_heading).to_be_visible()
    assert len(d.step_texts()) > 0, '操作步骤为空'
    # 断言：有「预期效果」区块
    expect(d.expected_effect_heading).to_be_visible()


@allure.feature('故障/预案库')
@allure.story('预案库')
@allure.title('数据库已有预案：关联故障、步骤和预期效果与前端详情完全一致')
@allure.severity(allure.severity_level.BLOCKER)
def test_plan_detail_matches_database(dm8_plan_library_route_page, db_fault_plan):
    route = dm8_plan_library_route_page
    plan = db_fault_plan

    # arrange：数据库先选定一条已有「预案 → 故障」关联，再从前端按预案名定位同一条
    route.search(keyword=plan['name'])
    index = next(
        (i for i in range(route.rows().count())
         if route.row_info(i)['plan'] == plan['name']),
        None,
    )
    assert index is not None, f'前端预案库没有数据库预案：{plan["name"]!r}'
    row = route.row_info(index)

    # assert：列表行的预案及关联故障就是数据库所存的同一组值
    assert row['plan'] == plan['name']
    assert row['fault_code'] == plan['faultCode']
    assert row['fault_name'] == plan['faultName']

    # action：人工打开这一行的详情；详情组件与卡片版共用
    route.open_detail(index)
    detail = FaultPlanLibraryPage(route.page)
    detail.back_to_library_button.wait_for(state='visible', timeout=30000)

    # assert：详情字段不是“有内容”而已，必须等于实际持久化数据
    assert detail.detail_plan_name() == plan['name']
    linked_fault = detail.linked_fault_text()
    assert plan['faultCode'] in linked_fault and plan['faultName'] in linked_fault

    expected_steps = [item['action'] for item in json.loads(plan['steps'])]
    actual_steps = [re.sub(r'^\d+\.\s*', '', text) for text in detail.step_texts()]
    assert actual_steps == expected_steps
    assert detail.expected_effect_text() == plan['expectedResult']


@allure.feature('故障/预案库')
@allure.story('预案库')
@allure.title('点「仿真」：带仿真入口的预案卡跳到对应的场景定义页')
@allure.severity(allure.severity_level.NORMAL)
def test_plan_library_simulate_opens_scenario(plan_library_page):
    plp = plan_library_page
    # 不是每张卡都有仿真入口，先找一张有的
    index = next((i for i in range(plp.cards().count())
                  if plp.simulate_button(i).count() > 0), None)
    if index is None:
        pytest.skip('当前预案列表没有带仿真入口的卡片')

    plp.open_simulate(index)
    definition = ScenarioDefinitionPage(plp.page)

    # 断言：URL 跳到带 id 的场景定义页（仿真入口指向已存场景，不是新建）
    expect(plp.page).to_have_url(re.compile(r'/scenarios\?id=[^&]+$'))
    # 断言：场景定义页的标志标题可见
    expect(definition.heading).to_be_visible()
