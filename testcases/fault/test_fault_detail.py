import re

import allure
import pytest
from playwright.sync_api import expect

from pages.fault.fault_catalog_page import FaultCatalogPage
from pages.fault.fault_detail_page import FaultDetailPage


# ==================== 头部 / tab ====================

@allure.feature('故障/预案库')
@allure.story('故障详情')
@allure.title('详情头部带出所点故障的 编码 / 名称 / 严重等级 / 分系统')
@allure.severity(allure.severity_level.CRITICAL)
def test_detail_header(fault_detail_page):
    d = fault_detail_page
    # 断言：头部四个字段显示的都是刚点开的那条故障
    for key in ('code', 'name', 'severity', 'subsystem'):
        expect(d.header_field(d.opened[key])).to_be_visible()


@allure.feature('故障/预案库')
@allure.story('故障详情')
@allure.title('详情页该有的都在：返回按钮 + 4 个子 tab，默认停在「关系图」')
@allure.severity(allure.severity_level.CRITICAL)
def test_detail_controls(fault_detail_page):
    d = fault_detail_page
    # 断言：有「返回」按钮
    expect(d.back_button).to_be_visible()
    # 断言：四个子 tab 都可见
    for name in FaultDetailPage.TABS:
        expect(d.tab(name)).to_be_visible()
    # 断言：进入详情默认停在「关系图」
    assert d.active_tab() == '关系图'


# ==================== 基本信息 ====================

@allure.feature('故障/预案库')
@allure.story('故障详情')
@allure.title('基本信息：故障描述 / 目标模块 / 分系统 字段都在')
@allure.severity(allure.severity_level.CRITICAL)
def test_basic_info_fields(fault_detail_page):
    d = fault_detail_page
    d.open_tab('基本信息')
    # 断言：有「故障描述」标题
    expect(d.section_heading('故障描述')).to_be_visible()
    # 断言：有「目标模块」字段
    expect(d.root).to_contain_text('目标模块')
    # 断言：基本信息里的分系统 = 头部/目录里那条故障的分系统
    expect(d.root).to_contain_text(f"分系统: {d.opened['subsystem']}")


@allure.feature('故障/预案库')
@allure.story('故障详情')
@allure.title('基本信息：小标题「故障原因 (N)」/「故障影响 (N)」的 N 与其下列出的条目数一致')
@allure.severity(allure.severity_level.CRITICAL)
def test_basic_info_counts_match(fault_detail_page):
    # 例：小标题写「故障原因 (2)」，下面就应正好列出 2 条原因
    d = fault_detail_page
    d.open_tab('基本信息')
    n_cause = d.section_count('故障原因')
    n_impact = d.section_count('故障影响')
    # 断言：括号里的数字确实是个数
    assert n_cause is not None and n_impact is not None
    # 断言：「故障原因 (N)」的 N == 下面列出的原因条数
    assert d.cause_items().count() == n_cause, \
        f'标题写 ({n_cause})，实际列出 {d.cause_items().count()} 条原因'
    # 断言：「故障影响 (N)」的 N == 下面列出的影响条数
    assert d.impact_items().count() == n_impact, \
        f'标题写 ({n_impact})，实际列出 {d.impact_items().count()} 条影响'


# ==================== 关系图 ====================

@allure.feature('故障/预案库')
@allure.story('故障详情')
@allure.title('关系图：canvas 渲染出来，左上角有搜索框')
@allure.severity(allure.severity_level.CRITICAL)
def test_graph_renders(fault_detail_page):
    d = fault_detail_page
    d.open_tab('关系图')
    # 断言：关系图 canvas 可见且有面积
    expect(d.graph_canvas.first).to_be_visible()
    box = d.graph_canvas.first.bounding_box()
    assert box and box['width'] > 0 and box['height'] > 0
    # 断言：有「搜索节点...」框
    expect(d.graph_search_input).to_be_visible()


@allure.feature('故障/预案库')
@allure.story('故障详情')
@allure.title('关系图图例：5 项都在、互不重叠、没被裁到画布外')
@allure.severity(allure.severity_level.NORMAL)
def test_graph_legend_layout(fault_detail_page):
    d = fault_detail_page
    d.open_tab('关系图')
    for item in FaultDetailPage.GRAPH_LEGEND:
        # 断言：5 个图例项都可见
        expect(d.legend_item(item).first).to_be_visible()

    boxes = d.legend_boxes()
    assert all(boxes), f'有图例项量不到位置：{boxes}'
    # 断言：任意两项的外框互不重叠
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            overlap = not (a['x'] + a['width'] <= b['x'] or b['x'] + b['width'] <= a['x']
                           or a['y'] + a['height'] <= b['y'] or b['y'] + b['height'] <= a['y'])
            assert not overlap, f'图例重叠：{FaultDetailPage.GRAPH_LEGEND[i]} 与 {FaultDetailPage.GRAPH_LEGEND[j]}'

    # 断言：每个图例项都落在关系图画布的水平范围内（没被裁到看不见）
    g = d.graph_canvas.first.bounding_box()
    for name, bx in zip(FaultDetailPage.GRAPH_LEGEND, boxes):
        assert g['x'] - 2 <= bx['x'] and bx['x'] + bx['width'] <= g['x'] + g['width'] + 2, \
            f'图例「{name}」超出画布水平范围：{bx} vs {g}'


@allure.feature('故障/预案库')
@allure.story('故障详情')
@allure.title('关系图：点节点 → 左下角弹出详情卡，带节点类别')
@allure.severity(allure.severity_level.NORMAL)
def test_graph_node_click_detail(fault_detail_page):
    d = fault_detail_page
    d.open_tab('关系图')
    expect(d.graph_canvas.first).to_be_visible()
    # 断言：没点节点时没有详情卡
    expect(d.graph_detail_card).to_have_count(0)

    if not d.click_a_node():
        pytest.skip('这条故障的关系图里没点到可选节点')
    # 断言：点中节点 → 出现 1 张详情卡
    expect(d.graph_detail_card).to_have_count(1)
    # 断言：详情卡带节点类别（图例里的某个词）
    expect(d.graph_detail_card).to_contain_text(re.compile('|'.join(FaultDetailPage.GRAPH_LEGEND)))
    # 断言：详情卡在画布左下区域
    cb, g = d.graph_detail_card.bounding_box(), d.graph_canvas.first.bounding_box()
    assert cb['x'] < g['x'] + g['width'] / 2, f'详情卡不在左侧：{cb} vs {g}'
    assert cb['y'] > g['y'] + g['height'] / 2, f'详情卡不在下方：{cb} vs {g}'


@allure.feature('故障/预案库')
@allure.story('故障详情')
@allure.title('关系图：详情卡点 × 关闭、点画布空白处也关闭')
@allure.severity(allure.severity_level.NORMAL)
def test_graph_detail_card_dismiss(fault_detail_page):
    d = fault_detail_page
    d.open_tab('关系图')

    if not d.click_a_node():
        pytest.skip('这条故障的关系图里没点到可选节点')
    expect(d.graph_detail_card).to_have_count(1)
    d.graph_detail_close.click()
    # 断言：点 × 详情卡关闭
    expect(d.graph_detail_card).to_have_count(0)

    d.click_a_node()
    expect(d.graph_detail_card).to_have_count(1)
    d.click_graph_blank()
    # 断言：点画布空白处详情卡也关闭
    expect(d.graph_detail_card).to_have_count(0)


@allure.feature('故障/预案库')
@allure.story('故障详情')
@allure.title('关系图：搜索框可输入、回车后画布不崩')
@allure.severity(allure.severity_level.NORMAL)
def test_graph_search_input(fault_detail_page):
    # 搜索命中后「节点居中 + 高亮」画在 canvas 上，DOM 看不到，这里只验证交互不报错。
    # 搜当前这条故障自己的名字——它必然是图里的一个节点，不写死。
    d = fault_detail_page
    d.open_tab('关系图')
    kw = d.opened['name']
    d.graph_search_input.fill(kw)
    expect(d.graph_search_input).to_have_value(kw)
    d.graph_search_input.press('Enter')
    # 断言：搜索后关系图 canvas 仍在
    expect(d.graph_canvas.first).to_be_visible()


# ==================== 处置预案 ====================

@allure.feature('故障/预案库')
@allure.story('故障详情')
@allure.title('处置预案：卡片含步骤列表、预期效果、版本，以及查看详情/仿真验证按钮')
@allure.severity(allure.severity_level.CRITICAL)
def test_disposal_plan_tab(fault_detail_page):
    d = fault_detail_page
    d.open_tab('处置预案')
    # 断言：至少一条操作步骤
    expect(d.plan_steps().first).to_be_visible()
    # 断言：有「预期效果」和「版本」字段
    expect(d.root).to_contain_text('预期效果')
    expect(d.root).to_contain_text('版本')
    # 断言：有「查看详情」「仿真验证」两个按钮
    expect(d.plan_detail_button).to_be_visible()
    expect(d.sim_verify_button).to_be_visible()


@allure.feature('故障/预案库')
@allure.story('故障详情')
@allure.title('处置预案：子 tab 的 (N) 与预案卡片数一致')
@allure.severity(allure.severity_level.NORMAL)
def test_disposal_plan_count_match(fault_detail_page):
    d = fault_detail_page
    d.open_tab('处置预案')
    assert d.tab_count('处置预案') == d.plan_cards().count()


@allure.feature('故障/预案库')
@allure.story('故障详情')
@allure.title('处置预案：无预案的故障点进去显示「暂未关联处置预案」，不崩')
@allure.severity(allure.severity_level.NORMAL)
def test_disposal_plan_empty_state(catalog_page):
    picked = catalog_page.open_first_fault_without_plans()
    if picked is None:
        pytest.skip('目录当前页没有「预案数 = 0」的故障')
    d = FaultDetailPage(catalog_page.page)
    d.open_tab('处置预案')
    # 断言：子 tab 计数是 (0)
    assert d.tab_count('处置预案') == 0
    # 断言：tab 切过去了（渲染没崩）
    expect(d.tab('处置预案')).to_have_attribute('aria-selected', 'true')
    # 断言：显示空态文案，而不是空白或报错
    expect(d.plan_empty_hint).to_be_visible()
    # 断言：没有预案卡片、没有「查看详情」按钮
    expect(d.plan_cards()).to_have_count(0)
    expect(d.plan_detail_button).to_have_count(0)


@allure.feature('故障/预案库')
@allure.story('故障详情')
@allure.title('处置预案：点「查看详情」跳到预案详情页 /fault/plans/<id>')
@allure.severity(allure.severity_level.CRITICAL)
def test_plan_view_detail_navigates(fault_detail_page):
    d = fault_detail_page
    d.open_tab('处置预案')
    d.plan_detail_button.first.click()
    # 断言：跳到预案详情页
    expect(d.page).to_have_url(re.compile(r'/fault/plans/'))
    # 断言：详情页带出关联故障（就是刚才那条）
    expect(d.page.locator('body')).to_contain_text(d.opened['code'])


@allure.feature('故障/预案库')
@allure.story('故障详情')
@allure.title('处置预案：点「仿真验证 (S-xx)」跳到对应场景页 /scenarios?id=S-xx')
@allure.severity(allure.severity_level.CRITICAL)
def test_plan_sim_verify_navigates(fault_detail_page):
    d = fault_detail_page
    d.open_tab('处置预案')
    scenario = d.sim_verify_scenario()
    assert scenario, '「仿真验证」按钮没带场景号'
    d.sim_verify_button.first.click()
    # 断言：跳到场景页，且场景号与按钮上的一致
    expect(d.page).to_have_url(re.compile(r'/scenarios\?.*\bid=' + re.escape(scenario)))


# ==================== 定位规则 ====================

@allure.feature('故障/预案库')
@allure.story('故障详情')
@allure.title('定位规则：规则表 4 列表头 + 至少一行、每列非空')
@allure.severity(allure.severity_level.CRITICAL)
def test_locate_rules_tab(fault_detail_page):
    d = fault_detail_page
    d.open_tab('定位规则')
    for header in FaultDetailPage.RULE_HEADERS:
        # 断言：规则表 4 个表头都在
        expect(d.rules_thead).to_contain_text(header)
    cells = d.first_rule_cells()
    # 断言：至少有一条规则（首行至少 4 列）
    assert len(cells) >= 4, f'规则表首行列数不足：{cells}'
    # 断言：首行前 4 列都非空
    assert all(cells[:4]), f'规则行有空列：{cells[:4]}'


@allure.feature('故障/预案库')
@allure.story('故障详情')
@allure.title('定位规则：子 tab 的 (N) 与规则表行数一致')
@allure.severity(allure.severity_level.NORMAL)
def test_locate_rules_count_match(fault_detail_page):
    d = fault_detail_page
    d.open_tab('定位规则')
    assert d.tab_count('定位规则') == d.rule_rows().count()


# ==================== 返回 ====================

@allure.feature('故障/预案库')
@allure.story('故障详情')
@allure.title('点「返回」回到故障总表（表头在、有数据行）')
@allure.severity(allure.severity_level.NORMAL)
def test_detail_back_to_catalog(fault_detail_page):
    d = fault_detail_page
    cp = FaultCatalogPage(d.page)
    cp.back_to_list()   # 点「返回」并等表格出现
    # 断言：回到故障总表（表头有「编码」）
    expect(cp.thead).to_contain_text('编码')
    # 断言：总表有数据行
    expect(cp.rows().first).to_be_visible()


# ==================== 逐条故障：详情页都打得开 ====================
# 上面那些用例只在「第一条有预案的故障」上跑（深度覆盖单条）。
# 这条对目录前几条故障各点一遍，验证「换成任意一条，详情页照样能开、头部对得上、
# 4 个 tab 都能点开不报错」——避免只固定测一条、别的故障数据有问题发现不了。
# 参数化而不是随机：失败时能一眼看出是第几条（test_...[3]），且可复现。
# 想覆盖更多就把 range 调大（代价是每多一条多跑一遍进模块的流程）。

@allure.feature('故障/预案库')
@allure.story('故障详情')
@allure.title('目录第 {row_idx} 条故障：详情页能打开、头部对得上、4 个 tab 都能点开')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize('row_idx', range(6))
def test_fault_detail_opens(catalog_page, row_idx):
    if row_idx >= catalog_page.row_count():
        pytest.skip(f'目录当前页只有 {catalog_page.row_count()} 条')
    picked = catalog_page.open_fault_at(row_idx)
    d = FaultDetailPage(catalog_page.page)
    # 断言：头部显示的就是这条故障
    expect(d.header_field(picked['code'])).to_be_visible()
    expect(d.header_field(picked['name'])).to_be_visible()
    # 断言：4 个子 tab 都在
    for name in FaultDetailPage.TABS:
        expect(d.tab(name)).to_be_visible()
    # 断言：每个 tab 都能点开并切过去（渲染不报错）
    for name in FaultDetailPage.TABS:
        d.open_tab(name)
        expect(d.tab(name)).to_have_attribute('aria-selected', 'true')
