import pytest

from pages.editor.editor_page import EditorPage
from pages.editor.grid_layout_page import GridLayoutPage
from pages.editor.grid_text_page import GridTextPage
from pages.editor.grid_chart_page import GridChartPage
from pages.editor.grid_gauge_page import GridGaugePage
from pages.editor.grid_status_page import GridStatusPage
from pages.editor.grid_indicator_page import GridIndicatorPage
from pages.editor.grid_input_page import GridInputPage
from pages.editor.grid_dropdown_page import GridDropdownPage
from pages.editor.grid_table_page import GridTablePage
from pages.editor.grid_number_page import GridNumberPage
from pages.editor.grid_fault_graph_page import GridFaultGraphPage
from pages.editor.grid_spacer_page import GridSpacerPage
from pages.editor.grid_container_page import GridContainerPage
from pages.editor.plugin_page import PluginManager


# 进入界面编辑器-栅格布局的编辑页
@pytest.fixture
def grid_layout_page(home_page):
    editor = EditorPage(home_page)
    editor.editor_button.click()
    editor.edit_button.wait_for(state='visible')
    editor.edit_button.click()
    editor.grid_layout_button.wait_for(state='visible')
    editor.grid_layout_button.click()
    glp = GridLayoutPage(home_page)
    glp.canvas.wait_for(state='visible')
    return glp


# 打开"插件"管理对话框，返回 PluginManager 页面对象。
# teardown 把所有开关恢复成启用、关掉弹窗 —— 禁用状态会持久化到后端，不恢复会影响其它用例。
@pytest.fixture
def plugin_manager(grid_layout_page):
    pm = PluginManager(grid_layout_page.page).open()
    yield pm
    try:
        if not pm.is_open():
            pm.open()
        pm.enable_all()
        pm.close()
    except Exception as e:
        print(f'[plugin_manager] 恢复插件开关失败: {e}')

# 栅格-文本
@pytest.fixture
def grid_text_page(grid_layout_page):
    grid_layout_page.drag_to_canvas('TextWidget')
    gtp = GridTextPage(grid_layout_page.page)
    gtp.select_widget(gtp.prop_content)
    return gtp

# 栅格-图表
@pytest.fixture
def grid_chart_page(grid_layout_page):
    grid_layout_page.drag_to_canvas('ChartWidget')
    gcp = GridChartPage(grid_layout_page.page)
    gcp.select_widget(gcp.prop_title)
    return gcp

# 栅格-仪表盘
@pytest.fixture
def grid_gauge_page(grid_layout_page):
    grid_layout_page.drag_to_canvas('GaugeWidget')
    ggp = GridGaugePage(grid_layout_page.page)
    ggp.select_widget(ggp.prop_title)
    return ggp

# 栅格-状态灯
@pytest.fixture
def grid_status_page(grid_layout_page):
    grid_layout_page.drag_to_canvas('StatusIndicator')
    gsp = GridStatusPage(grid_layout_page.page)
    gsp.select_widget(gsp.prop_label)
    return gsp

# 栅格-指示牌
@pytest.fixture
def grid_indicator_page(grid_layout_page):
    grid_layout_page.drag_to_canvas('IndicatorCard')
    gip = GridIndicatorPage(grid_layout_page.page)
    gip.select_widget(gip.prop_label)
    return gip

# 栅格-输入框
@pytest.fixture
def grid_input_page(grid_layout_page):
    source = grid_layout_page.drawer_item('InputWidget')
    source.scroll_into_view_if_needed()
    grid_layout_page.drag_to_canvas('InputWidget')
    gip = GridInputPage(grid_layout_page.page)
    gip.select_widget(gip.prop_label)
    return gip

# 栅格-下拉框
@pytest.fixture
def grid_dropdown_page(grid_layout_page):
    source = grid_layout_page.drawer_item('SelectWidget')
    source.scroll_into_view_if_needed()
    grid_layout_page.drag_to_canvas('SelectWidget')
    gdp = GridDropdownPage(grid_layout_page.page)
    gdp.select_widget(gdp.prop_label)
    return gdp

# 栅格-表格
@pytest.fixture
def grid_table_page(grid_layout_page):
    source = grid_layout_page.drawer_item('TableWidget')
    source.scroll_into_view_if_needed()
    grid_layout_page.drag_to_canvas('TableWidget')
    gtp = GridTablePage(grid_layout_page.page)
    gtp.select_widget(gtp.prop_title)
    return gtp

# 栅格-数值输入
@pytest.fixture
def grid_number_page(grid_layout_page):
    source = grid_layout_page.drawer_item('NumberWidget')
    source.scroll_into_view_if_needed()
    grid_layout_page.drag_to_canvas('NumberWidget')
    gnp = GridNumberPage(grid_layout_page.page)
    gnp.select_widget(gnp.prop_label)
    return gnp

# 栅格-故障关系图
@pytest.fixture
def grid_fault_graph_page(grid_layout_page):
    source = grid_layout_page.drawer_item('FaultGraphWidget')
    source.scroll_into_view_if_needed()
    grid_layout_page.drag_to_canvas('FaultGraphWidget')
    gfp = GridFaultGraphPage(grid_layout_page.page)
    gfp.select_widget(gfp.prop_fault_id)
    return gfp

# 栅格-容器
@pytest.fixture
def grid_container_page(grid_layout_page):
    source = grid_layout_page.drawer_item('ContainerWidget')
    source.scroll_into_view_if_needed()
    grid_layout_page.drag_to_canvas('ContainerWidget')
    gcp = GridContainerPage(grid_layout_page.page)
    gcp.select_widget(gcp.prop_title)
    return gcp

# 栅格-占位
@pytest.fixture
def grid_spacer_page(grid_layout_page):
    source = grid_layout_page.drawer_item('SpacerWidget')
    source.scroll_into_view_if_needed()
    grid_layout_page.drag_to_canvas('SpacerWidget')
    gsp = GridSpacerPage(grid_layout_page.page)
    gsp.select_widget(gsp.prop_height)
    return gsp


# 画布已放一个图表组件 + 打开的 Plugin Manager（栅格布局）。
# 返回 (PluginManager, GridChartPage)。teardown 把所有插件开关复位成启用
# （禁用状态会持久化到后端，不复位会影响其它用例）。
@pytest.fixture
def plugin_with_grid_chart(grid_chart_page):
    pm = PluginManager(grid_chart_page.page).open()
    yield pm, grid_chart_page
    try:
        if not pm.is_open():
            pm.open()
        pm.enable_all()
        pm.close()
    except Exception as e:
        print(f'[plugin_with_grid_chart] 恢复插件开关失败: {e}')


# 给栅格「保存(Publish)」类用例用：画布带一个文本组件（有 prop_content）。
# 栅格首次 Publish 后会对后续编辑防抖自动保存，所以 teardown 要彻底：
# 新建+确定清空画布 → 再显式 Publish 一次把持久化的布局覆盖成空。
@pytest.fixture
def grid_text_saved_cleanup(grid_text_page):
    yield grid_text_page
    try:
        ed = EditorPage(grid_text_page.page)
        ed.page.once('dialog', lambda d: d.accept())
        ed.new_button.click()
        ed.page.wait_for_timeout(1500)
        grid_text_page.save_layout('AUTOTEST-GRID-SAVE')
        ed.page.wait_for_timeout(1500)
    except Exception as e:
        print(f'[grid_text_saved_cleanup] 清理失败: {e}')
