import allure
import pytest
from playwright.sync_api import expect


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('添加图表后画布出现组件，渲染 echarts 画布')
@allure.severity(allure.severity_level.BLOCKER)
def test_chart_default(free_chart_page):
    expect(free_chart_page.canvas_widgets()).to_have_count(1)
    expect(free_chart_page.canvas_widgets().first).to_contain_text('真实数据图表')
    expect(free_chart_page.canvas_widgets().first).to_contain_text('演示数据')
    expect(free_chart_page.widget_canvas()).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('点击图表，属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_select_shows_properties(free_chart_page):
    free_chart_page.click_widget()
    expect(free_chart_page.prop_panel).to_be_visible()
    # 基础属性
    expect(free_chart_page.prop_title).to_have_value('真实数据图表')
    expect(free_chart_page.prop_chart_type).to_have_text('折线')
    expect(free_chart_page.prop_theme).to_have_text('深色')
    expect(free_chart_page.prop_legend_position).to_have_text('底部')
    # 数值项
    expect(free_chart_page.prop_warning_line).to_have_value('0')
    expect(free_chart_page.prop_danger_line).to_have_value('0')
    expect(free_chart_page.prop_line_width).to_have_value('1.5')
    expect(free_chart_page.prop_fill_opacity).to_have_value('0')
    # 是/否 单选
    expect(free_chart_page.legend_radio('是')).to_be_checked()
    expect(free_chart_page.tooltip_radio('是')).to_be_checked()
    expect(free_chart_page.zoom_radio('否')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('点空白区域，属性面板消失')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_click_blank_hides_properties(free_chart_page):
    free_chart_page.click_widget()
    expect(free_chart_page.prop_title).to_be_visible()
    free_chart_page.click_canvas_blank()
    expect(free_chart_page.prop_title).to_be_hidden()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('交互事件区六个下拉全部渲染，默认未选择')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_event_selects_default(free_chart_page):
    free_chart_page.click_widget()
    # 默认未选择时 MUI Select 展示为空（零宽字符），选中后才显示选项文案
    for label in free_chart_page.EVENT_SELECTS:
        sel = free_chart_page.event_select(label)
        expect(sel).to_be_visible()
        assert sel.inner_text().strip() in ('', '​'), f'{label} 默认应为空，实际 {sel.inner_text()!r}'


# ==================== 标题 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('修改标题为"母线电压趋势"')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_modify_title(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_title.fill('母线电压趋势')
    expect(free_chart_page.prop_title).to_have_value('母线电压趋势')
    expect(free_chart_page.canvas_widgets().first).to_contain_text('母线电压趋势')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('标题恢复为"真实数据图表"')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_title_recover(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_title.fill('母线电压趋势')
    free_chart_page.prop_title.fill('真实数据图表')
    expect(free_chart_page.prop_title).to_have_value('真实数据图表')


# ==================== 图表类型 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('切换图表类型')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('name', ['柱状', '饼图', '折线'])
def test_chart_type(free_chart_page, name):
    free_chart_page.click_widget()
    free_chart_page.pick_option(free_chart_page.prop_chart_type, name)
    expect(free_chart_page.prop_chart_type).to_have_text(name)


# ==================== 主题 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('切换主题为浅色，再切回深色')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_theme_toggle(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.pick_option(free_chart_page.prop_theme, '浅色')
    expect(free_chart_page.prop_theme).to_have_text('浅色')
    free_chart_page.pick_option(free_chart_page.prop_theme, '深色')
    expect(free_chart_page.prop_theme).to_have_text('深色')


# ==================== 图例位置 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('切换图例位置')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize('name', ['顶部', '左侧', '底部'])
def test_chart_legend_position(free_chart_page, name):
    free_chart_page.click_widget()
    free_chart_page.pick_option(free_chart_page.prop_legend_position, name)
    expect(free_chart_page.prop_legend_position).to_have_text(name)


# ==================== 图例 / 提示 / 缩放 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('隐藏图例再恢复')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_legend_toggle(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.legend_radio('否').check()
    expect(free_chart_page.legend_radio('否')).to_be_checked()
    free_chart_page.legend_radio('是').check()
    expect(free_chart_page.legend_radio('是')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('隐藏提示再恢复')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_tooltip_toggle(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.tooltip_radio('否').check()
    expect(free_chart_page.tooltip_radio('否')).to_be_checked()
    free_chart_page.tooltip_radio('是').check()
    expect(free_chart_page.tooltip_radio('是')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('开启数据缩放再关闭')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_zoom_toggle(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.zoom_radio('是').check()
    expect(free_chart_page.zoom_radio('是')).to_be_checked()
    free_chart_page.zoom_radio('否').check()
    expect(free_chart_page.zoom_radio('否')).to_be_checked()


# ==================== 警告线 / 危险线 / 线宽 / 填充透明度 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('修改警告线 / 危险线 / 线宽 / 填充透明度')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('attr, value', [
    ('prop_warning_line', '80'),
    ('prop_danger_line', '95'),
    ('prop_line_width', '3'),
    ('prop_fill_opacity', '0.4'),
])
def test_chart_numeric_props(free_chart_page, attr, value):
    free_chart_page.click_widget()
    field = getattr(free_chart_page, attr)
    field.fill(value)
    expect(field).to_have_value(value)


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('线宽从 3 恢复为 1.5')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_line_width_recover(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_line_width.fill('3')
    free_chart_page.prop_line_width.fill('1.5')
    expect(free_chart_page.prop_line_width).to_have_value('1.5')


# ==================== 交互事件 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('设置点击事件为"弹窗提示"')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_click_event_alert(free_chart_page):
    free_chart_page.click_widget()
    sel = free_chart_page.event_select('点击事件')
    free_chart_page.pick_option(sel, '弹窗提示')
    expect(sel).to_have_text('弹窗提示')


@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('设置定时触发为"刷新数据"')
@allure.severity(allure.severity_level.NORMAL)
def test_chart_timer_event_refresh(free_chart_page):
    free_chart_page.click_widget()
    sel = free_chart_page.event_select('定时触发')
    free_chart_page.pick_option(sel, '刷新数据')
    expect(sel).to_have_text('刷新数据')


# ==================== 数据绑定对话框 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-图表组件')
@allure.title('点击"配置数据绑定"打开对话框，取消关闭')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_bind_dialog_open_cancel(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.open_bind_dialog()
    expect(free_chart_page.bind_dialog).to_contain_text('配置图表真实数据')
    expect(free_chart_page.bind_dialog_save).to_be_visible()
    free_chart_page.close_bind_dialog()
    expect(free_chart_page.bind_dialog).to_have_count(0)


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
@allure.title('组合修改标题、图表类型、主题与警告线')
@allure.severity(allure.severity_level.CRITICAL)
def test_chart_combined(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.prop_title.fill('母线电压趋势')
    free_chart_page.pick_option(free_chart_page.prop_chart_type, '柱状')
    free_chart_page.pick_option(free_chart_page.prop_theme, '浅色')
    free_chart_page.prop_warning_line.fill('80')
    expect(free_chart_page.prop_title).to_have_value('母线电压趋势')
    expect(free_chart_page.prop_chart_type).to_have_text('柱状')
    expect(free_chart_page.prop_theme).to_have_text('浅色')
    expect(free_chart_page.prop_warning_line).to_have_value('80')
    expect(free_chart_page.canvas_widgets().first).to_contain_text('母线电压趋势')
