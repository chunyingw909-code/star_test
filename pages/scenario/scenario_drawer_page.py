import re

from pages.guide.guide_page import GuidePage


class ScenarioDrawerPage:
    """主页右侧管理抽屉的「场景」Tab。"""

    def __init__(self, page):
        self.page = page
        self.home_url = page.url.split('/scenarios', 1)[0]

        # ==================== 右侧抽屉 - 场景 Tab ====================
        self.drawer_open_button = page.get_by_role(
            'button', name='‹', exact=True).last
        self.scenario_tab = page.get_by_role('tab', name='场景', exact=True)
        self.quick_create_button = page.get_by_role(
            'button', name='快速创建', exact=True)
        self.advanced_create_button = page.get_by_role(
            'button', name='高级构建', exact=True)
        self.template_library_button = page.get_by_role(
            'button', name='模板库', exact=True)

        # ==================== 场景 Tab - 当前场景 ====================
        self.header = page.locator('header')
        self.current_scenario_chip = self.header.locator(
            'p').filter(has_text=re.compile(r'^T=')).locator(
                'xpath=preceding-sibling::div[contains(@class,"MuiChip-root")][1]')
        self.satellite_selection_label = page.get_by_text(
            re.compile(r'^卫星选择(?:\s*—.*)?$'))

        # ==================== 场景 Tab - 已存场景列表 ====================
        self.search_input = page.get_by_placeholder('搜索场景...')
        self.saved_count_text = page.get_by_text(
            re.compile(r'^已存场景 \(\d+\)$'))
        self.scenario_list = self.saved_count_text.locator(
            'xpath=following::ul[1]')
        self.scenario_rows = self.scenario_list.locator('li')
        self.scenario_names = self.scenario_rows.locator(
            '.MuiListItemText-primary')
        self.scenario_edit_buttons = self.scenario_rows.locator(
            'button:has(svg[data-testid="EditIcon"])')
        self.scenario_delete_buttons = self.scenario_rows.locator(
            'button:has(svg[data-testid="DeleteIcon"])')
        self.empty_scenario_text = page.get_by_text('暂无场景', exact=True)

        # ==================== 场景 Tab - 切换确认弹窗 ====================
        self.switch_dialog = page.get_by_role(
            'dialog', name='切换场景')
        self.switch_cancel_button = self.switch_dialog.get_by_role(
            'button', name='取消', exact=True)
        self.switch_confirm_button = self.switch_dialog.get_by_role(
            'button', name='确定切换', exact=True)

        # ==================== 场景 Tab - 删除确认弹窗 ====================
        self.delete_dialog = page.get_by_role(
            'dialog', name='确认删除该场景？')
        self.delete_cancel_button = self.delete_dialog.get_by_role(
            'button', name='取消', exact=True)
        self.delete_confirm_button = self.delete_dialog.get_by_role(
            'button', name='删除', exact=True)

        # ==================== 场景 Tab - 模板库弹窗 ====================
        self.template_dialog = page.get_by_role(
            'dialog', name='训练场景模板')
        self.template_cards = self.template_dialog.get_by_role('button')
        self.template_backdrop = page.locator('.MuiBackdrop-root')

        # ==================== 场景 Tab - 快速创建第一步 ====================
        self.quick_name_input = page.get_by_role(
            'textbox', name='名称', exact=True)
        self.quick_empty_name_error = page.get_by_text(
            '请输入场景名称', exact=True)
        self.quick_duplicate_name_error = page.get_by_text(
            '场景名称已存在', exact=True)
        self.quick_step_input = page.get_by_role(
            'spinbutton', name='仿真步长', exact=True)
        self.quick_next_button = page.get_by_role(
            'button', name='下一步', exact=True)

        # ==================== 场景 Tab - 快速创建空间环境 ====================
        self.quick_drag_coefficient_input = page.get_by_role(
            'spinbutton', name='大气阻力系数', exact=True)
        self.quick_moon_checkbox = page.get_by_role(
            'checkbox', name='月球', exact=True)

        # ==================== 场景 Tab - 快速创建轨道参数 ====================
        self.quick_satellite_name_input = page.get_by_role(
            'textbox', name='航天器名称', exact=True)
        self.quick_semimajor_axis_input = page.get_by_role(
            'spinbutton', name='半长轴 a (km)', exact=True)
        self.quick_inclination_input = page.get_by_role(
            'spinbutton', name='倾角 i (°)', exact=True)

        # ==================== 场景 Tab - 快速创建 AOCS 参数 ====================
        self.quick_satellite_mass_input = page.get_by_role(
            'spinbutton', name='卫星质量 (kg)', exact=True)
        self.quick_propellant_mass_input = page.get_by_role(
            'spinbutton', name='推进剂质量 (kg)', exact=True)
        self.quick_station_altitude_input = page.get_by_role(
            'spinbutton', name='测站海拔(m)', exact=True)

        # ==================== 场景 Tab - 快速创建保存 ====================
        self.quick_create_scene_button = page.get_by_role(
            'button', name='创建场景', exact=True)

    def open(self):
        """打开右侧抽屉并切到「场景」Tab。"""
        if not self.scenario_tab.is_visible():
            self.drawer_open_button.click()
            self.scenario_tab.wait_for(state='visible')
        if self.scenario_tab.get_attribute('aria-selected') != 'true':
            self.scenario_tab.click()
        self.saved_count_text.wait_for(state='visible')
        # 抽屉刚展开会先短暂渲染“已存场景 (0)”和空列表；等接口数据真正落地，
        # 避免测试和 teardown 把这个过渡态当成最终状态。
        deadline = self.page.evaluate('Date.now()') + 10000
        while self.page.evaluate('Date.now()') < deadline:
            count = self.saved_count()
            if count and count == self.scenario_rows.count():
                return self
            self.page.wait_for_timeout(200)
        raise AssertionError('场景抽屉打开后，已存场景数量与列表一直未稳定')

    def _scenario_index(self, name):
        """返回指定场景在当前筛选列表中的行号。"""
        names = [text.strip() for text in self.scenario_names.all_inner_texts()]
        if name not in names:
            raise AssertionError(f'当前场景列表中找不到「{name}」，实际为 {names}')
        return names.index(name)

    def scenario_row(self, name):
        """返回指定名称的场景行，供测试断言可见性。"""
        return self.scenario_rows.nth(self._scenario_index(name))

    def visible_scenario_names(self):
        """读取当前搜索条件下显示的全部场景名称。"""
        return [text.strip() for text in self.scenario_names.all_inner_texts()]

    def scenario_inventory(self):
        """通过 222 的场景接口读取当前真实场景，不依赖固定名称或数据库 ID。"""
        return self.page.evaluate(
            """async () => {
                const payload = await (await fetch('/api/scenarios')).json();
                const rows = Array.isArray(payload) ? payload : (payload?.data ?? []);
                return rows.map(row => ({
                    id: row.id,
                    name: row.name,
                    template: Boolean(row.template),
                }));
            }"""
        )

    def template_inventory(self):
        """通过模板接口读取当前真实模板，供模板库 UI 断言使用。"""
        return self.page.evaluate(
            """async () => {
                const token = localStorage.getItem('sarsat_token');
                const response = await fetch('/api/scenario-templates', {
                    headers: {'Authorization': `Bearer ${token}`},
                });
                if (!response.ok) {
                    throw new Error(`读取场景模板失败：HTTP ${response.status}`);
                }
                const payload = await response.json();
                const rows = Array.isArray(payload) ? payload : (payload?.data ?? []);
                return rows.map(row => ({
                    id: row.id,
                    name: row.name,
                    description: row.description ?? '',
                    type: row.type ?? row.definition?.type ?? '',
                }));
            }"""
        )

    def template_card(self, template):
        """返回接口所给模板在模板库里的卡片按钮。"""
        return self.template_cards.filter(
            has_text=template['name']).filter(has_not_text='删除模板').first

    def saved_count(self):
        """读取“已存场景 (N)”中的 N。"""
        match = re.search(r'\((\d+)\)', self.saved_count_text.inner_text())
        return int(match.group(1)) if match else None

    def click_scenario(self, name):
        """点击指定场景名称，打开场景切换确认弹窗。"""
        self.scenario_names.nth(self._scenario_index(name)).click()
        self.switch_dialog.wait_for(state='visible')

    def click_edit(self, name):
        """点击指定场景行的小笔图标，进入场景定义页。"""
        self.scenario_edit_buttons.nth(self._scenario_index(name)).click()

    def click_delete(self, name):
        """点击指定场景行的垃圾桶，打开删除确认弹窗。"""
        self.scenario_delete_buttons.nth(self._scenario_index(name)).click()
        self.delete_dialog.wait_for(state='visible')

    def confirm_delete_and_wait(self):
        """确认删除并等待 DELETE /api/scenarios/{id} 成功返回。"""
        with self.page.expect_response(
                lambda response: response.request.method == 'DELETE'
                and '/api/scenarios/' in response.url) as response_info:
            self.delete_confirm_button.click()
        response = response_info.value
        assert response.ok, f'删除场景接口失败：HTTP {response.status}'
        self.delete_dialog.wait_for(state='hidden')

    def set_current_scenario(self, scenario):
        """用场景接口返回的 id 设置当前场景，给切换测试准备稳定前置。"""
        self.page.evaluate(
            "id => localStorage.setItem('sarsat_last_scenario', id)", scenario['id'])
        self.page.reload(wait_until='networkidle')
        self.open()
        deadline = self.page.evaluate('Date.now()') + 10000
        while self.page.evaluate('Date.now()') < deadline:
            if self.current_scenario_chip.count() and (
                    self.current_scenario_chip.inner_text().strip() == scenario['name']):
                return
            self.page.wait_for_timeout(200)
        raise AssertionError(
            f'设置当前场景后，顶部仍未显示「{scenario["name"]}」')

    def return_home_and_open(self):
        """从场景定义页回到主页并重新打开场景抽屉。"""
        self.page.goto(self.home_url)
        self.page.wait_for_load_state('networkidle')
        GuidePage(self.page).complete()
        self.open()

    def delete_scenario_if_present(self, name):
        """测试收尾：若临时场景仍存在，则通过 UI 删除。"""
        self.return_home_and_open()
        self.search_input.fill('')
        if name not in self.visible_scenario_names():
            return
        self.click_delete(name)
        self.confirm_delete_and_wait()
        deadline = self.page.evaluate('Date.now()') + 5000
        while self.page.evaluate('Date.now()') < deadline:
            if name not in self.visible_scenario_names():
                return
            self.page.wait_for_timeout(200)
        raise AssertionError(f'清理临时场景「{name}」失败')
