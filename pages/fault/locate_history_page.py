import time
from datetime import datetime, timedelta

from common.utils import api_fetch, fault_root, wait_until_stable
from pages.fault.mui_pager import MuiTablePager


class FaultLocateHistoryPage:
    """故障/预案库 -「定位历史」子标签：过去的定位记录表。

    两种入口内容完全一致（表格结构/筛选/分页文案/反馈弹窗文案逐字相同），差别只在：
    内嵌 Tab 版本（主壳内点「定位历史」进，URL 仍 /zh-CN）外层有 data-testid=
    fault-catalog-root；独立路由版（/zh-CN/fault/history，直接改 URL / 头像菜单「故障
    管理」/ 先进快速定位再切都能进）没有这层包裹。root 用 fault_root() 兜底，两边通用。

    列：时间 / 状态 / 编码 / 故障 / 等级 / 反馈。
    - 状态只有「命中」/「未命中」；未命中时 编码 / 故障 是占位符「-」，等级为空。
    - 「反馈」列两态：未反馈 = 「标记为准确」「标记为误报」两个按钮；已反馈 = Chip
      「已确认」/「误报」，没有按钮。点按钮先出确认框：取消不动这条记录，
      「确认提交」之后不可撤销，按钮换成对应 Chip。
    顶部筛选：开始 / 结束时间（原生 datetime-local）+ 故障编码。
    分页和目录是同一套 MUI 分页（每页 10 / 20 / 50）。

    对应用例：testcases/fault/test_fault_locate_history.py
    """

    STATUSES = ('命中', '多命中', '未命中')
    MATCHED_STATUSES = ('命中', '多命中')
    SEVERITIES = ('I', 'II', 'III', 'IV')
    FEEDBACK_DONE = ('已确认', '误报')          # 已反馈行反馈列 Chip 的文字
    FEEDBACK_ACCURATE = '标记为准确'
    FEEDBACK_WRONG = '标记为误报'
    # 确认框正文。按钮是「取消 / 确认提交」，不是「确定」。
    FEEDBACK_DIALOG = {
        '准确': '确认该定位结果准确',
        '误报': '确认将该定位结果标记为误报',
    }
    BLANKS = ('', '-')                          # 未命中行 编码/故障 的占位表现
    TIME_RE = r'^\d{2}/\d{2} \d{2}:\d{2}:\d{2}$'  # 时间列固定格式 MM/DD HH:MM:SS
    CODE_RE = r'^[A-Z]{2,}-\d+$'                  # 命中行编码列固定格式

    @staticmethod
    def parse_time(mmdd_hms, ref=None):
        """'09/02 13:34:31' -> datetime。表里时间不带年，补 ref（默认现在）的年份；
        若补完比 ref 晚一天以上说明跨年了，回退一年。
        给 test_locate_history 里所有做时间比较的断言用。"""
        ref = ref or datetime.now()
        dt = datetime.strptime(f'{ref.year}/{mmdd_hms}', '%Y/%m/%d %H:%M:%S')
        if dt - ref > timedelta(days=1):
            dt = dt.replace(year=ref.year - 1)
        return dt

    # ---------- 定位（全部集中在 __init__）----------
    def __init__(self, page):
        self.page = page
        self.root = fault_root(page)
        self.table = self.root.locator('table')          # fixture 里 wait 它可见
        self._body_rows = self.table.locator('tbody tr')
        self.code_filter = self.root.get_by_placeholder('故障编码')
        # 开始 / 结束是原生 <input type="datetime-local">，没有独立日历组件，
        # 自动化统一用 .fill('YYYY-MM-DDTHH:MM') 设值（等同于用户在原生控件里选完）
        _dt = self.root.locator('input[type="datetime-local"]')
        self.start_time_input = _dt.nth(0)
        self.end_time_input = _dt.nth(1)
        self.empty_hint = self.root.get_by_text('暂无定位记录')
        self.feedback_dialog = page.get_by_role('dialog').filter(has_text='确认提交')
        # 分页和目录共用。翻页后等时间列稳定。
        self._pager = MuiTablePager(
            page, self.root, lambda: wait_until_stable(self.page, self.times))

    # ---------- 读表格（给 test_locate_history_rows / _filter_* / _time_range_* 用）----------

    def rows(self):
        """当前页数据行集合。给「有没有记录」这类判断用。"""
        return self._body_rows

    def row_count(self):
        """当前页数据行数（空态时是那条「暂无定位记录」行，也算 1）。"""
        return self._body_rows.count()

    def _col(self, n):
        """当前页第 n 列（1 起）所有单元格文本。"""
        return [t.strip() for t in self.root.locator(f'tbody tr td:nth-child({n})').all_inner_texts()]

    def codes(self):
        """当前页「编码」列。给 filter_by_code 后校验结果、settle 判稳用。"""
        return self._col(3)

    def times(self):
        """当前页「时间」列。给翻页/筛选后判稳、时间区间断言用。"""
        return self._col(1)

    def rows_data(self):
        """当前页每行 -> {time, status, code, fault, severity, fb_text, fb_buttons}。
        fb_text：未反馈 ''，已反馈「已确认」/「误报」；fb_buttons：未反馈 2，已反馈 0。
        空态行（列数不足 5）跳过。给 test_locate_history_rows 逐行校验用。"""
        out = []
        for i in range(self.row_count()):
            tds = self._body_rows.nth(i).locator('td')
            n = tds.count()
            if n < 5:
                continue
            fb = tds.nth(n - 1)
            out.append({
                'time': tds.nth(0).inner_text().strip(),
                'status': tds.nth(1).inner_text().strip(),
                'code': tds.nth(2).inner_text().strip(),
                'fault': tds.nth(3).inner_text().strip(),
                'severity': tds.nth(4).inner_text().strip(),
                'fb_text': fb.inner_text().strip(),
                'fb_buttons': fb.get_by_role('button').count(),
            })
        return out

    def all_rows_data(self):
        """rows_data() 的跨全部分页版本（从第一页翻到最后一页收集）。
        给 test_locate_history_rows 用——校验类用例要过「全部」行不是只看当前页。"""
        self.goto_first_page()
        lo, hi = self.page_range()
        per = max(1, hi - lo + 1)
        pages = max(1, -(-self.total_count() // per))   # 向上取整
        out = list(self.rows_data())
        for _ in range(pages - 1):
            self.goto_next_page()
            out.extend(self.rows_data())
        return out

    def row_datetimes(self, ref=None):
        """当前页「时间」列 -> datetime 列表（新到旧）。
        给 test_locate_history_time_range_between_records 取两条记录时间当区间边界用。"""
        return [self.parse_time(t, ref) for t in self.times()]

    def is_empty(self):
        """当前是不是「暂无定位记录」空态。给各筛选用例的前置 skip / 空态断言用。"""
        return self.empty_hint.count() > 0 and self.empty_hint.is_visible()

    # ---------- 筛选（给 test_locate_history_filter_* / _time_range_* / _future_empty 用）----------

    def filter_by_code(self, code):
        """在「故障编码」框输入并回车（精确匹配），等表格稳定。"""
        self.code_filter.fill(code)
        self.code_filter.press('Enter')
        wait_until_stable(self.page, self.row_count)

    def set_time_range(self, start=None, end=None):
        """设「开始 / 结束」时间（格式 'YYYY-MM-DDTHH:MM'）。None = 不动那一端，'' = 清空。
        live 生效，设完等表格稳定。"""
        if start is not None:
            self.start_time_input.fill(start)
        if end is not None:
            self.end_time_input.fill(end)
        wait_until_stable(self.page, self.row_count)

    # ---------- 分页（和目录同一套，给 test_locate_history_pagination 用）----------

    def total_count(self):
        """总记录数（"共 N 条" 里的 N）。"""
        return self._pager.total_count()

    def page_range(self):
        """当前页行号区间，如 (1, 10)。"""
        return self._pager.page_range()

    def rows_per_page(self):
        return self._pager.rows_per_page()

    def set_rows_per_page(self, n):
        self._pager.set_rows_per_page(n)

    def goto_next_page(self):
        """翻到下一页，等表格稳定。"""
        self._pager.goto_next_page()

    def goto_first_page(self):
        """点「上一页」直到回到第一页（all_rows_data 起手用）。"""
        self._pager.goto_first_page()

    def page_keys(self):
        """当前页用来区分两页内容的行标识。编码会重复，所以带上时间。"""
        return [
            (row['time'], row['status'], row['code'], row['fault'])
            for row in self.rows_data()
        ]

    # ---------- 反馈（给 test_locate_history_feedback_* 用）----------

    def api_create_pending(self, param='EPS_VBUS', value=25.3):
        """直接调 POST /api/fault/locate 造一条新的命中定位记录，不经过快速定位表单。
        给反馈相关用例当靶子——不从共享历史表里挑任意一条现成的未反馈记录（挑现成的
        会跟同时/先后跑的其它用例抢同一条，读到的是别人刚改完的状态，真实撞过）。
        试过 DELETE /api/fault/locate/<id>，404，没有对应的删除接口——这类记录本来
        就是真实定位日志，反馈完就是历史上一条「已确认/误报」的记录，不用清理。
        返回 {code, fault}（命中故障的编码/名称，供 wait_own_pending_row 用）。"""
        result = api_fetch(self.page, '/api/fault/locate', method='POST',
                            body=[{'param': param, 'value': value}])
        fault = result['data']['matchedFaults'][0]
        return {'code': fault['faultCode'], 'fault': fault['faultName']}

    def wait_own_pending_row(self, code, timeout_ms=8000):
        """按编码筛过之后等第 0 行是未反馈状态——新记录插在最前面（表默认新到旧排序），
        筛完编码后第 0 行就是 api_create_pending() 刚建的那条。返回这一行。"""
        self.filter_by_code(code)
        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            rows = self.rows_data()
            if rows and rows[0]['fb_buttons'] == 2:
                return rows[0]
            self.page.wait_for_timeout(150)
        raise AssertionError(f'筛「{code}」后没等到刚建的未反馈记录')

    def row_at(self, index):
        """第 index 行（DOM 行号，不是跳过空行之后的序号）。"""
        cells = self._body_rows.nth(index).locator('td')
        feedback = cells.last
        return {
            'time': cells.nth(0).inner_text().strip(),
            'status': cells.nth(1).inner_text().strip(),
            'code': cells.nth(2).inner_text().strip(),
            'fault': cells.nth(3).inner_text().strip(),
            'severity': cells.nth(4).inner_text().strip(),
            'fb_text': feedback.inner_text().strip(),
            'fb_buttons': feedback.get_by_role('button').count(),
        }

    def open_feedback(self, index, kind):
        """点这一行的「标记为准确」或「标记为误报」，等确认框出现。返回点击前的行。"""
        name = self.FEEDBACK_ACCURATE if kind == '准确' else self.FEEDBACK_WRONG
        before = self.row_at(index)
        self._body_rows.nth(index).get_by_role('button', name=name).click()
        self.feedback_dialog.wait_for(state='visible')
        return before

    def cancel_feedback(self):
        """确认框点「取消」。记录应保持未反馈。"""
        self.feedback_dialog.get_by_role('button', name='取消').click()
        self.feedback_dialog.wait_for(state='hidden')

    def confirm_feedback(self):
        """确认框点「确认提交」。提交后不可撤销。"""
        self.feedback_dialog.get_by_role('button', name='确认提交').click()
        self.feedback_dialog.wait_for(state='hidden')

    def row_by_key(self, key):
        """按 (时间, 状态, 编码, 故障) 找回一行。当前页没有就返回 None。"""
        for row in self.rows_data():
            if (row['time'], row['status'], row['code'], row['fault']) == key:
                return row
        return None

    def wait_feedback(self, key, text, timeout_ms=8000):
        """等到这条记录的反馈 Chip 变成 text（已确认 / 误报）。"""
        deadline = time.time() + timeout_ms / 1000
        last = None
        while time.time() < deadline:
            last = self.row_by_key(key)
            if last and last['fb_text'] == text and last['fb_buttons'] == 0:
                return last
            self.page.wait_for_timeout(150)
        raise AssertionError(f'反馈没有变成「{text}」：{last}')
