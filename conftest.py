import allure
import pytest
from playwright.sync_api import sync_playwright
from common.utils import read_yaml
from PIL import Image
import os
import shutil
from skimage.metrics import structural_similarity as ssim
import numpy as np

from pages.guide.guide_page import GuidePage

config = read_yaml('config/config.yaml')

# 生成图片对比
@pytest.fixture
def assert_screenshot():
    baseline_dir = 'screenshots/baseline'
    actual_dir = 'screenshots/actual'
    os.makedirs(baseline_dir, exist_ok=True)
    os.makedirs(actual_dir, exist_ok=True)

    def _compare(page_or_locator, name, threshold=0.95):
        actual_path = os.path.join(actual_dir, name)
        baseline_path = os.path.join(baseline_dir, name)

        box = page_or_locator.bounding_box()
        if box is None:
            raise ValueError("Element not visible")

        # 自由布局画布本身是可横向/纵向滚动的容器，组件默认宽度可能超出
        # 画布的可视区域，选中后右侧属性面板还会盖在画布上层。不管定位到
        # 哪个元素，只要沿 DOM 往上找到第一个 overflow:auto/scroll 的祖先，
        # 用它的 clientWidth/clientHeight（不含自身滚动条）裁剪，裁剪区域
        # 就不可能包含属性面板或滚动条像素——这是几何上的硬边界，不依赖任何
        # 具体页面对象的定位器，也跟动画/过渡的时机无关
        clip_bound = page_or_locator.evaluate("""
            el => {
                let node = el.parentElement;
                while (node) {
                    const cs = getComputedStyle(node);
                    const scrollable = ['auto', 'scroll'].includes(cs.overflowX)
                        || ['auto', 'scroll'].includes(cs.overflowY);
                    if (scrollable) {
                        const r = node.getBoundingClientRect();
                        return { right: r.x + node.clientWidth, bottom: r.y + node.clientHeight };
                    }
                    node = node.parentElement;
                }
                return null;
            }
        """)
        if clip_bound is not None:
            if clip_bound['right'] < box['x'] + box['width']:
                box['width'] = max(0, clip_bound['right'] - box['x'])
            if clip_bound['bottom'] < box['y'] + box['height']:
                box['height'] = max(0, clip_bound['bottom'] - box['y'])

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

        actual = np.array(Image.open(actual_path).convert('RGB'))
        baseline = np.array(Image.open(baseline_path).convert('RGB'))
        score = ssim(actual, baseline, channel_axis=2)
        if score < threshold:
            raise AssertionError(f'SSIM {score:.4f} 低于阈值 {threshold}')

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
    page.wait_for_load_state('networkidle')
    return page


# 跳过引导进主页，给其他模块用例用
@pytest.fixture
def home_page(page):
    page.goto(config['url'])
    page.wait_for_load_state('networkidle')
    guide = GuidePage(page)
    guide.complete()
    return page