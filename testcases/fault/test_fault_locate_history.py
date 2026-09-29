import re
from datetime import datetime, timedelta

import allure
import pytest
from playwright.sync_api import expect

from pages.fault.fault_library_page import FaultLibraryPage
from pages.fault.locate_history_page import FaultLocateHistoryPage
from testcases.fault.pager_checks import (
    assert_next_page, assert_page_size_10, assert_total_stable)

_FMT = '%Y-%m-%dT%H:%M'   # datetime-local 输入格式


# ==================== 进入 ====================

@allure.feature('故障/预案库')
@allure.story('定位历史')
@allure.title('点「定位历史」进到该子标签，6 个子标签都在')
@allure.severity(allure.severity_level.CRITICAL)
def test_locate_history_opens(locate_history_page):
    lib = FaultLibraryPage(locate_history_page.page)
    for name in FaultLibraryPage.TABS:
        expect(lib.tab(name)).to_be_visible()
    expect(lib.tab('定位历史')).to_have_attribute('aria-selected', 'true')


# ==================== 每行字段（跨全部分页）====================

@allure.feature('故障/预案库')
@allure.story('定位历史')
@allure.title('全部分页每一行：时间/状态/编码/故障/等级/反馈 均符合各自的取值与格式')
@allure.severity(allure.severity_level.CRITICAL)
def test_locate_history_rows(locate_history_page):
    h = locate_history_page
    rows = h.all_rows_data()          # 跨所有分页
    if not rows:
        pytest.skip('当前没有定位历史记录')

    P = FaultLocateHistoryPage
    for r in rows:
        # 时间：固定格式 MM/DD HH:MM:SS
        assert re.match(P.TIME_RE, r['time']), f'时间格式不符：{r}'
        # 状态：命中 / 多命中 / 未命中
        assert r['status'] in P.STATUSES, f'未知状态：{r}'

        if r['status'] in P.MATCHED_STATUSES:
            # 命中或多命中：编码固定格式、故障名非空、等级是 I~IV
            assert re.match(P.CODE_RE, r['code']), f'命中行编码格式不符：{r}'
            assert r['fault'], f'命中行故障名为空：{r}'
            assert r['severity'] in P.SEVERITIES, f'命中行等级异常：{r}'
        else:
            # 未命中：编码 / 故障 是占位符（''或'-'），等级为空
            assert r['code'] in P.BLANKS and r['fault'] in P.BLANKS and not r['severity'], \
                f'未命中行字段不是空/占位：{r}'

        # 反馈列：两态之一 —— 未反馈(2 个按钮) 或 已反馈(0 按钮 + Chip「已确认」/「误报」)
        assert (r['fb_buttons'] == 2
                or (r['fb_buttons'] == 0 and r['fb_text'] in P.FEEDBACK_DONE)), \
            f'反馈列状态异常：buttons={r["fb_buttons"]} text={r["fb_text"]!r} row={r}'


# ==================== 按故障编码筛选（精确匹配）====================

@allure.feature('故障/预案库')
@allure.story('定位历史')
@allure.title('输入第一条记录的编码筛选，结果的编码列精确等于该编码')
@allure.severity(allure.severity_level.CRITICAL)
def test_locate_history_filter_by_code_exact(locate_history_page):
    h = locate_history_page
    hit_codes = [r['code'] for r in h.rows_data()
                 if r['status'] in h.MATCHED_STATUSES and r['code']]
    if not hit_codes:
        pytest.skip('当前页没有带编码的命中记录')

    target = hit_codes[0]
    base_total = h.total_count()

    h.filter_by_code(target)
    assert h.row_count() > 0
    # 断言：精确匹配 —— 结果编码列全等于所输编码
    assert set(h.codes()) == {target}, f'精确匹配失败，出现别的编码：{set(h.codes())}'
    assert h.total_count() <= base_total


@allure.feature('故障/预案库')
@allure.story('定位历史')
@allure.title('乱输编码不会崩：出现「暂无定位记录」空态、总数 0')
@allure.severity(allure.severity_level.NORMAL)
def test_locate_history_filter_garbage(locate_history_page):
    h = locate_history_page
    h.filter_by_code('!!!乱输入###ZZZ-999')
    expect(h.empty_hint).to_be_visible()
    assert h.total_count() == 0


# ==================== 时间筛选 ====================

@allure.feature('故障/预案库')
@allure.story('定位历史')
@allure.title('用已有的两条记录时间当区间：筛选后每条记录的时间都落在区间内')
@allure.severity(allure.severity_level.CRITICAL)
def test_locate_history_time_range_between_records(locate_history_page):
    h = locate_history_page
    if h.is_empty() or h.row_count() < 4:
        pytest.skip('记录不足，无法取两条时间做区间')

    now = datetime.now()
    ts = h.row_datetimes(now)                       # 当前页，新 -> 旧
    # 取中间靠前的两条当上界、中间靠后的两条当下界，各留 1 分钟余量（输入是分钟精度）
    hi = max(ts[1], ts[2]) + timedelta(minutes=1)
    lo = min(ts[-3], ts[-2]) - timedelta(minutes=1)
    base_total = h.total_count()

    h.set_time_range(start=lo.strftime(_FMT), end=hi.strftime(_FMT))

    data = h.rows_data()
    # 断言：按已有记录时间做区间，结果不该为空
    assert data, '结果为空，说明区间没框住任何已有记录'
    # 断言：筛选有效 —— 每条结果的时间都在 [lo, hi] 内
    for r in data:
        t = FaultLocateHistoryPage.parse_time(r['time'], now)
        assert lo <= t <= hi, f'记录 {r["time"]} 超出区间 [{lo:%m/%d %H:%M}, {hi:%m/%d %H:%M}]'
    # 断言：区间比不筛时收敛
    assert h.total_count() <= base_total


@allure.feature('故障/预案库')
@allure.story('定位历史')
@allure.title('结束时间设为最近一小时：结果里每条记录的时间都在这一小时内')
@allure.severity(allure.severity_level.NORMAL)
def test_locate_history_time_range_recent_hour(locate_history_page):
    h = locate_history_page
    if h.is_empty() or h.row_count() == 0:
        pytest.skip('当前没有定位历史记录')

    now = datetime.now()
    lo, hi = now - timedelta(hours=1), now + timedelta(minutes=1)
    h.set_time_range(start=lo.strftime(_FMT), end=hi.strftime(_FMT))

    # 最近一小时不一定有记录；有的话，断言它们确实都在这一小时内
    for r in h.rows_data():
        t = FaultLocateHistoryPage.parse_time(r['time'], now)
        assert lo <= t <= hi, f'记录 {r["time"]} 不在最近一小时内'


@allure.feature('故障/预案库')
@allure.story('定位历史')
@allure.title('开始时间设为未来日期：出现空态、总数 0、不崩')
@allure.severity(allure.severity_level.NORMAL)
def test_locate_history_start_time_future_empty(locate_history_page):
    h = locate_history_page
    future = (datetime.now() + timedelta(days=3650)).strftime(_FMT)
    h.set_time_range(start=future)
    expect(h.empty_hint).to_be_visible()
    assert h.total_count() == 0


# ==================== 分页（和目录同一套：每页行数、总数、翻页不重叠）====================

@allure.feature('故障/预案库')
@allure.story('定位历史')
@allure.title('改「每页行数」为 10，当前页行数与行号区间随之变化')
@allure.severity(allure.severity_level.NORMAL)
def test_locate_history_rows_per_page(locate_history_page):
    # 断言：每页行数改成 10 后，当前页正好 10 行、行号 1-10
    assert_page_size_10(locate_history_page)


@allure.feature('故障/预案库')
@allure.story('定位历史')
@allure.title('总条数不随「每页行数」变化')
@allure.severity(allure.severity_level.NORMAL)
def test_locate_history_total_stable(locate_history_page):
    # 断言：换 10 / 50 / 20 都不改变总条数
    assert_total_stable(locate_history_page)


@allure.feature('故障/预案库')
@allure.story('定位历史')
@allure.title('翻到下一页：行号区间接着往后、内容与上一页不重叠')
@allure.severity(allure.severity_level.NORMAL)
def test_locate_history_pagination(locate_history_page):
    # 断言：行号接着上一页。编码会重复，用时间+状态+编码+故障认行，两页不重叠
    assert_next_page(locate_history_page, locate_history_page.page_keys)


# ==================== 反馈：对 / 错 ====================

def _row_key(row):
    return (row['time'], row['status'], row['code'], row['fault'])


def _open_pending(h, kind):
    """给反馈相关用例单独造一条定位记录再操作，不用共享历史表里现成的——现成的可能
    正被同时/先后跑的其它用例（包括快速定位自己的反馈用例）抢着改，读到的会是别人
    刚改完的状态。"""
    created = h.api_create_pending()
    h.wait_own_pending_row(created['code'])
    return h.open_feedback(0, kind)


@allure.feature('故障/预案库')
@allure.story('定位历史')
@allure.title('点「标记为准确」弹出确认框，点取消后这条记录仍是未反馈')
@allure.severity(allure.severity_level.CRITICAL)
def test_locate_history_feedback_accurate_cancel(locate_history_page):
    h = locate_history_page
    before = _open_pending(h, '准确')
    # 断言：确认框说明这是「准确」，并且提交后不能撤销
    expect(h.feedback_dialog).to_contain_text(h.FEEDBACK_DIALOG['准确'])
    expect(h.feedback_dialog).to_contain_text('不可直接撤销')
    h.cancel_feedback()
    # 断言：取消后确认框关掉，按钮还在，没有变成「已确认」
    expect(h.feedback_dialog).to_be_hidden()
    after = h.row_by_key(_row_key(before))
    assert after is not None, f'取消后找不到原记录：{before}'
    assert after['fb_buttons'] == 2 and after['fb_text'] == '', f'取消后记录被改了：{after}'


@allure.feature('故障/预案库')
@allure.story('定位历史')
@allure.title('点「标记为准确」再点确认提交，这条记录变成「已确认」且不能再点')
@allure.severity(allure.severity_level.CRITICAL)
def test_locate_history_feedback_accurate_confirm(locate_history_page):
    h = locate_history_page
    before = _open_pending(h, '准确')
    h.confirm_feedback()
    # 断言：确认提交后这条记录变成「已确认」，两个按钮都没了
    after = h.wait_feedback(_row_key(before), '已确认')
    assert after['fb_buttons'] == 0


@allure.feature('故障/预案库')
@allure.story('定位历史')
@allure.title('点「标记为误报」弹出确认框，点取消后这条记录仍是未反馈')
@allure.severity(allure.severity_level.CRITICAL)
def test_locate_history_feedback_wrong_cancel(locate_history_page):
    h = locate_history_page
    before = _open_pending(h, '误报')
    # 断言：确认框说明这是「误报」，并且提交后不能撤销
    expect(h.feedback_dialog).to_contain_text(h.FEEDBACK_DIALOG['误报'])
    expect(h.feedback_dialog).to_contain_text('不可直接撤销')
    h.cancel_feedback()
    # 断言：取消后确认框关掉，按钮还在，没有变成「误报」
    expect(h.feedback_dialog).to_be_hidden()
    after = h.row_by_key(_row_key(before))
    assert after is not None, f'取消后找不到原记录：{before}'
    assert after['fb_buttons'] == 2 and after['fb_text'] == '', f'取消后记录被改了：{after}'


@allure.feature('故障/预案库')
@allure.story('定位历史')
@allure.title('点「标记为误报」再点确认提交，这条记录变成「误报」且不能再点')
@allure.severity(allure.severity_level.CRITICAL)
def test_locate_history_feedback_wrong_confirm(locate_history_page):
    h = locate_history_page
    before = _open_pending(h, '误报')
    h.confirm_feedback()
    # 断言：确认提交后这条记录变成「误报」，两个按钮都没了
    after = h.wait_feedback(_row_key(before), '误报')
    assert after['fb_buttons'] == 0
