import re

from common.utils import wait_until_stable


class FaultPlanLibraryPage:
    """故障/预案库 -「预案库」子标签：处置预案的卡片列表 + 点开后的预案详情页。

    列表在主壳内（URL 仍 /zh-CN）；点开一张卡会跳到路由页 /fault/plans/<id>——另一套
    没有顶部导航的布局。详情只从这里点进去，所以不另起 page 对象，一并放这个类里。

    对应用例：testcases/fault/test_fault_plan_library.py
    """

    # ---------- 定位（全部集中在 __init__）----------
    def __init__(self, page):
        self.page = page
        self.root = page.get_by_test_id('fault-catalog-root')
        # 列表
        self.search_input = self.root.get_by_placeholder('搜索预案...')
        self._cards = self.root.locator('.MuiCard-root')
        # 详情（点开一张卡之后才有）
        self.back_to_library_button = page.get_by_role('button', name='返回预案库')
        self.steps_heading = page.get_by_role('heading', name='操作步骤')
        self.expected_effect_heading = page.get_by_role('heading', name='预期效果')
        self._breadcrumb_items = page.locator('.MuiBreadcrumbs-root li')
        self._step_items = page.locator('ol li')
        self._linked_fault_line = page.get_by_text(re.compile(r'关联故障[:：]'))

    # ---------- 列表：读（给 test_plan_library_has_plans / _search 用）----------

    def cards(self):
        """预案卡片集合。用于「列表非空」「搜索后剩几张」这类断言。"""
        return self._cards

    def card_info(self, index=0):
        """第 index 张卡片解析出的 {plan, fault_code, fault_name}。
        卡片文本前三行固定是 预案名 / 关联故障编码 / 关联故障名。
        用于「点进去前记下这张卡是什么，再和详情/搜索结果比对」（仿 FaultDetailPage.opened）。"""
        lines = [t.strip() for t in self.cards().nth(index).inner_text().splitlines() if t.strip()]
        assert len(lines) >= 3, f'第 {index} 张预案卡字段不足 3 行：{lines}'
        return {'plan': lines[0], 'fault_code': lines[1], 'fault_name': lines[2]}

    # ---------- 列表：动作（给 test_plan_library_search / _open_detail 用）----------

    def search(self, keyword):
        """在「搜索预案...」框输入关键字（模糊匹配、实时生效），等卡片列表稳定。"""
        self.search_input.fill(keyword)
        wait_until_stable(self.page, lambda: self.cards().count())

    def open_plan(self, index=0):
        """点开第 index 张预案卡进详情页，等「返回预案库」按钮出现。
        返回点开前从卡片读到的 {plan, fault_code, fault_name}，供详情比对。"""
        info = self.card_info(index)
        self.cards().nth(index).click()
        self.back_to_library_button.wait_for(state='visible')
        return info

    # ---------- 详情：读（给 test_plan_library_open_detail 用）----------

    def detail_plan_name(self):
        """详情页里的预案名（取面包屑最后一节）。"""
        return self._breadcrumb_items.last.inner_text().strip()

    def linked_fault_text(self):
        """详情页「关联故障: <编码> <名称>」这一行的文本。"""
        return self._linked_fault_line.first.inner_text().strip()

    def step_texts(self):
        """详情页「操作步骤」下的步骤条目文本列表。"""
        return [t.strip() for t in self._step_items.all_inner_texts()]
