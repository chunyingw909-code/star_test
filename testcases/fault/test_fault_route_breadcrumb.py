import allure


# 面包屑是路由版列表页独有的东西（「首页 / 故障库 / <页面名>」），内嵌 Tab 版列表没有。
# 所以这几条只挂路由版专用 fixture（catalog_route_page / locate_history_route_page /
# injection_route_page），不跟 embedded 共用参数化 fixture——不然每次跑都会生成一条
# 注定跳过的 [embedded] 用例，白占一条记录。预案库路由版本来就只有路由这一个入口，
# 同理不用判断。

def _breadcrumb_texts(page):
    """面包屑各节文字（过滤掉分隔符——它本身也是一个 li，文字是「/"）。"""
    items = [t.strip() for t in page.locator('.MuiBreadcrumbs-root li').all_inner_texts()]
    return [t for t in items if t and t != '/']


@allure.feature('故障/预案库')
@allure.story('路由版面包屑')
@allure.title('目录路由页面包屑：首页 / 故障库')
@allure.severity(allure.severity_level.NORMAL)
def test_catalog_route_breadcrumb(catalog_route_page):
    texts = _breadcrumb_texts(catalog_route_page.page)
    # 断言：面包屑是「首页 / 故障库」
    assert texts == ['首页', '故障库'], f'目录路由页面包屑不对：{texts}'


@allure.feature('故障/预案库')
@allure.story('路由版面包屑')
@allure.title('定位历史路由页面包屑：首页 / 故障库 / 定位历史')
@allure.severity(allure.severity_level.NORMAL)
def test_locate_history_route_breadcrumb(locate_history_route_page):
    texts = _breadcrumb_texts(locate_history_route_page.page)
    assert texts == ['首页', '故障库', '定位历史'], f'定位历史路由页面包屑不对：{texts}'


@allure.feature('故障/预案库')
@allure.story('路由版面包屑')
@allure.title('故障注入路由页面包屑：首页 / 故障库 / 故障注入')
@allure.severity(allure.severity_level.NORMAL)
def test_injection_route_breadcrumb(injection_route_page):
    texts = _breadcrumb_texts(injection_route_page.page)
    assert texts == ['首页', '故障库', '故障注入'], f'故障注入路由页面包屑不对：{texts}'


@allure.feature('故障/预案库')
@allure.story('路由版面包屑')
@allure.title('预案库路由页面包屑：首页 / 故障库 / 预案库')
@allure.severity(allure.severity_level.NORMAL)
def test_plan_library_route_breadcrumb(plan_library_route_page):
    texts = _breadcrumb_texts(plan_library_route_page.page)
    assert texts == ['首页', '故障库', '预案库'], f'预案库路由页面包屑不对：{texts}'


@allure.feature('故障/预案库')
@allure.story('路由版面包屑')
@allure.title('预案详情面包屑：不管从卡片还是表格进来，最后一节都是所点的预案名')
@allure.severity(allure.severity_level.NORMAL)
def test_plan_detail_breadcrumb(plan_detail_page):
    d = plan_detail_page
    texts = _breadcrumb_texts(d.page)
    # 断言：面包屑最后一节是所点预案的名字，前面带着「故障库 / 预案库」
    assert texts[-1] == d.picked['plan'], f'预案详情面包屑最后一节不对：{texts}'
    assert '故障库' in texts and '预案库' in texts, f'预案详情面包屑缺层级：{texts}'
