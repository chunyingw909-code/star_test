import re
from datetime import datetime


class QuickLocatePage:
    """故障/预案库 -「快速定位」子标签：路由页 /fault/locate（另一套路由页，不在
    fault-catalog-root 容器内；顶部导航 Tab 和左侧「仿真控制」侧栏还在，正常点）。

    左侧「遥测参数输入」：
      - 参数名 / 当前值 成对文本框（进来就有一行，预填 EPS_VBUS / 25.3 当示例）+
        「添加参数」加一行
      - 折叠的「粘贴 JSON（自动触发定位）」手风琴，展开后是 JSON 文本框（数组格式
        [{"param":..,"value":..}, ...]）+「解析并定位」按钮；JSON 语法错误时前端本地
        校验拦截、不发请求，提示「JSON 解析失败，请检查格式」
      - 「提交定位」按钮：POST /api/fault/locate，body 是参数数组

    提交后（命中与否都有）：
      - 「定位结果」区块：Chip 「已命中」/「未命中」；命中时有故障卡片（编码/名称/
        严重等级/置信度/命中规则/关联预案 + 步骤 + 预期），未命中只有一行提示
      - 「定位记录」时间线：最多展示最近 10 条，新的插在最前面。每条：时间（当前
        北京时间）+ 命中结果摘要 + 操作区——「重定位」（用这条当初的参数重新提交一次，
        产生一条新记录）+ 未反馈时是「准确」「误报」两个按钮（点了立即生效，没有二次
        确认弹窗，这点和「定位历史」表格页不同）；已反馈则变成一个 Chip（准确→「已确认」，
        误报→「误报」）。

    反馈接口：PUT /api/fault/locate/<id>/confirm，body {"confirmed": bool, "feedback": "准确"|"误报"}

    对应用例：testcases/fault/test_fault_quick_locate.py
    """

    # ---------- 定位（全部集中在 __init__）----------
    def __init__(self, page):
        self.page = page
        self.heading = page.get_by_role('heading', name='遥测参数输入')
        # 参数名 / 当前值 成对输入框
        self._param_inputs = page.get_by_placeholder('遥测参数 (如 EPS_VBUS)')
        self._value_inputs = page.get_by_placeholder('当前值')
        self.add_param_button = page.get_by_role('button', name='添加参数')
        self.submit_button = page.get_by_role('button', name='提交定位')
        # 粘贴 JSON（默认折叠的手风琴）
        self.json_accordion_summary = page.get_by_text('粘贴 JSON（自动触发定位）')
        # MUI 的自适应高度实现会伴生一个 aria-hidden 的隐藏 textarea 用来测量高度，
        # 真正可见可填的是 DOM 顺序里第一个
        self.json_textarea = page.locator('textarea').first
        self.json_parse_button = page.get_by_role('button', name='解析并定位')
        self.json_error_text = page.get_by_text('JSON 解析失败，请检查格式')
        # 定位结果（提交之后才有）
        self.result_heading = page.get_by_role('heading', name='定位结果')
        self.result_status_chip = self.result_heading.locator('xpath=following-sibling::div[1]')
        self._result_box = self.result_heading.locator('xpath=../..')
        self.result_card = self._result_box.locator('.MuiCard-root').first
        self.result_miss_hint = self._result_box.get_by_text('未匹配到故障，请尝试其他参数组合')
        # 定位记录时间线
        self.records_heading = page.get_by_role('heading', name='定位记录')
        self.refresh_button = self.records_heading.locator('xpath=following-sibling::button[1]')
        self._items = page.locator('ul.MuiTimeline-root li.MuiTimelineItem-root')

    # ---------- 表单：读 / 动作（给 test_quick_locate_panel / _add_param / _submit_* 用）----------

    def param_row_count(self):
        """当前「参数名/当前值」有几行。"""
        return self._param_inputs.count()

    def fill_param(self, name, value, index=0):
        """填第 index 行参数名/当前值。进来就有的第 0 行已预填 EPS_VBUS / 25.3。"""
        self._param_inputs.nth(index).fill(name)
        self._value_inputs.nth(index).fill(str(value))

    def add_param_row(self):
        """点「添加参数」加一行。"""
        self.add_param_button.click()

    def submit(self):
        """点「提交定位」，等「定位结果」区块出现，并等「定位记录」时间线顶部也刷新成
        这条新记录（未反馈状态）——两个区块不是同步更新的，只等「定位结果」出现，
        紧接着去读时间线第一条可能还是上一条旧的（负载高时这个时间差会被放大）。"""
        self.submit_button.click()
        self.result_heading.wait_for(state='visible')
        self._items.first.get_by_role('button', name='准确').wait_for(state='visible')

    def paste_json(self, text):
        """展开「粘贴 JSON」手风琴（如果还没展开）、填内容。"""
        if not self.json_textarea.is_visible():
            self.json_accordion_summary.click()
        self.json_textarea.fill(text)

    def submit_json(self, text):
        """展开手风琴、填 JSON、点「解析并定位」。格式对时等价于 submit()（同样等两个
        区块都刷新完）；格式错的场景不会有这两个区块，等不到很快超时——格式错的用例
        自己接住超时、去读 json_error_text，不依赖这里的等待。"""
        self.paste_json(text)
        self.json_parse_button.click()
        try:
            self.result_heading.wait_for(state='visible', timeout=3000)
            self._items.first.get_by_role('button', name='准确').wait_for(state='visible', timeout=3000)
        except Exception:
            pass

    # ---------- 定位记录：读（给 test_quick_locate_submit_* / _relocate / _feedback 用）----------

    def items(self):
        """定位记录时间线条目，新的在最前面。"""
        return self._items

    def item_time(self, index=0):
        """第 index 条的时间文案（HH:MM:SS）。"""
        return self._items.nth(index).locator('span.MuiTypography-caption').first.inner_text().strip()

    def item_text(self, index=0):
        """第 index 条的完整文案（时间 + 命中结果 + 反馈状态），用于粗粒度内容比对。"""
        return self._items.nth(index).inner_text()

    def item_is_miss(self, index=0):
        """第 index 条是不是「未命中」。"""
        return '未命中' in self.item_text(index)

    def item_has_pending_feedback(self, index=0):
        """第 index 条是不是还没反馈（还显示「准确」「误报」两个按钮）。"""
        return self._items.nth(index).get_by_role('button', name='准确').count() > 0

    def item_feedback_label(self, index=0):
        """已反馈那条的 Chip 文案（「已确认」/「误报」）；还没反馈返回 None。"""
        chip = self._items.nth(index).locator('.MuiChip-root')
        return chip.inner_text().strip() if chip.count() else None

    # ---------- 定位记录：动作 ----------

    def relocate(self, index=0):
        """点第 index 条的「重定位」——用那条当初的参数重新提交一次，产生一条新记录
        （插到最前面，未反馈状态），等「定位结果」区块和时间线顶部都刷新完。"""
        self._items.nth(index).get_by_role('button', name='重定位').click()
        self.result_heading.wait_for(state='visible')
        self._items.first.get_by_role('button', name='准确').wait_for(state='visible')

    def give_feedback(self, index, kind):
        """点第 index 条的「准确」或「误报」。立即生效，没有二次确认弹窗；
        等反馈按钮换成 Chip 再返回，避免调用方读到还没刷新的中间状态。"""
        item = self._items.nth(index)
        item.get_by_role('button', name=kind, exact=True).click()
        item.locator('.MuiChip-root').wait_for(state='visible')

    @staticmethod
    def beijing_now_hms():
        """当前时间的 HH:MM:SS（这台环境系统时钟就是北京时间，直接读本机时间即可）。
        给「时间是现在的北京时间」这类断言当参照用。"""
        return datetime.now().strftime('%H:%M:%S')

    @staticmethod
    def seconds_between(hms_a, hms_b):
        """两个 HH:MM:SS 之间相差的秒数（同一天内，不处理跨天）。"""
        fmt = '%H:%M:%S'
        return abs((datetime.strptime(hms_a, fmt) - datetime.strptime(hms_b, fmt)).total_seconds())
