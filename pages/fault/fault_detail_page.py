import re


class FaultDetailPage:
    """故障详情视图（从目录点某条故障进入；URL 仍 /fault，内容在 fault-catalog-root 内替换）。

    顶部：返回 + 编码 + 名称 + 严重等级(Chip) + 分系统。
    4 个子 tab（进来默认在「关系图」）：
      - 基本信息：故障描述 / 目标模块 / 故障原因 (N) / 故障影响 (N)
      - 关系图：canvas 画的（多层 canvas，节点/连线不在 DOM 里）+ 右上角图例 + 左上角搜索框
               + click 节点 → 左下角详情卡（带 × 关闭）。canvas 上的 hover 高亮 / 搜索居中 /
               缩放 / 拖动都画在像素里，DOM 看不到，只能验「不报错、canvas 还在」。
      - 处置预案 (N)：N 张预案卡片（步骤 / 预期效果 / 版本 / 查看详情 / 仿真验证）
      - 定位规则 (N)：规则表 N 行（参数编码 / 判据类型 / 判据表达式 / 优先级）

    对应用例：testcases/fault/test_fault_detail.py（fixture 会把所点那行的
    编码/名称/分系统/严重等级 存进 self.opened，供「详情就是所点这条」的断言比对）。
    """

    TABS = ['基本信息', '关系图', '处置预案', '定位规则']
    GRAPH_LEGEND = ['故障模式', '原因', '影响', '预案', '规则']
    RULE_HEADERS = ['参数编码', '判据类型', '判据表达式', '优先级']

    # ---------- 定位（不带参数的全部集中在 __init__；带参数的见下面的工厂方法）----------
    def __init__(self, page):
        self.page = page
        self.root = page.get_by_test_id('fault-catalog-root')
        self.back_button = self.root.get_by_role('button', name='返回')
        self._active_tab = self.root.locator('[role=tab][aria-selected="true"]')
        # 关系图
        self.graph_canvas = self.root.locator('canvas')
        self.graph_search_input = self.root.get_by_placeholder('搜索节点...')
        self.graph_detail_card = self.root.locator('.MuiCard-root').filter(
            has=page.get_by_test_id('CloseIcon'))            # 点节点后左下角那张
        self.graph_detail_close = self.graph_detail_card.get_by_test_id('CloseIcon')
        # 处置预案
        self._plan_cards = self.root.locator('.MuiCard-root')
        self._plan_steps = self.root.locator('li')
        self.plan_empty_hint = self.root.get_by_text('暂未关联处置预案')
        self.plan_detail_button = self.root.get_by_role('button', name='查看详情')
        self.sim_verify_button = self.root.get_by_role('button', name='仿真验证')
        # 定位规则
        self._rules_table = self.root.locator('table')
        self.rules_thead = self._rules_table.locator('thead')
        self._rule_rows = self._rules_table.locator('tbody tr')

    # ---------- 定位工厂（带参数，没法放 __init__）----------

    def header_field(self, value):
        """头部某个字段（编码/名称/严重等级/分系统）的 locator——每个都是唯一 exact 文本。"""
        return self.root.get_by_text(value, exact=True)

    def tab(self, name):
        """某个子 tab（处置预案 / 定位规则 文字带 " (N)"，按子串匹配）。"""
        return self.root.get_by_role('tab', name=name)

    def section_heading(self, text):
        """基本信息里的小标题 locator，如 '故障描述' / '故障原因' / '故障影响'。"""
        return self.root.get_by_role('heading', name=text)

    def legend_item(self, name):
        """关系图图例里某一项的 locator。"""
        return self.root.get_by_text(name, exact=True)

    # ---------- 头部 / tab（给 test_detail_header / _controls / _fault_detail_opens 用）----------

    def open_tab(self, name):
        """点某个子 tab（不写死等待，由调用方 expect 自动等）。"""
        self.tab(name).click()

    def active_tab(self):
        """当前选中的子 tab 名（去掉 " (N)"）；没有返回 None。"""
        return self._active_tab.inner_text().split('(')[0].strip() if self._active_tab.count() else None

    def tab_count(self, name):
        """子 tab 文字 " (N)" 里的 N（处置预案 / 定位规则）。取不到返回 None。
        给 test_disposal_plan_count_match / test_locate_rules_count_match 用。"""
        m = re.search(r'\((\d+)\)', self.tab(name).inner_text())
        return int(m.group(1)) if m else None

    # ---------- 基本信息（给 test_basic_info_fields / _counts_match 用）----------

    def section_count(self, label):
        """「<label> (N)」小标题里的 N（如 "故障原因 (2)" → 2）。取不到返回 None。"""
        m = re.search(r'\((\d+)\)', self.section_heading(label).inner_text())
        return int(m.group(1)) if m else None

    def _section_items(self, label):
        """带计数小标题「紧跟那一块」里的条目（li）。
        例：「故障原因 (2)」下面就是 杂散光干扰 / 星敏感器电子学故障 两条。"""
        return self.section_heading(label).locator('xpath=following-sibling::*[1]').locator('li')

    def cause_items(self):
        """「故障原因」小标题下列出的原因条目。"""
        return self._section_items('故障原因')

    def impact_items(self):
        """「故障影响」小标题下列出的影响条目。"""
        return self._section_items('故障影响')

    # ---------- 关系图（给 test_graph_* 用）----------

    def legend_boxes(self):
        """5 个图例项的 bounding_box（按 GRAPH_LEGEND 顺序）。用于「不重叠 / 没被裁掉」断言。"""
        return [self.legend_item(n).first.bounding_box() for n in self.GRAPH_LEGEND]

    def _graph_box(self):
        return self.graph_canvas.first.bounding_box()

    def click_a_node(self):
        """在画布上点出一个节点的详情卡。种子故障节点一般在正中，命不中就在附近扫几个点。
        返回是否点出了详情卡（都没点到返回 False，交给用例 skip）。"""
        b = self._graph_box()
        cx, cy = b['x'] + b['width'] / 2, b['y'] + b['height'] / 2
        for dx, dy in [(0, 0), (0, -60), (-60, 0), (60, 0), (0, 60), (-90, 60), (90, -60)]:
            x, y = cx + dx, cy + dy
            self.page.mouse.move(x - 100, y - 80, steps=6)
            self.page.mouse.move(x, y, steps=8)
            self.page.mouse.click(x, y)
            self.page.wait_for_timeout(200)
            if self.graph_detail_card.count() >= 1:
                return True
            self.click_graph_blank()
        return False

    def click_graph_blank(self):
        """点画布左上角空白处，取消节点选中。"""
        b = self._graph_box()
        self.page.mouse.click(b['x'] + 8, b['y'] + 8)

    # ---------- 处置预案（给 test_disposal_plan_* / test_plan_*_navigates 用）----------

    def plan_cards(self):
        """处置预案 tab 下的预案卡片。"""
        return self._plan_cards

    def plan_steps(self):
        """处置预案卡片里的操作步骤条目（li）。"""
        return self._plan_steps

    def sim_verify_scenario(self):
        """「仿真验证 (S-03)」按钮文字里的场景号（S-03）。取不到返回 None。
        点这个按钮会跳到 /scenarios?id=<场景号>。"""
        m = re.search(r'\(([^)]+)\)', self.sim_verify_button.first.inner_text())
        return m.group(1).strip() if m else None

    # ---------- 定位规则（给 test_locate_rules_* 用）----------

    def rule_rows(self):
        """定位规则表的数据行。"""
        return self._rule_rows

    def first_rule_cells(self):
        """定位规则表第一行各单元格的文本（去空白）。"""
        return [t.strip() for t in self._rule_rows.first.locator('td').all_inner_texts()]
