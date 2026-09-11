"""表格组件。

前面的交互事件跟图表一样：单击 → 弹窗提示 / 跳转 URL 生效，双击及其余动作不触发，
用例挂在文件末尾的共用用例集上，不重复写。

三类组织：
  一、基础属性        —— 不用绑数据源就能测（标题、最大高度、启用排序 / 分页开关、
                        删除、组合修改）
  二、绑好数据源之后    —— 真实数据下才看得出功能（每页行数、刷新间隔、筛选、排序、
                        列显示、关闭分页、清除绑定）
  三、「配置数据绑定」  —— 把这个弹窗当独立模块测（级联下拉、列勾选、乱点、预览、取消）
  四、点击事件         —— 共用用例集

⚠️ 自动化跑得快，会撞上「保存绑定」后的第一帧：那一帧的取数请求里排序字段还没重算，
   卡在 "satellite"（占位表头第三列「卫星」的内部字段名），真表没这列 → 后端报
   「排序字段不存在...当前为模拟数据」，画布退化成 1 行占位。
   手动操作基本看不到 —— 等人去看画布时早重渲染过了，排序字段已经重算正确。
   第二类的 free_table_bound fixture 靠 unstick_sort() 点一下表头把这一帧推过去，
   之后就是正常的真实数据。不为这一帧写用例。

⚠️ 数据绑定弹窗的三级下拉（关系型数据源 / Schema / 数据表）不写死任何库表名：
   每个数据源都试、每个 Schema 都试，用上第一张底下真有表的。
"""
import time

import allure
from playwright.sync_api import expect

from common.number_input import check_number_spinner
from testcases.editor.click_action_cases import ClickActionCases


# ==========================================================================
# 一、基础属性 —— 不用绑数据源就能测的
# ==========================================================================

@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('添加表格后画布出现组件，默认未绑定：占位表头 + 暂无数据')
@allure.severity(allure.severity_level.BLOCKER)
def test_table_add(free_table_page):
    tp = free_table_page
    # 画布断言
    expect(tp.canvas_widgets()).to_have_count(1)
    expect(tp.widget_title).to_have_text('数据表格')
    expect(tp.widget_unbound_chip).to_be_visible()
    expect(tp.widget_empty_hint).to_be_visible()
    assert tp.widget_headers() == tp.PLACEHOLDER_HEADERS, \
        f'默认占位表头应该是 {tp.PLACEHOLDER_HEADERS}，实际 {tp.widget_headers()}'
    assert tp.widget_row_count() == 0, '未绑定时不该有数据行'


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('点击表格，属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_defaults(free_table_page):
    tp = free_table_page
    tp.click_widget()
    # 右侧断言
    expect(tp.prop_panel).to_be_visible()
    expect(tp.prop_title).to_have_value('数据表格')
    expect(tp.prop_page_size).to_have_value('20')
    expect(tp.prop_max_height).to_have_value('400')
    expect(tp.prop_refresh_interval).to_have_value('0')
    expect(tp.sort_radio('是')).to_be_checked()
    expect(tp.pagination_radio('是')).to_be_checked()
    # 画布断言：启用排序时占位表头每列一个排序按钮
    expect(tp.widget_sort_labels()).to_have_count(len(tp.PLACEHOLDER_HEADERS))


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('点击画布空白区域，属性面板隐藏')
@allure.severity(allure.severity_level.NORMAL)
def test_table_panel_hides(free_table_page):
    tp = free_table_page
    tp.click_widget()
    expect(tp.prop_panel).to_be_visible()
    tp.click_canvas_blank()
    expect(tp.prop_panel).to_be_hidden()


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('修改标题为"异常事件表"，画布标题同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_title(free_table_page):
    tp = free_table_page
    tp.click_widget()
    tp.prop_title.fill('异常事件表')
    # 右侧断言
    expect(tp.prop_title).to_have_value('异常事件表')
    # 画布断言
    expect(tp.widget_title).to_have_text('异常事件表')


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('清空标题，面板留空但画布回落到默认「数据表格」')
@allure.severity(allure.severity_level.NORMAL)
def test_table_title_empty_fallback(free_table_page):
    # 表格跟文本 / 图表不一样：标题清空后画布不是空白，而是回落到默认「数据表格」。
    tp = free_table_page
    tp.click_widget()
    tp.prop_title.fill('自定义标题')
    expect(tp.widget_title).to_have_text('自定义标题')

    tp.prop_title.fill('')
    # 右侧断言：面板里是空的
    expect(tp.prop_title).to_have_value('')
    # 画布断言：回落到默认
    expect(tp.widget_title).to_have_text('数据表格')


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('最大高度改为 250px，作用在滚动容器上，箭头可用')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_max_height(free_table_page):
    # 最大高度不用绑数据源也能测：占位表格的滚动容器就在，改属性它的
    # max-height 真的跟着变。
    tp = free_table_page
    tp.click_widget()
    tp.prop_max_height.fill('250')
    # 右侧断言
    expect(tp.prop_max_height).to_have_value('250')
    # 画布断言
    expect(tp.widget_table_container).to_have_css('max-height', '250px')

    tp.prop_max_height.fill('400')
    expect(tp.widget_table_container).to_have_css('max-height', '400px')
    check_number_spinner(
        tp.prop_max_height, start='400',
        after=lambda v: expect(tp.widget_table_container).to_have_css('max-height', f'{v}px'))


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('关闭启用排序，表头排序按钮消失；打开后回到 5 个')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_sort_switch(free_table_page):
    tp = free_table_page
    tp.click_widget()
    n = len(tp.PLACEHOLDER_HEADERS)

    tp.sort_radio('否').click()
    # 右侧断言
    expect(tp.sort_radio('否')).to_be_checked()
    # 画布断言
    expect(tp.widget_sort_labels()).to_have_count(0)

    tp.sort_radio('是').click()
    expect(tp.sort_radio('是')).to_be_checked()
    expect(tp.widget_sort_labels()).to_have_count(n)


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('启用分页开关来回切，单选状态同步')
@allure.severity(allure.severity_level.NORMAL)
def test_table_pagination_switch(free_table_page):
    # 未绑定时画布上看不出分页效果，这里只校验单选状态。
    # 真实的「关闭分页显示全部」在第二类里测。
    tp = free_table_page
    tp.click_widget()
    tp.pagination_radio('否').click()
    expect(tp.pagination_radio('否')).to_be_checked()
    tp.pagination_radio('是').click()
    expect(tp.pagination_radio('是')).to_be_checked()


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('删除表格组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_delete(free_table_page):
    tp = free_table_page
    expect(tp.canvas_widgets()).to_have_count(1)
    tp.delete_widget()
    expect(tp.canvas_widgets()).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('同时修改标题、启用排序、最大高度')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_combined(free_table_page):
    tp = free_table_page
    tp.click_widget()
    tp.prop_title.fill('异常事件表')
    tp.sort_radio('否').click()
    tp.prop_max_height.fill('300')

    # 右侧断言
    expect(tp.prop_title).to_have_value('异常事件表')
    expect(tp.sort_radio('否')).to_be_checked()
    expect(tp.prop_max_height).to_have_value('300')
    # 画布断言
    expect(tp.widget_title).to_have_text('异常事件表')
    expect(tp.widget_sort_labels()).to_have_count(0)
    expect(tp.widget_table_container).to_have_css('max-height', '300px')


# ==========================================================================
# 二、绑好数据源之后 —— 真实数据下才看得出功能
# ==========================================================================
# free_table_bound 这个 fixture 已经：绑好第一张可用表 + 全勾列 + 保存 +
# 点排序表头把「保存后第一帧」推过去，交出来时画布上是真实数据、状态是「已登记数据源」。

@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('绑好数据源、点一下排序表头之后，画布出真实数据')
@allure.severity(allure.severity_level.BLOCKER)
def test_table_bound_shows_real_data(free_table_page):
    tp = free_table_page
    tp.click_widget()
    tp.open_bind_dialog()
    tp.bind_first_available()
    # 保存后的第一帧：排序字段还卡在 satellite，画布是「模拟数据」占位
    expect(tp.widget_mock_chip).to_be_visible()

    tp.unstick_sort()   # 点一下表头，把这一帧推过去
    # 画布断言：换成真实数据了
    expect(tp.widget_bound_chip).to_be_visible()
    expect(tp.widget_mock_chip).to_have_count(0)
    assert tp.widget_row_count() > 1, '真实数据应该不止 1 行'
    assert tp.widget_headers() != tp.PLACEHOLDER_HEADERS, '表头应换成真实列名'


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('每页行数改成 N，画布真的每页显示 N 行')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_bound_page_size(free_table_bound):
    tp = free_table_bound
    tp.click_widget()
    assert tp.widget_row_count() == 20, '默认每页 20 行'

    for n in (10, 5):
        tp.prop_page_size.fill(str(n))
        tp.page.wait_for_timeout(2000)
        # 右侧断言
        expect(tp.prop_page_size).to_have_value(str(n))
        # 画布断言：真的每页 N 行
        assert tp.widget_row_count() == n, \
            f'每页行数设成 {n}，画布应显示 {n} 行，实际 {tp.widget_row_count()}'
        assert f'1–{n} of' in tp.widget_pager.inner_text(), \
            f'分页文字应是「1–{n} of ...」，实际 {tp.widget_pager.inner_text()!r}'

    tp.prop_page_size.fill('20')
    tp.page.wait_for_timeout(1500)
    assert tp.widget_row_count() == 20, '改回 20 应恢复每页 20 行'


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('刷新间隔设成 2 秒，画布真的每 2 秒重新拉一次数；设 0 停止')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_bound_refresh_interval(free_table_bound):
    tp = free_table_bound
    tp.click_widget()
    page = tp.page

    hits = []
    page.on('request', lambda r: hits.append(time.time()) if '/query' in r.url else None)

    # 设 2 秒，盯 10 秒 —— 该有 4~5 次周期性取数
    tp.prop_refresh_interval.fill('2')
    page.wait_for_timeout(1000)
    hits.clear()
    page.wait_for_timeout(10000)
    n = len(hits)
    assert 3 <= n <= 7, f'刷新间隔 2 秒，10 秒内该发 4~5 次取数请求，实际 {n} 次'

    # 设 0，盯 6 秒，应该完全停下来
    tp.prop_refresh_interval.fill('0')
    page.wait_for_timeout(1000)
    hits.clear()
    page.wait_for_timeout(6000)
    assert len(hits) == 0, f'刷新间隔设成 0 后不该再自动取数，实际又发了 {len(hits)} 次'


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('列筛选：某列输入子串，行数变少，剩下的行该列都含这个子串')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_bound_filter(free_table_bound):
    tp = free_table_bound
    first_header = tp.widget_headers()[0]
    values = tp.widget_column_values(first_header)
    assert values, '绑定后应该有数据'
    keyword = values[0][:8]

    tp.filter_column(first_header, keyword)
    # 画布断言
    filtered = tp.widget_column_values(first_header)
    assert filtered, f'按 {keyword!r} 筛选后不该一行都不剩'
    assert all(keyword in v for v in filtered), \
        f'筛选后每一行的「{first_header}」列都该含 {keyword!r}，实际 {filtered}'
    assert len(filtered) <= len(values), '筛选后行数不该变多'

    tp.filter_column(first_header, '')
    assert len(tp.widget_column_values(first_header)) == len(values), '清空筛选后行数应该恢复'


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('点表头排序，行序实时变化，无需保存')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_bound_sort_realtime(free_table_bound):
    tp = free_table_bound
    header = tp.widget_headers()[0]
    before = tp.widget_column_values(header)[:5]

    tp.sort_by(header)          # 再点一次，方向翻转
    after = tp.widget_column_values(header)[:5]
    # 画布断言：不点保存，行序就变了
    assert before != after, f'点排序表头后行序应该实时变化，前 {before} 后 {after}'


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('绑定后关闭启用排序，表头排序按钮消失；打开后恢复')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_bound_sort_switch(free_table_bound):
    tp = free_table_bound
    tp.click_widget()
    col_count = len(tp.widget_headers())

    tp.sort_radio('否').click()
    # 右侧断言
    expect(tp.sort_radio('否')).to_be_checked()
    # 画布断言
    expect(tp.widget_sort_labels()).to_have_count(0)

    tp.sort_radio('是').click()
    expect(tp.sort_radio('是')).to_be_checked()
    expect(tp.widget_sort_labels()).to_have_count(col_count)


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('列显示菜单：取消勾选某列，该列表头和筛选框消失；勾回来恢复')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_bound_column_toggle(free_table_bound):
    tp = free_table_bound
    headers = tp.widget_headers()
    assert len(headers) >= 2, '至少要有两列才能测隐藏一列'
    target = headers[1]

    tp.open_column_menu()
    tp.toggle_column(target)
    # 画布断言：这一列没了
    assert target not in tp.widget_headers(), f'取消勾选后「{target}」列该从表头消失'
    expect(tp.widget_filter(target)).to_have_count(0)

    tp.open_column_menu()
    tp.toggle_column(target)
    # 画布断言：勾回来又出现了
    assert target in tp.widget_headers(), f'重新勾选后「{target}」列该回来'


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('关闭分页：整页数据全部显示、不丢行；打开后回到每页 20 行')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_bound_pagination_off(free_table_bound):
    tp = free_table_bound
    tp.click_widget()

    total = tp.total_rows()
    expect(tp.widget_pager).to_be_visible()
    assert tp.widget_row_count() == 20, '开着分页时首页应是 20 行'

    tp.pagination_radio('否').click()
    tp.page.wait_for_timeout(3000)
    # 画布断言：分页控件消失，行数变成「全部」（有 200 行上限）
    expect(tp.pagination_radio('否')).to_be_checked()
    expect(tp.widget_pager).to_have_count(0)
    expected = min(total, tp.UNPAGED_ROW_CAP)
    assert tp.widget_row_count() == expected, \
        f'关闭分页后应显示 {expected} 行（总 {total}，上限 {tp.UNPAGED_ROW_CAP}），实际 {tp.widget_row_count()}'

    tp.pagination_radio('是').click()
    tp.page.wait_for_timeout(1500)
    # 画布断言：回到分页态
    expect(tp.widget_pager).to_be_visible()
    assert tp.widget_row_count() == 20, '重新打开分页后应回到每页 20 行'


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('点「清除绑定」，画布恢复未绑定默认态，按钮本身消失')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_bound_clear(free_table_bound):
    tp = free_table_bound
    tp.click_widget()
    expect(tp.clear_binding_button).to_be_visible()

    tp.clear_binding()
    # 画布断言：回到占位表头 + 未绑定提示 + 暂无数据
    expect(tp.widget_unbound_chip).to_be_visible()
    expect(tp.widget_empty_hint).to_be_visible()
    assert tp.widget_headers() == tp.PLACEHOLDER_HEADERS, \
        f'清除绑定后应回到占位表头，实际 {tp.widget_headers()}'
    assert tp.widget_row_count() == 0
    # 「清除绑定」自己消失，「配置数据绑定」还在
    expect(tp.clear_binding_button).to_have_count(0)
    expect(tp.bind_button).to_be_visible()


# ==========================================================================
# 三、「配置数据绑定」这个按钮 —— 当独立模块测
# ==========================================================================
# 表格只支持关系型，弹窗里没有「数据来源」顶层选择器，直接是
# 关系型数据源 → Schema → 数据表 三级级联，选完表再勾「允许展示的列」。

@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('点「配置数据绑定」打开弹窗，标题和三个按钮都在，三级下拉默认空')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_dialog_open(free_table_page):
    tp = free_table_page
    tp.click_widget()
    tp.open_bind_dialog()
    # 弹窗断言
    expect(tp.bind_dialog).to_contain_text('配置表格真实数据')
    expect(tp.bind_dialog_cancel).to_be_visible()
    expect(tp.bind_dialog_preview).to_be_visible()
    expect(tp.bind_dialog_save).to_be_visible()
    expect(tp.bind_field('关系型数据源')).to_have_text('')
    expect(tp.bind_field('Schema')).to_have_text('')
    expect(tp.bind_field('数据表')).to_have_text('')


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('数据绑定是级联的：选完数据源和 Schema，才轮到数据表')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_dialog_cascade(free_table_page):
    tp = free_table_page
    tp.click_widget()
    tp.open_bind_dialog()

    chosen = tp.bind_pick_table()
    expect(tp.bind_field('关系型数据源')).to_have_text(chosen['数据源'])
    expect(tp.bind_field('Schema')).to_have_text(chosen['Schema'])
    expect(tp.bind_field('数据表')).to_have_text(chosen['数据表'])


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('选完表后出现「允许展示的列范围」勾选列表，默认一个都没勾')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_dialog_columns_list(free_table_page):
    tp = free_table_page
    tp.click_widget()
    tp.open_bind_dialog()
    tp.bind_pick_table()

    # 弹窗断言
    expect(tp.bind_dialog).to_contain_text('编辑态允许展示的总体列范围')
    n = tp.bind_column_checkboxes.count()
    assert n > 0, '选完表后应该列出可勾的列'
    checked = sum(1 for i in range(n) if tp.bind_column_checkboxes.nth(i).is_checked())
    assert checked == 0, f'列勾选框默认一个都不该勾，实际勾了 {checked} 个'


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('什么都不选就点「预览真实数据」，提示先选数据源，不崩')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_dialog_preview_empty(free_table_page):
    tp = free_table_page
    tp.click_widget()
    tp.open_bind_dialog()

    tp.bind_dialog_preview.click()
    tp.page.wait_for_timeout(2500)
    # 弹窗断言
    expect(tp.bind_need_table_hint).to_be_visible()
    expect(tp.bind_preview_table).to_have_count(0)
    expect(tp.bind_dialog).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('选到表但一列都不勾就点「保存绑定」，提示至少选一列，保存不了')
@allure.severity(allure.severity_level.CRITICAL)
def test_table_dialog_save_no_columns(free_table_page):
    tp = free_table_page
    tp.click_widget()
    tp.open_bind_dialog()
    tp.bind_pick_table()

    tp.bind_dialog_save.click()
    tp.page.wait_for_timeout(2500)
    # 弹窗断言：给提示、弹窗还在、画布没绑上
    expect(tp.bind_need_column_hint).to_be_visible()
    expect(tp.bind_dialog).to_be_visible()
    expect(tp.widget_unbound_chip).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('选到表但一列都不勾就点「预览真实数据」，同样提示至少选一列')
@allure.severity(allure.severity_level.NORMAL)
def test_table_dialog_preview_no_columns(free_table_page):
    tp = free_table_page
    tp.click_widget()
    tp.open_bind_dialog()
    tp.bind_pick_table()

    tp.bind_dialog_preview.click()
    tp.page.wait_for_timeout(3000)
    # 弹窗断言
    expect(tp.bind_need_column_hint).to_be_visible()
    expect(tp.bind_preview_table).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('选完表 + 全勾列点「预览真实数据」，弹窗里出真实数据表格')
@allure.severity(allure.severity_level.BLOCKER)
def test_table_dialog_preview_data(free_table_page):
    tp = free_table_page
    tp.click_widget()
    tp.open_bind_dialog()
    tp.bind_pick_table()
    tp.check_all_bind_columns()

    tp.bind_dialog_preview.click()
    tp.page.wait_for_timeout(3500)
    # 弹窗断言
    expect(tp.bind_preview_table).to_have_count(1)
    assert tp.bind_preview_table.locator('thead th').count() >= 1, '预览表格应该有表头'
    assert tp.bind_preview_table.locator('tbody tr').count() > 0, '预览表格应该有数据行'
    expect(tp.bind_need_column_hint).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('点「取消」关闭弹窗，画布保持未绑定')
@allure.severity(allure.severity_level.NORMAL)
def test_table_dialog_cancel(free_table_page):
    tp = free_table_page
    tp.click_widget()
    tp.open_bind_dialog()
    tp.close_bind_dialog()
    # 画布断言
    expect(tp.bind_dialog).to_have_count(0)
    expect(tp.widget_unbound_chip).to_be_visible()
    assert tp.widget_headers() == tp.PLACEHOLDER_HEADERS


@allure.feature('界面编辑器')
@allure.story('自由布局-表格组件')
@allure.title('选完表和列但点「取消」，画布仍然未绑定')
@allure.severity(allure.severity_level.NORMAL)
def test_table_dialog_cancel_filled(free_table_page):
    tp = free_table_page
    tp.click_widget()
    tp.open_bind_dialog()
    tp.bind_pick_table()
    tp.check_all_bind_columns()

    tp.close_bind_dialog()
    # 画布断言：填了没保存等于没绑
    expect(tp.widget_unbound_chip).to_be_visible()
    assert tp.widget_headers() == tp.PLACEHOLDER_HEADERS


# ==========================================================================
# 四、点击事件（共用用例集）
# ==========================================================================
# 单击 → 弹窗提示 / 跳转 URL —— 用例写在 click_action_cases.py，这里只挂上去。
# 双击 / 阈值 / 悬停 / 输入变化都不触发，不写。

class TestTableClickAction(ClickActionCases):
    widget_fixture = 'free_table_page'
    story = '自由布局-表格组件'
    marker_prop = 'prop_title'
