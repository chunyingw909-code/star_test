class ControlDrawerPage:
    """主页右侧管理抽屉的「管控」Tab：节点在线状态 + 指令序列编排与发送。

    「指令序列」是把「仿真控制 / 故障注入 / 卫星机动」这几类动作按时间顺序编排成
    一条可以一键回放的脚本（内置示例见 GET /api/commands/test-cases，比如「启动→
    3s 后注故障→12s 后暂停→复位」），不是真实卫星测控里上行的遥控指令序列，是这套
    数字验证平台自己的编排/回放功能，省得测试人员对着故障目录一步步手点。
    每行指令：延时(ms，相对序列起点的偏移) + 类型 + 参数（默认是「模块」文本框，
    套用「指令模板」后会换成该模板自己的参数输入，比如 deltaV/q1）；「目标节点」
    下拉是整条序列共用的，不是逐行设置。

    注意：套用「指令模板」后，那一行「类型」下拉显示的内容因模板而异——「姿态机动」
    套用后显示 MANEUVER，「位保点火」「对日定向」套用后这一格是空的（模板给的底层
    类型 STATION_KEEPING / ATTITUDE_SETPOINT 不在「类型」下拉自己的选项列表里）。
    这里只是记录现象，不代表这是需要修的问题。
    """

    TYPE_OPTIONS = ('START', 'MANEUVER', 'ATTITUDE', 'MODE', 'FAULT')
    TARGET_NODES = ('DV-SAT-01', 'DV-SAT-02')

    def __init__(self, page):
        self.page = page

        # ==================== 右侧抽屉 - 管控 Tab 入口 ====================
        self.drawer_open_button = page.get_by_role(
            'button', name='‹', exact=True).last
        self.control_tab = page.get_by_role('tab', name='管控', exact=True)

        # ==================== 管控 Tab - 内容容器（限定后面元素的查找范围，
        # 避免跟界面编辑器自己的同名「保存」按钮之类的撞名） ====================
        self.node_control_heading = page.get_by_role(
            'heading', name='节点管控', exact=True)
        self.panel = self.node_control_heading.locator('xpath=../..')

        # ==================== 管控 Tab - 节点管控 ====================
        self.node_list = self.node_control_heading.locator(
            'xpath=following::ul[1]')
        self.node_rows = self.node_list.get_by_role('button')
        self.node_names = self.node_rows.locator('.MuiListItemText-primary')
        self.node_status_chips = self.node_rows.locator('.MuiChip-root')

        # ==================== 管控 Tab - 指令序列：导入/保存/加载 ====================
        self.sequence_heading = page.get_by_role(
            'heading', name='指令序列', exact=True)
        self.import_csv_input = self.panel.locator(
            'input[type="file"][accept=".csv"]')
        self.import_csv_button = self.panel.get_by_role(
            'button', name='导入CSV', exact=True)
        self.save_sequence_button = self.panel.get_by_role(
            'button', name='保存', exact=True)
        self.load_sequence_button = self.panel.get_by_role(
            'button', name='加载', exact=True)

        # ==================== 管控 Tab - 指令序列：模板与目标节点 ====================
        # MUI Select 的可访问名会把当前选中值拼进去（比如「目标节点 DV-SAT-01」），
        # 「目标节点」一出场就带着默认值，不能用 exact 精确匹配纯 label。
        self.template_select = self.panel.get_by_role(
            'combobox', name='指令模板')
        self.target_node_select = self.panel.get_by_role(
            'combobox', name='目标节点')

        # ==================== 管控 Tab - 指令序列：指令行（延时/类型/参数/删除） ====================
        # 注意：套用「指令模板」后，行内第三个字段会从「模块」文本框换成模板自己的
        # 参数字段（比如 deltaV），module_inputs 这时就取不到值了，要用
        # page.get_by_role('spinbutton', name='deltaV') 这种按参数名取。
        self.delay_inputs = self.panel.get_by_role('spinbutton', name='延时')
        self.type_selects = self.panel.get_by_role('combobox', name='类型')
        self.module_inputs = self.panel.get_by_placeholder('模块')
        self.delete_row_buttons = self.panel.locator(
            'button:has(svg[data-testid="DeleteIcon"])')

        # ==================== 管控 Tab - 指令序列：新增/发送 ====================
        self.add_command_button = self.panel.get_by_role(
            'button', name='添加指令', exact=True)
        self.send_sequence_button = self.panel.get_by_role(
            'button', name='发送序列', exact=True)

    def open(self):
        """打开右侧抽屉并切到「管控」Tab。"""
        if not self.control_tab.is_visible():
            self.drawer_open_button.click()
            self.control_tab.wait_for(state='visible')
        if self.control_tab.get_attribute('aria-selected') != 'true':
            self.control_tab.click()
        self.node_control_heading.wait_for(state='visible')
        return self

    # ==================== 节点管控 ====================
    def node_names_list(self):
        """读取「节点管控」列表里的全部节点名。"""
        return [t.strip() for t in self.node_names.all_inner_texts()]

    def node_status(self, name):
        """读取指定节点的状态文案（如 ONLINE）。"""
        names = self.node_names_list()
        if name not in names:
            raise AssertionError(f'节点管控列表中找不到「{name}」，实际为 {names}')
        return self.node_status_chips.nth(names.index(name)).inner_text().strip()

    def click_node(self, name):
        """点击指定节点行，弹出该节点的连接信息（地址/TCP/UDP）气泡。"""
        names = self.node_names_list()
        if name not in names:
            raise AssertionError(f'节点管控列表中找不到「{name}」，实际为 {names}')
        self.node_rows.nth(names.index(name)).click()

    # ==================== 指令序列：行操作 ====================
    def row_count(self):
        """当前指令序列里的指令行数。"""
        return self.delay_inputs.count()

    def add_command(self, delay=None, command_type=None, module=None):
        """点「添加指令」新增一行，并按需填写该行的延时/类型/模块，返回新行下标。"""
        self.add_command_button.click()
        index = self.row_count() - 1
        if delay is not None:
            self.delay_inputs.nth(index).fill(str(delay))
        if command_type is not None:
            self.type_selects.nth(index).click()
            self.page.get_by_role('option', name=command_type, exact=True).click()
        if module is not None:
            self.module_inputs.nth(index).fill(module)
        return index

    def remove_command(self, index):
        """删除指定行号的指令。"""
        self.delete_row_buttons.nth(index).click()

    def select_template(self, name):
        """从「指令模板」下拉选择预置模板（对日定向/位保点火/姿态机动）。会用该模板
        替换掉当前整条指令序列，变成只有一行、带模板默认参数的指令。"""
        self.template_select.click()
        self.page.get_by_role('option', name=name, exact=True).click()

    def select_target_node(self, name):
        """设置指令序列的目标节点（DV-SAT-01/DV-SAT-02，整条序列共用一个）。"""
        self.target_node_select.click()
        self.page.get_by_role('option', name=name, exact=True).click()
