import allure
import pytest
from playwright.sync_api import expect


# 「预案库」子标签：处置预案的卡片列表 + 点开的预案详情。
# 点开后不断言 URL（路由后续可能改），只断言详情内容和所点卡片一致。


@allure.feature('故障/预案库')
@allure.story('预案库')
@allure.title('进入预案库，列出预案卡片，卡片带 预案名/关联故障编码/故障名')
@allure.severity(allure.severity_level.CRITICAL)
def test_plan_library_has_plans(plan_library_page):
    plp = plan_library_page
    # 断言：列出至少一张预案卡
    assert plp.cards().count() > 0
    # 断言：首张卡片三个关键字段都有
    info = plp.card_info(0)
    assert info['plan'] and info['fault_code'] and info['fault_name'], f'卡片字段缺失：{info}'


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
@allure.title('点开一张预案：详情页的 预案名 / 关联故障 / 操作步骤 与所点卡片一致')
@allure.severity(allure.severity_level.CRITICAL)
def test_plan_library_open_detail(plan_library_page):
    plp = plan_library_page
    picked = plp.open_plan(0)          # 仿 FaultDetailPage.opened：记下这张卡是什么

    # 断言：详情页预案名 = 所点卡片的预案名
    assert plp.detail_plan_name() == picked['plan'], \
        f'详情预案名 {plp.detail_plan_name()!r} != 卡片 {picked["plan"]!r}'
    # 断言：详情页「关联故障」行同时带上该故障的编码和名称
    linked = plp.linked_fault_text()
    assert picked['fault_code'] in linked and picked['fault_name'] in linked, \
        f'关联故障行「{linked}」缺编码/名称：{picked}'
    # 断言：有「操作步骤」区块且至少一步
    expect(plp.steps_heading).to_be_visible()
    assert len(plp.step_texts()) > 0, '操作步骤为空'
    # 断言：有「预期效果」区块
    expect(plp.expected_effect_heading).to_be_visible()
