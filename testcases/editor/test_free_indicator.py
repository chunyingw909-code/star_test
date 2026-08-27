import allure
from playwright.sync_api import expect


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('添加指示牌后画布出现组件，默认显示"CPU 使用率"')
@allure.severity(allure.severity_level.BLOCKER)
def test_indicator_default(free_indicator_page, assert_screenshot):
    # 画布断言
    expect(free_indicator_page.canvas_widgets()).to_have_count(1)
    expect(free_indicator_page.canvas_widgets().first).to_contain_text('CPU 使用率')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_default.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('点击组件，右侧属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_select_shows_properties(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    expect(free_indicator_page.prop_panel).to_be_visible()
    # 右侧断言
    expect(free_indicator_page.prop_label).to_have_value('CPU 使用率')
    expect(free_indicator_page.prop_value).to_have_value('45.2')
    expect(free_indicator_page.prop_unit).to_have_value('%')
    expect(free_indicator_page.prop_warning_threshold).to_have_value('70')
    expect(free_indicator_page.prop_danger_threshold).to_have_value('90')
    expect(free_indicator_page.prop_icon).to_have_text('CPU')
    expect(free_indicator_page.prop_decimal).to_have_value('1')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_select_shows_properties.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('点击画布空白区域，属性面板隐藏')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_click_blank_hides_properties(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    expect(free_indicator_page.prop_panel).to_be_visible()
    free_indicator_page.click_canvas_blank()
    expect(free_indicator_page.prop_panel).to_be_hidden()
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_click_blank_hides_properties.png')


# ==================== 标签 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('修改标签为"母线电流"')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_modify_label(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_label.fill('母线电流')
    # 右侧断言
    expect(free_indicator_page.prop_label).to_have_value('母线电流')
    # 画布断言
    expect(free_indicator_page.canvas_widgets().first).to_contain_text('母线电流')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_label_current.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('清空标签')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_clear_label(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_label.fill('')
    # 右侧断言
    expect(free_indicator_page.prop_label).to_have_value('')
    # 画布断言
    expect(free_indicator_page.canvas_widgets().first).not_to_contain_text('CPU 使用率')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_label_empty.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('标签恢复为"CPU 使用率"')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_label_recover(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_label.fill('母线电流')
    free_indicator_page.prop_label.fill('CPU 使用率')
    # 右侧断言
    expect(free_indicator_page.prop_label).to_have_value('CPU 使用率')
    # 画布断言
    expect(free_indicator_page.canvas_widgets().first).to_contain_text('CPU 使用率')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_label_recover.png')


# ==================== 数值 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('修改数值为88.5')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_modify_value(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_value.fill('88.5')
    # 右侧断言
    expect(free_indicator_page.prop_value).to_have_value('88.5')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_value_88_5.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('数值调整为0')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_value_zero(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_value.fill('0')
    # 右侧断言
    expect(free_indicator_page.prop_value).to_have_value('0')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_value_zero.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('数值恢复为45.2')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_value_recover(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_value.fill('88.5')
    free_indicator_page.prop_value.fill('45.2')
    # 右侧断言
    expect(free_indicator_page.prop_value).to_have_value('45.2')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_value_recover.png')


# ==================== 单位 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('修改单位为"A"')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_modify_unit(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_unit.fill('A')
    # 右侧断言
    expect(free_indicator_page.prop_unit).to_have_value('A')
    # 画布断言
    expect(free_indicator_page.canvas_widgets().first).to_contain_text('A')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_unit_a.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('清空单位')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_unit_clear(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_unit.fill('')
    # 右侧断言
    expect(free_indicator_page.prop_unit).to_have_value('')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_unit_empty.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('单位恢复为"%"')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_unit_recover(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_unit.fill('A')
    free_indicator_page.prop_unit.fill('%')
    # 右侧断言
    expect(free_indicator_page.prop_unit).to_have_value('%')
    # 画布断言
    expect(free_indicator_page.canvas_widgets().first).to_contain_text('%')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_unit_recover.png')


# ==================== 警告阈值 / 危险阈值 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('数值88.5，处于警告阈值(70)与危险阈值(90)之间')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_warning_threshold(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_warning_threshold.fill('70')
    free_indicator_page.prop_danger_threshold.fill('90')
    free_indicator_page.prop_value.fill('88.5')
    # 右侧断言
    expect(free_indicator_page.prop_warning_threshold).to_have_value('70')
    expect(free_indicator_page.prop_danger_threshold).to_have_value('90')
    expect(free_indicator_page.prop_value).to_have_value('88.5')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_warning_threshold.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('数值95，超过危险阈值(90)')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_danger_threshold(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_warning_threshold.fill('70')
    free_indicator_page.prop_danger_threshold.fill('90')
    free_indicator_page.prop_value.fill('95')
    # 右侧断言
    expect(free_indicator_page.prop_value).to_have_value('95')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_danger_threshold.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('数值50，低于警告阈值(70)，正常状态')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_normal_state(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_warning_threshold.fill('70')
    free_indicator_page.prop_danger_threshold.fill('90')
    free_indicator_page.prop_value.fill('50')
    # 右侧断言
    expect(free_indicator_page.prop_value).to_have_value('50')
    # 截图断言（数值50 < 警告70，卡片应为正常态）
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_normal_state.png')


# ==================== 图标 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('切换图标为"内存"')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_icon_memory(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_icon.click()
    free_indicator_page.page.get_by_role('option', name='内存').click()
    # 右侧断言
    expect(free_indicator_page.prop_icon).to_have_text('内存')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_icon_memory.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('切换图标为"网络"')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_icon_network(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_icon.click()
    free_indicator_page.page.get_by_role('option', name='网络').click()
    # 右侧断言
    expect(free_indicator_page.prop_icon).to_have_text('网络')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_icon_network.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('切换图标为"温度"')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_icon_temp(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_icon.click()
    free_indicator_page.page.get_by_role('option', name='温度').click()
    # 右侧断言
    expect(free_indicator_page.prop_icon).to_have_text('温度')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_icon_temp.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('切换图标为"速度"')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_icon_speed(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_icon.click()
    free_indicator_page.page.get_by_role('option', name='速度').click()
    # 右侧断言
    expect(free_indicator_page.prop_icon).to_have_text('速度')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_icon_speed.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('图标恢复为"CPU"')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_icon_recover(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_icon.click()
    free_indicator_page.page.get_by_role('option', name='温度').click()
    free_indicator_page.prop_icon.click()
    free_indicator_page.page.get_by_role('option', name='CPU').click()
    # 右侧断言
    expect(free_indicator_page.prop_icon).to_have_text('CPU')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_icon_recover.png')


# ==================== 小数位 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('小数位设置为0')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_decimal_0(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_decimal.fill('0')
    # 右侧断言
    expect(free_indicator_page.prop_decimal).to_have_value('0')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_decimal_0.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('小数位设置为3')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_decimal_3(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_decimal.fill('3')
    # 右侧断言
    expect(free_indicator_page.prop_decimal).to_have_value('3')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_decimal_3.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('小数位恢复为1')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_decimal_recover(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_decimal.fill('0')
    free_indicator_page.prop_decimal.fill('1')
    # 右侧断言
    expect(free_indicator_page.prop_decimal).to_have_value('1')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_decimal_recover.png')


# ==================== 显示状态 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('隐藏状态趋势（选择"否"）')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_hide_status(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.show_status_radio('否').check()
    # 右侧断言
    expect(free_indicator_page.show_status_radio('否')).to_be_checked()
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_hide_status.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('恢复显示状态趋势（选择"是"）')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_show_status_recover(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.show_status_radio('否').check()
    free_indicator_page.show_status_radio('是').check()
    # 右侧断言
    expect(free_indicator_page.show_status_radio('是')).to_be_checked()
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_show_status_recover.png')


# ==================== 数据绑定 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('输入数据源和字段路径')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_data_binding(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_data_source.fill('SAT-01')
    free_indicator_page.prop_field_path.fill('cpu.usage')
    # 右侧断言
    expect(free_indicator_page.prop_data_source).to_have_value('SAT-01')
    expect(free_indicator_page.prop_field_path).to_have_value('cpu.usage')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_data_binding.png')


@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('清空数据源和字段路径')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_data_binding_clear(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_data_source.fill('SAT-01')
    free_indicator_page.prop_field_path.fill('cpu.usage')
    free_indicator_page.prop_data_source.fill('')
    free_indicator_page.prop_field_path.fill('')
    # 右侧断言
    expect(free_indicator_page.prop_data_source).to_have_value('')
    expect(free_indicator_page.prop_field_path).to_have_value('')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_data_binding_clear.png')


# ==================== 删除 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('删除指示牌组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_delete(free_indicator_page):
    expect(free_indicator_page.canvas_widgets()).to_have_count(1)
    free_indicator_page.delete_widget()
    expect(free_indicator_page.canvas_widgets()).to_have_count(0)


# ==================== 组合修改 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-指示牌组件')
@allure.title('组合修改标签、数值、单位与阈值')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_combined(free_indicator_page, assert_screenshot):
    free_indicator_page.click_widget()
    free_indicator_page.prop_label.fill('母线电流')
    free_indicator_page.prop_value.fill('88.5')
    free_indicator_page.prop_unit.fill('A')
    free_indicator_page.prop_warning_threshold.fill('70')
    free_indicator_page.prop_danger_threshold.fill('90')
    # 右侧断言
    expect(free_indicator_page.prop_label).to_have_value('母线电流')
    expect(free_indicator_page.prop_value).to_have_value('88.5')
    expect(free_indicator_page.prop_unit).to_have_value('A')
    # 画布断言
    expect(free_indicator_page.canvas_widgets().first).to_contain_text('母线电流')
    expect(free_indicator_page.canvas_widgets().first).to_contain_text('A')
    # 截图断言
    assert_screenshot(free_indicator_page.canvas_widgets().first, 'free_indicator_combined.png')
