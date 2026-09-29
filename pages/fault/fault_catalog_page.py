from common.utils import wait_until_stable
from pages.fault.mui_pager import MuiTablePager


class FaultCatalogPage:
    """故障/预案库 -「目录」子标签（data-testid="fault-catalog-root"）。

    内嵌 Tab 版本（主壳内点「目录」进，URL 仍 /zh-CN）和独立路由版（/zh-CN/fault，直接
    改 URL / 头像菜单「故障管理」都能进）内容和 fault-catalog-root 包裹完全一致，这个类
    两边直接通用，不用额外兜底。

    一张可筛选 / 搜索 / 排序 / 分页的故障总表，点某行进故障详情。
    本类只暴露：定位（__init__ 里的属性）、读表格 / 分页的方法、筛选 / 搜索 / 排序 / 翻页 /
    进详情的动作，以及两个「从当前页面数据里取测试输入」的方法（first_nonempty_combo /
    keyword_present）。用例只写断言，不拼定位。数据会增删，别在用例或本类里写死条数。

    对应用例：testcases/fault/test_fault_catalog.py
    详情页另见 FaultDetailPage（open_fault_at 之后）。
    """

    TABLE_HEADERS = ['编码', '名称', '分系统', '严重等级', '预案数']
    # 「分系统」「严重等级」下拉框的可选项（来自用户手册 §4.3.1 与实测），属 UI 结构常量，
    # 给参数化用例和 test_filter_options 用
    SUBSYSTEMS = ['供配电', '测控', '综合电子', '姿轨控', '星间链路', '热控']
    SEVERITIES = ['I', 'II', 'III', 'IV']
    _COL_CODE, _COL_NAME, _COL_SUBSYSTEM, _COL_SEVERITY, _COL_PLANS = 1, 2, 3, 4, 5  # 列序号（1 起）

    # ---------- 定位（全部集中在 __init__）----------
    def __init__(self, page):
        self.page = page
        self.root = page.get_by_test_id('fault-catalog-root')
        self.table = self.root.locator('table')                 # test_catalog_visible 里断言可见
        self.thead = self.table.locator('thead')                # test_table_headers 里断言列头
        self._body_rows = self.root.locator('tbody tr')
        self.search_input = page.get_by_placeholder('搜索故障...')
        self.subsystem_filter = page.locator('.MuiFormControl-root', has_text='分系统').get_by_role('combobox')
        self.severity_filter = page.locator('.MuiFormControl-root', has_text='严重等级').get_by_role('combobox')
        self.empty_hint = self.root.get_by_text('未找到匹配的故障模式')   # test_empty_state
        self.clear_button = self.root.get_by_role('button', name='清空过滤条件')  # test_empty_state
        self.detail_back_button = self.root.get_by_role('button', name='返回')
        # 分页和定位历史是同一套 MUI 分页，稳定条件用编码列
        self._pager = MuiTablePager(page, self.root, self._settle)

    # ---------- 读表格 ----------

    def rows(self):
        """当前页数据行集合。给 test_open_detail_and_back 等断言首行可见用。"""
        return self._body_rows

    def row_count(self):
        """当前页数据行数。"""
        return self._body_rows.count()

    def _col_texts(self, n):
        """当前页第 n 列（1 起）所有单元格文本，去空白。"""
        return [t.strip() for t in self.root.locator(f'tbody tr td:nth-child({n})').all_inner_texts()]

    def codes(self):
        """当前页「编码」列。给排序 / 搜索 / 空态复原类用例校验用。"""
        return self._col_texts(self._COL_CODE)

    def names(self):
        """当前页「名称」列。给关键字搜索校验用。"""
        return self._col_texts(self._COL_NAME)

    def subsystems(self):
        """当前页「分系统」列。给分系统筛选 / 组合筛选校验用。"""
        return self._col_texts(self._COL_SUBSYSTEM)

    def severities(self):
        """当前页「严重等级」列。给严重等级筛选 / 组合筛选校验用。"""
        return self._col_texts(self._COL_SEVERITY)

    def row_cells(self, index=0):
        """第 index 行的 编码/名称/分系统/严重等级，返回 dict。
        给用例「取现有一行的某个字段当筛选输入 / 当详情比对基准」用。"""
        row = self._body_rows.nth(index)
        cell = lambda n: row.locator(f'td:nth-child({n})').inner_text().strip()
        return {'code': cell(1), 'name': cell(2), 'subsystem': cell(3), 'severity': cell(4)}

    def _plan_counts(self):
        """当前页各行「预案数」列（非数字按 0）。open_first_fault_with/without_plans 内部用。"""
        return [int(t) if t.strip().isdigit() else 0 for t in self._col_texts(self._COL_PLANS)]

    # ---------- 动作：搜索 / 排序 / 筛选 ----------

    def _settle(self):
        """等筛选 / 搜索 / 排序 / 翻页后表格稳定。重排瞬间会出现「编码列全空」的过渡态，
        先等真实数据或空态出现再等稳定。目录里可能合法存在空编码记录，不能要求每行
        编码都非空，否则每次操作都会白等 3 秒。"""
        for _ in range(30):
            c = self.codes()
            empty = self.empty_hint.count() > 0 and self.empty_hint.is_visible()
            if (c and any(c)) or empty:
                break
            self.page.wait_for_timeout(100)
        wait_until_stable(self.page, self.codes)

    def search(self, keyword):
        """在「搜索故障...」框输入关键字并回车。给 test_keyword_search / test_empty_state 等用。"""
        self.search_input.fill(keyword)
        self.search_input.press('Enter')
        self._settle()

    def sort_by(self, header_text):
        """点某个列标题切换该列排序。给 test_column_sort 用。"""
        self.thead.get_by_text(header_text, exact=True).click()
        self._settle()

    def filter_subsystem(self, name):
        """选「分系统」下拉；name 传分系统名或 '全部'（清除）。"""
        self._pick(self.subsystem_filter, name)

    def filter_severity(self, name):
        """选「严重等级」下拉；name 传 I/II/III/IV 或 '全部'（清除）。"""
        self._pick(self.severity_filter, name)

    def _pick(self, combobox, name):
        """打开下拉框并选中名为 name 的选项，等表格稳定。"""
        combobox.click()
        self.page.get_by_role('option', name=name, exact=True).click()
        self._settle()

    def _options_of(self, combobox):
        """打开下拉框，读出所有选项文本，再关掉。"""
        combobox.click()
        opts = [t.strip() for t in self.page.get_by_role('option').all_inner_texts()]
        self.page.keyboard.press('Escape')
        return opts

    def subsystem_options(self):
        """「分系统」下拉的全部选项。给 test_filter_options 用。"""
        return self._options_of(self.subsystem_filter)

    def severity_options(self):
        """「严重等级」下拉的全部选项。给 test_filter_options 用。"""
        return self._options_of(self.severity_filter)

    # ---------- 动作：进详情 / 返回 ----------

    def open_fault_at(self, index=0):
        """点第 index 行进详情视图，返回点击前读到的该行 编码/名称/分系统/严重等级。"""
        cells = self.row_cells(index)
        self._body_rows.nth(index).click()
        self.detail_back_button.wait_for(state='visible')
        return cells

    def open_first_fault_with_plans(self):
        """打开第一条「预案数 > 0」的故障——保证详情里处置预案 / 定位规则 / 关系图 有内容，
        又不写死是哪条。当前页找不到就退回第一条。给 fault_detail_page fixture 用。"""
        counts = self._plan_counts()
        idx = next((i for i, n in enumerate(counts) if n > 0), 0)
        return self.open_fault_at(idx)

    def open_first_fault_without_plans(self):
        """打开第一条「预案数 == 0」的故障；当前页没有就返回 None（用例据此 skip）。
        给 test_disposal_plan_empty_state 用。"""
        counts = self._plan_counts()
        idx = next((i for i, n in enumerate(counts) if n == 0), None)
        return self.open_fault_at(idx) if idx is not None else None

    def open_first_fault_without_rules(self):
        """打开当前页第一条「定位规则 (0)」的故障。目录表没有规则数列，得点进去看 tab。
        没有就返回 None，并回到总表。给 test_locate_rules_empty_state 用。"""
        from pages.fault.fault_detail_page import FaultDetailPage

        detail = FaultDetailPage(self.page)
        total = self.row_count()
        for i in range(total):
            picked = self.open_fault_at(i)
            if detail.tab_count('定位规则') == 0:
                return picked
            self.back_to_list()
        return None

    def back_to_list(self):
        """在详情视图点「返回」回到故障总表。给 test_detail_back_to_catalog 用。"""
        self.detail_back_button.click()
        self.table.wait_for(state='visible')

    # ---------- 分页（给 test_rows_per_page_change / _next_page / _total_count_stable / test_column_sort 用）----------

    def total_count(self):
        """总条数（"共 N 条" 里的 N），与每页行数无关。"""
        return self._pager.total_count()

    def page_range(self):
        """当前页行号区间，如 (1, 20)。"""
        return self._pager.page_range()

    def rows_per_page(self):
        """当前「每页行数」。"""
        return self._pager.rows_per_page()

    def set_rows_per_page(self, n):
        """改「每页行数」（选项 10 / 20 / 50），等表格稳定。"""
        self._pager.set_rows_per_page(n)

    def goto_next_page(self):
        """翻到下一页，等表格稳定。"""
        self._pager.goto_next_page()

    def _goto_first_page(self):
        """点「上一页」直到第一页（all_codes 起手用）。"""
        self._pager.goto_first_page()

    def all_codes(self):
        """「编码」列跨全部分页按页顺序拼起来（从第一页收集）。给 test_column_sort 校验
        「整个结果集」的排序用——codes() 只拿到当前页。按 总数 / 每页行数 算页数来翻，
        不靠「下一页按钮是否禁用」（重排瞬间那按钮会短暂 disabled，会少翻几页）。"""
        self._goto_first_page()
        self._settle()
        per = self.rows_per_page()
        pages = max(1, -(-self.total_count() // per))   # 向上取整
        out = list(self.codes())
        for _ in range(pages - 1):
            self.goto_next_page()
            out.extend(self.codes())
        return out

    # ---------- 从当前页面数据取测试输入 ----------

    def first_nonempty_combo(self):
        """遍历 分系统 × 严重等级 组合并应用筛选，返回第一个能筛出结果的 (分系统, 严重等级)；
        全为空返回 None。返回时页面上就是该组合的筛选结果。给 test_combined_filter 用。"""
        for sub in self.SUBSYSTEMS:
            for sev in self.SEVERITIES:
                self.filter_subsystem(sub)
                self.filter_severity(sev)
                if self.row_count() > 0:
                    return sub, sev
        return None

    def keyword_present(self):
        """返回一个必然命中当前至少一行的搜索关键字（第一行编码的前缀）。给 test_keyword_search 用。"""
        code = self.codes()[0]
        return code.split('-')[0] if '-' in code else code[:3]
