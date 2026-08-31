import allure
import pytest
from playwright.sync_api import expect


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('拖拽图表后画布出现组件，渲染 echarts 画布')
@allure.severity(allure.severity_level.BLOCKER)
def test_chart_default(grid_chart_page):
    expect(grid_chart_page.canvas_widgets()).to_have_count(1)
    expect(grid_chart_page.canvas_widgets().first).to_contain_text('真实数据图表')
    expect(grid_chart_page.widget_canvas()).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('点击图表，右侧属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_select_shows_properties(grid_chart_page):
    grid_chart_page.click_widget()
    expect(grid_chart_page.prop_title).to_have_value('真实数据图表')
    expect(grid_chart_page.prop_chart_type).to_have_value('{"value":"line"}')
    expect(grid_chart_page.prop_theme).to_have_value('{"value":"dark"}')
    expect(grid_chart_page.prop_legend_position).to_have_value('{"value":"bottom"}')
    expect(grid_chart_page.prop_warning_line).to_have_value('0')
    expect(grid_chart_page.prop_danger_line).to_have_value('0')
    expect(grid_chart_page.prop_line_width).to_have_value('1.5')
    expect(grid_chart_page.prop_fill_opacity).to_have_value('0')
    expect(grid_chart_page.legend_radio('是')).to_be_checked()
    expect(grid_chart_page.tooltip_radio('是')).to_be_checked()
    expect(grid_chart_page.zoom_radio('否')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('点击空白区域，右侧切换回Page属性')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_click_blank_shows_page(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.click_canvas_blank()
    expect(grid_chart_page.page_props_marker).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('交互事件下拉默认全部为"无"')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_event_selects_default(grid_chart_page):
    grid_chart_page.click_widget()
    for title in grid_chart_page.EVENT_SELECTS:
        expect(grid_chart_page.event_select(title)).to_have_value('{"value":""}')


# ==================== 标题 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('修改标题为"母线电压趋势"')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_modify_title(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_title.fill('母线电压趋势')
    expect(grid_chart_page.prop_title).to_have_value('母线电压趋势')
    expect(grid_chart_page.canvas_widgets().first).to_contain_text('母线电压趋势')


# ==================== 图表类型 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('切换图表类型')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('name', ['柱状', '饼图', '折线'])
def test_chart_type(grid_chart_page, name):
    grid_chart_page.click_widget()
    grid_chart_page.prop_chart_type.select_option(label=name)
    expect(grid_chart_page.prop_chart_type).to_have_value(grid_chart_page.CHART_TYPES[name])


# ==================== 主题 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('切换主题为浅色，再切回深色')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_theme_toggle(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_theme.select_option(label='浅色')
    expect(grid_chart_page.prop_theme).to_have_value('{"value":"light"}')
    grid_chart_page.prop_theme.select_option(label='深色')
    expect(grid_chart_page.prop_theme).to_have_value('{"value":"dark"}')


# ==================== 图例位置 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('切换图例位置')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize('name', ['顶部', '左侧', '底部'])
def test_chart_legend_position(grid_chart_page, name):
    grid_chart_page.click_widget()
    grid_chart_page.prop_legend_position.select_option(label=name)
    expect(grid_chart_page.prop_legend_position).to_have_value(grid_chart_page.LEGEND_POSITIONS[name])


# ==================== 图例 / 提示 / 缩放 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('隐藏图例再恢复')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_legend_toggle(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.legend_label('否').click()
    expect(grid_chart_page.legend_radio('否')).to_be_checked()
    grid_chart_page.legend_label('是').click()
    expect(grid_chart_page.legend_radio('是')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('隐藏提示再恢复')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_tooltip_toggle(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.tooltip_label('否').click()
    expect(grid_chart_page.tooltip_radio('否')).to_be_checked()
    grid_chart_page.tooltip_label('是').click()
    expect(grid_chart_page.tooltip_radio('是')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('开启数据缩放再关闭')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_zoom_toggle(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.zoom_label('是').click()
    expect(grid_chart_page.zoom_radio('是')).to_be_checked()
    grid_chart_page.zoom_label('否').click()
    expect(grid_chart_page.zoom_radio('否')).to_be_checked()


# ==================== 数值项 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('修改警告线 / 危险线 / 线宽 / 填充透明度')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('attr, value', [
    ('prop_warning_line', '80'),
    ('prop_danger_line', '95'),
    ('prop_line_width', '3'),
    ('prop_fill_opacity', '0.4'),
])
def test_chart_numeric_props(grid_chart_page, attr, value):
    grid_chart_page.click_widget()
    field = getattr(grid_chart_page, attr)
    field.fill(value)
    expect(field).to_have_value(value)


# ==================== 交互事件 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('设置点击事件为"弹窗提示"，并填写点击目标')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_click_event_alert(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.event_select('点击事件').select_option(label='弹窗提示')
    expect(grid_chart_page.event_select('点击事件')).to_have_value('{"value":"alert"}')
    target = grid_chart_page.prop_click_target
    target.fill('阈值超限')
    expect(target).to_have_value('阈值超限')


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('设置定时触发为"刷新数据"')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_timer_event_refresh(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.event_select('定时触发').select_option(label='刷新数据')
    expect(grid_chart_page.event_select('定时触发')).to_have_value('{"value":"refresh"}')


# ==================== 数据绑定对话框 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('点击"配置数据绑定"打开对话框，取消关闭')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bind_dialog_open_cancel(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.open_bind_dialog()
    expect(grid_chart_page.bind_dialog).to_contain_text('配置图表真实数据')
    expect(grid_chart_page.bind_dialog_save).to_be_visible()
    grid_chart_page.close_bind_dialog()
    expect(grid_chart_page.bind_dialog).to_have_count(0)


# ==================== 复制 / 删除 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('复制图表组件，画布出现两个相同组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_duplicate(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.duplicate_widget()
    expect(grid_chart_page.prop_title).to_have_value('真实数据图表')
    expect(grid_chart_page.canvas_widgets()).to_have_count(2)


@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('删除图表组件，画布无组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_delete(grid_chart_page):
    expect(grid_chart_page.canvas_widgets()).to_have_count(1)
    grid_chart_page.delete_widget()
    expect(grid_chart_page.canvas_widgets()).to_have_count(0)


# ==================== 组合修改 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-图表组件')
@allure.title('组合修改标题、图表类型、主题与警告线')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_combined(grid_chart_page):
    grid_chart_page.click_widget()
    grid_chart_page.prop_title.fill('母线电压趋势')
    grid_chart_page.prop_chart_type.select_option(label='柱状')
    grid_chart_page.prop_theme.select_option(label='浅色')
    grid_chart_page.prop_warning_line.fill('80')
    expect(grid_chart_page.prop_title).to_have_value('母线电压趋势')
    expect(grid_chart_page.prop_chart_type).to_have_value('{"value":"bar"}')
    expect(grid_chart_page.prop_theme).to_have_value('{"value":"light"}')
    expect(grid_chart_page.prop_warning_line).to_have_value('80')
    expect(grid_chart_page.canvas_widgets().first).to_contain_text('母线电压趋势')
