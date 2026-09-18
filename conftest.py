# Python 3.14 on Windows：stdlib socket.socketpair 的 TCP fallback 在本机
# 常被「Unexpected peer connection」打断（localhost 端口被抢连），Playwright
# sync API 起不来。先用带握手校验的实现顶上，再 import playwright。
import os
import socket as _socket

def _robust_socketpair(family=_socket.AF_INET, type=_socket.SOCK_STREAM, proto=0):
    lsock = _socket.socket(family, type, proto)
    try:
        lsock.bind(('127.0.0.1', 0))
        lsock.listen(1)
        addr = lsock.getsockname()
        token = os.urandom(16)
        csock = _socket.socket(family, type, proto)
        try:
            csock.connect(addr)
            lsock.settimeout(2.0)
            while True:
                ssock, _peer = lsock.accept()
                try:
                    csock.sendall(token)
                    if ssock.recv(16) == token:
                        return ssock, csock
                except OSError:
                    pass
                ssock.close()
        except Exception:
            csock.close()
            raise
    finally:
        lsock.close()

try:
    _a, _b = _socket.socketpair()
    _a.close(); _b.close()
except Exception:
    _socket.socketpair = _robust_socketpair

import allure
import pytest
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from common.utils import read_yaml, resolve_path
# from PIL import Image
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


def _pin_playwright_windows_to_bottom(stop_flag, browser_exe):
    """后台线程：把「Playwright 启动的这个 Chromium」的窗口一直压在桌面最底层。

    识别方式是「窗口所属进程的可执行文件 == Playwright 自带的 chromium」——
    不是「运行期间新出现的 Chrome 窗口」。后者会把用户自己后开的 Google Chrome
    窗口（新窗口 / 弹出 DevTools / 重启 Chrome 等，HWND 都是新的）也一起误伤，
    而且 Chrome_WidgetWin_1 这个窗口类 Electron 应用（VSCode / Slack 等）也在用。
    按进程路径认，用户自己的 Google Chrome（装在 Program Files 里）永远不受影响，
    想置顶置底都随意。
    """
    import win32api, win32con, win32gui, win32process

    browser_exe = browser_exe.lower()
    exe_by_pid = {}

    def proc_exe(pid):
        if pid not in exe_by_pid:
            path = None
            for access in (win32con.PROCESS_QUERY_LIMITED_INFORMATION,
                           win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ):
                try:
                    h = win32api.OpenProcess(access, False, pid)
                    try:
                        path = win32process.GetModuleFileNameEx(h, 0)
                    finally:
                        win32api.CloseHandle(h)
                    break
                except Exception:
                    continue
            exe_by_pid[pid] = (path or '').lower()
        return exe_by_pid[pid]

    def push_down(hwnd, _):
        if win32gui.GetClassName(hwnd) != 'Chrome_WidgetWin_1':
            return
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if proc_exe(pid) == browser_exe:
            win32gui.SetWindowPos(hwnd, win32con.HWND_BOTTOM, 0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)

    while not stop_flag.is_set():
        try:
            win32gui.EnumWindows(push_down, None)
        except Exception:
            pass
        stop_flag.wait(0.15)


@pytest.fixture(scope='session')
def browser():
    pw = sync_playwright().start()
    b = None
    stop_flag = None
    try:
        headless = os.getenv('CI', '') != ''
        b = pw.chromium.launch(headless=headless)
        if not headless:
            import threading
            stop_flag = threading.Event()
            threading.Thread(
                target=_pin_playwright_windows_to_bottom,
                args=(stop_flag, pw.chromium.executable_path),
                daemon=True,
            ).start()
        yield b
    finally:
        if stop_flag is not None:
            stop_flag.set()
        if b is not None:
            b.close()
        pw.stop()


# 浏览器自身/环境的良性噪音，不当成前端 bug
_BENIGN_PAGE_ERRORS = (
    'ResizeObserver loop',
    'Non-Error promise rejection captured',
    # 生产版 React 的 hydration HTML 不匹配会自行丢弃服务端树并完整重绘。
    # 当前系统偶发触发 #418，但页面功能和后续断言均正常；只豁免这个精确错误码。
    'Minified React error #418;',
)


@pytest.fixture
def page(browser):
    p = browser.new_page(viewport={'width': 1440, 'height': 900})
    # 全局兜底：收集「前端未捕获报错 / 渲染进程崩溃」。
    # 大多数白屏都是某个未捕获异常把 React 根卸载掉——它一定会走到 pageerror。
    # 收在这里，由下面的 fail_on_page_error 在用例结束时判定。
    p.page_errors = []
    p.console_errors = []
    p.on('pageerror', lambda e: p.page_errors.append(str(e)))
    p.on('crash', lambda: p.page_errors.append('页面渲染进程崩溃 (page crash)'))
    p.on('console', lambda m: p.console_errors.append(m.text) if m.type == 'error' else None)
    yield p
    p.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'allow_page_errors: 本用例预期会触发前端报错，豁免 fail_on_page_error 兜底',
    )


@pytest.fixture(autouse=True)
def fail_on_page_error(request, page):
    # 依赖 page，于是在 page 之前销毁——此时页面还没关，能截图
    yield
    rep = getattr(request.node, 'rep_call', None)
    # 用例自己就失败/跳过了，别再叠加噪音；只在「用例流程跑通了」时才追究前端报错
    if rep is None or not rep.passed:
        return
    if request.node.get_closest_marker('allow_page_errors'):
        return
    errs = [e for e in page.page_errors
            if not any(b in e for b in _BENIGN_PAGE_ERRORS)]
    if not errs:
        return
    allure.attach('\n\n'.join(errs), name='前端未捕获报错',
                  attachment_type=allure.attachment_type.TEXT)
    if page.console_errors:
        allure.attach('\n'.join(page.console_errors[-30:]), name='console error',
                      attachment_type=allure.attachment_type.TEXT)
    try:
        allure.attach(page.screenshot(), name='报错时截图',
                      attachment_type=allure.attachment_type.PNG)
    except Exception:
        pass
    pytest.fail('用例流程通过，但触发了前端未捕获报错（可能白屏）：\n- '
                + '\n- '.join(e[:400] for e in errs))


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


def _editor_entry_tab(page):
    """主页「界面编辑器」入口：优先新版 module-tab-editor，否则按名字。"""
    by_id = page.get_by_test_id('module-tab-editor')
    if by_id.count():
        return by_id
    return page.get_by_role('tab', name='界面编辑器').first


# 跳过引导进主页，给其他模块用例用
@pytest.fixture
def home_page(page):
    # 偶发：goto 后应用会瞬时弹到 /zh-CN/login（后端抖动等），页面停在登录页。
    # 导航后确认主页标志元素（界面编辑器 tab）真的出现，没出现就重试，最多 3 次。
    # 新版模块导航带 data-testid=module-tab-editor；旧版/并存时按名字取。
    for attempt in range(1, 4):
        page.goto(config['url'])
        page.wait_for_load_state('networkidle')
        GuidePage(page).complete()
        editor_button = _editor_entry_tab(page)
        try:
            editor_button.wait_for(state='visible', timeout=8000)
            return page
        except PlaywrightTimeoutError:
            print(f'[home_page] 第 {attempt} 次未进入主页，当前 URL={page.url}，重试')

    raise RuntimeError(f'home_page: 3 次导航后仍未进入主页，最后 URL={page.url}')
