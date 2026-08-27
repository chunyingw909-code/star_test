import allure
from playwright.sync_api import expect


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('添加图表后画布出现组件')
@allure.severity(allure.severity_level.BLOCKER)
def test_chart_default(free_chart_page):
    # 画布断言（未点击选中，无属性断言）
    expect(free_chart_page.canvas_widgets()).to_have_count(1)


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('点击图表，右侧属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_select_shows_properties(free_chart_page):
    free_chart_page.click_widget()
    expect(free_chart_page.prop_panel).to_be_visible()
    # 右侧断言
    expect(free_chart_page.prop_title).to_have_value('遥测图表')
    expect(free_chart_page.prop_x_field).to_have_value('time')
    expect(free_chart_page.prop_y_field).to_have_value('voltage,current')
    expect(free_chart_page.prop_series_name).to_have_value('母线电压,母线电流')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('点空白区域，属性面板消失')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_click_blank_hides_properties(free_chart_page):
    free_chart_page.click_widget()
    expect(free_chart_page.prop_panel).to_be_visible()
    free_chart_page.click_canvas_blank()
    expect(free_chart_page.prop_panel).to_be_hidden()


# ==================== 标题 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('修改标题为"母线电压趋势"')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_modify_title(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_title.fill('母线电压趋势')
    # 右侧断言
    expect(free_chart_page.prop_title).to_have_value('母线电压趋势')


# ==================== 图表类型 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('切换图表类型为柱状图')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_type_bar(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_chart_type.click()
    free_chart_page.page.get_by_role('option', name='柱状').click()
    # 右侧断言
    expect(free_chart_page.prop_chart_type).to_have_text('柱状')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('切换图表类型为饼图')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_type_pie(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_chart_type.click()
    free_chart_page.page.get_by_role('option', name='饼图').click()
    # 右侧断言
    expect(free_chart_page.prop_chart_type).to_have_text('饼图')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('切换图表类型回折线图')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_type_line(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_chart_type.click()
    free_chart_page.page.get_by_role('option', name='折线').click()
    # 右侧断言
    expect(free_chart_page.prop_chart_type).to_have_text('折线')


# ==================== 图例 / 提示 / 缩放 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('隐藏图例（选择"否"）')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_hide_legend(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.legend_radio('否').check()
    # 右侧断言
    expect(free_chart_page.legend_radio('否')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('恢复显示图例（选择"是"）')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_show_legend(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.legend_radio('否').check()
    free_chart_page.legend_radio('是').check()
    # 右侧断言
    expect(free_chart_page.legend_radio('是')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('隐藏提示（选择"否"）')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_hide_tooltip(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.tooltip_radio('否').check()
    # 右侧断言
    expect(free_chart_page.tooltip_radio('否')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('恢复显示提示（选择"是"）')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_show_tooltip(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.tooltip_radio('否').check()
    free_chart_page.tooltip_radio('是').check()
    # 右侧断言
    expect(free_chart_page.tooltip_radio('是')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('开启数据缩放（选择"是"）')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_enable_zoom(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.zoom_radio('是').check()
    # 右侧断言
    expect(free_chart_page.zoom_radio('是')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('关闭数据缩放（选择"否"）')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_disable_zoom(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.zoom_radio('是').check()
    free_chart_page.zoom_radio('否').check()
    # 右侧断言
    expect(free_chart_page.zoom_radio('否')).to_be_checked()


# ==================== X轴 / Y轴 / 系列名称 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('修改X轴字段为"timestamp"')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_modify_x_field(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_x_field.fill('timestamp')
    # 右侧断言
    expect(free_chart_page.prop_x_field).to_have_value('timestamp')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('X轴字段恢复为"time"')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_x_field_recover(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_x_field.fill('timestamp')
    free_chart_page.prop_x_field.fill('time')
    # 右侧断言
    expect(free_chart_page.prop_x_field).to_have_value('time')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('Y轴字段扩展为3个"voltage,current,a"，系列名称同步扩展')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_modify_y_field_three(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_y_field.fill('voltage,current,a')
    free_chart_page.prop_series_name.fill('母线电压,母线电流,a')
    # 右侧断言
    expect(free_chart_page.prop_y_field).to_have_value('voltage,current,a')
    expect(free_chart_page.prop_series_name).to_have_value('母线电压,母线电流,a')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('Y轴字段与系列名称恢复为2个')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_y_field_recover(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_y_field.fill('voltage,current,a')
    free_chart_page.prop_series_name.fill('母线电压,母线电流,a')
    free_chart_page.prop_y_field.fill('voltage,current')
    free_chart_page.prop_series_name.fill('母线电压,母线电流')
    # 右侧断言
    expect(free_chart_page.prop_y_field).to_have_value('voltage,current')
    expect(free_chart_page.prop_series_name).to_have_value('母线电压,母线电流')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('修改系列名称为"供电电压,供电电流"')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_modify_series_name(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_series_name.fill('供电电压,供电电流')
    # 右侧断言
    expect(free_chart_page.prop_series_name).to_have_value('供电电压,供电电流')


# ==================== 主题 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('切换主题为浅色')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_theme_light(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_theme.click()
    free_chart_page.page.get_by_role('option', name='浅色').click()
    # 右侧断言
    expect(free_chart_page.prop_theme).to_have_text('浅色')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('切换主题为深色（从浅色恢复）')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_theme_dark(free_chart_page):
    free_chart_page.click_widget()
    # 先切换到浅色
    free_chart_page.prop_theme.click()
    free_chart_page.page.get_by_role('option', name='浅色').click()
    # 再切回深色
    free_chart_page.prop_theme.click()
    free_chart_page.page.get_by_role('option', name='深色').click()
    # 右侧断言
    expect(free_chart_page.prop_theme).to_have_text('深色')


# ==================== 数据绑定 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('输入卫星标识和Y轴字段')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_satellite_data(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_satellite_id.fill('SAT-01')
    free_chart_page.prop_y_field.fill('voltage')
    # 右侧断言
    expect(free_chart_page.prop_satellite_id).to_have_value('SAT-01')
    expect(free_chart_page.prop_y_field).to_have_value('voltage')


# ==================== 删除 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('删除图表组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_delete(free_chart_page):
    expect(free_chart_page.canvas_widgets()).to_have_count(1)
    free_chart_page.delete_widget()
    expect(free_chart_page.canvas_widgets()).to_have_count(0)


# ==================== 组合修改 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('组合修改标题、图表类型与Y轴字段')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_combined(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_title.fill('母线电压趋势')
    free_chart_page.prop_chart_type.click()
    free_chart_page.page.get_by_role('option', name='柱状').click()
    free_chart_page.prop_y_field.fill('voltage,current,a')
    free_chart_page.prop_series_name.fill('母线电压,母线电流,a')
    # 右侧断言
    expect(free_chart_page.prop_title).to_have_value('母线电压趋势')
    expect(free_chart_page.prop_chart_type).to_have_text('柱状')
    expect(free_chart_page.prop_y_field).to_have_value('voltage,current,a')
    expect(free_chart_page.prop_series_name).to_have_value('母线电压,母线电流,a')
