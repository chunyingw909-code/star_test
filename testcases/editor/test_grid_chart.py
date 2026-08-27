import allure
from playwright.sync_api import expect


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('拖拽图表后画布出现组件')
@allure.severity(allure.severity_level.BLOCKER)
def test_chart_default(grid_chart_page):
    # 画布断言
    expect(grid_chart_page.canvas_widgets()).to_have_count(1)


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('点击图表，右侧属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_select_shows_properties(grid_chart_page):
    grid_chart_page.click_widget()
    # 右侧断言
    expect(grid_chart_page.prop_title).to_have_value('遥测图表')
    expect(grid_chart_page.prop_x_field).to_have_value('time')
    expect(grid_chart_page.prop_y_fields).to_have_value('voltage,current')
    expect(grid_chart_page.prop_series_names).to_have_value('母线电压,母线电流')


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('点击空白区域，右侧切换回Page属性')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_click_blank_shows_page(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.click_canvas_blank()
    expect(grid_chart_page.page.get_by_title('布局列数')).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('修改标题为"母线电压趋势"')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_modify_title(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_title.fill('母线电压趋势')
    # 右侧断言
    expect(grid_chart_page.prop_title).to_have_value('母线电压趋势')


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('切换图表类型为柱状图')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_type_bar(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_chart_type.select_option(label='柱状')
    # 右侧断言
    expect(grid_chart_page.prop_chart_type).to_have_value('{"value":"bar"}')


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('切换图表类型为饼图')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_type_pie(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_chart_type.select_option(label='饼图')
    # 右侧断言
    expect(grid_chart_page.prop_chart_type).to_have_value('{"value":"pie"}')


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('切换图表类型回折线图')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_type_line(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_chart_type.select_option(label='折线')
    # 右侧断言
    expect(grid_chart_page.prop_chart_type).to_have_value('{"value":"line"}')


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('隐藏图例（选择"否"）')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_hide_legend(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.legend_label('否').click()
    # 右侧断言
    expect(grid_chart_page.legend_radio('否')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('恢复显示图例（选择"是"）')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_show_legend(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.legend_label('否').click()
    grid_chart_page.legend_label('是').click()
    # 右侧断言
    expect(grid_chart_page.legend_radio('是')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('隐藏提示（选择"否"）')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_hide_tooltip(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.tooltip_label('否').click()
    # 右侧断言
    expect(grid_chart_page.tooltip_radio('否')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('恢复显示提示（选择"是"）')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_show_tooltip(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.tooltip_label('否').click()
    grid_chart_page.tooltip_label('是').click()
    # 右侧断言
    expect(grid_chart_page.tooltip_radio('是')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('开启数据缩放（选择"是"）')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_enable_zoom(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.zoom_label('是').click()
    # 右侧断言
    expect(grid_chart_page.zoom_radio('是')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('关闭数据缩放（选择"否"）')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_disable_zoom(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.zoom_label('是').click()
    grid_chart_page.zoom_label('否').click()
    # 右侧断言
    expect(grid_chart_page.zoom_radio('否')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('修改系列名称为"供电电压,供电电流"')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_modify_series_name(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_series_names.fill('供电电压,供电电流')
    # 右侧断言
    expect(grid_chart_page.prop_series_names).to_have_value('供电电压,供电电流')


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('修改X轴字段为"timestamp"')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_modify_x_field(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_x_field.fill('timestamp')
    # 右侧断言
    expect(grid_chart_page.prop_x_field).to_have_value('timestamp')


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('X轴字段恢复为"time"')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_x_field_recover(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_x_field.fill('timestamp')
    grid_chart_page.prop_x_field.fill('time')
    # 右侧断言
    expect(grid_chart_page.prop_x_field).to_have_value('time')


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('Y轴字段扩展为3个"voltage,current,a"，系列名称同步扩展')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_modify_y_fields_three(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_y_fields.fill('voltage,current,a')
    grid_chart_page.prop_series_names.fill('母线电压,母线电流,a')
    # 右侧断言
    expect(grid_chart_page.prop_y_fields).to_have_value('voltage,current,a')
    expect(grid_chart_page.prop_series_names).to_have_value('母线电压,母线电流,a')


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('Y轴字段与系列名称恢复为2个')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_y_fields_recover(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_y_fields.fill('voltage,current,a')
    grid_chart_page.prop_series_names.fill('母线电压,母线电流,a')
    grid_chart_page.prop_y_fields.fill('voltage,current')
    grid_chart_page.prop_series_names.fill('母线电压,母线电流')
    # 右侧断言
    expect(grid_chart_page.prop_y_fields).to_have_value('voltage,current')
    expect(grid_chart_page.prop_series_names).to_have_value('母线电压,母线电流')


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('切换主题为浅色')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_theme_light(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_theme.select_option(label='浅色')
    # 右侧断言
    expect(grid_chart_page.prop_theme).to_have_value('{"value":"light"}')


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('切换主题为深色（恢复）')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_theme_dark(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_theme.select_option(label='浅色')
    grid_chart_page.prop_theme.select_option(label='深色')
    # 右侧断言
    expect(grid_chart_page.prop_theme).to_have_value('{"value":"dark"}')


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('输入卫星标识和Y轴字段')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_satellite_data(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_data_source.fill('SAT-01')
    grid_chart_page.prop_y_fields.fill('voltage')
    # 右侧断言
    expect(grid_chart_page.prop_data_source).to_have_value('SAT-01')
    expect(grid_chart_page.prop_y_fields).to_have_value('voltage')


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('复制图表组件，画布出现两个相同组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_duplicate(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.duplicate_button.dispatch_event('click')
    # 右侧断言（复制后新组件被选中，属性不变）
    expect(grid_chart_page.prop_title).to_have_value('遥测图表')
    expect(grid_chart_page.prop_x_field).to_have_value('time')
    expect(grid_chart_page.prop_y_fields).to_have_value('voltage,current')
    # 数量断言
    expect(grid_chart_page.canvas_widgets()).to_have_count(2)


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('删除图表组件，画布无组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_delete(grid_chart_page):
    # 画布断言
    expect(grid_chart_page.canvas_widgets()).to_have_count(1)
    grid_chart_page.delete_button.click()
    # 数量断言
    expect(grid_chart_page.canvas_widgets()).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('组合修改标题、图表类型与Y轴字段')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_combined(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_title.fill('母线电压趋势')
    grid_chart_page.prop_chart_type.select_option(label='柱状')
    grid_chart_page.prop_y_fields.fill('voltage,current,a')
    grid_chart_page.prop_series_names.fill('母线电压,母线电流,a')
    # 右侧断言
    expect(grid_chart_page.prop_title).to_have_value('母线电压趋势')
    expect(grid_chart_page.prop_chart_type).to_have_value('{"value":"bar"}')
    expect(grid_chart_page.prop_y_fields).to_have_value('voltage,current,a')
    expect(grid_chart_page.prop_series_names).to_have_value('母线电压,母线电流,a')
