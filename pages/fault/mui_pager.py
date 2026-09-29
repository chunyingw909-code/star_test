import re


class MuiTablePager:
    """故障模块表格共用的 MUI 分页。

    两边都是「每页行数 10 / 20 / 50」加「起-止 / 共 N 条」。
    翻页、改每页行数之后怎么等表格稳定，由调用方传 settle：目录等编码列，
    定位历史等时间列。
    """

    PAGE_SIZES = (10, 20, 50)

    def __init__(self, page, root, settle):
        self.page = page
        self._settle = settle
        pager = root.locator('.MuiTablePagination-root')
        self.rows_per_page_select = pager.locator('.MuiTablePagination-select')
        self.displayed_rows = pager.locator('.MuiTablePagination-displayedRows')
        self.next_button = pager.get_by_role('button', name='next page')
        self.prev_button = pager.get_by_role('button', name='previous page')

    def _numbers(self):
        """分页文本（形如 "1-10 / 共 N 条"）里的数字 [起, 止, 总]。"""
        return [int(x) for x in re.findall(r'\d+', self.displayed_rows.inner_text())]

    def total_count(self):
        """总条数（"共 N 条" 里的 N），不随每页行数变化。"""
        return self._numbers()[-1]

    def page_range(self):
        """当前页行号区间，如 (1, 10)。"""
        start, end, _total = self._numbers()
        return start, end

    def rows_per_page(self):
        """当前「每页行数」。"""
        return int(self.rows_per_page_select.inner_text().strip())

    def set_rows_per_page(self, n):
        """改成页面提供的「每页行数」选项，等表格稳定。"""
        if self.rows_per_page() == n:
            return
        before = self.displayed_rows.inner_text()
        self.rows_per_page_select.click()
        self.page.get_by_role('option', name=str(n), exact=True).click()
        self._wait_page_label_changes(before)
        self._settle()

    def goto_next_page(self):
        """翻到下一页，等表格稳定。"""
        before = self.displayed_rows.inner_text()
        self.next_button.click()
        self._wait_page_label_changes(before)
        self._settle()

    def goto_first_page(self):
        """点「上一页」直到第一页。"""
        while not self.prev_button.is_disabled():
            before = self.displayed_rows.inner_text()
            self.prev_button.click()
            self._wait_page_label_changes(before)
            self._settle()

    def _wait_page_label_changes(self, before):
        """先等分页区间变化，避免表格旧内容尚未替换时 settle 误判为稳定。"""
        for _ in range(50):
            if self.displayed_rows.inner_text() != before:
                return
            self.page.wait_for_timeout(50)
