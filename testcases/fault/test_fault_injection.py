import re

import allure
import pytest
from playwright.sync_api import expect

from pages.fault.injection_page import FaultInjectionPage


# 「故障注入」子标签：左侧选故障类型 + 配置 + 「注入故障」，右侧 活动故障 / FDIR 日志。
# 仿真默认 STOPPED，点「注入故障」发 POST /api/sim/fault-inject 会 200 但不产生活动故障，
# 所以不会污染仿真状态。


@allure.feature('故障/预案库')
@allure.story('故障注入')
@allure.title('注入面板：标题、平台切换、两个下拉、搜索框都在，故障类型列表非空')
@allure.severity(allure.severity_level.CRITICAL)
def test_injection_panel(injection_page):
    ip = injection_page
    expect(ip.panel_heading).to_be_visible()
    expect(ip.platform_toggle).to_be_visible()
    expect(ip.channel_toggle).to_be_visible()
    expect(ip.target_satellite_select).to_be_visible()
    expect(ip.severity_select).to_be_visible()
    expect(ip.search_input).to_be_visible()
    assert ip.fault_type_names(), '故障类型列表里没有结构完整的「名称 + 等级」条目'


@allure.feature('故障/预案库')
@allure.story('故障注入')
@allure.title('平台切换：点「信道等效站」→ 它被选中、「卫星平台」取消；再点回来复原')
@allure.severity(allure.severity_level.CRITICAL)
def test_injection_platform_toggle(injection_page):
    ip = injection_page
    # 初始在「卫星平台」
    expect(ip.platform_toggle).to_have_attribute('aria-pressed', 'true')
    expect(ip.channel_toggle).to_have_attribute('aria-pressed', 'false')

    ip.switch_platform('信道等效站')
    expect(ip.channel_toggle).to_have_attribute('aria-pressed', 'true')
    expect(ip.platform_toggle).to_have_attribute('aria-pressed', 'false')

    ip.switch_platform('卫星平台')
    expect(ip.platform_toggle).to_have_attribute('aria-pressed', 'true')
    expect(ip.channel_toggle).to_have_attribute('aria-pressed', 'false')


@allure.feature('故障/预案库')
@allure.story('故障注入')
@allure.title('「{label}」下拉：有多个选项就切换；无目标卫星时验证空态')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('label', FaultInjectionPage.DROPDOWNS)
def test_injection_dropdown_select(injection_page, label):
    ip = injection_page
    sel = ip.dropdown(label)
    original = sel.inner_text().strip()

    opts = ip.dropdown_options(sel)
    # 系统未加载仿真卫星时目标卫星为空，这是当前正常空态。
    if label == '目标卫星' and not opts:
        assert not original.replace('\u200b', '').strip(), f'无卫星选项时下拉不应有值：{original!r}'
        return

    # 有数据时当前值必须来自选项；只有多个选项才有“切换到另一个”的意义。
    assert opts, f'「{label}」下拉没有任何选项'
    assert original in opts, f'当前值 {original!r} 不在选项里：{opts}'
    if len(opts) == 1:
        return

    picked = ip.select_other_option(sel)
    # 断言：选中的确实是另一个值，且下拉显示已切过去
    assert picked != original
    expect(sel).to_have_text(picked)


@allure.feature('故障/预案库')
@allure.story('故障注入')
@allure.title('搜索故障类型（模糊匹配）：命中收敛、乱输为空、清空复原')
@allure.severity(allure.severity_level.CRITICAL)
def test_injection_search(injection_page):
    ip = injection_page
    base = len(ip.fault_type_names())
    assert base > 1

    target = ip.fault_type_names()[0]
    ip.search(target)
    names = ip.fault_type_names()
    assert 0 < len(names) <= base
    assert target in names

    ip.search('zzz乱输入不存在xxx')
    assert ip.fault_type_names() == []

    ip.search('')
    assert len(ip.fault_type_names()) == base


@allure.feature('故障/预案库')
@allure.story('故障注入')
@allure.title('选中一个故障类型：该项高亮、提示消失、出现 描述 + 持续时长(默认60) + 注入按钮')
@allure.severity(allure.severity_level.CRITICAL)
def test_injection_select_fault_type(injection_page):
    ip = injection_page
    # 选中前：有提示、无注入按钮
    expect(ip.select_hint).to_be_visible()
    expect(ip.inject_button).to_have_count(0)

    name = ip.fault_type_names()[0]
    ip.select_fault_type(name)

    # 选中后：所点那项加了 Mui-selected
    expect(ip.fault_type_items().filter(has_text=name).first).to_have_class(re.compile(r'Mui-selected'))
    # 提示消失，出现 配置区
    expect(ip.select_hint).to_have_count(0)
    expect(ip.inject_button).to_be_visible()
    # 描述非空
    expect(ip.selected_fault_desc).to_be_visible()
    assert ip.selected_fault_desc.inner_text().strip()
    # 持续时长输入默认 60
    expect(ip.duration_input).to_be_visible()
    assert ip.duration_input.input_value() == '60'


@allure.feature('故障/预案库')
@allure.story('故障注入')
@allure.title('持续时长可改：填成 30 / 0 都能生效')
@allure.severity(allure.severity_level.NORMAL)
def test_injection_duration_editable(injection_page):
    ip = injection_page
    ip.select_fault_type(ip.fault_type_names()[0])

    ip.duration_input.fill('30')
    assert ip.duration_input.input_value() == '30'
    ip.duration_input.fill('0')
    assert ip.duration_input.input_value() == '0'


@allure.feature('故障/预案库')
@allure.story('故障注入')
@allure.title('活动故障 / FDIR 日志 面板：括号里的数字与下面条目数一致，为 0 时显示空态文案')
@allure.severity(allure.severity_level.CRITICAL)
def test_injection_side_panels(injection_page):
    ip = injection_page
    expect(ip.active_faults_heading).to_be_visible()
    # 「预案库」按钮在活动故障面板里
    expect(ip.plan_library_button).to_be_visible()

    n = ip.active_fault_count()
    # 断言：括号里的 N 与下面条目数一致
    assert ip.active_fault_items().count() == n
    if n == 0:
        # 断言：为 0 时显示「无活动故障」
        expect(ip.active_faults_empty).to_be_visible()

    # FDIR 日志：无条目时显示「无 FDIR 日志」
    expect(ip.fdir_panel).to_be_visible()
    if ip.fdir_log_items().count() == 0:
        expect(ip.fdir_empty).to_be_visible()


@allure.feature('故障/预案库')
@allure.story('故障注入')
@allure.title('点「注入故障」发 POST /api/sim/fault-inject（请求被测试拦截，不污染仿真）')
@allure.severity(allure.severity_level.CRITICAL)
def test_injection_submit(injection_page):
    ip = injection_page
    ip.select_fault_type(ip.fault_type_names()[0])

    captured = {}

    def mock_inject(route, request):
        captured['method'] = request.method
        captured['body'] = request.post_data
        route.fulfill(status=200, content_type='application/json', body='{}')

    ip.page.route('**/api/sim/fault-inject', mock_inject)
    try:
        with ip.page.expect_response(lambda r: 'fault-inject' in r.url) as ri:
            ip.inject_button.click()
        assert ri.value.status == 200
    finally:
        ip.page.unroute('**/api/sim/fault-inject', mock_inject)

    assert captured['method'] == 'POST'
    assert captured['body'], '注入请求应该带配置数据'
    # 请求没有离开浏览器，不会改变共享环境里的活动故障。
    assert ip.active_fault_count() == 0
