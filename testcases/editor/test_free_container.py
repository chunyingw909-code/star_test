"""容器组件 —— 能往里嵌套其它组件的盒子。

⚠️ 以下属性【故意不写用例】：
      最小高度   —— 改了画布看不出稳定变化

本文件覆盖两块：
  1. 容器自己的属性：标题、背景色、边框色、内边距，外加公用的通用样式
  2. 容器特有的嵌套行为：往容器里加组件、选中容器内的组件、改它的属性、
     删掉容器内的组件、删掉容器本身
"""
import math

import allure
import pytest
from playwright.sync_api import expect

from common.number_input import check_number_spinner
from testcases.editor.common_style_cases import CommonStyleCases


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('添加容器后画布出现容器，标题为"容器"，内部是空的')
@allure.severity(allure.severity_level.BLOCKER)
def test_container_added_to_canvas(free_container_page):
    cp = free_container_page
    # 画布断言
    expect(cp.canvas_widgets()).to_have_count(1)
    expect(cp.widget_title).to_have_text('容器')
    expect(cp.children, '刚加的容器里应该是空的').to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('点击容器，属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_default_properties(free_container_page):
    cp = free_container_page
    cp.click_widget()
    # 右侧断言
    expect(cp.prop_panel).to_be_visible()
    expect(cp.prop_title).to_have_value('容器')
    expect(cp.prop_bg_color).to_have_value('rgba(255,255,255,0.02)')
    expect(cp.prop_border_color).to_have_value('rgba(255,255,255,0.15)')
    expect(cp.prop_padding).to_have_value('8')
    expect(cp.prop_columns).to_have_value(str(cp.COLUMNS_DEFAULT))
    expect(cp.prop_gap).to_have_value(str(cp.GAP_DEFAULT))
    # 画布断言：内边距现在直接按 px 生效；默认 4 列、间距 8px
    expect(cp.widget_body).to_have_css('padding', f'{8 * cp.PADDING_UNIT_PX}px')
    assert cp.canvas_column_count() == cp.COLUMNS_DEFAULT, (
        f'默认应是 {cp.COLUMNS_DEFAULT} 列，实际 {cp.canvas_column_count()}')
    assert cp.canvas_gap_px() == cp.GAP_DEFAULT, (
        f'默认间距应是 {cp.GAP_DEFAULT}px，实际 {cp.canvas_gap_px()}')


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('点击画布空白区域，属性面板隐藏')
@allure.severity(allure.severity_level.NORMAL)
def test_container_panel_hides_on_blank_click(free_container_page):
    cp = free_container_page
    cp.click_widget()
    expect(cp.prop_panel).to_be_visible()
    cp.click_canvas_blank()
    expect(cp.prop_panel).to_be_hidden()


# ==================== 标题 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('修改标题为"指标区"，画布标签同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_modify_title(free_container_page):
    cp = free_container_page
    cp.click_widget()
    cp.prop_title.fill('指标区')
    # 右侧断言
    expect(cp.prop_title).to_have_value('指标区')
    # 画布断言
    expect(cp.widget_title).to_have_text('指标区')


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('清空标题，画布标题节点消失')
@allure.severity(allure.severity_level.NORMAL)
def test_container_clear_title(free_container_page):
    cp = free_container_page
    cp.click_widget()
    cp.prop_title.fill('')
    # 右侧断言
    expect(cp.prop_title).to_have_value('')
    # 画布断言：空标题不保留空的 caption 节点
    expect(cp.widget_title).to_have_count(0)


# ==================== 背景色 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('修改背景色为 #123456，色块与画布同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_background_color(free_container_page):
    cp = free_container_page
    cp.click_widget()
    cp.prop_bg_color.fill('#123456')
    # 右侧断言
    expect(cp.prop_bg_color).to_have_value('#123456')
    expect(cp.prop_bg_color_swatch).to_have_value('#123456')
    # 画布断言
    expect(cp.widget_body).to_have_css('background-color', 'rgb(18, 52, 86)')


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('用色块选背景色（等同在调色盘里选完），文本框与画布同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_background_color_via_swatch(free_container_page):
    cp = free_container_page
    cp.click_widget()
    cp.prop_bg_color_swatch.fill('#00ff00')
    # 右侧断言
    expect(cp.prop_bg_color_swatch).to_have_value('#00ff00')
    expect(cp.prop_bg_color).to_have_value('#00ff00')
    # 画布断言
    expect(cp.widget_body).to_have_css('background-color', 'rgb(0, 255, 0)')


# ==================== 边框色 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('修改边框色为 #abcdef，色块与画布同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_border_color(free_container_page):
    cp = free_container_page
    cp.click_widget()
    cp.prop_border_color.fill('#abcdef')
    # 右侧断言
    expect(cp.prop_border_color).to_have_value('#abcdef')
    expect(cp.prop_border_color_swatch).to_have_value('#abcdef')
    # 画布断言
    expect(cp.widget_body).to_have_css('border-color', 'rgb(171, 205, 239)')
    expect(cp.widget_body).to_have_css('border-width', '1px')


# ==================== 内边距 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('修改内边距，画布按像素值同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_padding(free_container_page):
    cp = free_container_page
    cp.click_widget()
    # 这个框现在直接使用像素值，逐档核对
    for value in ['0', '1', '2', '16']:
        cp.prop_padding.fill(value)
        # 右侧断言
        expect(cp.prop_padding).to_have_value(value)
        # 画布断言
        expect(cp.widget_body, f'内边距填 {value} 时画布应是 {int(value) * cp.PADDING_UNIT_PX}px') \
            .to_have_css('padding', f'{int(value) * cp.PADDING_UNIT_PX}px')


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('内边距的上下箭头：上一下 +1、下一下 -1，画布跟着变')
@allure.severity(allure.severity_level.NORMAL)
def test_container_padding_spinner(free_container_page):
    cp = free_container_page
    cp.click_widget()
    check_number_spinner(
        cp.prop_padding, start='8',
        after=lambda v: expect(cp.widget_body).to_have_css(
            'padding', f'{int(v) * cp.PADDING_UNIT_PX}px'))


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('内边距到上下限（0 / 32）后，再按箭头不会越界')
@allure.severity(allure.severity_level.NORMAL)
def test_container_padding_clamps_at_limits(free_container_page):
    cp = free_container_page
    cp.click_widget()
    expect(cp.prop_padding).to_have_attribute('min', '0')
    expect(cp.prop_padding).to_have_attribute('max', '32')

    cp.prop_padding.fill('32')
    cp.prop_padding.press('ArrowUp')
    cp.page.wait_for_timeout(400)
    expect(cp.prop_padding, '到上限 32 再按上箭头不该继续加').to_have_value('32')

    cp.prop_padding.fill('0')
    cp.prop_padding.press('ArrowDown')
    cp.page.wait_for_timeout(400)
    expect(cp.prop_padding, '到下限 0 再按下箭头不该继续减').to_have_value('0')


# ==================== 往容器里加组件 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('选中容器时点「添加组件」，组件加进容器内而不是画布上')
@allure.severity(allure.severity_level.BLOCKER)
def test_container_add_child(free_container_page):
    cp = free_container_page
    cp.add_child('文本')
    # 画布断言：画布上顶层还是只有容器这一个，多出来的在容器内部
    expect(cp.canvas_widgets(), '文本应该进容器里，不该变成画布上的第二个组件') \
        .to_have_count(1)
    expect(cp.children).to_have_count(1)
    expect(cp.widget).to_contain_text('标题')


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('容器里可以放多个组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_add_multiple_children(free_container_page):
    cp = free_container_page
    cp.add_child('文本')
    cp.add_child('状态灯')
    # 画布断言
    expect(cp.canvas_widgets()).to_have_count(1)
    expect(cp.children).to_have_count(2)


# ==================== 列数与间距 ====================

def _same_row(a, b, tol=8):
    return abs(a['y'] - b['y']) <= tol


def _horizontal_gap(left, right):
    return right['x'] - (left['x'] + left['w'])


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('容器里放两个组件后把间距改成 24px，右侧和两个组件之间的空隙都是 24')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_gap_changes_canvas(free_container_page):
    cp = free_container_page
    cp.add_child('文本')
    cp.add_child('文本')
    cp.select_container()
    expect(cp.children).to_have_count(2)
    expect(cp.prop_gap).to_have_value(str(cp.GAP_DEFAULT))
    assert cp.canvas_gap_px() == cp.GAP_DEFAULT

    before = cp.child_boxes()
    assert len(before) == 2
    assert _same_row(before[0], before[1]), '默认 4 列时两个子组件应在同一行'
    assert abs(_horizontal_gap(before[0], before[1]) - cp.GAP_DEFAULT) <= 1, (
        f'默认间距画布上应是 {cp.GAP_DEFAULT}px，实际两组件空隙 '
        f'{_horizontal_gap(before[0], before[1]):.1f}px')

    cp.prop_gap.fill('24')
    expect(cp.prop_gap).to_have_value('24')
    cp.page.wait_for_timeout(400)
    assert cp.canvas_gap_px() == 24, f'画布 gap 应是 24px，实际 {cp.canvas_gap_px()}'
    after = cp.child_boxes()
    assert _same_row(after[0], after[1]), '改间距不应把两个组件拆到两行'
    gap = _horizontal_gap(after[0], after[1])
    assert abs(gap - 24) <= 1, f'两个组件之间的空隙应是 24px，实际 {gap:.1f}px'


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('列数改为 {cols}，右侧是 {cols}，画布变成 {cols} 列')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('cols', [1, 2, 3, 4, 5, 6])
def test_container_columns_1_to_6(free_container_page, cols):
    cp = free_container_page
    cp.add_child('文本')
    cp.add_child('文本')
    cp.select_container()
    expect(cp.children).to_have_count(2)

    cp.prop_columns.fill(str(cols))
    expect(cp.prop_columns).to_have_value(str(cols))
    cp.page.wait_for_timeout(400)

    style = cp.widget_slot.get_attribute('style') or ''
    assert f'repeat({cols}, 1fr)' in style, (
        f'内部 grid 应是 repeat({cols}, 1fr)，实际 style={style}')
    assert cp.canvas_column_count() == cols, (
        f'画布应是 {cols} 列，实际 {cp.canvas_column_count()}')

    boxes = cp.child_boxes()
    rows = cp.child_rows()
    if cols == 1:
        assert len(rows) == 2, f'1 列时应上下堆成 2 行，实际 {len(rows)} 行'
        assert abs(boxes[0]['x'] - boxes[1]['x']) <= 1, '1 列时两个组件应左对齐'
        assert boxes[1]['y'] > boxes[0]['y'] + boxes[0]['h'] - 1, (
            '1 列时第二个组件应在第一个下面')
    else:
        assert len(rows) == 1, f'{cols} 列时两个组件应在同一行，实际 {len(rows)} 行'
        assert boxes[1]['x'] > boxes[0]['x'] + boxes[0]['w'] - 1, (
            f'{cols} 列时第二个组件应在第一个右边')
        slot_w = cp.widget_slot.bounding_box()['width']
        expected_w = (slot_w - (cols - 1) * cp.canvas_gap_px()) / cols
        for i, box in enumerate(boxes):
            assert abs(box['w'] - expected_w) <= 2, (
                f'{cols} 列时第 {i} 个子组件宽应约 {expected_w:.1f}px，实际 {box["w"]:.1f}px')


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('容器里放 7 个组件后改列数 1–6，不崩溃，列数和行数都跟着变')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_seven_children_change_columns(free_container_page):
    cp = free_container_page
    for _ in range(7):
        cp.add_child('文本')
    cp.select_container()
    expect(cp.children).to_have_count(7)
    expect(cp.canvas_widgets(), '7 个子组件都应在容器里，不应漏到画布上') \
        .to_have_count(1)

    body = cp.page.locator('body')
    for cols in range(cp.COLUMNS_MIN, cp.COLUMNS_MAX + 1):
        cp.prop_columns.fill(str(cols))
        expect(cp.prop_columns).to_have_value(str(cols))
        cp.page.wait_for_timeout(400)

        txt = body.inner_text()
        for s in ('Something went wrong', 'Minified React error', '页面出错', '页面崩溃'):
            assert s not in txt, f'列数改成 {cols} 后面出错文案：{s!r}'
        expect(cp.children, f'列数 {cols} 后子组件还在').to_have_count(7)
        expect(cp.canvas_widgets(), f'列数 {cols} 后画布上仍只有容器').to_have_count(1)

        style = cp.widget_slot.get_attribute('style') or ''
        assert f'repeat({cols}, 1fr)' in style, (
            f'列数 {cols}：grid 应是 repeat({cols}, 1fr)，实际 {style}')
        assert cp.canvas_column_count() == cols, (
            f'列数 {cols}：画布实际列数 {cp.canvas_column_count()}')

        rows = cp.child_rows()
        expected_rows = math.ceil(7 / cols)
        assert len(rows) == expected_rows, (
            f'列数 {cols} 时 7 个组件应排成 {expected_rows} 行，实际 {len(rows)} 行')
        # 除最后一行外，每行都应坐满 cols 个
        for i, row in enumerate(rows[:-1]):
            assert len(row) == cols, (
                f'列数 {cols} 第 {i + 1} 行应有 {cols} 个，实际 {len(row)} 个')
        assert len(rows[-1]) == 7 - cols * (expected_rows - 1), (
            f'列数 {cols} 最后一行个数不对：{ [len(r) for r in rows] }')


# ==================== 容器内的组件 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('点容器内的组件，属性面板标题带「（容器内）」并给出位置')
@allure.severity(allure.severity_level.BLOCKER)
def test_container_child_panel_marks_in_container(free_container_page):
    cp = free_container_page
    cp.add_child('文本')
    cp.select_child()
    # 右侧断言：标题是「文本（容器内）」，下面还有一行位置说明
    expect(cp.child_panel_title('文本')).to_be_visible()
    expect(cp.child_position_hint).to_be_visible()
    expect(cp.child_position_hint).to_contain_text('容器内位置')


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('容器内的组件改属性，画布跟着变')
@allure.severity(allure.severity_level.BLOCKER)
def test_container_child_property_change(free_container_page):
    cp = free_container_page
    cp.add_child('文本')
    cp.select_child()

    # 容器内那段文字（子组件是文本组件，内容渲染成 <p>）
    child_text = cp.widget.locator('p').first

    cp.page.get_by_label('内容').fill('容器内的文字')
    # 右侧断言
    expect(cp.page.get_by_label('内容')).to_have_value('容器内的文字')
    # 画布断言
    expect(child_text).to_have_text('容器内的文字')

    cp.page.get_by_label('颜色', exact=True).fill('#ff0000')
    # 右侧断言
    expect(cp.page.get_by_label('颜色', exact=True)).to_have_value('#ff0000')
    # 画布断言
    expect(child_text).to_have_css('color', 'rgb(255, 0, 0)')


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('点画布空白，容器内组件的属性面板也收起来')
@allure.severity(allure.severity_level.NORMAL)
def test_container_child_panel_hides_on_blank_click(free_container_page):
    cp = free_container_page
    cp.add_child('文本')
    cp.select_child()
    expect(cp.child_panel_title('文本')).to_be_visible()

    cp.click_canvas_blank()
    expect(cp.child_panel_title('文本')).to_be_hidden()
    expect(cp.prop_panel).to_be_hidden()


# ==================== 删除 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('删除容器内的组件，容器本身还在')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_delete_child(free_container_page):
    cp = free_container_page
    cp.add_child('文本')
    expect(cp.children).to_have_count(1)

    cp.delete_child()
    # 画布断言：容器里空了，容器自己还在画布上
    expect(cp.children).to_have_count(0)
    expect(cp.canvas_widgets()).to_have_count(1)
    expect(cp.widget_title).to_have_text('容器')


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('容器里放两个组件，删掉一个，另一个还在')
@allure.severity(allure.severity_level.NORMAL)
def test_container_delete_one_of_two_children(free_container_page):
    cp = free_container_page
    cp.add_child('文本')
    cp.add_child('状态灯')
    expect(cp.children).to_have_count(2)

    cp.delete_child(0)
    # 画布断言
    expect(cp.children).to_have_count(1)
    expect(cp.canvas_widgets()).to_have_count(1)


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('删除容器组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_delete(free_container_page):
    cp = free_container_page
    expect(cp.canvas_widgets()).to_have_count(1)
    cp.delete_container()
    # 画布断言
    expect(cp.canvas_widgets()).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('删除装着组件的容器，里面的组件跟着一起没')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_delete_with_children(free_container_page):
    cp = free_container_page
    cp.add_child('文本')
    expect(cp.children).to_have_count(1)

    cp.delete_container()
    # 画布断言：容器和它里面的组件都不在了
    expect(cp.canvas_widgets()).to_have_count(0)
    expect(cp.page.get_by_text('标题')).to_have_count(0)


# ==================== 组合修改 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-容器组件')
@allure.title('同时修改标题、背景色、边框色、内边距')
@allure.severity(allure.severity_level.CRITICAL)
def test_container_combined(free_container_page):
    cp = free_container_page
    cp.click_widget()
    cp.prop_title.fill('分系统状态区')
    cp.prop_bg_color.fill('#123456')
    cp.prop_border_color.fill('#abcdef')
    cp.prop_padding.fill('2')

    # 右侧断言
    expect(cp.prop_title).to_have_value('分系统状态区')
    expect(cp.prop_bg_color).to_have_value('#123456')
    expect(cp.prop_border_color).to_have_value('#abcdef')
    expect(cp.prop_padding).to_have_value('2')
    # 画布断言
    expect(cp.widget_title).to_have_text('分系统状态区')
    expect(cp.widget_body).to_have_css('background-color', 'rgb(18, 52, 86)')
    expect(cp.widget_body).to_have_css('border-color', 'rgb(171, 205, 239)')
    expect(cp.widget_body).to_have_css('padding', f'{2 * cp.PADDING_UNIT_PX}px')


# ==================== 通用样式（共用用例集）====================
# 上/下/左/右边距 · 圆角 · 透明度 —— 用例写在 common_style_cases.py，这里只挂上去

class TestContainerCommonStyle(CommonStyleCases):
    widget_fixture = 'free_container_page'
    story = '自由布局-容器组件'
