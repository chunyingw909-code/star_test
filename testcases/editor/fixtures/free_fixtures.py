import pytest
import requests

from common import echarts_option as eco
from common.utils import read_yaml
from pages.editor.editor_page import EditorPage
from pages.editor.free_layout_page import FreeLayoutPage
from pages.editor.free_text_page import FreeTextPage
from pages.editor.free_chart_page import FreeChartPage
from pages.editor.free_gauge_page import FreeGaugePage
from pages.editor.free_status_page import FreeStatusPage
from pages.editor.free_indicator_page import FreeIndicatorPage
from pages.editor.free_table_page import FreeTablePage
from pages.editor.free_spacer_page import FreeSpacerPage
from pages.editor.free_container_page import FreeContainerPage
from pages.editor.plugin_page import PluginManager
from pages.telemetry.telemetry_page import TelemetryPage


def _open_free_layout(home_page):
    """从当前模块进入界面编辑器的自由布局编辑态。"""
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


# 进入界面编辑器-自由布局的编辑页
@pytest.fixture
def free_layout_page(home_page):
    return _open_free_layout(home_page)


# 自由布局 - 实时遥测 Fix
# 复用当前场景已有节点；没有时只启动一颗。用例结束只恢复本 fixture 启动的
# 仿真循环和节点，避免破坏原本就在运行的环境状态。
@pytest.fixture
def realtime_free_layout_page(home_page):
    telemetry = TelemetryPage(home_page).open()
    scenario = telemetry.load_current_scenario()
    assert scenario, '当前界面选择的场景不存在或没有可读取的卫星配置'
    _satellite, node_started = telemetry.ensure_one_active_node()

    started_sim = not telemetry.play_button.is_disabled()
    if started_sim:
        telemetry.start_sim()
    assert telemetry.wait_sim_time_advances() > 0, '仿真循环启动后时间没有前进'

    try:
        yield _open_free_layout(home_page)
    finally:
        if started_sim:
            try:
                telemetry.stop_sim()
                telemetry.reset_sim()
            except Exception as e:
                print(f'[realtime_free_layout_page] 恢复仿真循环失败: {e}')
        if node_started:
            telemetry.stop_all_nodes()

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

# 已经绑好数据源、真的出了图的图表。
# 绑定这个动作本身在 test_free_chart.py 里有独立用例逐步断言（级联下拉 / 预览出
# 真实数据 / 保存后出图）；这个 fixture 只是把「绑好之后」这个场景固定下来，
# 给那些必须有图才测得了的用例复用，不是拿 fixture 绕过测试。
@pytest.fixture
def free_chart_bound(free_chart_page):
    free_chart_page.click_widget()
    free_chart_page.open_bind_dialog()
    free_chart_page.bound_with = free_chart_page.bind_first_available()
    # 属性面板要在选中态才看得到。绑完再点一次选中，等系列名换成真实字段。
    free_chart_page.click_widget()
    expected = sorted(free_chart_page.bound_with['数值字段'])
    free_chart_page.wait_chart(lambda o: sorted(eco.series_names(o)), expected)
    return free_chart_page


# 已经绑好数据源、正在显示真实数据的表格。
# 绑定这一步本身在 test_free_table.py 里有独立用例逐步断言，
# 这个 fixture 只是把「有真实数据」这个场景固定下来给别的用例复用。
@pytest.fixture
def free_table_bound(free_table_page):
    free_table_page.click_widget()
    free_table_page.open_bind_dialog()
    free_table_page.bound_with = free_table_page.bind_first_available()
    return free_table_page


# 自由-仪表盘
@pytest.fixture
def free_gauge_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('仪表盘').click()
    free_layout_page.canvas_widgets().first.wait_for(state='visible')
    return FreeGaugePage(free_layout_page.page)


# 自由-仪表盘（运行中的真实遥测）
@pytest.fixture
def free_gauge_realtime(realtime_free_layout_page):
    realtime_free_layout_page.add_component_button.click()
    realtime_free_layout_page.component_item('仪表盘').click()
    realtime_free_layout_page.canvas_widgets().first.wait_for(state='visible')
    return FreeGaugePage(realtime_free_layout_page.page)

# 自由-状态灯
@pytest.fixture
def free_status_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('状态灯').click()
    free_layout_page.canvas_widgets().first.wait_for(state='visible')
    return FreeStatusPage(free_layout_page.page)


# 自由-状态灯（运行中的真实遥测）
@pytest.fixture
def free_status_realtime(realtime_free_layout_page):
    realtime_free_layout_page.add_component_button.click()
    realtime_free_layout_page.component_item('状态灯').click()
    realtime_free_layout_page.canvas_widgets().first.wait_for(state='visible')
    return FreeStatusPage(realtime_free_layout_page.page)

# 自由-指示牌
@pytest.fixture
def free_indicator_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('指示牌').click()
    free_layout_page.canvas_widgets().first.wait_for(state='visible')
    return FreeIndicatorPage(free_layout_page.page)


# 自由-指示牌（运行中的真实遥测）
@pytest.fixture
def free_indicator_realtime(realtime_free_layout_page):
    realtime_free_layout_page.add_component_button.click()
    realtime_free_layout_page.component_item('指示牌').click()
    realtime_free_layout_page.canvas_widgets().first.wait_for(state='visible')
    return FreeIndicatorPage(realtime_free_layout_page.page)


# 自由-文本（运行中的真实遥测）
@pytest.fixture
def free_text_realtime(realtime_free_layout_page):
    realtime_free_layout_page.add_component_button.click()
    realtime_free_layout_page.component_item('文本').click()
    realtime_free_layout_page.canvas_widgets().first.wait_for(state='visible')
    return FreeTextPage(realtime_free_layout_page.page)

# 自由-表格
@pytest.fixture
def free_table_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('表格').click()
    free_layout_page.canvas_widgets().first.wait_for(state='visible')
    return FreeTablePage(free_layout_page.page)

# 自由-容器
@pytest.fixture
def free_container_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('容器').click()
    free_layout_page.canvas_widgets().first.wait_for(state='visible')
    return FreeContainerPage(free_layout_page.page)

# 自由-占位
@pytest.fixture
def free_spacer_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('占位').click()
    free_layout_page.canvas_widgets().first.wait_for(state='visible')
    return FreeSpacerPage(free_layout_page.page)


# 从后端接口取真实数据源 {类型: id}，给表格"绑定真实数据源"的用例用。
# 直接打接口而不是去右侧抽屉点"复制 ID"：抽屉+剪贴板在 http（非 https）下
# 用不了，接口稳定得多。
# proxies={'http': None, ...}：这台机器有本地代理（127.0.0.1:8080），requests
# 默认会走它、连不到内网测试环境，这里显式绕过代理直连。
@pytest.fixture(scope='session')
def datasource_ids():
    url = read_yaml('config/config.yaml')['url'].rstrip('/') + '/api/datasources'
    try:
        resp = requests.get(url, timeout=10, proxies={'http': None, 'https': None})
        resp.raise_for_status()
    except requests.RequestException as e:
        pytest.skip(f'数据源接口不可达（{url}）：{e}')
    body = resp.json()
    items = body if isinstance(body, list) else body.get('data') or body.get('items') or []
    return {it.get('type'): it.get('id') or it.get('_id') for it in items if it.get('type')}


# 打开「插件」管理对话框（空画布），返回 PluginManager 页面对象。
# Plugin Manager 是工具栏级弹框，与画布内容无关，所以挂在空的 free_layout_page 上。
# teardown 把所有开关恢复成启用、关掉弹窗 —— 禁用状态会持久化到后端，不恢复会影响其它用例。
@pytest.fixture
def plugin_manager(free_layout_page):
    pm = PluginManager(free_layout_page.page).open()
    yield pm
    try:
        if not pm.is_open():
            pm.open()
        pm.enable_all()
        pm.close()
    except Exception as e:
        print(f'[plugin_manager] 恢复插件开关失败: {e}')


# 画布已放一个图表组件 + 打开的 Plugin Manager。
# 返回 (PluginManager, FreeChartPage)。teardown 把所有插件开关复位成启用
# （禁用状态会持久化到后端，不复位会影响其它用例）。
@pytest.fixture
def plugin_with_chart(free_chart_page):
    pm = PluginManager(free_chart_page.page).open()
    yield pm, free_chart_page
    try:
        if pm.dialog.count() == 0:
            pm.open()
        pm.enable_all()
        pm.close()
    except Exception as e:
        print(f'[plugin_with_chart] 恢复插件开关失败: {e}')


# 给"保存"类用例用：画布已放一个文本组件（有 prop_content 可写唯一标记），
# teardown 里「新建」+确定，把持久化到后端的布局清掉。
# 不清的话，保存过的布局会在后续用例进编辑器时被自动加载，画布带着组件 → 污染。
@pytest.fixture
def free_text_saved_cleanup(free_text_page):
    yield free_text_page
    try:
        ed = EditorPage(free_text_page.page)
        ed.page.once('dialog', lambda d: d.accept())
        ed.new_button.click()
        ed.page.wait_for_timeout(1200)
        # 「新建」只清当前画布，不再删除后端已保存布局；把空画布覆盖保存，
        # 避免下一条用例刷新时重新加载本用例的组件。
        ed.layout_name_input.fill('AUTOTEST-SAVE')
        free_text_page.save_button.first.click()
        ed.page.wait_for_timeout(800)
    except Exception as e:
        print(f'[free_text_saved_cleanup] 清理失败: {e}')
