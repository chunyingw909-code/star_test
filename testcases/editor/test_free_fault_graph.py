import allure
from playwright.sync_api import expect


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-故障关系图组件')
@allure.title('添加故障关系图后画布出现组件，未配置时提示"请配置故障ID"')
@allure.severity(allure.severity_level.BLOCKER)
def test_fault_graph_default(free_fault_graph_page):
    expect(free_fault_graph_page.canvas_widgets()).to_have_count(1)
    expect(free_fault_graph_page.widget()).to_contain_text('请配置故障ID')


@allure.feature('界面编辑器')
@allure.story('自由布局-故障关系图组件')
@allure.title('点击组件，属性面板显示（故障 ID 默认空）')
@allure.severity(allure.severity_level.CRITICAL)
def test_fault_graph_select_shows_properties(free_fault_graph_page):
    free_fault_graph_page.click_widget()
    expect(free_fault_graph_page.prop_panel).to_be_visible()
    expect(free_fault_graph_page.prop_fault_id).to_have_value('')


@allure.feature('界面编辑器')
@allure.story('自由布局-故障关系图组件')
@allure.title('点击画布空白区域，属性面板隐藏')
@allure.severity(allure.severity_level.NORMAL)
def test_fault_graph_click_blank_hides_properties(free_fault_graph_page):
    free_fault_graph_page.click_widget()
    expect(free_fault_graph_page.prop_panel).to_be_visible()
    free_fault_graph_page.click_canvas_blank()
    expect(free_fault_graph_page.prop_panel).to_be_hidden()


# ==================== 绑定故障 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-故障关系图组件')
@allure.title('填入真实故障 UUID，关系图渲染出来')
@allure.severity(allure.severity_level.CRITICAL)
def test_fault_graph_bind_valid(free_fault_graph_page, faults):
    free_fault_graph_page.click_widget()
    free_fault_graph_page.prop_fault_id.fill(faults[0]['id'])
    widget = free_fault_graph_page.widget()
    # 关系图的几类节点
    expect(widget).to_contain_text('故障模式')
    expect(widget).to_contain_text('预案')
    expect(widget).to_contain_text('规则')
    expect(widget).not_to_contain_text('请配置故障ID')
    expect(widget).not_to_contain_text('加载关系图失败')


@allure.feature('界面编辑器')
@allure.story('自由布局-故障关系图组件')
@allure.title('填入 faultCode（而非 UUID），提示"加载关系图失败"')
@allure.severity(allure.severity_level.CRITICAL)
def test_fault_graph_bind_faultcode_fails(free_fault_graph_page, faults):
    free_fault_graph_page.click_widget()
    free_fault_graph_page.prop_fault_id.fill(faults[0]['faultCode'])
    expect(free_fault_graph_page.widget()).to_contain_text('加载关系图失败')


@allure.feature('界面编辑器')
@allure.story('自由布局-故障关系图组件')
@allure.title('填入无效故障 ID，提示"加载关系图失败"')
@allure.severity(allure.severity_level.CRITICAL)
def test_fault_graph_bind_invalid(free_fault_graph_page):
    free_fault_graph_page.click_widget()
    free_fault_graph_page.prop_fault_id.fill('not-a-real-fault-id')
    expect(free_fault_graph_page.widget()).to_contain_text('加载关系图失败')


@allure.feature('界面编辑器')
@allure.story('自由布局-故障关系图组件')
@allure.title('清空故障 ID，回到"请配置故障ID"')
@allure.severity(allure.severity_level.NORMAL)
def test_fault_graph_clear_fault_id(free_fault_graph_page, faults):
    free_fault_graph_page.click_widget()
    free_fault_graph_page.prop_fault_id.fill(faults[0]['id'])
    expect(free_fault_graph_page.widget()).not_to_contain_text('请配置故障ID')
    free_fault_graph_page.prop_fault_id.fill('')
    expect(free_fault_graph_page.prop_fault_id).to_have_value('')
    expect(free_fault_graph_page.widget()).to_contain_text('请配置故障ID')


# ==================== 删除 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-故障关系图组件')
@allure.title('删除故障关系图组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_fault_graph_delete(free_fault_graph_page):
    expect(free_fault_graph_page.canvas_widgets()).to_have_count(1)
    free_fault_graph_page.delete_widget()
    expect(free_fault_graph_page.canvas_widgets()).to_have_count(0)
