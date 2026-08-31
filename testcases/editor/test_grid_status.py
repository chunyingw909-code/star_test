import allure
from playwright.sync_api import expect


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('拖拽状态指示器后画布出现组件，默认显示"状态"和"正常"')
@allure.severity(allure.severity_level.BLOCKER)
def test_status_default(grid_status_page):
    # 画布断言
    expect(grid_status_page.canvas_widgets()).to_have_count(1)
    expect(grid_status_page.canvas_widgets().first).to_contain_text('状态')
    expect(grid_status_page.canvas_widgets().first).to_contain_text('正常')


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('点击组件，右侧属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_select_shows_properties(grid_status_page):
    # 右侧断言
    expect(grid_status_page.prop_label).to_have_value('状态')
    expect(grid_status_page.prop_status_text).to_have_value('正常')
    expect(grid_status_page.prop_normal_color).to_have_value('#2FC25B')
    expect(grid_status_page.prop_warning_color).to_have_value('#F4D03F')
    expect(grid_status_page.prop_danger_color).to_have_value('#E74C3C')
    expect(grid_status_page.prop_offline_color).to_have_value('#666')
    expect(grid_status_page.prop_size).to_have_value('36')
    # 画布断言
    dot = grid_status_page.canvas_widgets().first.locator('div:empty')
    expect(dot).to_have_css('width', '36px')
    expect(dot).to_have_css('height', '36px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('点击空白区域，右侧切换回Page属性')
@allure.severity(allure.severity_level.NORMAL)
def test_status_click_blank_shows_page(grid_status_page):
    grid_status_page.click_canvas_blank()
    expect(grid_status_page.page_props_marker).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('修改标签为"姿轨控姿态控制"')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_modify_label(grid_status_page):
    grid_status_page.prop_label.fill('姿轨控姿态控制')
    # 右侧断言
    expect(grid_status_page.prop_label).to_have_value('姿轨控姿态控制')
    # 画布断言
    expect(grid_status_page.canvas_widgets().first).to_contain_text('姿轨控姿态控制')


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('标签恢复为"状态"')
@allure.severity(allure.severity_level.NORMAL)
def test_status_label_recover(grid_status_page):
    grid_status_page.prop_label.fill('姿轨控姿态控制')
    grid_status_page.prop_label.fill('状态')
    # 右侧断言
    expect(grid_status_page.prop_label).to_have_value('状态')
    # 画布断言
    expect(grid_status_page.canvas_widgets().first).to_contain_text('状态')


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('修改状态文字为"警告"')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_modify_status_text(grid_status_page):
    grid_status_page.prop_status_text.fill('警告')
    # 右侧断言
    expect(grid_status_page.prop_status_text).to_have_value('警告')
    # 画布断言
    expect(grid_status_page.canvas_widgets().first).to_contain_text('警告')


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('状态文字恢复为"正常"')
@allure.severity(allure.severity_level.NORMAL)
def test_status_status_text_recover(grid_status_page):
    grid_status_page.prop_status_text.fill('警告')
    grid_status_page.prop_status_text.fill('正常')
    # 右侧断
    expect(grid_status_page.prop_status_text).to_have_value('正常')
    # 画布断言
    expect(grid_status_page.canvas_widgets().first).to_contain_text('正常')


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('修改正常颜色为 #00FF00')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_modify_normal_color(grid_status_page):
    grid_status_page.prop_normal_color.fill('#00FF00')
    # 右侧断言
    expect(grid_status_page.prop_normal_color).to_have_value('#00FF00')


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('修改警告颜色为 #FFA500')
@allure.severity(allure.severity_level.NORMAL)
def test_status_modify_warning_color(grid_status_page):
    grid_status_page.prop_warning_color.fill('#FFA500')
    # 右侧断言
    expect(grid_status_page.prop_warning_color).to_have_value('#FFA500')


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('修改危险颜色为 #FF0000')
@allure.severity(allure.severity_level.NORMAL)
def test_status_modify_danger_color(grid_status_page):
    grid_status_page.prop_danger_color.fill('#FF0000')
    # 右侧断言
    expect(grid_status_page.prop_danger_color).to_have_value('#FF0000')


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('修改离线颜色为 #999999')
@allure.severity(allure.severity_level.NORMAL)
def test_status_modify_offline_color(grid_status_page):
    grid_status_page.prop_offline_color.fill('#999999')
    # 右侧断言
    expect(grid_status_page.prop_offline_color).to_have_value('#999999')


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('颜色恢复为默认')
@allure.severity(allure.severity_level.NORMAL)
def test_status_color_recover(grid_status_page):
    grid_status_page.prop_normal_color.fill('#00FF00')
    grid_status_page.prop_normal_color.fill('#2FC25B')
    # 右侧断言
    expect(grid_status_page.prop_normal_color).to_have_value('#2FC25B')


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('尺寸调大为80')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_modify_size_large(grid_status_page):
    grid_status_page.prop_size.fill('80')
    # 右侧断言
    expect(grid_status_page.prop_size).to_have_value('80')
    # 画布断言
    dot = grid_status_page.canvas_widgets().first.locator('div:empty')
    expect(dot).to_have_css('width', '80px')
    expect(dot).to_have_css('height', '80px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('尺寸调小为12')
@allure.severity(allure.severity_level.NORMAL)
def test_status_modify_size_small(grid_status_page):
    grid_status_page.prop_size.fill('12')
    # 右侧断言
    expect(grid_status_page.prop_size).to_have_value('12')
    # 画布断言
    dot = grid_status_page.canvas_widgets().first.locator('div:empty')
    expect(dot).to_have_css('width', '12px')
    expect(dot).to_have_css('height', '12px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('尺寸恢复为36')
@allure.severity(allure.severity_level.NORMAL)
def test_status_size_recover(grid_status_page):
    grid_status_page.prop_size.fill('80')
    grid_status_page.prop_size.fill('36')
    # 右侧断言
    expect(grid_status_page.prop_size).to_have_value('36')
    # 画布断言
    dot = grid_status_page.canvas_widgets().first.locator('div:empty')
    expect(dot).to_have_css('width', '36px')
    expect(dot).to_have_css('height', '36px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('隐藏标签（选择"否"）')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_hide_label(grid_status_page):
    # 原生 input 被自定义样式的装饰层遮挡，点击外层 label 绕开遮挡
    grid_status_page.show_label_label('否').click()
    # 右侧断言
    expect(grid_status_page.show_label_radio('否')).to_be_checked()
    # 画布断言
    expect(grid_status_page.canvas_widgets().first).not_to_contain_text('状态')


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('恢复显示标签（选择"是"）')
@allure.severity(allure.severity_level.NORMAL)
def test_status_show_label_recover(grid_status_page):
    grid_status_page.show_label_label('否').click()
    grid_status_page.show_label_label('是').click()
    # 右侧断言
    expect(grid_status_page.show_label_radio('是')).to_be_checked()
    # 画布断言
    expect(grid_status_page.canvas_widgets().first).to_contain_text('状态')


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('关闭告警闪烁（选择"否"）')
@allure.severity(allure.severity_level.NORMAL)
def test_status_blink_off(grid_status_page):
    grid_status_page.blink_label('否').click()
    # 右侧断言
    expect(grid_status_page.blink_radio('否')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('开启告警闪烁（选择"是"）')
@allure.severity(allure.severity_level.NORMAL)
def test_status_blink_on(grid_status_page):
    grid_status_page.blink_label('否').click()
    grid_status_page.blink_label('是').click()
    # 右侧断言
    expect(grid_status_page.blink_radio('是')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('输入数据源和字段路径')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_data_binding(grid_status_page):
    grid_status_page.prop_data_source.fill('SAT-01')
    grid_status_page.prop_field_path.fill('attitude.status')
    # 右侧断言
    expect(grid_status_page.prop_data_source).to_have_value('SAT-01')
    expect(grid_status_page.prop_field_path).to_have_value('attitude.status')


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('复制状态指示器组件，画布出现两个相同组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_duplicate(grid_status_page):
    grid_status_page.duplicate_widget()
    # 右侧断言（复制后新组件被选中，属性不变）
    expect(grid_status_page.prop_label).to_have_value('状态')
    expect(grid_status_page.prop_size).to_have_value('36')
    # 数量断言
    expect(grid_status_page.canvas_widgets()).to_have_count(2)
    # 画布断言：两个组件均为默认样式
    expect(grid_status_page.canvas_widgets().nth(0)).to_contain_text('状态')
    expect(grid_status_page.canvas_widgets().nth(0)).to_contain_text('正常')
    expect(grid_status_page.canvas_widgets().nth(1)).to_contain_text('状态')
    expect(grid_status_page.canvas_widgets().nth(1)).to_contain_text('正常')


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('删除状态指示器组件，画布无组件，右侧切换为Page属性')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_delete(grid_status_page):
    grid_status_page.delete_widget()
    # 右侧断言（删除后无组件，切换为Page属性）
    expect(grid_status_page.page_props_marker).to_be_visible()
    # 数量断言
    expect(grid_status_page.canvas_widgets()).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('栅格布局-状态灯组件')
@allure.title('组合修改标签、状态文字、警告颜色与尺寸')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_combined(grid_status_page):
    grid_status_page.prop_label.fill('姿轨控 姿态控制')
    grid_status_page.prop_status_text.fill('警告')
    grid_status_page.prop_warning_color.fill('#FFA500')
    grid_status_page.prop_size.fill('80')
    # 右侧断言
    expect(grid_status_page.prop_label).to_have_value('姿轨控 姿态控制')
    expect(grid_status_page.prop_status_text).to_have_value('警告')
    expect(grid_status_page.prop_warning_color).to_have_value('#FFA500')
    expect(grid_status_page.prop_size).to_have_value('80')
    # 画布断言
    expect(grid_status_page.canvas_widgets().first).to_contain_text('姿轨控 姿态控制')
    expect(grid_status_page.canvas_widgets().first).to_contain_text('警告')
    dot = grid_status_page.canvas_widgets().first.locator('div:empty')
    expect(dot).to_have_css('width', '80px')
    expect(dot).to_have_css('height', '80px')
