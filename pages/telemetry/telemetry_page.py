import re

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from common import echarts_option as eco


class TelemetryPage:
    """卫星遥测模块 + 左侧「仿真控制」面板 —— 合成一个页面对象。

    顶部导航 Tab「卫星遥测」进入，页面标题「星座数字验证系统」。

    左侧「仿真控制」面板（从上到下）：
      播放 / 暂停 / 停止 三个图标按钮 → 重置 → 速度档(1x~16x) + 自定义 + 应用 →
      保存快照 / 加载断点 → 进度/卫星数/链路数/队列深度 读数 →
      卫星选择(SAT-01/02/03) → 仿真节点列表(每行 RUNNING/STOPPED + 停止图标) + 启动。

    主区：模拟节点 / 真实节点 顶部切换；5 个分系统子标签（供配电/测控/综合电子/
    姿轨控/设备接口），每个下面是遥测参数卡片（可勾选）；底部 导入/导出/批量修改 +
    「参数表: N 条」；再下面是「实时曲线」(ECharts) + 1M/5M/10M 时间窗。

    约定：本类方法只做「定位 + 动作」，断言写在用例里。定位一律放在 __init__。
    对应用例：testcases/telemetry/test_telemetry_smoke.py（分系统/速度/节点模式冒烟）
              testcases/telemetry/test_sim_control.py（仿真控制完整流程）
    """

    # 主区分系统子标签（role=tab，靠 aria-selected 标当前）
    SUBTABS = ['供配电', '测控', '综合电子', '姿轨控', '设备接口']
    # 主区固定参数清单：分系统 -> 分组 -> [(参数名, 单位)]。
    # 这些是产品定义，不随场景和卫星变化；测试用它同时校验分组、参数、单位和总数。
    SUBSYSTEM_PARAMETERS = {
        '供配电': {
            '太阳阵': [('电压', 'V'), ('电流', 'A'), ('功率', 'W')],
            '蓄电池': [('电压', 'V'), ('SOC', '%'), ('温度', '°C')],
            '母线': [('电压', 'V'), ('电流', 'A')],
        },
        '测控': {
            '上行链路': [('信号强度', 'dBm'), ('误码率', '')],
            '下行链路': [('功率', 'dBm'), ('帧速率', 'fps')],
        },
        '综合电子': {
            'CPU': [('使用率', '%')],
            '内存': [('已用', 'MB')],
            '调度': [('任务队列', '')],
        },
        '姿轨控': {
            '姿态': [('wx', 'rad/s'), ('wy', 'rad/s')],
            '轨道': [('X', 'km'), ('Y', 'km')],
            '执行器': [('飞轮0', 'rpm'), ('飞轮1', 'rpm')],
        },
        '设备接口': {
            'CAN': [('接收帧', ''), ('错误', '')],
            'RS422': [('接收字节', 'B')],
            'IO': [('IN0', ''), ('IN1', '')],
        },
    }
    # 仿真速度档（MUI Chip，当前档是 MuiChip-filled，其余 MuiChip-outlined）
    SPEEDS = ['1x', '2x', '4x', '8x', '16x']
    # 实时曲线时间窗档（MUI ToggleButton，value 是窗口秒数）
    CURVE_RANGES = ['1M', '5M', '10M']
    _CURVE_RANGE_VALUE = {'1M': '60', '5M': '300', '10M': '600'}
    # 「真实节点」子标签下的占位文案
    REAL_NODE_NOTICE = '节点预留中，暂不可用'

    def __init__(self, page):
        self.page = page
        self.selected_scenario = None
        self.configured_satellites = []

        # ==================== 模块外壳 ====================
        self.nav_entry = page.get_by_role('tab', name='卫星遥测', exact=True)
        # 进入模块的标志元素（进本模块不改 URL）
        self.title = page.get_by_role('heading', name='星座数字验证系统')
        self.sim_control_heading = page.get_by_role('heading', name='仿真控制')

        # ==================== 仿真控制 · 播放控制 ====================
        # 播放按钮的 title 会按前置状态变化，不能按名称定位；从“速度”所在块向前取
        # 播放控制行，可避开节点列表里同样使用 PlayArrowIcon 的“启动节点”按钮。
        # 普通用户只读模式不渲染这整行，因此三个 locator 的 count 都是 0。
        self.speed_label = page.get_by_text(re.compile(r'速度:\s*[\d.]+x'))
        self.play_control_row = self.speed_label.locator(
            'xpath=parent::div/preceding-sibling::div[1]')
        self.play_button = self.play_control_row.locator('button').nth(0)
        self.pause_button = self.play_control_row.locator('button').nth(1)
        self.stop_button = self.play_control_row.locator('button').nth(2)
        # 「重置」：exact 避免命中画布/主区里含"重置"的其它控件
        self.reset_button = page.get_by_role('button', name='重置', exact=True)
        # 「应用」：自定义速度旁的应用按钮
        self.apply_button = page.get_by_role('button', name='应用', exact=True)

        # ==================== 仿真控制 · 速度 ====================
        # "速度: 4x" 这行文案已在播放控制组中声明，随点击的档位变。
        # 自定义倍速输入框（type=number, min=0.1 max=16 step=0.1）
        self.custom_speed_input = page.get_by_placeholder('自定义')

        # ==================== 仿真控制 · 快照 / 断点 ====================
        self.save_snapshot_button = page.get_by_role('button', name='保存快照', exact=True)
        self.load_breakpoint_button = page.get_by_role('button', name='加载断点', exact=True)
        # 点「保存快照」弹出的命名对话框（标题「保存快照」，一个「快照名称」输入 + 取消/确认）
        self.snapshot_name_dialog = page.get_by_role('dialog').filter(has_text='保存快照')
        # 点「加载断点」弹出的对话框（标题「断点恢复」，列出已存快照 + 每条一个删除图标 + 关闭）
        self.breakpoint_dialog = page.get_by_role('dialog').filter(has_text='断点恢复')

        # ==================== 仿真控制 · 进度读数（只读）====================
        # 顶部「T=0.0s」仿真时间
        self.sim_time_text = page.get_by_text(re.compile(r'T=\s*[\d.]+\s*s'))
        self.progress_text = page.get_by_text(re.compile(r'进度:\s*\d+%'))
        self.sat_count_text = page.get_by_text(re.compile(r'卫星数:\s*\d+'))
        self.link_count_text = page.get_by_text(re.compile(r'链路数:\s*\d+'))
        self.queue_depth_text = page.get_by_text(re.compile(r'队列深度:\s*\d+'))

        # ==================== 仿真控制 · 卫星选择 ====================
        # 「卫星选择 — <当前场景名>」标题
        self.satellite_select_label = page.get_by_text(re.compile(r'卫星选择\s*—'))

        # ==================== 仿真控制 · 仿真节点 ====================
        # 仿真节点面板：含「仿真节点」标题 + 「启动」按钮的那块
        # 先按唯一的「启动」按钮定位，再向上找同时包含「仿真节点」标题的最近祖先。
        # 原先用一串 MuiBox/MuiPaper + last，在节点启动重渲染后会漂到错误容器。
        self.node_start_button = page.get_by_role('button', name='启动', exact=True)
        self.node_section = self.node_start_button.locator(
            'xpath=ancestor::*[.//*[normalize-space(text())="仿真节点"]][1]')
        # 每行末尾的红色停止图标按钮（停掉单个节点）
        self.node_stop_buttons = self.node_section.locator('button:has(svg[data-testid="StopIcon"])')
        # 主面板「启动」只负责打开弹窗；需在弹窗里选择卫星后真正拉起 Python 进程。
        self.node_launch_dialog = page.get_by_role('dialog').filter(has_text='启动仿真进程')
        self.node_launch_satellite = self.node_launch_dialog.get_by_role('combobox')
        self.node_launch_options = page.get_by_role('option')
        self.node_launch_button = self.node_launch_dialog.get_by_role(
            'button', name='启动 (python3 main.py)', exact=True)
        self.node_launch_close = self.node_launch_dialog.get_by_role(
            'button', name='关闭', exact=True)

        # ==================== 仿真控制 · 节点模式 ====================
        # ToggleButtonGroup，aria-pressed 标当前
        self.sim_node_button = page.get_by_role('button', name='模拟节点', exact=True)
        self.real_node_button = page.get_by_role('button', name='真实节点', exact=True)
        self.real_node_notice = page.get_by_text(self.REAL_NODE_NOTICE).first

        # ==================== 遥测主区 · 参数操作 ====================
        self.telemetry_checkboxes = page.get_by_role('checkbox')
        # 每个参数项都是一个带 checkbox 的 MUI Grid item；按结构定位，不依赖生成的 css-* 类。
        self.parameter_cards = page.locator('.MuiGrid-item').filter(
            has=page.get_by_role('checkbox'))
        self.import_button = page.get_by_role('button', name='导入', exact=True)
        self.export_button = page.get_by_role('button', name='导出', exact=True)
        self.batch_edit_button = page.get_by_role('button', name='批量修改', exact=True)
        self.batch_edit_dialog = page.get_by_role('dialog').filter(has_text='批量修改')
        # 「参数表: N 条」计数
        self.param_table_count_text = page.get_by_text(re.compile(r'参数表:\s*\d+\s*条'))

        # ==================== 遥测主区 · 实时曲线 ====================
        self.curve_heading = page.get_by_text('实时曲线', exact=True)
        # 曲线是 ECharts 画在 canvas 上；容器带 _echarts_instance_ 属性
        self.curve_chart = page.locator('[_echarts_instance_]').last

        # ==================== 通用 ====================
        # 只取 MUI Snackbar 内的业务提示，避开 Next.js 常驻的空 route announcer。
        self.snackbar = page.locator('.MuiSnackbar-root').get_by_role('alert').last
        self.snackbar_message = self.snackbar

    # ==================== 进入模块 ====================

    def open(self):
        """点顶部「卫星遥测」Tab，等「仿真控制」面板渲染出来。返回 self。"""
        self.nav_entry.click()
        self.sim_control_heading.wait_for(state='visible')
        self.page.wait_for_load_state('networkidle')
        return self

    # ==================== 场景前置条件 ====================

    def scenario_inventory(self):
        """只读列出所有场景及其卫星，返回 [{id, name, satellites}]。"""
        return self.page.evaluate(
            """async () => {
                const unwrap = payload => Array.isArray(payload) ? payload : (payload?.data ?? []);
                const scenarios = unwrap(await (await fetch('/api/scenarios')).json());
                const result = [];
                for (const scenario of scenarios) {
                    const response = await fetch(
                        `/api/satellites?scenarioId=${encodeURIComponent(scenario.id)}`);
                    const satellites = response.ok ? unwrap(await response.json()) : [];
                    result.push({
                        id: scenario.id,
                        name: scenario.name,
                        template: Boolean(scenario.template),
                        satellites: satellites.map(s => ({id: s.id, name: s.name})),
                    });
                }
                return result;
            }"""
        )

    def find_scenario_with_satellites(self, min_count=1):
        """通过应用自己的只读接口找一条配置了卫星的场景。

        不依赖某套环境里的固定场景名称或数据库 ID；优先选择用户保存的非模板场景，
        再回退到标准模板场景。返回第一条至少有 min_count 颗卫星的场景；找不到返回 None。
        """
        scenarios = self.scenario_inventory()
        scenarios.sort(key=lambda item: item['template'])
        return next(
            (item for item in scenarios if len(item['satellites']) >= min_count), None)

    def find_scenario_without_satellites(self):
        """返回第一条未配置卫星的场景；当前数据没有时返回 None。"""
        return next(
            (item for item in self.scenario_inventory() if not item['satellites']), None)

    def select_scenario(self, scenario):
        """通过应用使用的 localStorage 键选择场景并刷新，再回到卫星遥测模块。

        场景发现不依赖右侧抽屉 DOM；抽屉以后由独立 UI 用例覆盖。
        """
        self.page.evaluate(
            "id => localStorage.setItem('sarsat_last_scenario', id)", scenario['id'])
        self.page.reload(wait_until='networkidle')
        self.open()
        self.satellite_select_label.wait_for(state='visible', timeout=15000)
        self.selected_scenario = scenario
        self.configured_satellites = scenario['satellites']
        return scenario

    def select_first_scenario_with_satellites(self):
        """发现并选择第一条有卫星的场景；找不到时返回 None。"""
        scenario = self.find_scenario_with_satellites()
        return self.select_scenario(scenario) if scenario else None

    def load_current_scenario(self):
        """读取界面当前选择的场景及其卫星，不切换场景、不打断已有节点。"""
        scenario = self.page.evaluate(
            """async () => {
                const unwrap = payload => Array.isArray(payload) ? payload : (payload?.data ?? []);
                const id = localStorage.getItem('sarsat_last_scenario');
                const scenarios = unwrap(await (await fetch('/api/scenarios')).json());
                const current = scenarios.find(item => String(item.id) === String(id));
                if (!current) return null;
                const response = await fetch(
                    `/api/satellites?scenarioId=${encodeURIComponent(current.id)}`);
                if (!response.ok) return null;
                const satellites = unwrap(await response.json());
                return {
                    id: current.id,
                    name: current.name,
                    satellites: satellites.map(s => ({id: s.id, name: s.name})),
                };
            }"""
        )
        if scenario:
            self.selected_scenario = scenario
            self.configured_satellites = scenario['satellites']
        return scenario

    # ==================== 分系统子标签 ====================

    def subtab(self, name):
        """某个分系统子标签的 locator（role=tab）。"""
        return self.page.get_by_role('tab', name=name, exact=True)

    def open_subtab(self, name):
        """点开某个分系统子标签。选中态由调用方 expect(...) 自动等待。"""
        self.subtab(name).click()

    def selected_subtab(self):
        """当前选中的分系统子标签名（按 aria-selected 判断），没有返回 None。"""
        for name in self.SUBTABS:
            if self.subtab(name).get_attribute('aria-selected') == 'true':
                return name
        return None

    def parameter_group(self, name):
        """分系统里的参数分组，例如「太阳阵」「上行链路」。"""
        return self.page.get_by_role('heading', name=name, exact=True).locator('xpath=..')

    def parameter_cards_in_group(self, name):
        """某个参数分组下所有带 checkbox 的参数卡片。"""
        return self.parameter_group(name).locator('.MuiGrid-item').filter(
            has=self.page.get_by_role('checkbox'))

    # ==================== 速度档 ====================

    def speed_chip(self, name):
        """某个速度档 Chip 的 locator（name 传 '1x' / '2x' / ...）。"""
        return self.page.get_by_role('button', name=name, exact=True)

    def set_speed(self, name):
        """点某个预设速度档 Chip。"""
        self.speed_chip(name).click()

    def current_speed(self):
        """当前速度，如 '4x' / '0.5x'（从状态文案解析）；解析不到返回 None。"""
        m = re.search(r'速度:\s*([\d.]+x)', self.speed_label.inner_text())
        return m.group(1) if m else None

    def speed_is_active(self, name):
        """该速度档是否为当前档（Chip 是实心 MuiChip-filled）。"""
        return 'MuiChip-filled' in (self.speed_chip(name).get_attribute('class') or '')

    def set_custom_speed(self, value):
        """在「自定义」输入框填倍速值并点「应用」。value 传数字或字符串。"""
        self.custom_speed_input.fill(str(value))
        self.apply_button.click()

    # ==================== 播放控制 ====================

    def start_sim(self):
        """点 ▶「启动仿真循环」。"""
        self.play_button.click()

    def pause_sim(self):
        """点 ⏸「暂停仿真循环」。"""
        self.pause_button.click()

    def stop_sim(self):
        """点 ⏹「停止仿真循环」。"""
        self.stop_button.click()

    def reset_sim(self):
        """点「重置」——仿真时间 / 进度 / 速度归零。"""
        self.reset_button.click()

    def teardown_sim(self):
        """收尾用：停仿真循环、重置。失败静默。不停卫星节点——这台环境是共享的，
        节点可能是别的用例或别人的会话留下的；而且真实拉起一次节点进程很慢，
        每条用例都顺手关掉，下一条要用仿真的用例又得重新冷启动一遍。"""
        try:
            if self.stop_button.count() and self.stop_button.is_enabled():
                self.stop_button.click(timeout=2000)
                self.page.wait_for_timeout(300)
            if self.reset_button.count() and self.reset_button.is_enabled():
                self.reset_button.click(timeout=2000)
                self.page.wait_for_timeout(300)
        except Exception:
            pass

    # ==================== 进度读数 ====================

    def _read_int(self, locator, pattern):
        """从 locator 文本里按 pattern 抠出第一个整数；读不到返回 None。"""
        try:
            m = re.search(pattern, locator.inner_text())
            return int(m.group(1)) if m else None
        except PlaywrightTimeoutError:
            return None

    def sim_time(self):
        """顶部「T=Ns」里的秒数（float）；读不到返回 None。"""
        try:
            m = re.search(r'T=\s*([\d.]+)\s*s', self.sim_time_text.inner_text())
            return float(m.group(1)) if m else None
        except PlaywrightTimeoutError:
            return None

    def progress_percent(self):
        """「进度: N%」里的 N（int）。"""
        return self._read_int(self.progress_text, r'进度:\s*(\d+)%')

    def satellite_count(self):
        """「卫星数: N」里的 N（int）。"""
        return self._read_int(self.sat_count_text, r'卫星数:\s*(\d+)')

    def link_count(self):
        """「链路数: N」里的 N（int）。"""
        return self._read_int(self.link_count_text, r'链路数:\s*(\d+)')

    def queue_depth(self):
        """「队列深度: N」里的 N（int）。"""
        return self._read_int(self.queue_depth_text, r'队列深度:\s*(\d+)')

    def wait_sim_time_advances(self, timeout_ms=15000, poll_ms=500):
        """轮询顶部 T，直到它 > 0（仿真真的跑起来了）或超时。返回最终读到的秒数。"""
        deadline = self.page.evaluate('Date.now()') + timeout_ms
        while self.page.evaluate('Date.now()') < deadline:
            t = self.sim_time()
            if t and t > 0:
                return t
            self.page.wait_for_timeout(poll_ms)
        return self.sim_time()

    # ==================== 快照 / 断点 ====================

    def save_snapshot(self, name):
        """点「保存快照」→ 在弹窗填快照名 → 点「确认」。之后按 snackbar「快照已保存」断言。"""
        self.save_snapshot_button.click()
        self.snapshot_name_dialog.wait_for(state='visible')
        self.snapshot_name_dialog.locator('input').first.fill(name)
        self.snapshot_name_dialog.get_by_role('button', name='确认', exact=True).click()
        self.snapshot_name_dialog.wait_for(state='hidden')

    def open_breakpoint_dialog(self):
        """点「加载断点」，等「断点恢复」弹窗出现。"""
        self.load_breakpoint_button.click()
        self.breakpoint_dialog.wait_for(state='visible')

    def close_breakpoint_dialog(self):
        """关闭「断点恢复」弹窗。优先点「关闭」，点不到（删条目后偶发重渲染）就按 Esc 兜底。"""
        try:
            self.breakpoint_dialog.get_by_role('button', name='关闭', exact=True).click(timeout=4000)
        except Exception:
            self.page.keyboard.press('Escape')
        try:
            self.breakpoint_dialog.wait_for(state='hidden', timeout=4000)
        except Exception:
            pass

    def breakpoint_entries(self):
        """「断点恢复」弹窗里的快照条目集合（每条是一个 MuiListItemButton）。"""
        return self.breakpoint_dialog.locator('.MuiListItemButton-root')

    def breakpoint_entry(self, name):
        """按名字匹配的某个快照条目。"""
        return self.breakpoint_entries().filter(has_text=name)

    def apply_breakpoint(self, name):
        """点某个快照条目本身 = 恢复到该断点。"""
        self.breakpoint_entry(name).first.click()

    def delete_breakpoint(self, name):
        """删除某个快照：点该条目行内的删除图标（svg data-testid=DeleteIcon）。"""
        self.breakpoint_entry(name).first.locator(
            'button:has(svg[data-testid="DeleteIcon"])').click()

    def delete_all_breakpoints(self, name_contains):
        """在已打开的「断点恢复」弹窗里，循环删掉所有名字含 name_contains 的快照。收尾清理用。"""
        for _ in range(20):  # 兜底上限，防止意外死循环
            row = self.breakpoint_entries().filter(has_text=name_contains).first
            if not row.count():
                break
            row.locator('button:has(svg[data-testid="DeleteIcon"])').click()
            self.page.wait_for_timeout(400)

    # ==================== 卫星选择 ====================

    def satellite_button(self, name):
        """按接口返回的卫星名称定位 Chip；可访问名可能带状态圆点后缀。"""
        return self.page.get_by_role(
            'button', name=re.compile(rf'^{re.escape(name)}(?:\s|●|$)'))

    def active_satellite_button(self, name):
        """已启动卫星的 Chip（名称后带状态圆点）。"""
        return self.page.get_by_role(
            'button', name=re.compile(rf'^{re.escape(name)}\s*●'))

    def selected_satellite(self):
        """当前选中的卫星名（Chip 为实心 MuiChip-filled）；没有返回 None。"""
        for satellite in self.configured_satellites:
            name = satellite['name']
            btn = self.satellite_button(name).first
            if 'MuiChip-filled' in (btn.get_attribute('class') or ''):
                return name
        return None

    def select_satellite(self, name):
        """按接口返回的名称选择卫星。"""
        self.satellite_button(name).first.click()

    # ==================== 仿真节点进程 ====================

    def _start_node(self, name, timeout_ms):
        """在启动弹窗拉起一颗卫星，并等待它进入活动态。"""
        self.node_start_button.click()
        self.node_launch_dialog.wait_for(state='visible', timeout=5000)
        self.node_launch_satellite.click()
        self.page.get_by_role('option', name=name, exact=True).click()
        self.node_launch_button.click()

        try:
            self.active_satellite_button(name).wait_for(
                state='visible', timeout=timeout_ms)
        except Exception as exc:
            scenario = (
                self.selected_scenario['name']
                if self.selected_scenario else '当前场景')
            raise AssertionError(
                f'场景「{scenario}」启动卫星「{name}」后仍未进入运行态') from exc
        finally:
            try:
                if self.node_launch_dialog.is_visible():
                    self.node_launch_close.click(timeout=2000)
                    self.node_launch_dialog.wait_for(state='hidden', timeout=3000)
            except Exception:
                pass

    def ensure_one_active_node(self, timeout_ms=20000):
        """复用一颗已有活动卫星；没有时只启动第一颗。返回 (名称, 是否新启动)。"""
        assert self.configured_satellites, '当前场景没有配置卫星'
        for satellite in self.configured_satellites:
            name = satellite['name']
            if self.active_satellite_button(name).count() > 0:
                return name, False

        name = self.configured_satellites[0]['name']
        self._start_node(name, timeout_ms)
        return name, True

    def start_nodes(self, timeout_ms=20000):
        """通过启动弹窗逐个拉起当前场景配置的卫星进程。"""
        for satellite in self.configured_satellites:
            name = satellite['name']
            if self.active_satellite_button(name).count() > 0:
                continue
            self._start_node(name, timeout_ms)

    def stop_all_nodes(self, timeout_ms=20000):
        """停止当前场景所有运行节点；供 fixture teardown 使用。"""
        deadline = self.page.evaluate('Date.now()') + timeout_ms
        try:
            while self.page.evaluate('Date.now()') < deadline:
                before = self.node_stop_buttons.count()
                if before == 0:
                    return
                self.node_stop_buttons.first.click(timeout=3000)
                # 每次只停一个节点；等这一行消失再点下一行，避免重渲染时点到旧 DOM。
                while self.page.evaluate('Date.now()') < deadline:
                    if self.node_stop_buttons.count() < before:
                        break
                    self.page.wait_for_timeout(200)
        except Exception:
            pass

    def ensure_nodes_running(self):
        """启动 selected_scenario（没有则自动选一条配置了卫星的场景）配置的卫星节点，
        等它们都进入活动态。真实拉起 python 进程——这是少数几个别的模块（如故障注入）
        也要依赖的跨模块前置，出错代价大（拖垮一整条后面的用例），系统繁忙时第一次
        可能等不到「运行态」。失败了就整套重来一次：刷新页面回到干净状态再选场景/
        启动，不在已经点开一半的弹窗上瞎重试（避免重复拉起同一颗卫星的进程），
        重试一次仍失败才真的报错。"""
        scenario = self.selected_scenario or self.select_first_scenario_with_satellites()
        assert scenario, '当前没有任何配置了卫星的场景'
        try:
            self.start_nodes()
            visible = self.wait_active_satellites()
            assert visible, '启动节点后左侧仍没有活动卫星'
        except AssertionError:
            self.page.reload(wait_until='networkidle')
            self.open()
            self.select_scenario(scenario)
            self.start_nodes()
            visible = self.wait_active_satellites()
            assert visible, f'重试一次后场景「{scenario["name"]}」仍没有活动卫星'
        return scenario

    def wait_active_satellites(self, timeout_ms=20000):
        """等已配置卫星在左侧卫星选择区出现，返回当前出现的名称。"""
        deadline = self.page.evaluate('Date.now()') + timeout_ms
        expected = [s['name'] for s in self.configured_satellites]
        while self.page.evaluate('Date.now()') < deadline:
            visible = [name for name in expected if self.satellite_button(name).count() > 0]
            if visible:
                return visible
            self.page.wait_for_timeout(300)
        return []

    def active_satellite_names(self):
        """当前场景配置中，已经显示运行状态圆点的卫星名称。"""
        return [
            item['name'] for item in self.configured_satellites
            if self.active_satellite_button(item['name']).count() > 0
        ]

    def node_statuses(self):
        """读取仿真节点区当前配置卫星的 RUNNING / STOPPED 状态。"""
        lines = [line.strip() for line in self.node_section.inner_text().splitlines() if line.strip()]
        result = {}
        for item in self.configured_satellites:
            name = item['name']
            if name not in lines:
                continue
            index = lines.index(name)
            if index + 1 < len(lines) and lines[index + 1] in ('RUNNING', 'STOPPED'):
                result[name] = lines[index + 1]
        return result

    # ==================== 节点模式 ====================

    def node_mode(self):
        """当前仿真节点模式：'sim'（模拟节点）/ 'real'（真实节点）/ None。"""
        if self.sim_node_button.get_attribute('aria-pressed') == 'true':
            return 'sim'
        if self.real_node_button.get_attribute('aria-pressed') == 'true':
            return 'real'
        return None

    def set_node_mode(self, mode):
        """切换仿真节点模式。mode: 'sim' / 'real'。"""
        (self.sim_node_button if mode == 'sim' else self.real_node_button).click()

    # ==================== 遥测主区 · 参数操作 ====================

    def select_first_param(self):
        """勾选第一个遥测参数 checkbox（勾上后「批量修改」「导出」才可用）。"""
        self.telemetry_checkboxes.first.check()

    def param_table_count(self):
        """「参数表: N 条」里的 N（int）；读不到返回 None。"""
        return self._read_int(self.param_table_count_text, r'参数表:\s*(\d+)\s*条')

    def open_batch_edit(self):
        """点「批量修改」，等对话框出现。"""
        self.batch_edit_button.click()
        self.batch_edit_dialog.wait_for(state='visible')

    def close_batch_edit(self):
        """关闭「批量修改」对话框（点取消）。"""
        self.batch_edit_dialog.get_by_role('button', name='取消').click()
        self.batch_edit_dialog.wait_for(state='hidden')

    # ==================== 遥测主区 · 实时曲线 ====================

    def curve_option(self):
        """读取实时曲线正在渲染的 ECharts option。"""
        return eco.get_option(self.curve_chart)

    def curve_point_count(self):
        """实时曲线所有系列当前数据点总数。"""
        option = self.curve_option() or {}
        return sum(len(eco.as_list(series.get('data'))) for series in eco.series_list(option))

    def wait_curve_points_increase(self, before=0, timeout_ms=15000, poll_ms=300):
        """等待实时曲线数据点总数超过 before，返回最新点数。"""
        deadline = self.page.evaluate('Date.now()') + timeout_ms
        while self.page.evaluate('Date.now()') < deadline:
            count = self.curve_point_count()
            if count > before:
                return count
            self.page.wait_for_timeout(poll_ms)
        return self.curve_point_count()

    def curve_range_button(self, name):
        """实时曲线时间窗档按钮的 locator（name 传 '1M' / '5M' / '10M'）。
        这几个是 MUI ToggleButton，算不出可访问名、"1M" 又是 "10M" 的子串，
        按 value 属性定位最稳（1M=60 / 5M=300 / 10M=600 秒）。"""
        return self.page.locator(
            f'button.MuiToggleButton-root[value="{self._CURVE_RANGE_VALUE[name]}"]')

    def set_curve_range(self, name):
        """点某个实时曲线时间窗档。"""
        self.curve_range_button(name).click()

    def curve_range_is_active(self, name):
        """该时间窗档是否为当前档（ToggleButton 的 aria-pressed=true / Mui-selected）。"""
        btn = self.curve_range_button(name)
        cls = btn.get_attribute('class') or ''
        return btn.get_attribute('aria-pressed') == 'true' or 'Mui-selected' in cls
