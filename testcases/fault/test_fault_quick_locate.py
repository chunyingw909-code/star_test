import re

import allure
import pytest
from playwright.sync_api import expect


@allure.feature('故障/预案库')
@allure.story('快速定位')
@allure.title('面板结构：遥测参数输入区、定位记录时间线都在，已有历史记录')
@allure.severity(allure.severity_level.CRITICAL)
def test_quick_locate_panel(quick_locate_page):
    qlp = quick_locate_page
    # 断言：表单区各控件都在
    expect(qlp.heading).to_be_visible()
    assert qlp.param_row_count() == 1, '进来应该有一行参数输入'
    expect(qlp.add_param_button).to_be_visible()
    expect(qlp.submit_button).to_be_visible()
    expect(qlp.json_accordion_summary).to_be_visible()
    # 断言：定位记录区有历史数据（这台环境一直有别的用例在写定位记录，不会是空的）
    expect(qlp.records_heading).to_be_visible()
    assert qlp.items().count() > 0, '定位记录时间线为空'


@allure.feature('故障/预案库')
@allure.story('快速定位')
@allure.title('「添加参数」加一行参数名/当前值输入框')
@allure.severity(allure.severity_level.NORMAL)
def test_quick_locate_add_param_row(quick_locate_page):
    qlp = quick_locate_page
    before = qlp.param_row_count()

    qlp.add_param_row()

    # 断言：多了一行
    assert qlp.param_row_count() == before + 1


@allure.feature('故障/预案库')
@allure.story('快速定位')
@allure.title('提交定位（命中）：定位结果显示已命中的故障，定位记录顶部出现新一条，时间是现在')
@allure.severity(allure.severity_level.BLOCKER)
def test_quick_locate_submit_hit(quick_locate_page):
    qlp = quick_locate_page
    now = qlp.beijing_now_hms()

    # 用进来就预填的 EPS_VBUS / 25.3（对应 EPS-001 母线欠压故障的判据）直接提交
    qlp.submit()

    # 断言：定位结果区显示「已命中」和匹配到的故障卡片
    expect(qlp.result_status_chip).to_have_text('已命中')
    assert qlp.result_card.count() > 0, '命中了但没有出现故障详情卡片'
    assert 'EPS-001' in qlp.result_card.inner_text()

    # 断言：定位记录时间线顶部插入了这次命中的新记录
    assert 'EPS-001' in qlp.item_text(0)
    # 断言：新记录时间是现在（允许一定秒级误差，等渲染 + 网络耗时）
    assert qlp.seconds_between(qlp.item_time(0), now) <= 30, \
        f'记录时间 {qlp.item_time(0)} 和提交时间 {now} 差太多'


@allure.feature('故障/预案库')
@allure.story('快速定位')
@allure.title('提交定位（未命中）：定位结果显示未命中提示，定位记录也记一条「未命中」')
@allure.severity(allure.severity_level.CRITICAL)
def test_quick_locate_submit_miss(quick_locate_page):
    qlp = quick_locate_page
    qlp.fill_param('ZZ_NO_SUCH_PARAM', 0)

    qlp.submit()

    # 断言：定位结果区显示「未命中」，没有故障卡片，有对应提示文案
    expect(qlp.result_status_chip).to_have_text('未命中')
    assert qlp.result_card.count() == 0
    expect(qlp.result_miss_hint).to_be_visible()
    # 断言：定位记录顶部这条也是「未命中」
    assert qlp.item_is_miss(0)


@allure.feature('故障/预案库')
@allure.story('快速定位')
@allure.title('「重定位」：用原参数重新提交一次，定位记录顶部再插入一条新记录')
@allure.severity(allure.severity_level.CRITICAL)
def test_quick_locate_relocate(quick_locate_page):
    qlp = quick_locate_page
    qlp.submit()                       # 先提交一次（默认 EPS_VBUS/25.3），产生一条命中记录
    now = qlp.beijing_now_hms()

    qlp.relocate(0)

    # 断言：顶部这条是「重定位」新产生的——命中内容和原来那次一样（同样的参数），
    # 时间刷新成了现在，且是刚产生、还没反馈的状态
    assert 'EPS-001' in qlp.item_text(0)
    assert qlp.seconds_between(qlp.item_time(0), now) <= 30
    assert qlp.item_has_pending_feedback(0)


@allure.feature('故障/预案库')
@allure.story('快速定位')
@allure.title('反馈「{feedback}」：立即生效（没有二次确认弹窗），Chip 变成「{chip_label}」')
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.parametrize('feedback,chip_label', [('准确', '已确认'), ('误报', '误报')])
def test_quick_locate_feedback(quick_locate_page, feedback, chip_label):
    qlp = quick_locate_page
    qlp.submit()
    assert qlp.item_has_pending_feedback(0), '刚提交的记录应该还没反馈'

    qlp.give_feedback(0, feedback)

    # 断言：反馈按钮消失，换成对应的 Chip；点了立即生效，不用过确认弹窗
    expect(qlp.page.get_by_role('dialog')).to_have_count(0)
    assert not qlp.item_has_pending_feedback(0)
    assert qlp.item_feedback_label(0) == chip_label


@allure.feature('故障/预案库')
@allure.story('快速定位')
@allure.title('粘贴 JSON 提交：格式对时和手填参数一样能定位出结果')
@allure.severity(allure.severity_level.CRITICAL)
def test_quick_locate_json_valid_submits(quick_locate_page):
    qlp = quick_locate_page

    qlp.submit_json('[{"param":"EPS_VBUS","value":25.3}]')
    qlp.result_heading.wait_for(state='visible')

    # 断言：走 JSON 路径一样能定位命中，行为和手填参数提交一致
    expect(qlp.result_status_chip).to_have_text('已命中')
    assert 'EPS-001' in qlp.item_text(0)


@allure.feature('故障/预案库')
@allure.story('快速定位')
@allure.title('粘贴 JSON 格式不对：提示「JSON 解析失败，请检查格式」，不发请求')
@allure.severity(allure.severity_level.CRITICAL)
def test_quick_locate_json_invalid_format(quick_locate_page):
    qlp = quick_locate_page
    fired = []
    qlp.page.on('request', lambda r: fired.append(r.url)
                if r.method == 'POST' and r.url.endswith('/api/fault/locate') else None)

    qlp.submit_json('{not valid json')
    qlp.page.wait_for_timeout(500)

    # 断言：格式错误提示出现，没有真的发定位请求
    expect(qlp.json_error_text).to_be_visible()
    assert not fired, 'JSON 格式错误时不应该发请求'
