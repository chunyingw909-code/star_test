from playwright.sync_api import expect


# 添加图表后画布出现组件
def test_chart_default(grid_chart_page):
    expect(grid_chart_page.canvas_widgets()).to_have_count(1)


# 点击图表，属性面板显示默认值
def test_chart_select_shows_properties(grid_chart_page):
    grid_chart_page.click_widget()
    expect(grid_chart_page.prop_title).to_have_value('遥测图表')
    expect(grid_chart_page.prop_x_field).to_have_value('time')
    expect(grid_chart_page.prop_y_fields).to_have_value('voltage,current')
    expect(grid_chart_page.prop_series_names).to_have_value('母线电压,母线电流')


# 点空白区域，切换回Page属性
def test_chart_click_blank_shows_page(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.click_canvas_blank()
    expect(grid_chart_page.page.get_by_title('布局列数')).to_be_visible()


# 修改标题
def test_chart_modify_title(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_title.fill('母线电压趋势')
    expect(grid_chart_page.prop_title).to_have_value('母线电压趋势')


# 切换图表类型为柱状图
def test_chart_type_bar(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_chart_type.select_option(label='柱状')
    expect(grid_chart_page.prop_chart_type).to_have_value('{"value":"bar"}')


# 切换图表类型为饼图
def test_chart_type_pie(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_chart_type.select_option(label='饼图')
    expect(grid_chart_page.prop_chart_type).to_have_value('{"value":"pie"}')


# 切换图表类型回折线图
def test_chart_type_line(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_chart_type.select_option(label='折线')
    expect(grid_chart_page.prop_chart_type).to_have_value('{"value":"line"}')


# 隐藏图例
def test_chart_hide_legend(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.legend_label('否').click()
    expect(grid_chart_page.legend_radio('否')).to_be_checked()


# 显示图例从否改回是
def test_chart_show_legend(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.legend_label('否').click()
    grid_chart_page.legend_label('是').click()
    expect(grid_chart_page.legend_radio('是')).to_be_checked()


# 隐藏提示
def test_chart_hide_tooltip(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.tooltip_label('否').click()
    expect(grid_chart_page.tooltip_radio('否')).to_be_checked()


# 显示提示从否改回是
def test_chart_show_tooltip(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.tooltip_label('否').click()
    grid_chart_page.tooltip_label('是').click()
    expect(grid_chart_page.tooltip_radio('是')).to_be_checked()


# 开启数据缩放
def test_chart_enable_zoom(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.zoom_label('是').click()
    expect(grid_chart_page.zoom_radio('是')).to_be_checked()


# 关闭数据缩放
def test_chart_disable_zoom(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.zoom_label('是').click()
    grid_chart_page.zoom_label('否').click()
    expect(grid_chart_page.zoom_radio('否')).to_be_checked()


# 修改系列名称
def test_chart_modify_series_name(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_series_names.fill('供电电压,供电电流')
    expect(grid_chart_page.prop_series_names).to_have_value('供电电压,供电电流')


# 切换主题为浅色
def test_chart_theme_light(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_theme.select_option(label='浅色')
    expect(grid_chart_page.prop_theme).to_have_value('{"value":"light"}')


# 切换主题为深色（恢复）
def test_chart_theme_dark(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_theme.select_option(label='浅色')
    grid_chart_page.prop_theme.select_option(label='深色')
    expect(grid_chart_page.prop_theme).to_have_value('{"value":"dark"}')


# 输入卫星标识和Y轴字段
def test_chart_satellite_data(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_data_source.fill('SAT-01')
    grid_chart_page.prop_y_fields.fill('voltage')
    expect(grid_chart_page.prop_data_source).to_have_value('SAT-01')
    expect(grid_chart_page.prop_y_fields).to_have_value('voltage')


# 删除图表（不截图）
def test_chart_delete(grid_chart_page):
    expect(grid_chart_page.canvas_widgets()).to_have_count(1)
    grid_chart_page.delete_button.click()
    expect(grid_chart_page.canvas_widgets()).to_have_count(0)