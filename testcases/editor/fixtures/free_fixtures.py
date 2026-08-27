import pytest

from pages.editor.editor_page import EditorPage
from pages.editor.free_layout_page import FreeLayoutPage
from pages.editor.free_text_page import FreeTextPage
from pages.editor.free_chart_page import FreeChartPage
from pages.editor.free_gauge_page import FreeGaugePage
from pages.editor.free_status_page import FreeStatusPage
from pages.editor.free_indicator_page import FreeIndicatorPage
from pages.editor.free_input_page import FreeInputPage
from pages.editor.free_dropdown_page import FreeDropdownPage


# 进入界面编辑器-自由布局的编辑页
@pytest.fixture
def free_layout_page(home_page):
    editor = EditorPage(home_page)
    editor.editor_button.click()
    editor.edit_button.wait_for(state='visible')
    editor.edit_button.click()
    editor.free_layout_button.wait_for(state='visible')
    editor.free_layout_button.click()
    home_page.locator('.react-grid-layout').wait_for(state='visible')
    editor.edit_manage_button.click()
    home_page.wait_for_load_state('networkidle')
    return FreeLayoutPage(home_page)

# 自由-文本
@pytest.fixture
def free_text_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('文本').click()
    free_layout_page.canvas_widgets().first.wait_for(state='visible')
    return FreeTextPage(free_layout_page.page)

# 自由-图表
@pytest.fixture
def free_chart_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('图表').click()
    free_layout_page.canvas_widgets().first.wait_for(state='visible')
    return FreeChartPage(free_layout_page.page)

# 自由-仪表盘
@pytest.fixture
def free_gauge_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('仪表盘').click()
    free_layout_page.canvas_widgets().first.wait_for(state='visible')
    return FreeGaugePage(free_layout_page.page)

# 自由-状态灯
@pytest.fixture
def free_status_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('状态灯').click()
    free_layout_page.canvas_widgets().first.wait_for(state='visible')
    return FreeStatusPage(free_layout_page.page)

# 自由-指示牌
@pytest.fixture
def free_indicator_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('指示牌').click()
    free_layout_page.canvas_widgets().first.wait_for(state='visible')
    return FreeIndicatorPage(free_layout_page.page)

# 自由-输入框
@pytest.fixture
def free_input_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('输入框').click()
    free_layout_page.canvas_widgets().first.wait_for(state='visible')
    return FreeInputPage(free_layout_page.page)

# 自由-下拉框
@pytest.fixture
def free_dropdown_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('下拉框').click()
    free_layout_page.canvas_widgets().first.wait_for(state='visible')
    return FreeDropdownPage(free_layout_page.page)
