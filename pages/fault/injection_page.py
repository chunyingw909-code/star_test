import re

from common.utils import fault_root, wait_until_stable


class FaultInjectionPage:
    """故障/预案库 -「故障注入」子标签。

    两种入口内容完全一致（面板结构/故障类型列表/注入按钮/默认时长/活动故障面板全部
    相同），差别只在：内嵌 Tab 版本（主壳内点「故障注入」进，URL 仍 /zh-CN）外层有
    data-testid=fault-catalog-root；独立路由版（/zh-CN/fault/inject）没有这层包裹。
    root 用 fault_root() 兜底，两边通用。

    左侧注入面板：
      - 卫星平台 / 信道等效站 ToggleButtonGroup（aria-pressed 标当前档）
      - 目标卫星（SAT-01/02/03）+ 严重程度（WARN/ERROR/CRITICAL）两个下拉
      - 搜索框 + 故障类型列表（<div role=button>，来自 /api/faults/catalog）
      - 点一项 = 选中（该项加 Mui-selected 类）→ 右侧出现 该故障描述 + 持续时长(默认 60)
        数字输入 + 「注入故障」按钮；点「注入故障」发 POST /api/sim/fault-inject。
    右侧：
      - 活动故障 (N) 面板（含一个「预案库」按钮）—— 仿真 STOPPED 时注入请求 200 但不产生
        活动故障，N=0 时显示「无活动故障」。每条活动故障是一个带 Chip 的条目（不是
        <li>）：严重等级 Chip + "卫星/分系统 故障名" 文案 + 倒计时("Ns") + 关闭(×)按钮。
        点 × 或倒计时归零都会让这条消失、FDIR 日志追加一条 RECOVERY 记录。
      - FDIR 日志 面板 —— 无日志时显示「无 FDIR 日志」。每条日志也是带 Chip 的条目：
        INJECTION（橙）或 RECOVERY（绿）+ 一行文案。
      - 「预案库」按钮弹一个对话框「故障预案库」：左侧预案列表，点一条右侧出该预案的
        处置步骤 + 一个「执行预案」按钮——预案没配置结构化执行指令时这个按钮是禁用的
        （title 和按钮下方的文案会说明原因）。

    活动故障需要仿真循环在跑（顶部 T 在走）才会真正出现，用
    testcases/fault/conftest.py 里的 running_injection_page fixture。

    对应用例：testcases/fault/test_fault_injection.py
    """

    DROPDOWNS = ('目标卫星', '严重程度')   # 面板上两个下拉的 label（结构，不是数据值）
    SEVERITIES = ('I', 'II', 'III', 'IV')

    # ---------- 定位（全部集中在 __init__）----------
    def __init__(self, page):
        self.page = page
        self.root = fault_root(page)
        self.panel_heading = self.root.get_by_role('heading', name='故障注入')
        # 平台切换
        self.platform_toggle = self.root.get_by_role('button', name='卫星平台')
        self.channel_toggle = self.root.get_by_role('button', name='信道等效站')
        # 两个下拉（目标卫星 / 严重程度）——选项值不写死，运行时从下拉里读
        self.target_satellite_select = self.dropdown('目标卫星')
        self.severity_select = self.dropdown('严重程度')
        # 故障类型列表
        self.search_input = self.root.get_by_placeholder('搜索故障...')
        self._fault_type_list = self.root.get_by_role('list')
        # 选中前的提示 / 选中后的配置区
        self.select_hint = self.root.get_by_text('选择故障类型以注入')
        self.inject_button = self.root.get_by_role('button', name='注入故障')     # 选中后才有
        self._config_box = self.inject_button.locator('xpath=..')                # 配置区容器
        self.selected_fault_desc = self._config_box.locator('span.MuiTypography-caption')
        self.duration_input = self._config_box.locator('input[type="number"]')
        # 右侧两个面板
        self.active_faults_panel = page.locator('.MuiPaper-outlined').filter(has_text='活动故障')
        self.active_faults_heading = self.active_faults_panel.get_by_role('heading', name=re.compile('活动故障'))
        self.active_faults_empty = self.active_faults_panel.get_by_text('无活动故障')
        self.plan_library_button = self.active_faults_panel.get_by_role('button', name='预案库')
        self.fdir_panel = page.locator('.MuiPaper-outlined').filter(has_text='FDIR 日志')
        self.fdir_empty = self.fdir_panel.get_by_text('无 FDIR 日志')
        # 活动故障 / FDIR 日志的条目：每条都带一个 MuiChip（严重等级 / INJECTION / RECOVERY），
        # 结构是 Chip + 文案 的 Box，不是 <li>；用 Chip 的父级作为一条记录的容器。
        self._active_fault_rows = self.active_faults_panel.locator('.MuiChip-root').locator('xpath=..')
        self._fdir_log_rows = self.fdir_panel.locator('.MuiChip-root').locator('xpath=..')
        # 预案库弹窗（点「预案库」按钮才有）
        self.plan_library_dialog = page.get_by_role('dialog').filter(has_text='故障预案库')
        self._plan_library_items = self.plan_library_dialog.get_by_role('button')
        self.plan_library_steps_label = self.plan_library_dialog.get_by_text('处置步骤:')
        self.plan_library_execute_button = self.plan_library_dialog.get_by_role('button', name='执行预案')

    # ---------- 读（给 test_injection_panel / _select_fault_type / _side_panels 用）----------

    def fault_type_items(self):
        """故障类型列表里的可点项。fixture 等它出现、用例数它/点它/断言 Mui-selected。"""
        return self._fault_type_list.get_by_role('button')

    def fault_type_names(self):
        """故障类型列表当前显示的有效名称。

        目录数据可能夹有空名称，或只剩严重等级的残缺记录。交互用例只操作至少包含
        「名称 + 等级」两行的有效项；残缺数据不会再让整组测试抛 IndexError。
        """
        names = []
        for text in self.fault_type_items().all_inner_texts():
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            if len(lines) >= 2 and lines[0] not in self.SEVERITIES:
                names.append(lines[0])
        return names

    def active_fault_count(self):
        """「活动故障 (N)」标题里的 N。给 test_injection_side_panels / _submit 用。"""
        m = re.search(r'\((\d+)\)', self.active_faults_heading.inner_text())
        return int(m.group(1)) if m else None

    def active_fault_items(self):
        """活动故障面板里的条目。N==0 时为 0 条、显示「无活动故障」。"""
        return self._active_fault_rows

    def active_fault_countdown(self, index=0):
        """第 index 条活动故障的倒计时文案（如 "20s"）。给 test_injection_submit_* 用。"""
        return self._active_fault_rows.nth(index).locator('span.MuiTypography-caption').last.inner_text()

    def fdir_log_items(self):
        """FDIR 日志面板里的条目。无日志时为 0 条、显示「无 FDIR 日志」。"""
        return self._fdir_log_rows

    def fdir_log_info(self, index=0):
        """第 index 条 FDIR 日志的 {type, text}：type 是 Chip 文案（INJECTION/RECOVERY）。
        日志按发生时间从旧到新排列，最新一条在最后，见 latest_fdir_log()。"""
        row = self._fdir_log_rows.nth(index)
        return {
            'type': row.locator('.MuiChip-root').inner_text().strip(),
            'text': row.locator('span.MuiTypography-caption').inner_text().strip(),
        }

    def latest_fdir_log(self):
        """最新一条 FDIR 日志的 {type, text}（日志从旧到新排列，新的追加在末尾）。"""
        row = self._fdir_log_rows.last
        return {
            'type': row.locator('.MuiChip-root').inner_text().strip(),
            'text': row.locator('span.MuiTypography-caption').inner_text().strip(),
        }

    # ---------- 动作（给 test_injection_toggle / _*_select / _search / _select_fault_type / _duration 用）----------

    def dropdown(self, label):
        """label（'目标卫星' / '严重程度'）对应的下拉框 combobox 定位。"""
        return self.root.locator('.MuiFormControl-root', has_text=label).get_by_role('combobox')

    def switch_platform(self, name):
        """点「卫星平台」/「信道等效站」切换档位。name 传两者之一。"""
        (self.platform_toggle if name == '卫星平台' else self.channel_toggle).click()

    def dropdown_options(self, combobox):
        """打开下拉读出全部选项文本，再关掉。给 test_injection_dropdown_select 断言用。"""
        combobox.click()
        opts = [t.strip() for t in self.page.get_by_role('option').all_inner_texts()]
        self.page.keyboard.press('Escape')
        return opts

    def select_other_option(self, combobox):
        """打开下拉、选一个跟当前值不一样的选项，返回被选中的文本。
        选项值不写死——从下拉里现读，挑第一个不等于当前值的。"""
        current = combobox.inner_text().strip()
        combobox.click()
        opts = [t.strip() for t in self.page.get_by_role('option').all_inner_texts()]
        other = next(o for o in opts if o != current)
        self.page.get_by_role('option', name=other, exact=True).click()
        return other

    def search(self, keyword):
        """在「搜索故障...」框输入关键字过滤故障类型列表（模糊匹配、实时生效），等列表稳定。"""
        self.search_input.fill(keyword)
        wait_until_stable(self.page, lambda: self.fault_type_items().count())

    def select_fault_type(self, name):
        """点选某个故障类型，等「注入故障」按钮出现。"""
        self.fault_type_items().filter(has_text=name).first.click()
        self.inject_button.wait_for(state='visible')

    # ---------- 动作（给 test_injection_submit_* / _plan_library_dialog 用）----------

    def close_active_fault(self, index=0):
        """点第 index 条活动故障的关闭(×)按钮，手动标记恢复。"""
        self._active_fault_rows.nth(index).get_by_test_id('CloseIcon').click()

    def open_plan_library_dialog(self):
        """点「预案库」按钮，等「故障预案库」弹窗和左侧预案列表都出现。"""
        self.plan_library_button.click()
        self.plan_library_dialog.wait_for(state='visible')
        self._plan_library_items.first.wait_for(state='visible')

    def plan_library_items(self):
        """弹窗左侧的预案条目。"""
        return self._plan_library_items

    def select_plan_library_item(self, name):
        """点弹窗左侧某个预案，等右侧「处置步骤:」出现。"""
        self._plan_library_items.filter(has_text=name).first.click()
        self.plan_library_steps_label.wait_for(state='visible')
