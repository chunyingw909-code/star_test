import re

from common.utils import wait_until_stable


class FaultPlanLibraryRoutePage:
    """故障/预案库 -「预案库」的独立路由版（/zh-CN/fault/plans，直接改 URL / 头像菜单
    「故障管理」/ 先进快速定位再切标签都能到）。

    和内嵌 Tab 版本（FaultPlanLibraryPage：卡片 + 1 个「搜索预案...」框）是两套不同的
    UI，定位符不通用：这边是表格（预案编号 / 关联故障 / 操作步骤摘要 / 预期效果 / 操作），
    搜索拆成「预案关键字 / 故障编码 / 故障名称」三个独立输入框；「仿真」按钮没有场景号
    后缀（内嵌版是「仿真 (S-02)」这种，这边就是「仿真」）。

    详情页是两边共享的同一个组件（点「仿真」以外的入口都会到同一个 /fault/plans/<id>
    URL、同一份数据），详情相关的读取直接复用 FaultPlanLibraryPage 的方法（那边本来就
    不依赖 root，两边通用），这个类只管列表部分。

    对应用例：testcases/fault/test_fault_plan_library_route.py
    """

    # ---------- 定位（全部集中在 __init__）----------
    def __init__(self, page):
        self.page = page
        self.keyword_input = page.get_by_placeholder('预案关键字...')
        self.fault_code_input = page.get_by_placeholder('故障编码...')
        self.fault_name_input = page.get_by_placeholder('故障名称...')
        self.table = page.locator('table').filter(has_text='预案编号')
        self._rows = self.table.locator('tbody tr')
        self._first_data_action_cell = self._rows.first.locator('td').nth(4)
        self.detail_buttons = self.table.get_by_role('button', name='详情')
        self.simulate_buttons = self.table.get_by_role('button', name='仿真', exact=True)

    # ---------- 列表：读（给 test_route_has_plans / _search 用）----------

    def rows(self):
        """预案行集合。用于「列表非空」「搜索后剩几行」这类断言。"""
        return self._rows

    def wait_for_data(self, timeout=30000):
        """等五列表格的首条真实预案完成渲染，排除先出现的空态占位行。"""
        self._first_data_action_cell.wait_for(state='visible', timeout=timeout)
        wait_until_stable(self.page, lambda: self._rows.all_inner_texts())

    def row_info(self, index=0):
        """第 index 行解析出的 {plan, fault_code, fault_name, steps_summary, expected}。
        预案编号列名称后缀版本号 v1，去掉；关联故障列是 编码+名称 两行。"""
        cells = self._rows.nth(index).locator('td').all_inner_texts()
        assert len(cells) >= 5, f'第 {index} 行不是完整的预案数据行：{cells}'
        plan = re.sub(r'v\d+$', '', cells[0].strip()).strip()
        fault_lines = [t.strip() for t in cells[1].splitlines() if t.strip()]
        assert fault_lines, f'第 {index} 行「关联故障」列为空'
        return {
            'plan': plan,
            'fault_code': fault_lines[0],
            'fault_name': fault_lines[1] if len(fault_lines) > 1 else '',
            'steps_summary': cells[2].strip(),
            'expected': cells[3].strip(),
        }

    # ---------- 列表：动作（给 test_route_search / _open_detail / _simulate 用）----------

    def search(self, keyword=None, fault_code=None, fault_name=None):
        """填「预案关键字」/「故障编码」/「故障名称」（只传要用的那个），等表格行数稳定。"""
        if keyword is not None:
            self.keyword_input.fill(keyword)
        if fault_code is not None:
            self.fault_code_input.fill(fault_code)
        if fault_name is not None:
            self.fault_name_input.fill(fault_name)
        wait_until_stable(self.page, lambda: self._rows.all_inner_texts())

    def open_detail(self, index=0):
        """点第 index 行的「详情」按钮，跳到 /fault/plans/<id>。
        返回点开前从这行读到的 {plan, fault_code, fault_name, ...}，供详情比对。"""
        info = self.row_info(index)
        self._rows.nth(index).get_by_role('button', name='详情').click()
        return info

    def open_simulate(self, index=0):
        """点第 index 行的「仿真」按钮，跳到场景定义页。调用方自行用 ScenarioDefinitionPage 断言。"""
        self.simulate_buttons.nth(index).click()
