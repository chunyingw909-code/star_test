import uuid
from pathlib import Path

import pytest

from common.utils import api_fetch, read_secrets, read_yaml, resolve_path
from common.dm8_client import Dm8Unavailable, fault_plan_with_fault, fetch_rows
from pages.fault.fault_library_page import FaultLibraryPage
from pages.fault.fault_catalog_page import FaultCatalogPage
from pages.fault.fault_detail_page import FaultDetailPage
from pages.fault.plan_library_page import FaultPlanLibraryPage
from pages.fault.plan_library_route_page import FaultPlanLibraryRoutePage
from pages.fault.locate_history_page import FaultLocateHistoryPage
from pages.fault.injection_page import FaultInjectionPage
from pages.fault.management_page import FaultManagementPage
from pages.fault.management_route_page import FaultManagementRoutePage
from pages.fault.quick_locate_page import QuickLocatePage
from pages.telemetry.telemetry_page import TelemetryPage

config = read_yaml('config/config.yaml')

# 「目录」「定位历史」「故障注入」都有两个入口：主壳内点子标签（embedded，URL 仍
# /zh-CN）、独立路由页（route，直接改 URL / 头像菜单「故障管理」/ 先进快速定位再切
# 标签都能到）。两边内容和交互逐字一致（已经手工核对过），差别只在内嵌版外层多一层
# data-testid=fault-catalog-root。用 fixture 参数化让同一批用例在两个入口各跑一遍
# （用例 id 会带上 [embedded] / [route] 后缀），而不是复制一份用例文件。
FAULT_ROUTE_PATH = {
    '目录': '/fault',
    '定位历史': '/fault/history',
    '故障注入': '/fault/inject',
}


def _enter_fault_tab(home_page, tab_name, mode):
    """进「故障/预案库」某个子标签。mode='route' 直接改 URL 进独立路由页；
    mode='embedded'（默认）走主壳顶部 Tab 点进去。"""
    if mode == 'route':
        home_page.goto(config['url'].rstrip('/') + '/zh-CN' + FAULT_ROUTE_PATH[tab_name])
        home_page.wait_for_load_state('networkidle')
    else:
        FaultLibraryPage(home_page).open().open_tab(tab_name)


# 进入故障/预案库模块（顶部导航 → /fault）。只给「预案库」「管理」「快速定位」这几个
# 没有内嵌/路由双入口参数化的子标签用。
@pytest.fixture
def fault_library_page(home_page):
    return FaultLibraryPage(home_page).open()


# 「目录」：embedded / route 两个入口各跑一遍
@pytest.fixture(params=['embedded', 'route'])
def catalog_page(request, home_page):
    _enter_fault_tab(home_page, '目录', request.param)
    cp = FaultCatalogPage(home_page)
    cp.root.wait_for(state='visible')
    cp.entry_mode = request.param
    return cp


# 「目录」路由版专用——面包屑这类只有路由版才有的东西用这个，不跟 embedded 掺一起跑
# 出一条注定跳过的用例。
@pytest.fixture
def catalog_route_page(home_page):
    _enter_fault_tab(home_page, '目录', 'route')
    cp = FaultCatalogPage(home_page)
    cp.root.wait_for(state='visible')
    cp.entry_mode = 'route'
    return cp


# 上一步 → 点开第一条「有处置预案」的故障进详情（不写死是哪条，但保证详情各 tab 有内容）；
# d.opened 记着这条的 编码/名称/分系统/严重等级，供用例断言“详情就是所点这条”
@pytest.fixture
def fault_detail_page(catalog_page):
    d = FaultDetailPage(catalog_page.page)
    d.opened = catalog_page.open_first_fault_with_plans()
    d.back_button.wait_for(state='visible')
    return d


# 进入故障/预案库 → 切到「预案库」子标签（所有处置预案的汇总列表，卡片版）
@pytest.fixture
def plan_library_page(fault_library_page):
    fault_library_page.open_tab('预案库')
    plp = FaultPlanLibraryPage(fault_library_page.page)
    plp.cards().first.wait_for(state='visible')
    return plp


# 预案库 - 数据库→前端一致性 Fix
@pytest.fixture
def db_fault_plan():
    """读取一条已存在的预案及其关联故障；本地未配 DM8 时跳过，绝不写库。"""
    try:
        return fault_plan_with_fault()
    except Dm8Unavailable as error:
        pytest.skip(str(error))


# 预案库 - 与 DM8 同环境的前端 Fix
@pytest.fixture
def dm8_plan_library_route_page(page):
    """登录 DM8 配套的 222 前端并进入预案库路由页；不写业务数据。"""
    app_url = config['url'].rstrip('/')
    account = read_secrets()['accounts']['admin']
    response = page.request.post(
        app_url + '/api/auth/login',
        data={'username': account['username'], 'password': account['password']},
    )
    body = response.json() if response.ok else {}
    token = body.get('data', {}).get('token')
    if not token:
        raise RuntimeError(f'登录 DM8 配套前端失败：HTTP {response.status}')

    page.goto(app_url + '/zh-CN/login')
    page.evaluate(
        "(token) => localStorage.setItem('sarsat_token', token)",
        token,
    )
    page.goto(app_url + '/zh-CN/fault/plans', wait_until='domcontentloaded')
    plans = FaultPlanLibraryRoutePage(page)
    plans.wait_for_data()

    # 222 当前仍会弹「系统首次初始化向导」。不能在数据一致性用例里点「完成配置」：
    # 那会写系统配置。只移除本次临时浏览器页的遮罩及 aria-hidden，不改服务端状态。
    page.evaluate("""
        () => {
            const clearGuide = () => {
                document.querySelectorAll('.MuiModal-root').forEach(modal => {
                    if (modal.textContent.includes('系统首次初始化向导')) modal.remove();
                });
                document.querySelectorAll('[aria-hidden="true"]').forEach(element => {
                    element.removeAttribute('aria-hidden');
                });
            };
            window.__dm8GuideObserver = new MutationObserver(clearGuide);
            window.__dm8GuideObserver.observe(document.body, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: ['aria-hidden'],
            });
            clearGuide();
        }
    """)
    return plans


# 预案库的独立路由版（/fault/plans，表格版，见 FaultPlanLibraryRoutePage 类注释）
@pytest.fixture
def plan_library_route_page(home_page):
    home_page.goto(config['url'].rstrip('/') + '/zh-CN/fault/plans')
    home_page.wait_for_load_state('networkidle')
    plp = FaultPlanLibraryRoutePage(home_page)
    plp.wait_for_data()
    return plp


# 进一条预案详情——分别用「内嵌卡片点进去」和「路由表格点详情」两种入口各跑一遍。
# 详情页本身是两边共享的同一个组件（同一个 /fault/plans/<id> URL），断言方法复用
# FaultPlanLibraryPage（那边本来就不依赖 root，两边通用），这里只是换入口方式。
@pytest.fixture(params=['embedded', 'route'])
def plan_detail_page(request, home_page):
    if request.param == 'route':
        home_page.goto(config['url'].rstrip('/') + '/zh-CN/fault/plans')
        home_page.wait_for_load_state('networkidle')
        route_list = FaultPlanLibraryRoutePage(home_page)
        route_list.wait_for_data()
        picked = route_list.open_detail(0)
        detail = FaultPlanLibraryPage(home_page)   # 表格版没有详情方法，详情页共享，换个类读
        detail.back_to_library_button.wait_for(state='visible')
    else:
        FaultLibraryPage(home_page).open().open_tab('预案库')
        detail = FaultPlanLibraryPage(home_page)
        detail.cards().first.wait_for(state='visible')
        picked = detail.open_plan(0)               # 同一个类自带详情方法，直接复用这个实例
    detail.picked = picked
    detail.entry_mode = request.param
    return detail


# 「定位历史」：embedded / route 两个入口各跑一遍
@pytest.fixture(params=['embedded', 'route'])
def locate_history_page(request, home_page):
    _enter_fault_tab(home_page, '定位历史', request.param)
    h = FaultLocateHistoryPage(home_page)
    h.table.wait_for(state='visible')
    # 等首行（数据行或「暂无定位记录」空态行）真的渲染出来，
    # 否则用例里读 row_count() / total_count() 会撞上加载中的空表
    h.rows().first.wait_for(state='visible')
    h.entry_mode = request.param
    return h


# 「定位历史」路由版专用——同 catalog_route_page，给面包屑这类用例用。
@pytest.fixture
def locate_history_route_page(home_page):
    _enter_fault_tab(home_page, '定位历史', 'route')
    h = FaultLocateHistoryPage(home_page)
    h.table.wait_for(state='visible')
    h.rows().first.wait_for(state='visible')
    h.entry_mode = 'route'
    return h


# 「故障注入」：embedded / route 两个入口各跑一遍
@pytest.fixture(params=['embedded', 'route'])
def injection_page(request, home_page):
    _enter_fault_tab(home_page, '故障注入', request.param)
    ip = FaultInjectionPage(home_page)
    ip.panel_heading.wait_for(state='visible')
    ip.fault_type_items().first.wait_for(state='visible')   # 等故障类型列表加载
    ip.entry_mode = request.param
    return ip


# 「故障注入」路由版专用——同 catalog_route_page，给面包屑这类用例用。
@pytest.fixture
def injection_route_page(home_page):
    _enter_fault_tab(home_page, '故障注入', 'route')
    ip = FaultInjectionPage(home_page)
    ip.panel_heading.wait_for(state='visible')
    ip.fault_type_items().first.wait_for(state='visible')
    ip.entry_mode = 'route'
    return ip


# 上一步 → 让仿真循环跑起来。活动故障要看到倒计时/自动恢复日志，得先让顶部 T 在走
# （仿真 STOPPED 时注入请求仍是 200，但不会产生活动故障，见 FaultInjectionPage 类注释）。
# 「仿真控制」是常驻左侧栏，不需要切到「卫星遥测」也能点——但播放按钮要等有活动卫星
# 节点才可用；没有就现拉一个（select_scenario 会刷新页面并跳回卫星遥测模块，拉完节点
# 再切回故障注入）。
# teardown 只停仿真循环 + 重置，不停卫星节点：这台环境是共享的，节点可能是别的用例
# 或别人的会话留下的，不该被这里顺手关掉。
@pytest.fixture
def running_injection_page(injection_page):
    ip = injection_page
    tp = TelemetryPage(ip.page)
    if tp.play_button.is_disabled():
        tp.ensure_nodes_running()
        # select_scenario 内部会刷新页面、跳回卫星遥测模块；按 injection_page 当初用的
        # 入口方式（embedded/route）切回去，不能一律走 Tab（route 场景下那样会切错入口）
        _enter_fault_tab(ip.page, '故障注入', ip.entry_mode)
        ip.panel_heading.wait_for(state='visible')
        ip.fault_type_items().first.wait_for(state='visible')
    tp.start_sim()
    tp.wait_sim_time_advances()
    yield ip
    try:
        tp.stop_sim()
        tp.reset_sim()
    except Exception:
        pass


# 进入故障/预案库 → 切到「管理」子标签
@pytest.fixture
def management_page(fault_library_page):
    fault_library_page.open_tab('管理')
    mp = FaultManagementPage(fault_library_page.page)
    mp.cards().first.wait_for(state='visible')
    return mp


# 独立路由管理页 - AUTOTEST 白名单与页面 Fix
@pytest.fixture(scope='session')
def fault_test_records():
    """加载本机登记的 AUTOTEST 故障并逐条核对 DM8；缺配置时跳过白盒用例。"""
    path = Path(resolve_path('config/fault_test_records.local.yaml'))
    if not path.is_file():
        pytest.skip(f'缺少故障测试数据白名单：{path}')
    data = read_yaml('config/fault_test_records.local.yaml') or {}
    if data.get('environment', '').rstrip('/') != config['url'].rstrip('/'):
        pytest.skip('故障测试数据白名单与当前前端环境不一致')

    records = data.get('records') or []
    if not records or any(not item.get('code', '').startswith('AUTOTEST-') for item in records):
        raise RuntimeError('故障测试数据白名单为空或包含非 AUTOTEST 编码')
    try:
        for item in records:
            fault_id = item['id'].replace("'", "''")
            rows = fetch_rows(
                'SELECT "id", "faultCode", "faultName" '
                f'FROM SARSAT_SCHED."fault_catalog" WHERE "id" = \'{fault_id}\''
            )
            if len(rows) != 1 or rows[0]['faultCode'] != item['code']:
                raise RuntimeError(f'白名单记录与 DM8 不一致：{item}')
    except Dm8Unavailable as error:
        pytest.skip(str(error))
    return records


@pytest.fixture
def management_route_page(home_page, fault_test_records):
    """从真实用户菜单进入表格版管理页，并把登记的 AUTOTEST 行放到当前页。"""
    library = FaultLibraryPage(home_page)
    library.open_management_from_user_menu()
    route = FaultManagementRoutePage(home_page)
    route.wait_for_data()
    route.set_rows_per_page(50)
    route.sort_by_code()
    if route.row_by_code(fault_test_records[0]['code']).count() == 0:
        route.sort_by_code()
    route.row_by_code(fault_test_records[0]['code']).wait_for(state='visible')
    return route


@pytest.fixture
def route_test_fault(fault_test_records):
    """所有详情增删改都只使用这条已登记的 AUTOTEST 故障。"""
    return fault_test_records[0]


# 独立路由管理页 - 故障字段编辑后精确还原 Fix
@pytest.fixture
def restorable_route_fault(management_route_page, route_test_fault):
    """保存 AUTOTEST 故障原值；即使用例失败，也通过接口精确还原。"""
    route = management_route_page
    record = route_test_fault
    snapshot = route.api_fault(record['id'])
    yield record
    fields = (
        'faultCode', 'faultName', 'faultType', 'subsystem', 'severity',
        'description', 'targetModule', 'satModel', 'status', 'defaultParams',
    )
    route.api_update(record['id'], record['code'], {
        key: snapshot.get(key) for key in fields if key in snapshot
    })


# 独立路由管理页 - 子项 CRUD 精确清理 Fix
@pytest.fixture
def route_mutation_scope(management_route_page, route_test_fault):
    """生成唯一 AUTOTEST 标记；只清理该故障下以该标记开头的子项。"""
    marker = f'AUTOTEST-{uuid.uuid4().hex[:12].upper()}'
    yield marker

    fault_id = route_test_fault['id'].replace("'", "''")
    escaped_marker = marker.replace("'", "''")
    cleanup = (
        ('fault_causes', 'fault_id', 'causeDescription', 'causes'),
        ('fault_effects', 'fault_id', 'effectDescription', 'effects'),
        ('fault_plans', 'faultId', 'name', 'plans'),
        ('fault_telemetry_rules', 'fault_id', 'paramCode', 'rules'),
    )
    for table, fault_column, marker_column, endpoint in cleanup:
        if endpoint == 'plans':
            sql = (
                f'SELECT "id" FROM SARSAT_SCHED."{table}" '
                f'WHERE "{marker_column}" LIKE \'{escaped_marker}%\''
            )
        else:
            sql = (
                f'SELECT "id" FROM SARSAT_SCHED."{table}" '
                f'WHERE "{fault_column}" = \'{fault_id}\' '
                f'AND "{marker_column}" LIKE \'{escaped_marker}%\''
            )
        rows = fetch_rows(sql)
        for row in rows:
            item_id = row['id']
            if endpoint == 'plans':
                api_fetch(management_route_page.page,
                          f'/api/fault/plans/{item_id}', method='DELETE')
            else:
                api_fetch(management_route_page.page,
                          f'/api/fault/{route_test_fault["id"]}/{endpoint}/{item_id}',
                          method='DELETE')


# 上一步 → 用接口（不经过「新建故障」表单）直接建一条测试故障，给「编辑 / 废弃 / 删除」
# 这类不是在测新建流程本身、只是需要一条已存在故障当靶子的用例用。编码带 ZZTEST- 前缀
# + 随机后缀，不会跟真实目录数据撞车。
# management_page 进来时列表已经取过一次数据，接口建的这条不会自动出现在页面上，建完
# 得刷新回管理页才能在卡片列表里点到它。
# teardown 用接口删掉；用例里已经手动删过（比如删除用例本身）也不报错。
@pytest.fixture
def seeded_fault(management_page):
    mp = management_page
    code = f'ZZTEST-{uuid.uuid4().hex[:8].upper()}'
    created = mp.api_create(code=code, name='自动化测试故障', fault_type='auto_test_type')

    mp.page.reload(wait_until='networkidle')
    FaultLibraryPage(mp.page).open().open_tab('管理')
    mp.cards().first.wait_for(state='visible')

    yield created
    mp.api_delete(created['id'], created['faultCode'])


# 进入故障/预案库 → 切到「快速定位」子标签。这个子标签是路由页 /fault/locate（不在
# fault-catalog-root 容器内），但顶部导航 Tab 还在，切换方式和其它子标签一样。
@pytest.fixture
def quick_locate_page(fault_library_page):
    fault_library_page.open_tab('快速定位')
    qlp = QuickLocatePage(fault_library_page.page)
    qlp.heading.wait_for(state='visible')
    qlp.records_heading.wait_for(state='visible')
    return qlp
