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

# 栅格-文本
@pytest.fixture
def grid_text_page(grid_layout_page):
    grid_layout_page.drag_to_canvas('TextWidget')
    gtp = GridTextPage(grid_layout_page.page)
    gtp.click_widget()
    gtp.prop_content.wait_for(state='visible')
    return gtp

# 栅格-图表
@pytest.fixture
def grid_chart_page(grid_layout_page):
    grid_layout_page.drag_to_canvas('ChartWidget')
    gcp = GridChartPage(grid_layout_page.page)
    gcp.click_widget()  # 拖拽后自动选中，但点击一下确保右侧属性加载
    gcp.prop_title.wait_for(state='visible')
    return gcp

# 栅格-仪表盘
@pytest.fixture
def grid_gauge_page(grid_layout_page):
    grid_layout_page.drag_to_canvas('GaugeWidget')
    ggp = GridGaugePage(grid_layout_page.page)
    ggp.click_widget()
    ggp.prop_title.wait_for(state='visible')
    return ggp

# 栅格-状态灯
@pytest.fixture
def grid_status_page(grid_layout_page):
    grid_layout_page.drag_to_canvas('StatusIndicator')
    gsp = GridStatusPage(grid_layout_page.page)
    gsp.click_widget()
    gsp.prop_label.wait_for(state='visible')
    return gsp

# 栅格-指示牌
@pytest.fixture
def grid_indicator_page(grid_layout_page):
    grid_layout_page.drag_to_canvas('IndicatorCard')
    gip = GridIndicatorPage(grid_layout_page.page)
    gip.click_widget()
    gip.prop_label.wait_for(state='visible')
    return gip

# 栅格-输入框
@pytest.fixture
def grid_input_page(grid_layout_page):
    source = grid_layout_page.drawer_item('InputWidget')
    source.scroll_into_view_if_needed()
    grid_layout_page.drag_to_canvas('InputWidget')
    gip = GridInputPage(grid_layout_page.page)
    gip.click_widget()
    gip.prop_label.wait_for(state='visible')
    return gip

# 栅格-下拉框
@pytest.fixture
def grid_dropdown_page(grid_layout_page):
    source = grid_layout_page.drawer_item('SelectWidget')
    source.scroll_into_view_if_needed()
    grid_layout_page.drag_to_canvas('SelectWidget')
    gdp = GridDropdownPage(grid_layout_page.page)
    gdp.click_widget()
    gdp.prop_label.wait_for(state='visible')
    return gdp
