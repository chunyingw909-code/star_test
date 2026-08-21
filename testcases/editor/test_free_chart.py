from playwright.sync_api import expect


# 添加图表后画布出现组件
def test_chart_default(free_chart_page):
    expect(free_chart_page.canvas_widgets()).to_have_count(1)
    # 无属性断言，因为未点击选中


# 点击图表，属性面板显示默认值
def test_chart_select_shows_properties(free_chart_page):
    free_chart_page.click_widget()
    expect(free_chart_page.prop_panel).to_be_visible()
    # 右侧断言
    expect(free_chart_page.prop_title).to_have_value('遥测图表')
    expect(free_chart_page.prop_x_field).to_have_value('time')
    expect(free_chart_page.prop_y_field).to_have_value('voltage,current')
    expect(free_chart_page.prop_series_name).to_have_value('母线电压,母线电流')


# 点空白区域 属性面板消失
def test_chart_click_blank_hides_properties(free_chart_page):
    free_chart_page.click_widget()
    expect(free_chart_page.prop_panel).to_be_visible()
    free_chart_page.click_canvas_blank()
    expect(free_chart_page.prop_panel).to_be_hidden()


# 修改标题
def test_chart_modify_title(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_title.fill('母线电压趋势')
    # 右侧断言
    expect(free_chart_page.prop_title).to_have_value('母线电压趋势')


# 切换图表类型为柱状图
def test_chart_type_bar(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_chart_type.click()
    free_chart_page.page.get_by_role('option', name='柱状').click()
    # 右侧断言
    expect(free_chart_page.prop_chart_type).to_have_text('柱状')


# 切换图表类型为饼图
def test_chart_type_pie(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_chart_type.click()
    free_chart_page.page.get_by_role('option', name='饼图').click()
    # 右侧断言
    expect(free_chart_page.prop_chart_type).to_have_text('饼图')


# 切换图表类型回折线图
def test_chart_type_line(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_chart_type.click()
    free_chart_page.page.get_by_role('option', name='折线').click()
    # 右侧断言
    expect(free_chart_page.prop_chart_type).to_have_text('折线')


# 隐藏图例
def test_chart_hide_legend(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.legend_radio('否').check()
    # 右侧断言
    expect(free_chart_page.legend_radio('否')).to_be_checked()


# 显示图例从否改回是
def test_chart_show_legend(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.legend_radio('否').check()
    free_chart_page.legend_radio('是').check()
    # 右侧断言
    expect(free_chart_page.legend_radio('是')).to_be_checked()


# 隐藏提示
def test_chart_hide_tooltip(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.tooltip_radio('否').check()
    # 右侧断言
    expect(free_chart_page.tooltip_radio('否')).to_be_checked()


# 显示提示从否改回是
def test_chart_show_tooltip(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.tooltip_radio('否').check()
    free_chart_page.tooltip_radio('是').check()
    # 右侧断言
    expect(free_chart_page.tooltip_radio('是')).to_be_checked()


# 开启数据缩放
def test_chart_enable_zoom(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.zoom_radio('是').check()
    # 右侧断言
    expect(free_chart_page.zoom_radio('是')).to_be_checked()


# 关闭数据缩放
def test_chart_disable_zoom(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.zoom_radio('是').check()
    free_chart_page.zoom_radio('否').check()
    # 右侧断言
    expect(free_chart_page.zoom_radio('否')).to_be_checked()


# 修改系列名称
def test_chart_modify_series_name(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_series_name.fill('供电电压,供电电流')
    # 右侧断言
    expect(free_chart_page.prop_series_name).to_have_value('供电电压,供电电流')


# 切换主题为浅色
def test_chart_theme_light(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_theme.click()
    free_chart_page.page.get_by_role('option', name='浅色').click()
    # 右侧断言
    expect(free_chart_page.prop_theme).to_have_text('浅色')


# 输入卫星标识和Y轴字段
def test_chart_satellite_data(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_satellite_id.fill('SAT-01')
    free_chart_page.prop_y_field.fill('voltage')
    # 右侧断言
    expect(free_chart_page.prop_satellite_id).to_have_value('SAT-01')
    expect(free_chart_page.prop_y_field).to_have_value('voltage')


# 删除图表
def test_chart_delete(free_chart_page, assert_screenshot):
    expect(free_chart_page.canvas_widgets()).to_have_count(1)
    free_chart_page.delete_widget()
    expect(free_chart_page.canvas_widgets()).to_have_count(0)

# 切换主题为深色（从浅色恢复）
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