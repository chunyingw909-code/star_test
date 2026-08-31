import allure
import pytest
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from common.utils import read_yaml, resolve_path
# from PIL import Image
import os
# import shutil
# from skimage.metrics import structural_similarity as ssim
# import numpy as np

from pages.guide.guide_page import GuidePage

config = read_yaml('config/config.yaml')

# ─────────────────────────────────────────────────────────────────────
# assert_screenshot：截图 SSIM 对比。已停用 —— 基线与环境强绑定
#   （无头/有头、机器、DPI 不同 → 组件渲染宽高差几像素 → SSIM 直接
#   ValueError: dimensions must match）。组件的视觉正确性改由各用例的
#   to_have_css / to_have_value / to_contain_text 覆盖。
#   如需重新启用：取消下面整块 + 顶部 4 个 import 的注释，删掉
#   screenshots/baseline/*.png 跑两遍重建基线。
# ─────────────────────────────────────────────────────────────────────
# # 生成图片对比
# @pytest.fixture
# def assert_screenshot():
#     baseline_dir = resolve_path('screenshots', 'baseline')
#     actual_dir = resolve_path('screenshots', 'actual')
#     os.makedirs(baseline_dir, exist_ok=True)
#     os.makedirs(actual_dir, exist_ok=True)
#
#     def _measure_visible_box(page_or_locator):
#         """量出组件落在「画布可视区」内的裁剪矩形。
#
#         自由布局画布是可滚动容器，组件可能超出可视区、甚至整个被滚出去。
#         沿 DOM 往上找到第一个 overflow:auto/scroll 的祖先，用它的
#         clientWidth/clientHeight（不含滚动条）作为硬边界裁剪——这样裁出来
#         的区域不会包含属性面板或滚动条像素。组件完全在区外时宽/高会是 0。
#         返回 {x, y, width, height}；bounding_box 读不到时返回 None。
#         """
#         raw = page_or_locator.bounding_box()
#         if raw is None:
#             return None
#         clip_bound = page_or_locator.evaluate("""
#             el => {
#                 let node = el.parentElement;
#                 while (node) {
#                     const cs = getComputedStyle(node);
#                     const scrollable = ['auto', 'scroll'].includes(cs.overflowX)
#                         || ['auto', 'scroll'].includes(cs.overflowY);
#                     if (scrollable) {
#                         const r = node.getBoundingClientRect();
#                         return { right: r.x + node.clientWidth, bottom: r.y + node.clientHeight };
#                     }
#                     node = node.parentElement;
#                 }
#                 return null;
#             }
#         """)
#         b = dict(raw)
#         if clip_bound is not None:
#             if clip_bound['right'] < b['x'] + b['width']:
#                 b['width'] = max(0, clip_bound['right'] - b['x'])
#             if clip_bound['bottom'] < b['y'] + b['height']:
#                 b['height'] = max(0, clip_bound['bottom'] - b['y'])
#         return b
#
#     def _compare(page_or_locator, name, threshold=0.95):
#         actual_path = os.path.join(actual_dir, name)
#         baseline_path = os.path.join(baseline_dir, name)
#
#         # 改属性后画布可能还在重排，先等元素可见（Page 没有带 state 的 wait_for）
#         if hasattr(page_or_locator, 'wait_for'):
#             page_or_locator.wait_for(state='visible')
#
#         # 组件可能被滚出画布可视区（裁剪后宽/高为 0）。先把它滚回视野再量，
#         # 最多试 3 次；3 次都不行就打印现场信息再报错
#         box = None
#         last = None
#         for _ in range(3):
#             if hasattr(page_or_locator, 'scroll_into_view_if_needed'):
#                 page_or_locator.scroll_into_view_if_needed()
#                 page_or_locator.page.wait_for_timeout(200)
#             last = _measure_visible_box(page_or_locator)
#             if last and last['width'] > 0 and last['height'] > 0:
#                 box = last
#                 break
#
#         if box is None:
#             print(f'[assert_screenshot] {name}: 滚动 3 次后组件仍不在画布可视区内，'
#                   f'最后测得 {last}')
#             raise ValueError(f'{name}: 组件不在画布可视区内，无法截图')
#
#         box = {
#             'x': round(box['x']),
#             'y': round(box['y']),
#             'width': round(box['width']),
#             'height': round(box['height']),
#         }
#         page = page_or_locator.page
#
#         # 等画面稳定再定稿：反复截这块区域，直到连续两张字节完全一致
#         # （echarts 仪表盘指针扫动等 canvas 动画结束才会稳），最多约 4s。
#         # 这样就不用在用例里写死 wait_for_timeout(1000)。
#         shot = page.screenshot(clip=box)
#         for _ in range(20):
#             page.wait_for_timeout(200)
#             nxt = page.screenshot(clip=box)
#             if nxt == shot:
#                 break
#             shot = nxt
#         with open(actual_path, 'wb') as f:
#             f.write(shot)
#
#         if not os.path.exists(baseline_path):
#             shutil.copy(actual_path, baseline_path)
#             pytest.skip(f'基准图已生成: {baseline_path}，请确认后重跑')
#
#         actual = np.array(Image.open(actual_path).convert('RGB'))
#         baseline = np.array(Image.open(baseline_path).convert('RGB'))
#         score = ssim(actual, baseline, channel_axis=2)
#         if score < threshold:
#             raise AssertionError(f'SSIM {score:.4f} 低于阈值 {threshold}')
#
#     return _compare


@pytest.fixture(scope='session')
def browser():
    pw = sync_playwright().start()
    b = None
    try:
        headless = os.getenv('CI', '') != ''
        b = pw.chromium.launch(headless=headless)
        yield b
    finally:
        # 打开的资源都在 finally 里按相反顺序关闭，用例异常时也能收干净
        if b is not None:
            b.close()
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
def screenshot_on_failure(request, page):
    # 显式依赖 page：强制本 fixture 在 page 之后建立、于是在 page 之前销毁，
    # 保证下面截图时 page 还没被 page fixture 的 p.close() 关掉
    # （否则销毁顺序颠倒，page.screenshot() 会抛 TargetClosedError 变成 teardown error）
    yield
    if not (hasattr(request.node, "rep_call") and request.node.rep_call.failed):
        return
    try:
        allure.attach(page.screenshot(), name="失败截图", attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        # 页面/浏览器已崩溃等极端情况，截图失败不该把用例结果污染成 teardown error
        print(f"失败截图抓取失败: {e}")


# 只打开页面，给引导流程用例用
@pytest.fixture
def open_page(page):
    page.goto(config['url'])
    page.wait_for_load_state('networkidle')
    return page


# 跳过引导进主页，给其他模块用例用
@pytest.fixture
def home_page(page):
    # 偶发：goto 后应用会瞬时弹到 /zh-CN/login（后端抖动等），页面停在登录页。
    # 原来的实现不检查就返回，30 秒后才在下游 fixture 里以"找不到 界面编辑器
    # 按钮"的形式报错，很难看出真因。这里改成：导航后确认主页标志元素
    # （界面编辑器按钮）真的出现，没出现就重试整个导航，最多 3 次。
    editor_button = page.get_by_role('button', name='界面编辑器')
    for attempt in range(1, 4):
        page.goto(config['url'])
        page.wait_for_load_state('networkidle')
        GuidePage(page).complete()
        try:
            editor_button.wait_for(state='visible', timeout=8000)
            return page
        except PlaywrightTimeoutError:
            print(f'[home_page] 第 {attempt} 次未进入主页，当前 URL={page.url}，重试')

    raise RuntimeError(f'home_page: 3 次导航后仍未进入主页，最后 URL={page.url}')