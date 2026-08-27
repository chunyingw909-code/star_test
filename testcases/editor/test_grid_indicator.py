import allure
from playwright.sync_api import expect


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('拖拽指示牌后画布出现组件，默认显示"CPU 使用率"')
@allure.severity(allure.severity_level.BLOCKER)
def test_indicator_default(grid_indicator_page):
    # 画布断言
    expect(grid_indicator_page.canvas_widgets()).to_have_count(1)
    expect(grid_indicator_page.canvas_widgets().first).to_contain_text('CPU 使用率')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('点击组件，右侧属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_select_shows_properties(grid_indicator_page):
    # 右侧断言
    expect(grid_indicator_page.prop_label).to_have_value('CPU 使用率')
    expect(grid_indicator_page.prop_value).to_have_value('45.2')
    expect(grid_indicator_page.prop_unit).to_have_value('%')
    expect(grid_indicator_page.prop_warning_threshold).to_have_value('70')
    expect(grid_indicator_page.prop_danger_threshold).to_have_value('90')
    expect(grid_indicator_page.prop_icon).to_have_value('{"value":"cpu"}')
    expect(grid_indicator_page.prop_decimal).to_have_value('1')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('点击空白区域，右侧切换回Page属性')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_click_blank_shows_page(grid_indicator_page):
    grid_indicator_page.click_canvas_blank()
    expect(grid_indicator_page.page.get_by_title('布局列数')).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('修改标签为"母线电流"')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_modify_label(grid_indicator_page):
    grid_indicator_page.prop_label.fill('母线电流')
    # 右侧断言
    expect(grid_indicator_page.prop_label).to_have_value('母线电流')
    # 画布断言
    expect(grid_indicator_page.canvas_widgets().first).to_contain_text('母线电流')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('清空标签，画布不再显示原标签文字')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_clear_label(grid_indicator_page):
    grid_indicator_page.prop_label.fill('')
    # 右侧断言
    expect(grid_indicator_page.prop_label).to_have_value('')
    # 画布断言
    expect(grid_indicator_page.canvas_widgets().first).not_to_contain_text('CPU 使用率')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('标签恢复为"CPU 使用率"')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_label_recover(grid_indicator_page):
    grid_indicator_page.prop_label.fill('母线电流')
    grid_indicator_page.prop_label.fill('CPU 使用率')
    # 右侧断言
    expect(grid_indicator_page.prop_label).to_have_value('CPU 使用率')
    # 画布断言
    expect(grid_indicator_page.canvas_widgets().first).to_contain_text('CPU 使用率')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('修改数值为88.5')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_modify_value(grid_indicator_page):
    grid_indicator_page.prop_value.fill('88.5')
    # 右侧断言
    expect(grid_indicator_page.prop_value).to_have_value('88.5')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('数值调整为0')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_value_zero(grid_indicator_page):
    grid_indicator_page.prop_value.fill('0')
    # 右侧断言
    expect(grid_indicator_page.prop_value).to_have_value('0')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('数值恢复为45.2')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_value_recover(grid_indicator_page):
    grid_indicator_page.prop_value.fill('88.5')
    grid_indicator_page.prop_value.fill('45.2')
    # 右侧断言
    expect(grid_indicator_page.prop_value).to_have_value('45.2')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('修改单位为"A"')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_modify_unit(grid_indicator_page):
    grid_indicator_page.prop_unit.fill('A')
    # 右侧断言
    expect(grid_indicator_page.prop_unit).to_have_value('A')
    # 画布断言
    expect(grid_indicator_page.canvas_widgets().first).to_contain_text('A')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('清空单位')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_unit_clear(grid_indicator_page):
    grid_indicator_page.prop_unit.fill('')
    # 右侧断言
    expect(grid_indicator_page.prop_unit).to_have_value('')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('单位恢复为"%"')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_unit_recover(grid_indicator_page):
    grid_indicator_page.prop_unit.fill('A')
    grid_indicator_page.prop_unit.fill('%')
    # 右侧断言
    expect(grid_indicator_page.prop_unit).to_have_value('%')
    # 画布断言
    expect(grid_indicator_page.canvas_widgets().first).to_contain_text('%')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('数值88.5，处于警告阈值(70)与危险阈值(90)之间')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_warning_threshold(grid_indicator_page):
    grid_indicator_page.prop_warning_threshold.fill('70')
    grid_indicator_page.prop_danger_threshold.fill('90')
    grid_indicator_page.prop_value.fill('88.5')
    # 右侧断言
    expect(grid_indicator_page.prop_warning_threshold).to_have_value('70')
    expect(grid_indicator_page.prop_danger_threshold).to_have_value('90')
    expect(grid_indicator_page.prop_value).to_have_value('88.5')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('数值95，超过危险阈值(90)')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_danger_threshold(grid_indicator_page):
    grid_indicator_page.prop_warning_threshold.fill('70')
    grid_indicator_page.prop_danger_threshold.fill('90')
    grid_indicator_page.prop_value.fill('95')
    # 右侧断言
    expect(grid_indicator_page.prop_value).to_have_value('95')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('数值50，低于警告阈值(70)，正常状态')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_normal_state(grid_indicator_page):
    grid_indicator_page.prop_warning_threshold.fill('70')
    grid_indicator_page.prop_danger_threshold.fill('90')
    grid_indicator_page.prop_value.fill('50')
    # 右侧断言
    expect(grid_indicator_page.prop_value).to_have_value('50')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('切换图标为"内存"')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_icon_memory(grid_indicator_page):
    grid_indicator_page.prop_icon.select_option(label='内存')
    # 右侧断言
    expect(grid_indicator_page.prop_icon).to_have_value('{"value":"memory"}')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('切换图标为"网络"')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_icon_network(grid_indicator_page):
    grid_indicator_page.prop_icon.select_option(label='网络')
    # 右侧断言
    expect(grid_indicator_page.prop_icon).to_have_value('{"value":"network"}')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('切换图标为"温度"')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_icon_temp(grid_indicator_page):
    grid_indicator_page.prop_icon.select_option(label='温度')
    # 右侧断言
    expect(grid_indicator_page.prop_icon).to_have_value('{"value":"temp"}')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('切换图标为"速度"')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_icon_speed(grid_indicator_page):
    grid_indicator_page.prop_icon.select_option(label='速度')
    # 右侧断言
    expect(grid_indicator_page.prop_icon).to_have_value('{"value":"speed"}')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('图标恢复为"CPU"')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_icon_recover(grid_indicator_page):
    grid_indicator_page.prop_icon.select_option(label='温度')
    grid_indicator_page.prop_icon.select_option(label='CPU')
    # 右侧断言
    expect(grid_indicator_page.prop_icon).to_have_value('{"value":"cpu"}')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('小数位设置为0')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_decimal_0(grid_indicator_page):
    grid_indicator_page.prop_decimal.fill('0')
    # 右侧断言
    expect(grid_indicator_page.prop_decimal).to_have_value('0')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('小数位设置为3')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_decimal_3(grid_indicator_page):
    grid_indicator_page.prop_decimal.fill('3')
    # 右侧断言
    expect(grid_indicator_page.prop_decimal).to_have_value('3')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('小数位恢复为1')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_decimal_recover(grid_indicator_page):
    grid_indicator_page.prop_decimal.fill('0')
    grid_indicator_page.prop_decimal.fill('1')
    # 右侧断言
    expect(grid_indicator_page.prop_decimal).to_have_value('1')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('隐藏状态趋势（选择"否"）')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_hide_status(grid_indicator_page):
    grid_indicator_page.show_status_label('否').click()
    # 右侧断言
    expect(grid_indicator_page.show_status_radio('否')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('恢复显示状态趋势（选择"是"）')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_show_status_recover(grid_indicator_page):
    grid_indicator_page.show_status_label('否').click()
    grid_indicator_page.show_status_label('是').click()
    # 右侧断言
    expect(grid_indicator_page.show_status_radio('是')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('输入数据源和字段路径')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_data_binding(grid_indicator_page):
    grid_indicator_page.prop_data_source.fill('SAT-01')
    grid_indicator_page.prop_field_path.fill('cpu.usage')
    # 右侧断言
    expect(grid_indicator_page.prop_data_source).to_have_value('SAT-01')
    expect(grid_indicator_page.prop_field_path).to_have_value('cpu.usage')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('清空数据源和字段路径')
@allure.severity(allure.severity_level.NORMAL)
def test_indicator_data_binding_clear(grid_indicator_page):
    grid_indicator_page.prop_data_source.fill('SAT-01')
    grid_indicator_page.prop_field_path.fill('cpu.usage')
    grid_indicator_page.prop_data_source.fill('')
    grid_indicator_page.prop_field_path.fill('')
    # 右侧断言
    expect(grid_indicator_page.prop_data_source).to_have_value('')
    expect(grid_indicator_page.prop_field_path).to_have_value('')


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('复制指示牌组件，画布出现两个相同组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_duplicate(grid_indicator_page):
    grid_indicator_page.duplicate_button.dispatch_event('click')
    # 右侧断言（复制后新组件被选中，属性不变）
    expect(grid_indicator_page.prop_label).to_have_value('CPU 使用率')
    expect(grid_indicator_page.prop_unit).to_have_value('%')
    # 数量断言
    expect(grid_indicator_page.canvas_widgets()).to_have_count(2)


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('删除指示牌组件，画布无组件，右侧切换为Page属性')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_delete(grid_indicator_page):
    grid_indicator_page.delete_button.dispatch_event('click')
    # 右侧断言（删除后无组件，切换为Page属性）
    expect(grid_indicator_page.page.get_by_title('布局列数')).to_be_visible()
    # 数量断言
    expect(grid_indicator_page.canvas_widgets()).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('栅格布局-指示牌组件')
@allure.title('组合修改标签、数值、单位与阈值')
@allure.severity(allure.severity_level.CRITICAL)
def test_indicator_combined(grid_indicator_page):
    grid_indicator_page.prop_label.fill('母线电流')
    grid_indicator_page.prop_value.fill('88.5')
    grid_indicator_page.prop_unit.fill('A')
    grid_indicator_page.prop_warning_threshold.fill('70')
    grid_indicator_page.prop_danger_threshold.fill('90')
    # 右侧断言
    expect(grid_indicator_page.prop_label).to_have_value('母线电流')
    expect(grid_indicator_page.prop_value).to_have_value('88.5')
    expect(grid_indicator_page.prop_unit).to_have_value('A')
    # 画布断言
    expect(grid_indicator_page.canvas_widgets().first).to_contain_text('母线电流')
    expect(grid_indicator_page.canvas_widgets().first).to_contain_text('A')
