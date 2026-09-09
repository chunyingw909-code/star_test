import time

import allure
import pytest
from playwright.sync_api import expect

from pages.telemetry.telemetry_page import TelemetryPage


# 卫星遥测 +「仿真控制」完整流程用例。
# 覆盖：进入模块、5 个分系统切换、模拟/真实节点切换、播放/暂停/停止/重置、
#       速度档、进度读数、保存快照 / 加载断点、卫星选择、仿真节点、实时曲线时间窗、批量修改。
# 断言口径：能确定的行为（档位切换 / T 递增 / snackbar / 弹窗）严格断言；
#           已知实现不稳或非本轮重点的（自定义倍速生效、卫星切换生效、计数变化）只断言
#           "可点击 / 有响应 / 不崩"。前端未捕获报错由根 conftest 的 fail_on_page_error 兜底。


# ==================== 进入模块 ====================

@allure.feature('卫星遥测')
@allure.story('仿真控制-进入模块')
@allure.title('点顶部「卫星遥测」进入，显示「星座数字验证系统」+「仿真控制」面板，默认停在「供配电」')
@allure.severity(allure.severity_level.BLOCKER)
def test_enter_module(telemetry_page):
    expect(telemetry_page.title).to_be_visible()
    expect(telemetry_page.sim_control_heading).to_be_visible()
    assert telemetry_page.selected_subtab() == '供配电'


# ==================== 分系统子标签（5 个模式切换）====================

@allure.feature('卫星遥测')
@allure.story('仿真控制-分系统切换')
@allure.title('点分系统「{name}」→ 它被选中，其余全部取消选中')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('name', TelemetryPage.SUBTABS)
def test_subtab_switch(telemetry_page, name):
    telemetry_page.open_subtab(name)
    expect(telemetry_page.subtab(name)).to_have_attribute('aria-selected', 'true')
    for other in TelemetryPage.SUBTABS:
        if other != name:
            expect(telemetry_page.subtab(other)).to_have_attribute('aria-selected', 'false')


@allure.feature('卫星遥测')
@allure.story('仿真控制-分系统切换')
@allure.title('5 个分系统连续来回切两轮，选中态始终跟手、不串页、不报错')
@allure.severity(allure.severity_level.NORMAL)
def test_subtabs_rapid_roundtrip(telemetry_page):
    order = TelemetryPage.SUBTABS + list(reversed(TelemetryPage.SUBTABS))
    for name in order:
        telemetry_page.open_subtab(name)
        assert telemetry_page.selected_subtab() == name, f'切到「{name}」后当前却是「{telemetry_page.selected_subtab()}」'
    # 收尾停在第一个，面板仍健康
    telemetry_page.open_subtab('供配电')
    expect(telemetry_page.sim_control_heading).to_be_visible()


# ==================== 模拟节点 / 真实节点 ====================

@allure.feature('卫星遥测')
@allure.story('仿真控制-节点模式')
@allure.title('点「真实节点」→ 它被按下、「模拟节点」弹起；点回「模拟节点」复原')
@allure.severity(allure.severity_level.CRITICAL)
def test_node_mode_toggle(telemetry_page):
    assert telemetry_page.node_mode() == 'sim'          # 默认模拟节点

    telemetry_page.set_node_mode('real')
    expect(telemetry_page.real_node_button).to_have_attribute('aria-pressed', 'true')
    expect(telemetry_page.sim_node_button).to_have_attribute('aria-pressed', 'false')

    telemetry_page.set_node_mode('sim')
    expect(telemetry_page.sim_node_button).to_have_attribute('aria-pressed', 'true')
    expect(telemetry_page.real_node_button).to_have_attribute('aria-pressed', 'false')


@allure.feature('卫星遥测')
@allure.story('仿真控制-节点模式')
@allure.title('切到「真实节点」显示「节点预留中，暂不可用」，切回「模拟节点」恢复正常')
@allure.severity(allure.severity_level.NORMAL)
def test_real_node_shows_reserved_notice(telemetry_page):
    telemetry_page.set_node_mode('real')
    expect(telemetry_page.real_node_notice).to_be_visible()
    telemetry_page.set_node_mode('sim')
    expect(telemetry_page.sim_control_heading).to_be_visible()


# ==================== 播放 / 暂停 / 停止 / 重置 ====================

@allure.feature('卫星遥测')
@allure.story('仿真控制-播放控制')
@allure.title('点▶启动：暂停键可用、播放键置灰，顶部 T 开始递增，实时曲线区出现')
@allure.severity(allure.severity_level.BLOCKER)
def test_start_sim_runs_and_shows_curve(telemetry_page):
    tp = telemetry_page
    expect(tp.pause_button).to_be_disabled()            # 启动前暂停不可用

    tp.start_sim()
    t = tp.wait_sim_time_advances()
    assert t and t > 0, f'启动后顶部 T 未开始递增（读到 {t}）'
    expect(tp.pause_button).to_be_enabled()
    expect(tp.play_button).to_be_disabled()
    expect(tp.curve_heading).to_be_visible()
    expect(tp.curve_chart).to_be_visible()


@allure.feature('卫星遥测')
@allure.story('仿真控制-播放控制')
@allure.title('运行中点⏸暂停：仿真时间冻结、不再推进')
@allure.severity(allure.severity_level.CRITICAL)
def test_pause_sim(running_sim):
    tp = running_sim
    t1 = tp.sim_time() or 0
    tp.pause_sim()
    tp.page.wait_for_timeout(3000)
    t2 = tp.sim_time() or 0
    # 暂停后 T 基本冻结（放宽 2s，容忍暂停瞬间的最后一帧）
    assert (t2 - t1) < 2.0, f'点暂停后仿真时间仍在推进：T {t1}s → {t2}s'
    expect(tp.sim_control_heading).to_be_visible()


@allure.feature('卫星遥测')
@allure.story('仿真控制-播放控制')
@allure.title('运行中点⏹停止：仿真结束，播放键恢复可用、暂停键置灰')
@allure.severity(allure.severity_level.CRITICAL)
def test_stop_sim(running_sim):
    running_sim.stop_sim()
    expect(running_sim.play_button).to_be_enabled()
    expect(running_sim.pause_button).to_be_disabled()


@allure.feature('卫星遥测')
@allure.story('仿真控制-播放控制')
@allure.title('改速度档 + 运行后点「重置」：T 归零、速度回到 1x、进度归零')
@allure.severity(allure.severity_level.CRITICAL)
def test_reset_clears_progress(running_sim):
    tp = running_sim
    tp.set_speed('8x')
    assert tp.current_speed() == '8x'

    tp.reset_sim()
    tp.page.wait_for_timeout(800)
    assert (tp.sim_time() or 0) == 0, f'重置后 T 应为 0，实际 {tp.sim_time()}'
    assert tp.speed_is_active('1x'), '重置后速度档应回到 1x'
    assert (tp.progress_percent() or 0) == 0


# ==================== 仿真速度 ====================

@allure.feature('卫星遥测')
@allure.story('仿真控制-速度')
@allure.title('点速度档「{speed}」→「速度: {speed}」文案更新，该档高亮为当前档')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('speed', TelemetryPage.SPEEDS)
def test_speed_preset(telemetry_page, speed):
    telemetry_page.set_speed(speed)
    expect(telemetry_page.speed_label).to_contain_text(f'速度: {speed}')
    assert telemetry_page.current_speed() == speed
    assert telemetry_page.speed_is_active(speed)


@allure.feature('卫星遥测')
@allure.story('仿真控制-速度')
@allure.title('速度档 16x → 1x 来回切，文案与高亮同步')
@allure.severity(allure.severity_level.NORMAL)
def test_speed_preset_roundtrip(telemetry_page):
    telemetry_page.set_speed('16x')
    assert telemetry_page.current_speed() == '16x'
    telemetry_page.set_speed('1x')
    assert telemetry_page.current_speed() == '1x'
    assert telemetry_page.speed_is_active('1x')
    assert not telemetry_page.speed_is_active('16x')


@allure.feature('卫星遥测')
@allure.story('仿真控制-速度')
@allure.title('自定义倍速输入框可填写、「应用」可点击，操作后面板不报错')
@allure.severity(allure.severity_level.NORMAL)
def test_custom_speed_clickable(telemetry_page):
    # 只验证"能填、能点、不崩"；自定义倍速是否真正生效不在本用例断言范围内
    expect(telemetry_page.custom_speed_input).to_be_visible()
    telemetry_page.set_custom_speed('0.1')
    expect(telemetry_page.custom_speed_input).to_have_value('0.1')
    expect(telemetry_page.sim_control_heading).to_be_visible()


# ==================== 进度读数 ====================

@allure.feature('卫星遥测')
@allure.story('仿真控制-进度读数')
@allure.title('进度 / 卫星数 / 链路数 / 队列深度 四项均能读到数字')
@allure.severity(allure.severity_level.NORMAL)
def test_counters_readable(telemetry_page):
    tp = telemetry_page
    for name, val in (('进度', tp.progress_percent()), ('卫星数', tp.satellite_count()),
                      ('链路数', tp.link_count()), ('队列深度', tp.queue_depth())):
        assert isinstance(val, int) and val >= 0, f'「{name}」读到的不是非负整数：{val!r}'


@allure.feature('卫星遥测')
@allure.story('仿真控制-进度读数')
@allure.title('点▶启动等待片刻，顶部 T 由 0 变为大于 0')
@allure.severity(allure.severity_level.CRITICAL)
def test_time_advances_after_start(telemetry_page):
    assert (telemetry_page.sim_time() or 0) == 0
    telemetry_page.start_sim()
    t = telemetry_page.wait_sim_time_advances()
    assert t and t > 0, f'启动后等待仍未见 T 递增（读到 {t}）'


# ==================== 保存快照 / 加载断点 ====================

@allure.feature('卫星遥测')
@allure.story('仿真控制-快照与断点')
@allure.title('运行中「保存快照」并命名 → 提示「快照已保存」')
@allure.severity(allure.severity_level.CRITICAL)
# 收尾会删断点条目，同 test_snapshot_appears_and_deletable，偶发前端报错 "V"，豁免兜底。
@pytest.mark.allow_page_errors
def test_save_snapshot_shows_toast(running_sim):
    tp = running_sim
    # 保存快照按钮在仿真启动后才可用
    expect(tp.save_snapshot_button).to_be_enabled()
    name = f'AUTOTEST-SNAP-{int(time.time() * 1000)}'
    tp.save_snapshot(name)
    expect(tp.snackbar_message).to_contain_text('快照已保存')
    # 收尾：删掉本条快照，避免持久化到后端堆积
    tp.open_breakpoint_dialog()
    tp.delete_breakpoint(name)
    tp.close_breakpoint_dialog()


@allure.feature('卫星遥测')
@allure.story('仿真控制-快照与断点')
@allure.title('保存快照后点「加载断点」，「断点恢复」弹窗里能看到该快照，并可删除')
@allure.severity(allure.severity_level.CRITICAL)
# 现状：删除断点条目会偶发触发一个前端未捕获报错（错误文本仅 "V"），
# 功能本身（条目消失）正常。豁免 fail_on_page_error 兜底，缺陷另见缺陷清单。
@pytest.mark.allow_page_errors
def test_snapshot_appears_and_deletable_in_breakpoint_dialog(running_sim):
    tp = running_sim
    name = f'AUTOTEST-SNAP-{int(time.time() * 1000)}'
    tp.save_snapshot(name)
    expect(tp.snackbar_message).to_contain_text('快照已保存')

    tp.open_breakpoint_dialog()
    expect(tp.breakpoint_dialog).to_be_visible()
    expect(tp.breakpoint_entry(name)).to_be_visible()      # 出现在断点弹窗

    tp.delete_breakpoint(name)
    expect(tp.breakpoint_entry(name)).to_have_count(0)     # 删掉后消失
    tp.close_breakpoint_dialog()


# ==================== 卫星选择 / 仿真节点 ====================

@allure.feature('卫星遥测')
@allure.story('仿真控制-卫星选择')
@allure.title('卫星选择 SAT-01/02/03 三个按钮均可见可点击，点击后面板不报错')
@allure.severity(allure.severity_level.NORMAL)
def test_satellite_buttons_clickable(telemetry_page):
    for n in (1, 2, 3):
        expect(telemetry_page.satellite_button(n).first).to_be_visible()
    telemetry_page.select_satellite(2)
    telemetry_page.page.wait_for_timeout(500)
    telemetry_page.select_satellite(1)
    expect(telemetry_page.sim_control_heading).to_be_visible()


@allure.feature('卫星遥测')
@allure.story('仿真控制-仿真节点')
@allure.title('仿真节点面板：「启动」按钮可用，每个节点行都有停止图标按钮')
@allure.severity(allure.severity_level.NORMAL)
def test_node_controls_present(telemetry_page):
    expect(telemetry_page.node_start_button).to_be_enabled()
    assert telemetry_page.node_stop_buttons.count() >= 1


# ==================== 实时曲线时间窗 ====================

@allure.feature('卫星遥测')
@allure.story('仿真控制-实时曲线')
@allure.title('实时曲线时间窗档「{rng}」可点击，点击后成为当前档')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize('rng', TelemetryPage.CURVE_RANGES)
def test_curve_range_switch(telemetry_page, rng):
    telemetry_page.set_curve_range(rng)
    telemetry_page.page.wait_for_timeout(300)
    assert telemetry_page.curve_range_is_active(rng), f'点「{rng}」后它未成为当前档'


# ==================== 批量修改 ====================

@allure.feature('卫星遥测')
@allure.story('仿真控制-批量修改')
@allure.title('勾选遥测参数后「批量修改」由灰变亮，点开弹出对话框，取消可关闭')
@allure.severity(allure.severity_level.NORMAL)
def test_batch_edit_opens_after_select(telemetry_page):
    tp = telemetry_page
    expect(tp.batch_edit_button).to_be_disabled()       # 未勾选时置灰
    tp.select_first_param()
    expect(tp.batch_edit_button).to_be_enabled()

    tp.open_batch_edit()
    expect(tp.batch_edit_dialog).to_be_visible()
    tp.close_batch_edit()
    expect(tp.batch_edit_dialog).to_have_count(0)
