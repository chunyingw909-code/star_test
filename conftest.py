import allure
import pytest
from playwright.sync_api import sync_playwright
from common.utils import read_yaml
from PIL import Image
import os
import shutil

from pages.guide.guide_page import GuidePage
from pages.editor.editor_page import EditorPage
from pages.editor.free_layout_page import FreeLayoutPage
from pages.editor.free_text_page import FreeTextPage
from pages.editor.grid_layout_page import GridLayoutPage
from pages.editor.grid_text_page import GridTextPage
from pages.editor.free_chart_page import FreeChartPage
from pages.editor.grid_chart_page import GridChartPage
from pages.editor.grid_gauge_page import GridGaugePage
from pages.editor.free_gauge_page import FreeGaugePage
from pages.editor.free_status_page import FreeStatusPage
from pages.editor.free_indicator_page import FreeIndicatorPage
from pages.editor.grid_status_page import GridStatusPage
from pages.editor.grid_indicator_page import GridIndicatorPage


config = read_yaml('config/config.yaml')

# 生成图片对比
@pytest.fixture
def assert_screenshot():
    baseline_dir = 'screenshots/baseline'
    actual_dir = 'screenshots/actual'
    os.makedirs(baseline_dir, exist_ok=True)
    os.makedirs(actual_dir, exist_ok=True)

    def _compare(page_or_locator, name, threshold=0.03):
        actual_path = os.path.join(actual_dir, name)
        baseline_path = os.path.join(baseline_dir, name)

        page_or_locator.scroll_into_view_if_needed()
        box = page_or_locator.bounding_box()
        if box is None:
            raise ValueError("Element not visible")
        box = {
            'x': round(box['x']),
            'y': round(box['y']),
            'width': round(box['width']),
            'height': round(box['height']),
        }
        page = page_or_locator.page
        page.screenshot(path=actual_path, clip=box)

        if not os.path.exists(baseline_path):
            shutil.copy(actual_path, baseline_path)
            pytest.skip(f'基准图已生成: {baseline_path}，请确认后重跑')

        actual = Image.open(actual_path)
        baseline = Image.open(baseline_path)
        if actual.size != baseline.size:
            raise AssertionError(f'截图尺寸不一致: {actual.size} vs {baseline.size}')

        pixels_a = list(actual.get_flattened_data())
        pixels_b = list(baseline.get_flattened_data())
        diff_count = sum(1 for a, b in zip(pixels_a, pixels_b) if a != b)
        diff_ratio = diff_count / len(pixels_a)
        if diff_ratio > threshold:
            raise AssertionError(f'截图差异 {diff_ratio:.2%} 超过阈值 {threshold:.2%}')

    return _compare


@pytest.fixture(scope='session')
def browser():
    pw = sync_playwright().start()
    try:
        headless = os.getenv('CI', '') != ''
        b = pw.chromium.launch(headless=headless)
        yield b
        b.close()
    finally:
        pw.stop()

@pytest.fixture
def page(browser):
    p = browser.new_page(viewport={'width': 1440, 'height': 900})
    yield p
    p.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(autouse=True)
def screenshot_on_failure(request):
    yield
    page = request.node.funcargs.get("page") or request.node.funcargs.get("login")
    if page and hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        allure.attach(page.screenshot(), name="失败截图", attachment_type=allure.attachment_type.PNG)


# 只打开页面，给引导流程用例用
@pytest.fixture
def open_page(page):
    page.goto(config['url'])
    return page


# 跳过引导进主页，给其他模块用例用
@pytest.fixture
def home_page(page):
    page.goto(config['url'])
    guide = GuidePage(page)
    guide.complete()
    return page

# 进入界面编辑器-自由布局的编辑页
@pytest.fixture
def free_layout_page(home_page):
    editor = EditorPage(home_page)
    editor.editor_button.click()
    editor.edit_button.click()
    editor.free_layout_button.click()
    editor.edit_manage_button.click()
    return FreeLayoutPage(home_page)

# 自由-文本
@pytest.fixture
def free_text_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('文本').click()
    return FreeTextPage(free_layout_page.page)

# 自由-图表
@pytest.fixture
def free_chart_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('图表').click()
    return FreeChartPage(free_layout_page.page)

# 自由-仪表盘
@pytest.fixture
def free_gauge_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('仪表盘').click()
    return FreeGaugePage(free_layout_page.page)

# 自由-状态灯
@pytest.fixture
def free_status_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('状态灯').click()
    return FreeStatusPage(free_layout_page.page)

# 自由-指示牌
@pytest.fixture
def free_indicator_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('指示牌').click()
    return FreeIndicatorPage(free_layout_page.page)

# 进入界面编辑器-栅格布局的编辑页
@pytest.fixture
def grid_layout_page(home_page):
    editor = EditorPage(home_page)
    editor.editor_button.click()
    editor.edit_button.click()
    editor.grid_layout_button.click()
    return GridLayoutPage(home_page)

# 栅格-文本
@pytest.fixture
def grid_text_page(grid_layout_page):
    grid_layout_page.drag_to_canvas('TextWidget')
    gtp = GridTextPage(grid_layout_page.page)
    gtp.click_widget()
    return gtp

# 栅格-图表
@pytest.fixture
def grid_chart_page(grid_layout_page):
    grid_layout_page.drag_to_canvas('ChartWidget')
    gcp = GridChartPage(grid_layout_page.page)
    gcp.click_widget()  # 拖拽后自动选中，但点击一下确保右侧属性加载
    return gcp

# 栅格-仪表盘
@pytest.fixture
def grid_gauge_page(grid_layout_page):
    grid_layout_page.drag_to_canvas('GaugeWidget')
    ggp = GridGaugePage(grid_layout_page.page)
    ggp.click_widget()
    return ggp

# 栅格-状态灯
@pytest.fixture
def grid_status_page(grid_layout_page):
    grid_layout_page.drag_to_canvas('StatusIndicator')
    gsp = GridStatusPage(grid_layout_page.page)
    gsp.click_widget()
    return gsp

# 栅格-指示牌
@pytest.fixture
def grid_indicator_page(grid_layout_page):
    grid_layout_page.drag_to_canvas('IndicatorCard')
    gip = GridIndicatorPage(grid_layout_page.page)
    gip.click_widget()
    return gip