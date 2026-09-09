import pytest

from pages.fault.fault_library_page import FaultLibraryPage
from pages.fault.fault_catalog_page import FaultCatalogPage
from pages.fault.fault_detail_page import FaultDetailPage
from pages.fault.plan_library_page import FaultPlanLibraryPage
from pages.fault.locate_history_page import FaultLocateHistoryPage
from pages.fault.injection_page import FaultInjectionPage


# 进入故障/预案库模块（顶部导航 → /fault）
@pytest.fixture
def fault_library_page(home_page):
    return FaultLibraryPage(home_page).open()


# 上一步 → 切到「目录」子标签
@pytest.fixture
def catalog_page(fault_library_page):
    fault_library_page.open_tab('目录')
    cp = FaultCatalogPage(fault_library_page.page)
    cp.root.wait_for(state='visible')
    return cp


# 上一步 → 点开第一条「有处置预案」的故障进详情（不写死是哪条，但保证详情各 tab 有内容）；
# d.opened 记着这条的 编码/名称/分系统/严重等级，供用例断言“详情就是所点这条”
@pytest.fixture
def fault_detail_page(catalog_page):
    d = FaultDetailPage(catalog_page.page)
    d.opened = catalog_page.open_first_fault_with_plans()
    d.back_button.wait_for(state='visible')
    return d


# 进入故障/预案库 → 切到「预案库」子标签（所有处置预案的汇总列表）
@pytest.fixture
def plan_library_page(fault_library_page):
    fault_library_page.open_tab('预案库')
    plp = FaultPlanLibraryPage(fault_library_page.page)
    plp.cards().first.wait_for(state='visible')
    return plp


# 进入故障/预案库 → 切到「定位历史」子标签
@pytest.fixture
def locate_history_page(fault_library_page):
    fault_library_page.open_tab('定位历史')
    h = FaultLocateHistoryPage(fault_library_page.page)
    h.table.wait_for(state='visible')
    # 等首行（数据行或「暂无定位记录」空态行）真的渲染出来，
    # 否则用例里读 row_count() / total_count() 会撞上加载中的空表
    h.rows().first.wait_for(state='visible')
    return h


# 进入故障/预案库 → 切到「故障注入」子标签
@pytest.fixture
def injection_page(fault_library_page):
    fault_library_page.open_tab('故障注入')
    ip = FaultInjectionPage(fault_library_page.page)
    ip.panel_heading.wait_for(state='visible')
    ip.fault_type_items().first.wait_for(state='visible')   # 等故障类型列表加载
    return ip
