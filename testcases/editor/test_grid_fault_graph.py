import allure
from playwright.sync_api import expect


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-故障关系图组件')
@allure.title('拖拽故障关系图后画布出现组件，未配置时提示"请配置故障ID"')
@allure.severity(allure.severity_level.BLOCKER)
def test_fault_graph_default(grid_fault_graph_page):
    expect(grid_fault_graph_page.canvas_widgets()).to_have_count(1)
    expect(grid_fault_graph_page.widget()).to_contain_text('请配置故障ID')


@allure.feature('界面编辑器')
@allure.story('栅格布局-故障关系图组件')
@allure.title('点击组件，右侧属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_fault_graph_select_shows_properties(grid_fault_graph_page):
    expect(grid_fault_graph_page.prop_col_span).to_have_value('2')
    expect(grid_fault_graph_page.prop_fault_id).to_have_value('')


@allure.feature('界面编辑器')
@allure.story('栅格布局-故障关系图组件')
@allure.title('点击空白区域，右侧切换回Page属性')
@allure.severity(allure.severity_level.NORMAL)
def test_fault_graph_click_blank_shows_page(grid_fault_graph_page):
    grid_fault_graph_page.click_canvas_blank()
    expect(grid_fault_graph_page.page_props_marker).to_be_visible()


# ==================== 跨列数 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-故障关系图组件')
@allure.title('跨列数改为 6')
@allure.severity(allure.severity_level.CRITICAL)
def test_fault_graph_col_span_6(grid_fault_graph_page):
    grid_fault_graph_page.prop_col_span.fill('6')
    expect(grid_fault_graph_page.prop_col_span).to_have_value('6')
    expect(grid_fault_graph_page.canvas_widgets().first).to_have_css('grid-column', 'span 6')


@allure.feature('界面编辑器')
@allure.story('栅格布局-故障关系图组件')
@allure.title('跨列数恢复为 2')
@allure.severity(allure.severity_level.NORMAL)
def test_fault_graph_col_span_recover(grid_fault_graph_page):
    grid_fault_graph_page.prop_col_span.fill('6')
    grid_fault_graph_page.prop_col_span.fill('2')
    expect(grid_fault_graph_page.prop_col_span).to_have_value('2')
    expect(grid_fault_graph_page.canvas_widgets().first).to_have_css('grid-column', 'span 2')


# ==================== 绑定故障 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-故障关系图组件')
@allure.title('填入真实故障 UUID，关系图渲染出来')
@allure.severity(allure.severity_level.CRITICAL)
def test_fault_graph_bind_valid(grid_fault_graph_page, faults):
    grid_fault_graph_page.prop_fault_id.fill(faults[0]['id'])
    widget = grid_fault_graph_page.widget()
    expect(widget).to_contain_text('故障模式')
    expect(widget).to_contain_text('预案')
    expect(widget).to_contain_text('规则')
    expect(widget).not_to_contain_text('请配置故障ID')
    expect(widget).not_to_contain_text('加载关系图失败')


@allure.feature('界面编辑器')
@allure.story('栅格布局-故障关系图组件')
@allure.title('填入 faultCode（而非 UUID），提示"加载关系图失败"')
@allure.severity(allure.severity_level.CRITICAL)
def test_fault_graph_bind_faultcode_fails(grid_fault_graph_page, faults):
    grid_fault_graph_page.prop_fault_id.fill(faults[0]['faultCode'])
    expect(grid_fault_graph_page.widget()).to_contain_text('加载关系图失败')


@allure.feature('界面编辑器')
@allure.story('栅格布局-故障关系图组件')
@allure.title('填入无效故障 ID，提示"加载关系图失败"')
@allure.severity(allure.severity_level.CRITICAL)
def test_fault_graph_bind_invalid(grid_fault_graph_page):
    grid_fault_graph_page.prop_fault_id.fill('not-a-real-fault-id')
    expect(grid_fault_graph_page.widget()).to_contain_text('加载关系图失败')


@allure.feature('界面编辑器')
@allure.story('栅格布局-故障关系图组件')
@allure.title('清空故障 ID，回到"请配置故障ID"')
@allure.severity(allure.severity_level.NORMAL)
def test_fault_graph_clear_fault_id(grid_fault_graph_page, faults):
    grid_fault_graph_page.prop_fault_id.fill(faults[0]['id'])
    expect(grid_fault_graph_page.widget()).not_to_contain_text('请配置故障ID')
    grid_fault_graph_page.prop_fault_id.fill('')
    expect(grid_fault_graph_page.prop_fault_id).to_have_value('')
    expect(grid_fault_graph_page.widget()).to_contain_text('请配置故障ID')


# ==================== 复制 / 删除 ====================

@allure.feature('界面编辑器')
@allure.story('栅格布局-故障关系图组件')
@allure.title('复制故障关系图组件，画布出现两个组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_fault_graph_duplicate(grid_fault_graph_page):
    grid_fault_graph_page.duplicate_widget()
    expect(grid_fault_graph_page.canvas_widgets()).to_have_count(2)


@allure.feature('界面编辑器')
@allure.story('栅格布局-故障关系图组件')
@allure.title('删除故障关系图组件，画布无组件，右侧切换为Page属性')
@allure.severity(allure.severity_level.CRITICAL)
def test_fault_graph_delete(grid_fault_graph_page):
    grid_fault_graph_page.delete_widget()
    expect(grid_fault_graph_page.page_props_marker).to_be_visible()
    expect(grid_fault_graph_page.canvas_widgets()).to_have_count(0)
