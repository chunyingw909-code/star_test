import re

import allure
from playwright.sync_api import expect

from pages.scenario.scenario_definition_page import ScenarioDefinitionPage


@allure.feature('右侧管理抽屉')
@allure.story('场景 Tab - 列表与搜索')
@allure.title('基础入口可见，已存场景数量与列表一致，搜索支持命中和空结果')
@allure.severity(allure.severity_level.CRITICAL)
def test_scenario_list_count_and_search(scenario_drawer_page):
    drawer = scenario_drawer_page

    # 三个场景创建入口和搜索框均可见。
    for locator in (
            drawer.quick_create_button,
            drawer.advanced_create_button,
            drawer.template_library_button,
            drawer.search_input):
        expect(locator).to_be_visible()

    # “已存场景 (N)”和列表内容必须与 /api/scenarios 当前响应一致。
    api_names = [item['name'] for item in drawer.scenario_inventory()]
    initial_names = drawer.visible_scenario_names()
    assert drawer.saved_count() == len(initial_names)
    assert initial_names == api_names
    assert api_names, '场景接口当前没有可用于搜索验证的数据'
    target = api_names[-1]

    # 输入当前列表中真实存在的完整名称，只显示该场景，数量同步变为 1。
    drawer.search_input.fill(target)
    expect(drawer.saved_count_text).to_have_text('已存场景 (1)')
    assert drawer.visible_scenario_names() == [target]

    # 输入不存在的关键字，列表为空并显示“暂无场景”。
    drawer.search_input.fill('AUTOTEST-NO-SUCH-SCENARIO')
    expect(drawer.saved_count_text).to_have_text('已存场景 (0)')
    expect(drawer.empty_scenario_text).to_be_visible()
    assert drawer.visible_scenario_names() == []


@allure.feature('右侧管理抽屉')
@allure.story('场景 Tab - 场景切换')
@allure.title('切换场景弹窗文案正确：取消不切换，确定后顶部和卫星选择同步更新')
@allure.severity(allure.severity_level.BLOCKER)
def test_switch_scenario_cancel_then_confirm(scenario_switch_page):
    drawer, source, target = scenario_switch_page

    # 固定前置已生效：顶部和卫星选择区都显示原场景。
    expect(drawer.current_scenario_chip).to_have_text(source)
    expect(drawer.satellite_selection_label).to_contain_text(source)

    drawer.click_scenario(target)

    # 弹窗明确提示切换影响，并同时列出当前场景与目标场景。
    expect(drawer.switch_dialog).to_contain_text('切换场景将停止当前场景的仿真进程。')
    expect(drawer.switch_dialog).to_contain_text(f'当前 {source}')
    expect(drawer.switch_dialog).to_contain_text(f'切换到 {target}')

    # 取消后场景保持不变。
    drawer.switch_cancel_button.click()
    expect(drawer.switch_dialog).to_be_hidden()
    expect(drawer.current_scenario_chip).to_have_text(source)
    expect(drawer.satellite_selection_label).to_contain_text(source)

    # 再次选择并确认，两个场景标志都应同步更新。
    drawer.click_scenario(target)
    drawer.switch_confirm_button.click()
    expect(drawer.switch_dialog).to_be_hidden()
    expect(drawer.current_scenario_chip).to_have_text(target)
    expect(drawer.satellite_selection_label).to_contain_text(target)


@allure.feature('右侧管理抽屉')
@allure.story('场景 Tab - 快速创建')
@allure.title('快速创建可展开/收起，场景名称必填且不能与已存场景重名')
@allure.severity(allure.severity_level.CRITICAL)
def test_quick_create_toggle_and_name_validation(scenario_drawer_page):
    drawer = scenario_drawer_page
    scenarios = drawer.scenario_inventory()
    assert scenarios, '场景接口当前没有可用于重名校验的数据'
    duplicate_name = scenarios[-1]['name']

    drawer.quick_create_button.click()

    # 空名称显示必填提示，“下一步”不可用。
    expect(drawer.quick_name_input).to_be_visible()
    expect(drawer.quick_empty_name_error).to_be_visible()
    expect(drawer.quick_next_button).to_be_disabled()

    # 输入已存场景名称显示重名提示，仍不能进入下一步。
    drawer.quick_name_input.fill(duplicate_name)
    expect(drawer.quick_duplicate_name_error).to_be_visible()
    expect(drawer.quick_next_button).to_be_disabled()

    # 再点一次快速创建收起表单，场景列表仍保留。
    drawer.quick_create_button.click()
    expect(drawer.quick_name_input).to_be_hidden()
    expect(drawer.saved_count_text).to_be_visible()


@allure.feature('右侧管理抽屉')
@allure.story('场景 Tab - 快速创建与删除')
@allure.title('快速创建保留自定义参数；删除取消不生效，确认删除后列表数量实时恢复')
@allure.severity(allure.severity_level.BLOCKER)
def test_quick_create_values_persist_and_delete_flow(scenario_create_case):
    drawer, name = scenario_create_case
    satellite_name = 'SAT-01'
    initial_count = drawer.saved_count()

    drawer.quick_create_button.click()

    # 第一步：名称和时空参数。
    drawer.quick_name_input.fill(name)
    drawer.quick_step_input.fill('2')
    expect(drawer.quick_next_button).to_be_enabled()
    drawer.quick_next_button.click()

    # 第二步：空间环境参数。
    drawer.quick_drag_coefficient_input.fill('2.5')
    drawer.quick_moon_checkbox.uncheck()
    drawer.quick_next_button.click()

    # 第三步：轨道参数。
    expect(drawer.quick_satellite_name_input).to_have_value(satellite_name)
    expect(drawer.quick_satellite_name_input).to_have_attribute('readonly', '')
    drawer.quick_semimajor_axis_input.fill('7200')
    drawer.quick_inclination_input.fill('50')
    drawer.quick_next_button.click()

    # 第四步不添加事件，直接进入 AOCS 参数。
    drawer.quick_next_button.click()

    # 第五步：AOCS 专有参数。
    drawer.quick_satellite_mass_input.fill('650')
    drawer.quick_propellant_mass_input.fill('65')
    drawer.quick_station_altitude_input.fill('80')
    drawer.quick_next_button.click()

    # 第六步保留默认节点配置并创建场景。
    drawer.quick_create_scene_button.click()

    # 创建成功后表单收起、列表数量加一、新场景立即出现。
    expect(drawer.quick_name_input).to_be_hidden()
    expect(drawer.saved_count_text).to_have_text(
        f'已存场景 ({initial_count + 1})')
    expect(drawer.scenario_row(name)).to_be_visible()

    drawer.click_edit(name)
    definition = ScenarioDefinitionPage(drawer.page)

    # 小笔进入带场景 ID 的定义页，保存的关键参数全部回显。
    expect(drawer.page).to_have_url(re.compile(r'/scenarios\?id=[^&]+$'))
    expect(definition.heading).to_be_visible()
    expect(definition.name_input).to_have_value(name)
    expect(definition.step_input).to_have_value('2')
    expect(definition.drag_coefficient_input).to_have_value('2.5')
    expect(definition.moon_checkbox).not_to_be_checked()

    # 轨道、AOCS 和节点参数按场景定义页的 Tab 分组回显。
    definition.orbit_tab.click()
    expect(definition.satellite_name_input).to_have_value(satellite_name)
    expect(definition.semimajor_axis_input).to_have_value('7200')
    expect(definition.inclination_input).to_have_value('50')

    definition.aocs_tab.click()
    expect(definition.satellite_mass_input).to_have_value('650')
    expect(definition.propellant_mass_input).to_have_value('65')
    expect(definition.station_altitude_input).to_have_value('80')

    drawer.return_home_and_open()
    drawer.click_delete(name)

    # 删除提示明确；点取消后场景和数量都不变。
    expect(drawer.delete_dialog).to_contain_text('确认删除该场景？')
    drawer.delete_cancel_button.click()
    expect(drawer.delete_dialog).to_be_hidden()
    expect(drawer.scenario_row(name)).to_be_visible()
    assert drawer.saved_count() == initial_count + 1

    # 再次打开并确认删除，行消失且数量恢复。
    drawer.click_delete(name)
    drawer.confirm_delete_and_wait()
    expect(drawer.saved_count_text).to_have_text(
        f'已存场景 ({initial_count})')
    assert name not in drawer.visible_scenario_names()


@allure.feature('右侧管理抽屉')
@allure.story('场景 Tab - 编辑入口')
@allure.title('点击现有场景的小笔，进入带该场景 ID 的场景定义页')
@allure.severity(allure.severity_level.CRITICAL)
def test_edit_existing_scenario_opens_definition(scenario_drawer_page):
    drawer = scenario_drawer_page
    scenarios = drawer.scenario_inventory()
    assert scenarios, '场景接口当前没有可用于编辑入口验证的数据'
    target = scenarios[-1]['name']

    drawer.click_edit(target)
    definition = ScenarioDefinitionPage(drawer.page)

    # 编辑现有场景的 URL 带 id，定义页名称与所点场景一致。
    expect(drawer.page).to_have_url(re.compile(r'/scenarios\?id=[^&]+$'))
    expect(definition.heading).to_be_visible()
    expect(definition.name_input).to_have_value(target)


@allure.feature('右侧管理抽屉')
@allure.story('场景 Tab - 高级构建')
@allure.title('点击高级构建进入不带 ID 的新场景定义页，名称为空且创建按钮禁用')
@allure.severity(allure.severity_level.CRITICAL)
def test_advanced_create_opens_blank_definition(scenario_drawer_page):
    drawer = scenario_drawer_page

    drawer.advanced_create_button.click()
    definition = ScenarioDefinitionPage(drawer.page)

    # 新建 URL 不带 id，必填名称为空，所以“创建场景”不可用。
    expect(drawer.page).to_have_url(re.compile(r'/scenarios$'))
    expect(definition.heading).to_be_visible()
    expect(definition.name_input).to_have_value('')
    expect(definition.create_button).to_be_disabled()


@allure.feature('右侧管理抽屉')
@allure.story('场景 Tab - 模板库')
@allure.title('模板库显示已有模板，点击弹窗外空白处可关闭')
@allure.severity(allure.severity_level.NORMAL)
def test_template_dialog_closes_on_backdrop(scenario_drawer_page):
    drawer = scenario_drawer_page
    templates = drawer.template_inventory()
    assert templates, '场景模板接口当前没有可用于模板库验证的数据'

    drawer.template_library_button.click()

    # 模板弹窗打开，接口返回的真实模板可见。
    expect(drawer.template_dialog).to_be_visible()
    expect(drawer.template_card(templates[0])).to_be_visible()

    # 点击弹窗外遮罩关闭模板库。
    drawer.template_backdrop.click(position={'x': 5, 'y': 5}, force=True)
    expect(drawer.template_dialog).to_be_hidden()
