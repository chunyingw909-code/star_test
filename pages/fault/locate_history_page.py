import re
from datetime import datetime, timedelta

from common.utils import wait_until_stable


class FaultLocateHistoryPage:
    """故障/预案库 -「定位历史」子标签：过去的定位记录表（主壳内，URL 仍 /zh-CN，正常）。

    列：时间 / 状态 / 编码 / 故障 / 等级 / 反馈。
    - 状态只有「命中」/「未命中」；未命中时 编码 / 故障 是占位符「-」，等级为空。
    - 「反馈」列两态：未反馈 = 两个图标按钮（✓ 准确 / ✗ 误报）；已反馈 = 一个 Chip
      「已确认」/「误报」+ 0 按钮。别点按钮（点了单向变化、没有清理接口）。
    顶部筛选：开始 / 结束时间（原生 datetime-local）+ 故障编码。带 MUI 分页。

    对应用例：testcases/fault/test_fault_locate_history.py
    """

    STATUSES = ('命中', '多命中', '未命中')
    MATCHED_STATUSES = ('命中', '多命中')
    SEVERITIES = ('I', 'II', 'III', 'IV')
    FEEDBACK_DONE = ('已确认', '误报')          # 已反馈行反馈列 Chip 的文字
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
        self.root = page.get_by_test_id('fault-catalog-root')
        self.table = self.root.locator('table')          # fixture 里 wait 它可见
        self._body_rows = self.table.locator('tbody tr')
        self.code_filter = self.root.get_by_placeholder('故障编码')
        # 开始 / 结束是原生 <input type="datetime-local">，没有独立日历组件，
        # 自动化统一用 .fill('YYYY-MM-DDTHH:MM') 设值（等同于用户在原生控件里选完）
        _dt = self.root.locator('input[type="datetime-local"]')
        self.start_time_input = _dt.nth(0)
        self.end_time_input = _dt.nth(1)
        self.empty_hint = self.root.get_by_text('暂无定位记录')
        self._pager = self.root.locator('.MuiTablePagination-root')
        self._displayed_rows = self._pager.locator('.MuiTablePagination-displayedRows')
        self._next_page_btn = self._pager.get_by_role('button', name='next page')
        self._prev_page_btn = self._pager.get_by_role('button', name='previous page')

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

    # ---------- 分页（给 test_locate_history_pagination + all_rows_data 内部用）----------

    def _pager_nums(self):
        """分页文本（形如 "1-10 / 共 N 条"）里的数字 [起, 止, 总]。"""
        return [int(x) for x in re.findall(r'\d+', self._displayed_rows.inner_text())]

    def total_count(self):
        """总记录数（"共 N 条" 里的 N）。"""
        return self._pager_nums()[-1]

    def page_range(self):
        """当前页行号区间，如 (1, 10)。"""
        n = self._pager_nums()
        return n[0], n[1]

    def goto_next_page(self):
        """翻到下一页，等表格稳定。"""
        self._next_page_btn.click()
        wait_until_stable(self.page, self.times)

    def goto_first_page(self):
        """点「上一页」直到回到第一页（all_rows_data 起手用）。"""
        while not self._prev_page_btn.is_disabled():
            self._prev_page_btn.click()
            wait_until_stable(self.page, self.times)
