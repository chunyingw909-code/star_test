import allure
import pytest
from playwright.sync_api import expect


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-表格组件')
@allure.title('拖拽表格后画布出现组件，默认标题"数据表格"、演示数据渲染')
@allure.severity(allure.severity_level.BLOCKER)
def test_table_default(grid_table_page):
    expect(grid_table_page.canvas_widgets()).to_have_count(1)
    widget = grid_table_page.canvas_widgets().first
    expect(widget).to_contain_text('数据表格')
    expect(widget).to_contain_text('演示数据')
    for h in grid_table_page.DEMO_HEADERS:
        expect(grid_table_page.widget_thead()).to_contain_text(h)
    assert grid_table_page.widget_row_count() == grid_table_page.DEMO_ROW_COUNT


@allure.feature('界面编辑器')
@allure.story('栅格布局-表格组件')
@allure.title('点击组件，右侧属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_select_shows_properties(grid_table_page):
    expect(grid_table_page.prop_title).to_have_value('数据表格')
    expect(grid_table_page.prop_page_size).to_have_value('20')
    expect(grid_table_page.prop_max_height).to_have_value('400')
    expect(grid_table_page.prop_refresh_interval).to_have_value('0')
    expect(grid_table_page.sort_radio('是')).to_be_checked()
    expect(grid_table_page.pagination_radio('是')).to_be_checked()
    expect(grid_table_page.widget_sort_labels()).to_have_count(5)


@allure.feature('界面编辑器')
@allure.story('栅格布局-表格组件')
@allure.title('点击空白区域，右侧切换回Page属性')
@allure.severity(allure.severity_level.NORMAL)
def test_table_click_blank_shows_page(grid_table_page):
    grid_table_page.click_canvas_blank()
    expect(grid_table_page.page_props_marker).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('栅格布局-表格组件')
@allure.title('五个列筛选框渲染，placeholder 正确')
@allure.severity(allure.severity_level.NORMAL)
def test_table_filter_inputs_render(grid_table_page):
    for ph in grid_table_page.FILTER_PLACEHOLDERS:
        expect(grid_table_page.widget_filter(ph)).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('栅格布局-表格组件')
@allure.title('交互事件下拉默认全部为"无"')
@allure.severity(allure.severity_level.NORMAL)
def test_table_event_selects_default(grid_table_page):
    for title in grid_table_page.EVENT_SELECTS:
        expect(grid_table_page.event_select(title)).to_have_value('{"value":""}')


# ==================== 标题 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-表格组件')
@allure.title('修改标题为"异常事件表"')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_modify_title(grid_table_page):
    grid_table_page.prop_title.fill('异常事件表')
    expect(grid_table_page.prop_title).to_have_value('异常事件表')
    expect(grid_table_page.canvas_widgets().first).to_contain_text('异常事件表')


@allure.feature('界面编辑器')
@allure.story('栅格布局-表格组件')
@allure.title('标题恢复为"数据表格"')
@allure.severity(allure.severity_level.NORMAL)
def test_table_title_recover(grid_table_page):
    grid_table_page.prop_title.fill('异常事件表')
    grid_table_page.prop_title.fill('数据表格')
    expect(grid_table_page.prop_title).to_have_value('数据表格')
    expect(grid_table_page.canvas_widgets().first).to_contain_text('数据表格')


# ==================== 每页行数 ====================
# 演示数据固定 24 行、不分页，改每页行数在画布上没有可见变化，只校验属性值。

@allure.feature('界面编辑器')
@allure.story('栅格布局-表格组件')
@allure.title('每页行数改为 10 再恢复为 20')
@allure.severity(allure.severity_level.NORMAL)
def test_table_page_size(grid_table_page):
    grid_table_page.prop_page_size.fill('10')
    expect(grid_table_page.prop_page_size).to_have_value('10')
    grid_table_page.prop_page_size.fill('20')
    expect(grid_table_page.prop_page_size).to_have_value('20')


# ==================== 启用排序 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-表格组件')
@allure.title('关闭排序，表头排序按钮消失；恢复后回到 5 个')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_sort_toggle(grid_table_page):
    grid_table_page.sort_label('否').click()
    expect(grid_table_page.sort_radio('否')).to_be_checked()
    expect(grid_table_page.widget_sort_labels()).to_have_count(0)
    grid_table_page.sort_label('是').click()
    expect(grid_table_page.sort_radio('是')).to_be_checked()
    expect(grid_table_page.widget_sort_labels()).to_have_count(5)


# ==================== 启用分页 ====================
# 演示表格当前不渲染分页控件，只能校验单选状态。

@allure.feature('界面编辑器')
@allure.story('栅格布局-表格组件')
@allure.title('关闭分页再恢复，单选状态同步')
@allure.severity(allure.severity_level.NORMAL)
def test_table_pagination_toggle(grid_table_page):
    grid_table_page.pagination_label('否').click()
    expect(grid_table_page.pagination_radio('否')).to_be_checked()
    grid_table_page.pagination_label('是').click()
    expect(grid_table_page.pagination_radio('是')).to_be_checked()


# ==================== 最大高度 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-表格组件')
@allure.title('最大高度改为 250px，作用在滚动容器上')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_max_height_250(grid_table_page):
    grid_table_page.prop_max_height.fill('250')
    expect(grid_table_page.prop_max_height).to_have_value('250')
    expect(grid_table_page.widget_table_container()).to_have_css('max-height', '250px')


@allure.feature('界面编辑器')
@allure.story('栅格布局-表格组件')
@allure.title('最大高度恢复为 400px')
@allure.severity(allure.severity_level.NORMAL)
def test_table_max_height_recover(grid_table_page):
    grid_table_page.prop_max_height.fill('250')
    grid_table_page.prop_max_height.fill('400')
    expect(grid_table_page.prop_max_height).to_have_value('400')
    expect(grid_table_page.widget_table_container()).to_have_css('max-height', '400px')


# ==================== 刷新间隔 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-表格组件')
@allure.title('刷新间隔设为 5 秒再恢复为 0')
@allure.severity(allure.severity_level.NORMAL)
def test_table_refresh_interval(grid_table_page):
    grid_table_page.prop_refresh_interval.fill('5')
    expect(grid_table_page.prop_refresh_interval).to_have_value('5')
    grid_table_page.prop_refresh_interval.fill('0')
    expect(grid_table_page.prop_refresh_interval).to_have_value('0')


# ==================== 交互事件 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-表格组件')
@allure.title('设置点击事件为"跳转 URL"，并填写点击目标')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_click_event_navigate(grid_table_page):
    grid_table_page.event_select('点击事件').select_option(label='跳转 URL')
    expect(grid_table_page.event_select('点击事件')).to_have_value('{"value":"navigate"}')
    target = grid_table_page.prop_click_target
    target.fill('/detail')
    expect(target).to_have_value('/detail')


# ==================== 数据绑定对话框 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-表格组件')
@allure.title('点击"配置数据绑定"打开对话框，取消关闭')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_bind_dialog_open_cancel(grid_table_page):
    grid_table_page.open_bind_dialog()
    expect(grid_table_page.bind_dialog).to_contain_text('配置表格真实数据')
    expect(grid_table_page.bind_dialog_save).to_be_visible()
    grid_table_page.close_bind_dialog()
    expect(grid_table_page.bind_dialog).to_have_count(0)


# ==================== 复制 / 删除 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-表格组件')
@allure.title('复制表格组件，画布出现两个组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_duplicate(grid_table_page):
    grid_table_page.duplicate_widget()
    expect(grid_table_page.canvas_widgets()).to_have_count(2)
    expect(grid_table_page.canvas_widgets().nth(0)).to_contain_text('数据表格')
    expect(grid_table_page.canvas_widgets().nth(1)).to_contain_text('数据表格')


@allure.feature('界面编辑器')
@allure.story('栅格布局-表格组件')
@allure.title('删除表格组件，画布无组件，右侧切换为Page属性')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_delete(grid_table_page):
    grid_table_page.delete_widget()
    expect(grid_table_page.page_props_marker).to_be_visible()
    expect(grid_table_page.canvas_widgets()).to_have_count(0)


# ==================== 组合修改 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-表格组件')
@allure.title('组合修改标题、每页行数、排序与最大高度')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_combined(grid_table_page):
    grid_table_page.prop_title.fill('异常事件表')
    grid_table_page.prop_page_size.fill('10')
    grid_table_page.sort_label('否').click()
    grid_table_page.prop_max_height.fill('300')
    expect(grid_table_page.prop_title).to_have_value('异常事件表')
    expect(grid_table_page.prop_page_size).to_have_value('10')
    expect(grid_table_page.sort_radio('否')).to_be_checked()
    expect(grid_table_page.prop_max_height).to_have_value('300')
    expect(grid_table_page.canvas_widgets().first).to_contain_text('异常事件表')
    expect(grid_table_page.widget_sort_labels()).to_have_count(0)
    expect(grid_table_page.widget_table_container()).to_have_css('max-height', '300px')
