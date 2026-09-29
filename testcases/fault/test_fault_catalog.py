import allure
import pytest
from playwright.sync_api import expect

from testcases.fault.pager_checks import (
    assert_next_page, assert_page_size_10, assert_total_stable)

from pages.fault.fault_catalog_page import FaultCatalogPage


# 「目录」子标签的用例。只校验功能：表格出现、筛选真的把结果收敛到所选条件、搜索按编码/名称
# 过滤、排序升降序、点行进详情再返回。元素定位、动作、以及「遍历组合找测试数据」都在
# FaultCatalogPage 里，用例只写「动作 + 断言」，断言一律配 # 断言：注释。
# 期望值都从当前页面数据里取，故障库增删数据不影响用例。
# 进入模块、面包屑、6 个子标签属于「模块外壳」，见 test_fault_library.py。


# ==================== 页面出现 ====================

@allure.feature('故障/预案库')
@allure.story('目录')
@allure.title('切到「目录」后故障总表出现且有数据')
@allure.severity(allure.severity_level.BLOCKER)
def test_catalog_visible(catalog_page):
    # 断言：目录页容器出现
    expect(catalog_page.root).to_be_visible()
    # 断言：故障总表可见
    expect(catalog_page.table).to_be_visible()
    # 断言：默认至少列出一条故障
    assert catalog_page.row_count() > 0


@allure.feature('故障/预案库')
@allure.story('目录')
@allure.title('故障总表表头：编码 / 名称 / 分系统 / 严重等级 / 预案数')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_headers(catalog_page):
    for header in FaultCatalogPage.TABLE_HEADERS:
        # 断言：五个列头都在
        expect(catalog_page.thead).to_contain_text(header)


# ==================== 分系统筛选 ====================

@allure.feature('故障/预案库')
@allure.story('目录')
@allure.title('按分系统「{subsystem}」筛选后，结果的分系统列全部等于所选值')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('subsystem', FaultCatalogPage.SUBSYSTEMS)
def test_subsystem_filter(catalog_page, subsystem):
    catalog_page.filter_subsystem(subsystem)
    leaked = set(catalog_page.subsystems()) - {subsystem}
    # 断言：结果里没有别的分系统（筛选没漏）
    assert not leaked, f'筛选「{subsystem}」后仍出现：{leaked}'


@allure.feature('故障/预案库')
@allure.story('目录')
@allure.title('分系统筛选能收敛结果，选「全部」可复位')
@allure.severity(allure.severity_level.NORMAL)
def test_subsystem_filter_reset(catalog_page):
    base = catalog_page.row_count()
    target = catalog_page.row_cells(0)['subsystem']   # 取现有一行的分系统，保证有结果

    catalog_page.filter_subsystem(target)
    # 断言：筛选后结果收敛（>0 且不多于未筛选时）
    assert 0 < catalog_page.row_count() <= base
    # 断言：结果里全是该分系统
    assert set(catalog_page.subsystems()) <= {target}

    catalog_page.filter_subsystem('全部')
    # 断言：复位后行数回到未筛选状态
    assert catalog_page.row_count() == base


# ==================== 严重等级筛选 ====================

@allure.feature('故障/预案库')
@allure.story('目录')
@allure.title('按严重等级「{severity}」筛选后，结果的严重等级列全部等于所选值')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('severity', FaultCatalogPage.SEVERITIES)
def test_severity_filter(catalog_page, severity):
    catalog_page.filter_severity(severity)
    leaked = set(catalog_page.severities()) - {severity}
    # 断言：结果里没有别的等级
    assert not leaked, f'筛选「{severity}」后仍出现：{leaked}'


@allure.feature('故障/预案库')
@allure.story('目录')
@allure.title('严重等级筛选能收敛结果，选「全部」可复位')
@allure.severity(allure.severity_level.NORMAL)
def test_severity_filter_reset(catalog_page):
    base = catalog_page.row_count()
    target = catalog_page.row_cells(0)['severity']   # 取现有一行的严重等级，保证有结果

    catalog_page.filter_severity(target)
    # 断言：筛选后结果收敛（>0 且不多于未筛选时）
    assert 0 < catalog_page.row_count() <= base
    # 断言：结果里全是该等级
    assert set(catalog_page.severities()) <= {target}

    catalog_page.filter_severity('全部')
    # 断言：复位后行数回到未筛选状态
    assert catalog_page.row_count() == base


# ==================== 筛选下拉选项 ====================

@allure.feature('故障/预案库')
@allure.story('目录')
@allure.title('分系统 / 严重等级 下拉的选项 =「全部」+ 既定清单')
@allure.severity(allure.severity_level.NORMAL)
def test_filter_options(catalog_page):
    # 断言：分系统下拉 =「全部」+ 六个分系统
    assert catalog_page.subsystem_options() == ['全部'] + FaultCatalogPage.SUBSYSTEMS
    # 断言：严重等级下拉 =「全部」+ I/II/III/IV
    assert catalog_page.severity_options() == ['全部'] + FaultCatalogPage.SEVERITIES


# ==================== 组合筛选 ====================

@allure.feature('故障/预案库')
@allure.story('目录')
@allure.title('分系统 + 严重等级 组合筛选，结果同时满足两个条件')
@allure.severity(allure.severity_level.CRITICAL)
def test_combined_filter(catalog_page):
    # 遍历 分系统×严重等级 组合，找一个当前有数据的（数据库会变，写死某个组合可能没数据）
    combo = catalog_page.first_nonempty_combo()
    if combo is None:
        pytest.skip('没有任何 分系统×严重等级 组合能筛出结果')
    sub, sev = combo

    # 断言：结果里分系统列全部等于所选值
    assert set(catalog_page.subsystems()) <= {sub}
    # 断言：结果里严重等级列全部等于所选值
    assert set(catalog_page.severities()) <= {sev}


# ==================== 空状态 ====================

@allure.feature('故障/预案库')
@allure.story('目录')
@allure.title('搜不存在的关键字 → 出现空状态；点「清空过滤条件」→ 空状态消失、故障列表恢复原样')
@allure.severity(allure.severity_level.NORMAL)
def test_empty_state(catalog_page):
    original_codes = catalog_page.codes()   # 搜索前的完整故障列表

    catalog_page.search('zzz_不存在的故障_zzz')
    # 断言：出现空状态文案
    expect(catalog_page.empty_hint).to_be_visible()
    # 断言：空状态里有「清空过滤条件」按钮
    expect(catalog_page.clear_button).to_be_visible()

    catalog_page.clear_button.click()
    # 断言：点「清空过滤条件」后空状态消失
    expect(catalog_page.empty_hint).to_be_hidden()
    # 断言：故障列表恢复到搜索前的行数与内容
    expect(catalog_page.rows()).to_have_count(len(original_codes))
    assert catalog_page.codes() == original_codes


# ==================== 搜索 ====================

@allure.feature('故障/预案库')
@allure.story('目录')
@allure.title('搜索按编码或名称过滤，结果均含关键字，清空后恢复')
@allure.severity(allure.severity_level.CRITICAL)
def test_keyword_search(catalog_page):
    original_codes = catalog_page.codes()
    kw = catalog_page.keyword_present().lower()   # 必然命中当前至少一行的关键字

    catalog_page.search(kw)
    # 断言：搜索后结果非空
    assert catalog_page.row_count() > 0
    # 断言：每条结果的编码或名称都含关键字
    assert all(kw in c.lower() or kw in n.lower()
               for c, n in zip(catalog_page.codes(), catalog_page.names())), \
        f'结果里有不含「{kw}」的行：{list(zip(catalog_page.codes(), catalog_page.names()))}'

    catalog_page.search('')
    # 断言：清空搜索后故障列表恢复原样
    assert catalog_page.codes() == original_codes


@allure.feature('故障/预案库')
@allure.story('目录')
@allure.title('分系统筛选叠加搜索，结果同时满足分系统与关键字')
@allure.severity(allure.severity_level.NORMAL)
def test_search_with_filter(catalog_page):
    target = catalog_page.row_cells(0)['subsystem']
    catalog_page.filter_subsystem(target)
    if catalog_page.row_count() == 0:
        pytest.skip(f'分系统「{target}」下没有数据')
    kw = catalog_page.codes()[0]

    catalog_page.search(kw)
    # 断言：结果非空
    assert catalog_page.row_count() > 0
    # 断言：结果仍全是该分系统（筛选没被搜索覆盖）
    assert set(catalog_page.subsystems()) <= {target}
    # 断言：每条结果的编码都含关键字
    assert all(kw in c for c in catalog_page.codes())


# ==================== 排序 ====================

@allure.feature('故障/预案库')
@allure.story('目录')
@allure.title('点「编码」列标题两次，整个结果集在升序 ↔ 降序间完全颠倒')
@allure.severity(allure.severity_level.NORMAL)
def test_column_sort(catalog_page):
    if catalog_page.total_count() < 2:
        pytest.skip('数据不足 2 行，无法验证排序')

    # all_codes() 跨所有分页收集，拿到的是「整个结果集」的排序，不只是当前页
    catalog_page.sort_by('编码')
    order1 = catalog_page.all_codes()
    catalog_page.sort_by('编码')
    order2 = catalog_page.all_codes()

    # 断言：两次点击把整个结果集完全颠倒
    assert order1 == list(reversed(order2)), f'两次排序不是互为倒序：{order1} / {order2}'
    # 空编码在后端按 NULLS FIRST/LAST 放在两端；只对非空编码验证字典序。
    nonempty1 = [code for code in order1 if code]
    nonempty2 = [code for code in order2 if code]
    assert sorted(nonempty1) in (nonempty1, nonempty2), \
        f'两次排序的非空编码都不是升序：{order1} / {order2}'


# ==================== 分页 ====================

@allure.feature('故障/预案库')
@allure.story('目录')
@allure.title('改「每页行数」为 10，当前页行数与行号区间随之变化')
@allure.severity(allure.severity_level.NORMAL)
def test_rows_per_page_change(catalog_page):
    # 断言：每页行数改成 10 后，当前页正好 10 行、行号 1-10
    assert_page_size_10(catalog_page)


@allure.feature('故障/预案库')
@allure.story('目录')
@allure.title('总条数不随「每页行数」变化')
@allure.severity(allure.severity_level.NORMAL)
def test_total_count_stable_across_rows_per_page(catalog_page):
    # 断言：换 10 / 50 / 20 都不改变总条数
    assert_total_stable(catalog_page)


@allure.feature('故障/预案库')
@allure.story('目录')
@allure.title('翻到下一页：行号区间接着往后、内容与上一页不重叠')
@allure.severity(allure.severity_level.NORMAL)
def test_next_page(catalog_page):
    # 断言：行号接着上一页，下一页编码和上一页不重叠
    assert_next_page(catalog_page, catalog_page.codes)


# ==================== 点行进详情，再返回 ====================

@allure.feature('故障/预案库')
@allure.story('目录')
@allure.title('点某条故障进详情、详情显示该行编码与名称，点「返回」回到总表')
@allure.severity(allure.severity_level.CRITICAL)
def test_open_detail_and_back(catalog_page):
    picked = catalog_page.open_fault_at(0)

    # 断言：进入详情视图（出现「返回」按钮）
    expect(catalog_page.detail_back_button).to_be_visible()
    # 断言：详情显示的正是刚点的那一行
    expect(catalog_page.root).to_contain_text(picked['code'])
    expect(catalog_page.root).to_contain_text(picked['name'])

    catalog_page.back_to_list()
    # 断言：点「返回」后回到故障总表（表格重新可见、有数据行）
    expect(catalog_page.table).to_be_visible()
    expect(catalog_page.rows().first).to_be_visible()
