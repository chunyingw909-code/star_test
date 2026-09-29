import re

from common import g6_graph


class FaultDetailPage:
    """故障详情视图（从目录点某条故障进入；URL 仍 /fault，内容在 fault-catalog-root 内替换）。

    顶部：返回 + 编码 + 名称 + 严重等级(Chip) + 分系统。
    4 个子 tab（进来默认在「关系图」）：
      - 基本信息：故障描述 / 目标模块 / 故障原因 (N) / 故障影响 (N)
      - 关系图：AntV G6 画在多层 canvas 上（节点/连线不在 DOM 里）+ 右上角图例 + 左上角搜索框
               + click 节点 → 左下角详情卡（带 × 关闭）。高亮是画出来的白描边加粗，
               搜索还会把命中节点挪到视口中心。用 g6_graph 读 getElementRenderStyle。
               模型里的 opacity 0.2 没有画到节点上，不能拿来当高亮断言。
      - 处置预案 (N)：N 张预案卡片（步骤 / 预期效果 / 版本 / 查看详情）。
        「仿真验证」不是每张卡都有，不在这张卡的必有项里。
      - 定位规则 (N)：规则表 N 行（参数编码 / 判据类型 / 判据表达式 / 优先级）。
        没有规则时显示「暂未关联定位规则」，和处置预案的空态同一类。

    对应用例：testcases/fault/test_fault_detail.py（fixture 会把所点那行的
    编码/名称/分系统/严重等级 存进 self.opened，供「详情就是所点这条」的断言比对）。
    """

    TABS = ['基本信息', '关系图', '处置预案', '定位规则']
    GRAPH_LEGEND = ['故障模式', '原因', '影响', '预案', '规则']
    # 详情卡上的类别文案，比图例全（图例写「原因」，卡上写「故障原因」）
    NODE_KIND = {
        'faultMode': '故障模式',
        'cause': '故障原因',
        'effect': '故障影响',
        'plan': '处置预案',
        'rule': '定位规则',
    }
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
        self.rules_empty_hint = self.root.get_by_text('暂未关联定位规则')
        self._rules_table = self.root.locator('table')
        self.rules_thead = self._rules_table.locator('thead')
        self._rule_rows = self._rules_table.locator('tbody tr')

    # ---------- 定位工厂（带参数，没法放 __init__）----------

    def header_field(self, value):
        """头部某个字段（编码/名称/严重等级/分系统）的 locator。

        关系图区域可能再次显示同一个编码/名称；详情头在 DOM 中排在前面，取精确文本
        的首项，避免 strict mode 命中两处。严重等级和分系统是普通文本，不限定 heading。
        """
        return self.root.get_by_text(value, exact=True).first

    def tab(self, name):
        """某个子 tab（处置预案 / 定位规则 文字带 " (N)"，按子串匹配）。"""
        return self.root.get_by_role('tab', name=name)

    def section_heading(self, text):
        """基本信息里的小标题 locator，如 '故障描述' / '故障原因' / '故障影响'。"""
        return self.root.get_by_role('heading', name=text)

    def legend_item(self, name):
        """关系图图例里某一项的 locator。"""
        return self.root.get_by_text(name, exact=True)

    def search_graph_node(self, keyword):
        """关系图搜索框填关键字 + 回车。fill() 之后立刻 press('Enter') 中间不留间隔时，
        偶尔会遇到 Enter 触发时组件自己的 onChange 状态还没提交、回车像是打在空值上的
        情况（人工操作因为打字本身有间隔不会碰到）；这里补一个短暂等待让状态先落定。"""
        self.graph_search_input.fill(keyword)
        self.page.wait_for_timeout(300)
        self.graph_search_input.press('Enter')

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

    def read_graph(self):
        """当前这一帧：节点、连线、视口中心。画布还没挂上 G6 时返回 None。"""
        return g6_graph.read_graph(self.graph_canvas.first)

    def wait_graph(self):
        return g6_graph.wait_graph(self.graph_canvas.first)

    def pick_highlight_node(self, snap=None):
        """挑一个点下去能分出「加粗 / 保持原色」的节点。

        优先度数最小的「原因」：它通常只连中心故障，其余节点不会被描白。
        不点「预案」，那个点击会跳走。
        """
        snap = snap or self.wait_graph()
        degree = {node['id']: 0 for node in snap['nodes']}
        for edge in snap['edges']:
            degree[edge['source']] = degree.get(edge['source'], 0) + 1
            degree[edge['target']] = degree.get(edge['target'], 0) + 1
        total = len(snap['nodes'])
        candidates = [
            node for node in snap['nodes']
            if node['nodeType'] != 'plan' and degree.get(node['id'], 0) < max(total - 1, 1)
        ]
        if not candidates:
            candidates = [node for node in snap['nodes'] if node['nodeType'] == 'faultMode'] or snap['nodes']
        candidates.sort(key=lambda node: (node['nodeType'] != 'cause', degree.get(node['id'], 0)))
        return candidates[0]

    def click_graph_node(self, node_id):
        """按 G6 给出的屏幕坐标点这个节点，返回该节点。点预案会触发跳转，调用方自己避开。"""
        snap = self.read_graph() or self.wait_graph()
        node = next((item for item in snap['nodes'] if item['id'] == node_id), None)
        if node is None:
            raise AssertionError(f'关系图上没有节点 {node_id}')
        x, y = node['client']
        box = self._graph_box()
        inside = box['x'] <= x <= box['x'] + box['width'] and box['y'] <= y <= box['y'] + box['height']
        if not inside:
            raise AssertionError(f"节点「{node['label']}」不在画布里，坐标 {node['client']}，画布 {box}")
        self.page.mouse.click(x, y)
        return node

    def click_a_node(self):
        """点当前故障的「故障模式」节点，打开左下角详情卡。点不到返回 False。"""
        snap = self.wait_graph()
        fault = next((node for node in snap['nodes'] if node['nodeType'] == 'faultMode'), None)
        if fault is None:
            return False
        self.click_graph_node(fault['id'])
        self.page.wait_for_timeout(200)
        return self.graph_detail_card.count() >= 1

    def wait_highlight_around(self, node_id):
        """点中 node_id 之后：它和邻居是白色加粗描边，其余保持原色。"""
        snap = self.read_graph() or self.wait_graph()
        lit_nodes, lit_edges = g6_graph.incident(snap, node_id)
        return g6_graph.wait_paint(self.graph_canvas.first, lit_nodes, lit_edges)

    def wait_search_highlight(self, keyword):
        """搜索回车后：命中的节点和相连边是白色加粗描边，其余保持原色，第一个命中居中。
        触发搜索见 search_graph_node()。孤立单跑几十次量过，回车后大约 1s 就画完，
        从没超过 2.5s；只有在整套用例并发跑、系统繁忙时才偶发看到「从头到尾一点没变」——
        不是画得慢，是那次回车被系统繁忙吞掉了、压根没传到组件。所以先按 2.5s 等一轮，
        没等到就当一次「没触发」，重按一次回车再等一轮，而不是靠拉长超时去掩盖。"""
        snap = self.read_graph() or self.wait_graph()
        matched, lit_nodes, lit_edges = g6_graph.search_hits(snap, keyword)
        if not matched:
            raise AssertionError(f'搜索「{keyword}」没有命中任何节点：{[n["label"] for n in snap["nodes"]]}')
        try:
            painted = g6_graph.wait_paint(
                self.graph_canvas.first, lit_nodes, lit_edges, focus_id=matched[0]['id'], timeout_ms=2500)
        except AssertionError:
            self.graph_search_input.press('Enter')
            painted = g6_graph.wait_paint(
                self.graph_canvas.first, lit_nodes, lit_edges, focus_id=matched[0]['id'])
        return matched[0], painted

    def wait_highlight_cleared(self):
        return g6_graph.wait_restored(self.graph_canvas.first)

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
