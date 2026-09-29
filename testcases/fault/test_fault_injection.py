import json
import re

import allure
import pytest
from playwright.sync_api import expect

from pages.fault.injection_page import FaultInjectionPage


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
@allure.title('注入故障：出现下发提示，活动故障面板新增一条（带倒计时），FDIR 日志追加 INJECTION 记录')
@allure.severity(allure.severity_level.BLOCKER)
def test_injection_submit_creates_active_fault(running_injection_page):
    ip = running_injection_page
    before = ip.active_fault_count()

    name = ip.fault_type_names()[0]
    ip.select_fault_type(name)
    ip.duration_input.fill('30')
    ip.inject_button.click()

    # 断言：出现「已下发注入指令：<故障名>」提示
    expect(ip.page.get_by_text(f'已下发注入指令：{name}')).to_be_visible()
    # 断言：活动故障数 +1
    expect(ip.active_faults_heading).to_have_text(f'活动故障 ({before + 1})')
    # 断言：新增那条带倒计时（形如 "Ns"），不是「无活动故障」空态。新条目追加在末尾，
    # 所以取第 before 条（before==0 时就是第一条）
    expect(ip.active_faults_empty).to_have_count(0)
    countdown = ip.active_fault_countdown(before)
    assert re.fullmatch(r'\d+s', countdown), f'倒计时格式不对：{countdown!r}'
    # 断言：FDIR 日志里最新一条（追加在末尾）是这次注入的 INJECTION 记录
    log = ip.latest_fdir_log()
    assert log['type'] == 'INJECTION' and name in log['text'], f'FDIR 日志与本次注入不符：{log}'

    ip.close_active_fault(before)  # 收尾：手动恢复，别把 30s 的活动故障留给下一条用例


@allure.feature('故障/预案库')
@allure.story('故障注入')
@allure.title('点活动故障的 × ：出现恢复提示，这条消失，FDIR 日志追加一条「已恢复」的 RECOVERY 记录')
@allure.severity(allure.severity_level.BLOCKER)
def test_injection_close_active_fault_recovers(running_injection_page):
    ip = running_injection_page
    name = ip.fault_type_names()[0]
    ip.select_fault_type(name)
    ip.inject_button.click()
    expect(ip.active_faults_heading).to_have_text('活动故障 (1)')
    # 等「已下发注入指令」提示消失，避免和下面的恢复提示混在一起断言
    expect(ip.page.get_by_text(f'已下发注入指令：{name}')).to_have_count(0, timeout=10000)

    ip.close_active_fault(0)

    # 断言：出现「已下发恢复指令：<故障名>」提示
    expect(ip.page.get_by_text(f'已下发恢复指令：{name}')).to_be_visible()
    # 断言：活动故障回到 0、显示空态
    expect(ip.active_faults_heading).to_have_text('活动故障 (0)')
    expect(ip.active_faults_empty).to_be_visible()
    # 断言：FDIR 日志最新一条是 RECOVERY，文案里带「已恢复」和故障名
    log = ip.latest_fdir_log()
    assert log['type'] == 'RECOVERY', f'关闭后 FDIR 最新记录不是 RECOVERY：{log}'
    assert '已恢复' in log['text'] and name in log['text'], f'恢复记录文案不对：{log}'


@allure.feature('故障/预案库')
@allure.story('故障注入')
@allure.title('接口回归：注入故障打 fault-inject，点 × 恢复打 fault-recover，不是同一个请求')
@allure.severity(allure.severity_level.CRITICAL)
def test_injection_and_recovery_hit_different_apis(running_injection_page):
    ip = running_injection_page
    name = ip.fault_type_names()[0]
    ip.select_fault_type(name)

    with ip.page.expect_request(re.compile(r'/api/sim/fault-inject$')) as inject_req:
        ip.inject_button.click()
    expect(ip.active_faults_heading).to_have_text('活动故障 (1)')

    with ip.page.expect_request(re.compile(r'/api/sim/fault-recover')) as recover_req:
        ip.close_active_fault(0)
    expect(ip.active_faults_heading).to_have_text('活动故障 (0)')

    # 断言：两次都是 POST，且打的不是同一个接口——回归以前「注入和恢复发的是同一个
    # 请求」的 bug
    assert inject_req.value.method == 'POST' and recover_req.value.method == 'POST'
    assert inject_req.value.url != recover_req.value.url, \
        f'注入和恢复打了同一个接口：{inject_req.value.url}'


@allure.feature('故障/预案库')
@allure.story('故障注入')
@allure.title('改持续时长再注入：请求发送 45 秒，页面显示与 45 秒时长相符的倒计时')
@allure.severity(allure.severity_level.NORMAL)
def test_injection_duration_affects_countdown(running_injection_page):
    ip = running_injection_page
    name = ip.fault_type_names()[0]
    ip.select_fault_type(name)

    ip.duration_input.fill('45')
    try:
        with ip.page.expect_request(re.compile(r'/api/sim/fault-inject$')) as request_info:
            ip.inject_button.click()
        payload = json.loads(request_info.value.post_data)
        assert payload['duration'] == 45, f'输入 45 秒，注入接口实际发送 {payload}'
        expect(ip.active_faults_heading).to_have_text('活动故障 (1)')

        # 222 环境后端时间约快 2~3 秒，页面按后端 injectTime 计算时可能从 48 开始；
        # 同时给页面渲染留出少量耗时，因此 42~48 都属于 45 秒故障的合理初始值。
        countdown = ip.active_fault_countdown(0)
        match = re.fullmatch(r'(\d+)s', countdown)
        assert match, f'活动故障倒计时格式不对：{countdown!r}'
        seconds = int(match.group(1))
        assert 42 <= seconds <= 48, (
            f'注入接口已发送 duration=45，但页面倒计时初始值为 {seconds}s')
    finally:
        if ip.active_fault_count() > 0:
            ip.close_active_fault(0)  # 即使断言失败也恢复，不把活动故障留给后续用例


@allure.feature('故障/预案库')
@allure.story('故障注入')
@allure.title('持续时长到点：不用点 × ，倒计时结束后活动故障也会自动消失并记一条 RECOVERY')
@allure.severity(allure.severity_level.NORMAL)
def test_injection_duration_expiry_auto_recovers(running_injection_page):
    ip = running_injection_page
    name = ip.fault_type_names()[0]
    ip.select_fault_type(name)
    ip.duration_input.fill('4')          # 填个短时长——够断言先抓到「活动」态，又不用等太久
    ip.inject_button.click()
    expect(ip.active_faults_heading).to_have_text('活动故障 (1)')

    # 断言：不点 × ，倒计时结束后活动故障自己归零（轮询等待，不写死具体等几秒）
    expect(ip.active_faults_heading).to_have_text('活动故障 (0)', timeout=15000)
    expect(ip.active_faults_empty).to_be_visible()
    # 断言：FDIR 日志同样落一条 RECOVERY
    log = ip.latest_fdir_log()
    assert log['type'] == 'RECOVERY' and name in log['text'], f'到期后 FDIR 记录不对：{log}'


@allure.feature('故障/预案库')
@allure.story('故障注入')
@allure.title('「预案库」弹窗：左侧预案列表，点一条右侧出处置步骤，「执行预案」按钮当前是禁用的')
@allure.severity(allure.severity_level.NORMAL)
def test_injection_plan_library_dialog(injection_page):
    ip = injection_page
    ip.open_plan_library_dialog()

    # 断言：弹窗标题 + 左侧预案列表非空
    expect(ip.plan_library_dialog.get_by_role('heading', name='故障预案库')).to_be_visible()
    assert ip.plan_library_items().count() > 0, '预案库弹窗左侧列表为空'

    first_name = ip.plan_library_items().first.inner_text().strip()
    ip.select_plan_library_item(first_name)

    # 断言：右侧出现所点预案的名字和处置步骤
    expect(ip.plan_library_dialog.get_by_role('heading', name=first_name)).to_be_visible()
    expect(ip.plan_library_steps_label).to_be_visible()
    # 断言：「执行预案」按钮当前是禁用状态（预案未配置结构化执行指令）
    expect(ip.plan_library_execute_button).to_be_disabled()
