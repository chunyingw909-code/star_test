import allure
import pytest
from playwright.sync_api import expect


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('添加表格后画布出现组件，默认标题"数据表格"、演示数据渲染')
@allure.severity(allure.severity_level.BLOCKER)
def test_table_default(free_table_page):
    expect(free_table_page.canvas_widgets()).to_have_count(1)
    widget = free_table_page.canvas_widgets().first
    expect(widget).to_contain_text('数据表格')
    expect(widget).to_contain_text('演示数据')
    # 演示表格：中文表头 + 分页（首页 20 行 / 共 24 行）
    for h in free_table_page.DEMO_HEADERS:
        expect(free_table_page.widget_thead()).to_contain_text(h)
    assert free_table_page.widget_row_count() == free_table_page.DEMO_PAGE_SIZE
    expect(free_table_page.canvas_widgets().first).to_contain_text(
        f'of {free_table_page.DEMO_ROW_COUNT}')


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('点击组件，属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_select_shows_properties(free_table_page):
    free_table_page.click_widget()
    expect(free_table_page.prop_panel).to_be_visible()
    expect(free_table_page.prop_title).to_have_value('数据表格')
    expect(free_table_page.prop_page_size).to_have_value('20')
    expect(free_table_page.prop_max_height).to_have_value('400')
    expect(free_table_page.prop_refresh_interval).to_have_value('0')
    expect(free_table_page.sort_radio('是')).to_be_checked()
    expect(free_table_page.pagination_radio('是')).to_be_checked()
    # 启用排序时每列一个排序按钮
    expect(free_table_page.widget_sort_labels()).to_have_count(5)


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('点击画布空白区域，属性面板隐藏')
@allure.severity(allure.severity_level.NORMAL)
def test_table_click_blank_hides_properties(free_table_page):
    free_table_page.click_widget()
    expect(free_table_page.prop_title).to_be_visible()
    free_table_page.click_canvas_blank()
    expect(free_table_page.prop_title).to_be_hidden()


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('五个列筛选框渲染，placeholder 正确')
@allure.severity(allure.severity_level.NORMAL)
def test_table_filter_inputs_render(free_table_page):
    free_table_page.click_widget()
    for ph in free_table_page.FILTER_PLACEHOLDERS:
        expect(free_table_page.widget_filter(ph)).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('交互事件区六个下拉全部渲染，默认未选择')
@allure.severity(allure.severity_level.NORMAL)
def test_table_event_selects_default(free_table_page):
    free_table_page.click_widget()
    # 默认未选择时 MUI Select 展示为空（零宽字符），选中后才显示选项文案
    for label in free_table_page.EVENT_SELECTS:
        sel = free_table_page.event_select(label)
        expect(sel).to_be_visible()
        assert sel.inner_text().strip() in ('', '​'), f'{label} 默认应为空，实际 {sel.inner_text()!r}'


# ==================== 标题 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('修改标题为"异常事件表"')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_modify_title(free_table_page):
    free_table_page.click_widget()
    free_table_page.prop_title.fill('异常事件表')
    expect(free_table_page.prop_title).to_have_value('异常事件表')
    expect(free_table_page.canvas_widgets().first).to_contain_text('异常事件表')


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('标题恢复为"数据表格"')
@allure.severity(allure.severity_level.NORMAL)
def test_table_title_recover(free_table_page):
    free_table_page.click_widget()
    free_table_page.prop_title.fill('异常事件表')
    free_table_page.prop_title.fill('数据表格')
    expect(free_table_page.prop_title).to_have_value('数据表格')
    expect(free_table_page.canvas_widgets().first).to_contain_text('数据表格')


# ==================== 每页行数 ====================
# 只校验属性值来回改能生效。

@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('每页行数改为 10 再恢复为 20')
@allure.severity(allure.severity_level.NORMAL)
def test_table_page_size(free_table_page):
    free_table_page.click_widget()
    free_table_page.prop_page_size.fill('10')
    expect(free_table_page.prop_page_size).to_have_value('10')
    free_table_page.prop_page_size.fill('20')
    expect(free_table_page.prop_page_size).to_have_value('20')


# ==================== 启用排序 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('关闭排序，表头排序按钮消失；恢复后回到 5 个')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_sort_toggle(free_table_page):
    free_table_page.click_widget()
    free_table_page.sort_radio('否').click()
    expect(free_table_page.sort_radio('否')).to_be_checked()
    expect(free_table_page.widget_sort_labels()).to_have_count(0)
    free_table_page.sort_radio('是').click()
    expect(free_table_page.sort_radio('是')).to_be_checked()
    expect(free_table_page.widget_sort_labels()).to_have_count(5)


# ==================== 启用分页 ====================
# 演示表格当前不渲染分页控件，只能校验单选状态。

@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('关闭分页再恢复，单选状态同步')
@allure.severity(allure.severity_level.NORMAL)
def test_table_pagination_toggle(free_table_page):
    free_table_page.click_widget()
    free_table_page.pagination_radio('否').click()
    expect(free_table_page.pagination_radio('否')).to_be_checked()
    free_table_page.pagination_radio('是').click()
    expect(free_table_page.pagination_radio('是')).to_be_checked()


# ==================== 最大高度 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('最大高度改为 250px，作用在滚动容器上')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_max_height_250(free_table_page):
    free_table_page.click_widget()
    free_table_page.prop_max_height.fill('250')
    expect(free_table_page.prop_max_height).to_have_value('250')
    expect(free_table_page.widget_table_container()).to_have_css('max-height', '250px')


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('最大高度恢复为 400px')
@allure.severity(allure.severity_level.NORMAL)
def test_table_max_height_recover(free_table_page):
    free_table_page.click_widget()
    free_table_page.prop_max_height.fill('250')
    free_table_page.prop_max_height.fill('400')
    expect(free_table_page.prop_max_height).to_have_value('400')
    expect(free_table_page.widget_table_container()).to_have_css('max-height', '400px')


# ==================== 刷新间隔 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('刷新间隔设为 5 秒再恢复为 0')
@allure.severity(allure.severity_level.NORMAL)
def test_table_refresh_interval(free_table_page):
    free_table_page.click_widget()
    free_table_page.prop_refresh_interval.fill('5')
    expect(free_table_page.prop_refresh_interval).to_have_value('5')
    free_table_page.prop_refresh_interval.fill('0')
    expect(free_table_page.prop_refresh_interval).to_have_value('0')


# ==================== 交互事件 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('设置点击事件为"跳转 URL"')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_click_event_navigate(free_table_page):
    free_table_page.click_widget()
    sel = free_table_page.event_select('点击事件')
    free_table_page.pick_option(sel, '跳转 URL')
    expect(sel).to_have_text('跳转 URL')


# ==================== 数据绑定对话框 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('点击"配置数据绑定"打开对话框，取消关闭')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_bind_dialog_open_cancel(free_table_page):
    free_table_page.click_widget()
    free_table_page.open_bind_dialog()
    expect(free_table_page.bind_dialog).to_contain_text('配置表格真实数据')
    expect(free_table_page.bind_dialog_save).to_be_visible()
    free_table_page.close_bind_dialog()
    expect(free_table_page.bind_dialog).to_have_count(0)


# ==================== 删除 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('删除表格组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_delete(free_table_page):
    expect(free_table_page.canvas_widgets()).to_have_count(1)
    free_table_page.delete_widget()
    expect(free_table_page.canvas_widgets()).to_have_count(0)


# ==================== 组合修改 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('组合修改标题、每页行数、排序与最大高度')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_combined(free_table_page):
    free_table_page.click_widget()
    free_table_page.prop_title.fill('异常事件表')
    free_table_page.prop_page_size.fill('10')
    free_table_page.sort_radio('否').click()
    free_table_page.prop_max_height.fill('300')
    expect(free_table_page.prop_title).to_have_value('异常事件表')
    expect(free_table_page.prop_page_size).to_have_value('10')
    expect(free_table_page.sort_radio('否')).to_be_checked()
    expect(free_table_page.prop_max_height).to_have_value('300')
    expect(free_table_page.canvas_widgets().first).to_contain_text('异常事件表')
    expect(free_table_page.widget_sort_labels()).to_have_count(0)
    expect(free_table_page.widget_table_container()).to_have_css('max-height', '300px')
