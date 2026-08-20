import allure
import pytest
from playwright.sync_api import sync_playwright
from common.utils import read_yaml
from PIL import Image
import os
from pages.guide_page import GuidePage
from pages.editor_page import EditorPage
from pages.free_layout_page import FreeLayoutPage
from pages.free_text_page import FreeTextPage
config = read_yaml('config/config.yaml')

# 生成图片对比
@pytest.fixture
def assert_screenshot():
    baseline_dir = 'screenshots/baseline'
    actual_dir = 'screenshots/actual'
    os.makedirs(baseline_dir, exist_ok=True)
    os.makedirs(actual_dir, exist_ok=True)

    def _compare(page_or_locator, name, threshold=0.01):
        actual_path = os.path.join(actual_dir, name)
        baseline_path = os.path.join(baseline_dir, name)
        page_or_locator.screenshot(path=actual_path)

        if not os.path.exists(baseline_path):
            # 没有基准图，自动存一份，标记跳过
            import shutil
            shutil.copy(actual_path, baseline_path)
            pytest.skip(f'基准图已生成: {baseline_path}，请确认后重跑')

        actual = Image.open(actual_path)
        baseline = Image.open(baseline_path)
        if actual.size != baseline.size:
            raise AssertionError(f'截图尺寸不一致: {actual.size} vs {baseline.size}')

        pixels_a = list(actual.getdata())
        pixels_b = list(baseline.getdata())
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
    p = browser.new_page()
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

# 界面编辑器-自由布局-文本
@pytest.fixture
def free_text_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('文本').click()
    return FreeTextPage(free_layout_page.page)

