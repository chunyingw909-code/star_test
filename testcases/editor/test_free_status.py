import allure
from playwright.sync_api import expect


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('添加状态灯后画布出现组件，默认显示"状态"和"正常"')
@allure.severity(allure.severity_level.BLOCKER)
def test_status_default(free_status_page):
    # 画布断言
    expect(free_status_page.canvas_widgets()).to_have_count(1)
    expect(free_status_page.canvas_widgets().first).to_contain_text('状态')
    expect(free_status_page.canvas_widgets().first).to_contain_text('正常')


@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('点击组件，属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_select_shows_properties(free_status_page):
    free_status_page.click_widget()
    expect(free_status_page.prop_panel).to_be_visible()
    # 右侧断言
    expect(free_status_page.prop_label).to_have_value('状态')
    expect(free_status_page.prop_status_text).to_have_value('正常')
    expect(free_status_page.prop_normal_color).to_have_value('#2FC25B')
    expect(free_status_page.prop_warning_color).to_have_value('#F4D03F')
    expect(free_status_page.prop_danger_color).to_have_value('#E74C3C')
    expect(free_status_page.prop_offline_color).to_have_value('#666')
    expect(free_status_page.prop_size).to_have_value('36')


@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('点击画布空白区域，属性面板隐藏')
@allure.severity(allure.severity_level.NORMAL)
def test_status_click_blank_hides_properties(free_status_page):
    free_status_page.click_widget()
    expect(free_status_page.prop_panel).to_be_visible()
    free_status_page.click_canvas_blank()
    expect(free_status_page.prop_panel).to_be_hidden()


# ==================== 标签 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('修改标签为"姿轨控 姿态控制"')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_modify_label(free_status_page):
    free_status_page.click_widget()
    free_status_page.prop_label.fill('姿轨控 姿态控制')
    # 右侧断言
    expect(free_status_page.prop_label).to_have_value('姿轨控 姿态控制')
    # 画布断言
    expect(free_status_page.canvas_widgets().first).to_contain_text('姿轨控 姿态控制')


@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('清空标签')
@allure.severity(allure.severity_level.NORMAL)
def test_status_clear_label(free_status_page):
    free_status_page.click_widget()
    free_status_page.prop_label.fill('')
    # 右侧断言
    expect(free_status_page.prop_label).to_have_value('')


@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('标签恢复为"状态"')
@allure.severity(allure.severity_level.NORMAL)
def test_status_label_recover(free_status_page):
    free_status_page.click_widget()
    free_status_page.prop_label.fill('姿轨控 姿态控制')
    free_status_page.prop_label.fill('状态')
    # 右侧断言
    expect(free_status_page.prop_label).to_have_value('状态')
    # 画布断言
    expect(free_status_page.canvas_widgets().first).to_contain_text('状态')


# ==================== 状态文字 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('修改状态文字为"警告"')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_modify_status_text(free_status_page):
    free_status_page.click_widget()
    free_status_page.prop_status_text.fill('警告')
    # 右侧断言
    expect(free_status_page.prop_status_text).to_have_value('警告')
    # 画布断言
    expect(free_status_page.canvas_widgets().first).to_contain_text('警告')


@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('清空状态文字')
@allure.severity(allure.severity_level.NORMAL)
def test_status_clear_status_text(free_status_page):
    free_status_page.click_widget()
    free_status_page.prop_status_text.fill('')
    # 右侧断言
    expect(free_status_page.prop_status_text).to_have_value('')
    # 画布断言
    expect(free_status_page.canvas_widgets().first).not_to_contain_text('正常')


@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('状态文字恢复为"正常"')
@allure.severity(allure.severity_level.NORMAL)
def test_status_status_text_recover(free_status_page):
    free_status_page.click_widget()
    free_status_page.prop_status_text.fill('警告')
    free_status_page.prop_status_text.fill('正常')
    # 右侧断言
    expect(free_status_page.prop_status_text).to_have_value('正常')
    # 画布断言
    expect(free_status_page.canvas_widgets().first).to_contain_text('正常')


# ==================== 颜色 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('修改正常颜色为 #00FF00')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_normal_color_green(free_status_page):
    free_status_page.click_widget()
    free_status_page.prop_normal_color.fill('#00FF00')
    # 右侧断言
    expect(free_status_page.prop_normal_color).to_have_value('#00FF00')


@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('正常颜色恢复为默认 #2FC25B')
@allure.severity(allure.severity_level.NORMAL)
def test_status_normal_color_recover(free_status_page):
    free_status_page.click_widget()
    free_status_page.prop_normal_color.fill('#00FF00')
    free_status_page.prop_normal_color.fill('#2FC25B')
    # 右侧断言
    expect(free_status_page.prop_normal_color).to_have_value('#2FC25B')


@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('修改警告颜色为 #F4D03F')
@allure.severity(allure.severity_level.NORMAL)
def test_status_warning_color(free_status_page):
    free_status_page.click_widget()
    free_status_page.prop_warning_color.fill('#F4D03F')
    # 右侧断言
    expect(free_status_page.prop_warning_color).to_have_value('#F4D03F')


@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('修改危险颜色为 #FF0000')
@allure.severity(allure.severity_level.NORMAL)
def test_status_danger_color(free_status_page):
    free_status_page.click_widget()
    free_status_page.prop_danger_color.fill('#FF0000')
    # 右侧断言
    expect(free_status_page.prop_danger_color).to_have_value('#FF0000')


@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('修改离线颜色为 #999999')
@allure.severity(allure.severity_level.NORMAL)
def test_status_offline_color(free_status_page):
    free_status_page.click_widget()
    free_status_page.prop_offline_color.fill('#999999')
    # 右侧断言
    expect(free_status_page.prop_offline_color).to_have_value('#999999')


# ==================== 尺寸 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('尺寸调大为80')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_size_80(free_status_page):
    free_status_page.click_widget()
    free_status_page.prop_size.fill('80')
    # 右侧断言
    expect(free_status_page.prop_size).to_have_value('80')


@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('尺寸调小为12')
@allure.severity(allure.severity_level.NORMAL)
def test_status_size_12(free_status_page):
    free_status_page.click_widget()
    free_status_page.prop_size.fill('12')
    # 右侧断言
    expect(free_status_page.prop_size).to_have_value('12')


@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('尺寸恢复为36')
@allure.severity(allure.severity_level.NORMAL)
def test_status_size_recover(free_status_page):
    free_status_page.click_widget()
    free_status_page.prop_size.fill('80')
    free_status_page.prop_size.fill('36')
    # 右侧断言
    expect(free_status_page.prop_size).to_have_value('36')


# ==================== 显示标签 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('隐藏标签（选择"否"）')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_hide_label(free_status_page):
    free_status_page.click_widget()
    free_status_page.show_label_radio('否').check()
    # 右侧断言
    expect(free_status_page.show_label_radio('否')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('恢复显示标签（选择"是"）')
@allure.severity(allure.severity_level.NORMAL)
def test_status_show_label_recover(free_status_page):
    free_status_page.click_widget()
    free_status_page.show_label_radio('否').check()
    free_status_page.show_label_radio('是').check()
    # 右侧断言
    expect(free_status_page.show_label_radio('是')).to_be_checked()
    # 画布断言
    expect(free_status_page.canvas_widgets().first).to_contain_text('状态')


# ==================== 告警闪烁 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('关闭告警闪烁（选择"否"）')
@allure.severity(allure.severity_level.NORMAL)
def test_status_blink_off(free_status_page):
    free_status_page.click_widget()
    free_status_page.blink_radio('否').check()
    # 右侧断言
    expect(free_status_page.blink_radio('否')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('开启告警闪烁（选择"是"）')
@allure.severity(allure.severity_level.NORMAL)
def test_status_blink_on(free_status_page):
    free_status_page.click_widget()
    free_status_page.blink_radio('否').check()
    free_status_page.blink_radio('是').check()
    # 右侧断言
    expect(free_status_page.blink_radio('是')).to_be_checked()


# ==================== 数据绑定 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('输入数据源和字段路径')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_data_binding(free_status_page):
    free_status_page.click_widget()
    free_status_page.prop_data_source.fill('SAT-01')
    free_status_page.prop_field_path.fill('attitude.status')
    # 右侧断言
    expect(free_status_page.prop_data_source).to_have_value('SAT-01')
    expect(free_status_page.prop_field_path).to_have_value('attitude.status')


# ==================== 删除 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('删除状态灯组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_delete(free_status_page):
    expect(free_status_page.canvas_widgets()).to_have_count(1)
    free_status_page.delete_widget()
    expect(free_status_page.canvas_widgets()).to_have_count(0)


# ==================== 组合修改 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-状态灯组件')
@allure.title('组合修改标签、状态文字、警告颜色与尺寸')
@allure.severity(allure.severity_level.CRITICAL)
def test_status_combined(free_status_page):
    free_status_page.click_widget()
    free_status_page.prop_label.fill('姿轨控 姿态控制')
    free_status_page.prop_status_text.fill('警告')
    free_status_page.prop_warning_color.fill('#FFA500')
    free_status_page.prop_size.fill('80')
    # 右侧断言
    expect(free_status_page.prop_label).to_have_value('姿轨控 姿态控制')
    expect(free_status_page.prop_status_text).to_have_value('警告')
    expect(free_status_page.prop_warning_color).to_have_value('#FFA500')
    expect(free_status_page.prop_size).to_have_value('80')
    # 画布断言
    expect(free_status_page.canvas_widgets().first).to_contain_text('姿轨控 姿态控制')
    expect(free_status_page.canvas_widgets().first).to_contain_text('警告')
