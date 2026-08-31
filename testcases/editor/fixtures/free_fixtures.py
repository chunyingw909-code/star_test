import pytest
import requests

from common.utils import read_yaml
from pages.editor.editor_page import EditorPage
from pages.editor.free_layout_page import FreeLayoutPage
from pages.editor.free_text_page import FreeTextPage
from pages.editor.free_chart_page import FreeChartPage
from pages.editor.free_gauge_page import FreeGaugePage
from pages.editor.free_status_page import FreeStatusPage
from pages.editor.free_indicator_page import FreeIndicatorPage
from pages.editor.free_input_page import FreeInputPage
from pages.editor.free_dropdown_page import FreeDropdownPage
from pages.editor.free_table_page import FreeTablePage
from pages.editor.free_number_page import FreeNumberPage
from pages.editor.free_fault_graph_page import FreeFaultGraphPage
from pages.editor.free_spacer_page import FreeSpacerPage
from pages.editor.free_container_page import FreeContainerPage
from pages.editor.plugin_page import PluginManager


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

# 自由-表格
@pytest.fixture
def free_table_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('表格').click()
    free_layout_page.canvas_widgets().first.wait_for(state='visible')
    return FreeTablePage(free_layout_page.page)

# 自由-数值输入
@pytest.fixture
def free_number_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('数值输入').click()
    free_layout_page.canvas_widgets().first.wait_for(state='visible')
    return FreeNumberPage(free_layout_page.page)

# 自由-故障关系图
@pytest.fixture
def free_fault_graph_page(free_layout_page):
    free_layout_page.add_component_button.click()
    free_layout_page.component_item('故障关系图').click()
    free_layout_page.canvas_widgets().first.wait_for(state='visible')
    return FreeFaultGraphPage(free_layout_page.page)

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


# 从后端取真实故障 {id, faultCode, ...} 列表，给故障关系图"绑定故障"的用例用。
# 组件的"故障 ID"要的是 UUID（id），不是 faultCode（AOCS-001 那种）。
@pytest.fixture(scope='session')
def faults():
    url = read_yaml('config/config.yaml')['url'].rstrip('/') + '/api/fault/list'
    try:
        resp = requests.get(url, timeout=10, proxies={'http': None, 'https': None})
        resp.raise_for_status()
    except requests.RequestException as e:
        pytest.skip(f'故障列表接口不可达（{url}）：{e}')
    data = resp.json().get('data') or {}
    items = data.get('list') if isinstance(data, dict) else data
    return [it for it in (items or []) if it.get('id')]


# 从后端接口取真实数据源 {类型: id}，给表格"绑定真实数据源"的用例用。
# 直接打接口而不是去右侧抽屉点"复制 ID"：抽屉+剪贴板在 http（非 https）下
# 用不了，接口稳定得多。
# proxies={'http': None, ...}：这台机器有本地代理（127.0.0.1:8080），requests
# 默认会走它、连不到内网的 192.168.1.185，这里显式绕过代理直连。
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
    except Exception as e:
        print(f'[free_text_saved_cleanup] 清理失败: {e}')
