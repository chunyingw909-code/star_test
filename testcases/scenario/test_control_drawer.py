import re

import allure
from playwright.sync_api import expect


@allure.feature('右侧管理抽屉')
@allure.story('管控 Tab - 节点管控')
@allure.title('基础入口可见，两个仿真节点均在线，默认自带一行 START/延时0 的指令')
@allure.severity(allure.severity_level.CRITICAL)
def test_control_tab_shows_nodes_and_default_row(control_drawer_page):
    drawer = control_drawer_page

    for locator in (
            drawer.node_control_heading,
            drawer.sequence_heading,
            drawer.import_csv_button,
            drawer.add_command_button,
            drawer.send_sequence_button):
        expect(locator).to_be_visible()

    assert drawer.node_names_list() == ['DV-SAT-01', 'DV-SAT-02']
    assert drawer.node_status('DV-SAT-01') == 'ONLINE'
    assert drawer.node_status('DV-SAT-02') == 'ONLINE'

    # 首次进入自带一行默认指令：延时 0、类型 START。
    assert drawer.row_count() == 1
    expect(drawer.delay_inputs.first).to_have_value('0')
    expect(drawer.type_selects.first).to_have_text('START')


@allure.feature('右侧管理抽屉')
@allure.story('管控 Tab - 节点管控')
@allure.title('点击节点行弹出该节点的连接信息（地址/TCP/UDP端口）')
@allure.severity(allure.severity_level.NORMAL)
def test_click_node_shows_connection_info(control_drawer_page):
    drawer = control_drawer_page

    drawer.click_node('DV-SAT-02')
    expect(drawer.page.get_by_text(re.compile(r'TCP\s*[:：]?\s*\d+'))).to_be_visible()


@allure.feature('右侧管理抽屉')
@allure.story('管控 Tab - 指令序列')
@allure.title('添加指令行可填写延时/类型/模块，删除后行数恢复')
@allure.severity(allure.severity_level.CRITICAL)
def test_add_and_remove_command_row(control_drawer_page):
    drawer = control_drawer_page
    initial_count = drawer.row_count()

    index = drawer.add_command(delay=3000, command_type='FAULT', module='EPS')
    assert drawer.row_count() == initial_count + 1
    expect(drawer.delay_inputs.nth(index)).to_have_value('3000')
    expect(drawer.type_selects.nth(index)).to_have_text('FAULT')
    expect(drawer.module_inputs.nth(index)).to_have_value('EPS')

    drawer.remove_command(index)
    assert drawer.row_count() == initial_count


@allure.feature('右侧管理抽屉')
@allure.story('管控 Tab - 指令序列')
@allure.title('指令行「类型」下拉的可选项固定为 START/MANEUVER/ATTITUDE/MODE/FAULT 五种')
@allure.severity(allure.severity_level.NORMAL)
def test_command_type_options(control_drawer_page):
    drawer = control_drawer_page

    drawer.type_selects.first.click()
    options = drawer.page.get_by_role('option')
    assert [o.strip() for o in options.all_inner_texts()] == list(drawer.TYPE_OPTIONS)


@allure.feature('右侧管理抽屉')
@allure.story('管控 Tab - 指令序列')
@allure.title('目标节点下拉可在 DV-SAT-01/DV-SAT-02 间切换')
@allure.severity(allure.severity_level.NORMAL)
def test_target_node_select_switch(control_drawer_page):
    drawer = control_drawer_page

    expect(drawer.target_node_select).to_have_text('DV-SAT-01')
    drawer.select_target_node('DV-SAT-02')
    expect(drawer.target_node_select).to_have_text('DV-SAT-02')


@allure.feature('右侧管理抽屉')
@allure.story('管控 Tab - 指令模板')
@allure.title('姿态机动模板套用后类型/参数正确回显（deltaV=10）')
@allure.severity(allure.severity_level.NORMAL)
def test_maneuver_template_prefills_type_and_param(control_drawer_page):
    drawer = control_drawer_page

    drawer.select_template('姿态机动 (SATELLITE)')

    # 套用模板会把整条序列收窄成一行，带出模板的默认参数。
    assert drawer.row_count() == 1
    expect(drawer.type_selects.first).to_have_text('MANEUVER')
    expect(drawer.page.get_by_role('spinbutton', name='deltaV', exact=True)).to_have_value('10')
