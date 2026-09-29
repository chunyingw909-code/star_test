import pytest


def assert_page_size_10(view):
    """每页行数改成 10 后，当前页应正好 10 行，行号从 1 到 10。"""
    if view.total_count() <= 10:
        pytest.skip('数据不足一页（≤10 条），无法验证每页行数')
    view.set_rows_per_page(10)
    assert view.rows_per_page() == 10
    assert view.row_count() == 10
    assert view.page_range() == (1, 10)


def assert_total_stable(view):
    """换 10 / 50 / 20 都不改变总条数。"""
    total = view.total_count()
    for n in (10, 50, 20):
        view.set_rows_per_page(n)
        assert view.total_count() == total, f'每页 {n} 行时总数从 {total} 变成了 {view.total_count()}'


def assert_next_page(view, keys):
    """翻页后行号接着上一页，而且两页的内容不重叠。keys() 返回当前页用来认行的值。"""
    view.set_rows_per_page(10)
    if view.total_count() <= 10:
        pytest.skip('数据不足一页（≤10 条），没有下一页')
    _start, last = view.page_range()
    first_keys = list(keys())
    view.goto_next_page()
    assert view.page_range()[0] == last + 1
    nxt = list(keys())
    overlap = set(first_keys) & set(nxt)
    assert not overlap, f'下一页和上一页有相同行：{overlap}'
