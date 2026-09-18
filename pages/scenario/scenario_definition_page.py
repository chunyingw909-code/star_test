class ScenarioDefinitionPage:
    """场景定义页；本轮只覆盖抽屉入口和快速创建参数回显。"""

    def __init__(self, page):
        self.page = page

        # ==================== 场景定义 - 页面标志 ====================
        self.heading = page.get_by_role(
            'heading', name='场景定义', exact=True)
        self.name_input = page.get_by_role(
            'textbox', name='名称', exact=True)
        self.create_button = page.get_by_role(
            'button', name='创建场景', exact=True)

        # ==================== 场景定义 - 参数分区 Tab ====================
        self.orbit_tab = page.get_by_role(
            'tab', name='轨道参数', exact=True)
        self.aocs_tab = page.get_by_role(
            'tab', name='AOCS 专有参数', exact=True)

        # ==================== 场景定义 - 快速创建参数回显 ====================
        self.step_input = page.get_by_role(
            'spinbutton', name='仿真步长', exact=True).last
        self.drag_coefficient_input = page.get_by_role(
            'spinbutton', name='大气阻力系数', exact=True)
        self.moon_checkbox = page.get_by_role(
            'checkbox', name='月球', exact=True)
        self.satellite_name_input = page.get_by_role(
            'textbox', name='航天器名称', exact=True)
        self.semimajor_axis_input = page.get_by_role(
            'spinbutton', name='半长轴 a (km)', exact=True)
        self.inclination_input = page.get_by_role(
            'spinbutton', name='倾角 i (°)', exact=True)
        self.satellite_mass_input = page.get_by_role(
            'spinbutton', name='卫星质量 (kg)', exact=True)
        self.propellant_mass_input = page.get_by_role(
            'spinbutton', name='推进剂质量 (kg)', exact=True)
        self.station_altitude_input = page.get_by_role(
            'spinbutton', name='测站海拔(m)', exact=True)
