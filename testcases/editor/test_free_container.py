"""容器组件 —— 能往里嵌套其它组件的盒子。

⚠️ 以下属性【故意不写用例】，系统这边不生效，写了也是白写：
      最小高度   —— 不生效
   等开发修好再补，补的位置就在本文件里。

本文件覆盖两块：
  1. 容器自己的属性：标题、背景色、边框色、内边距，外加公用的通用样式
  2. 容器特有的嵌套行为：往容器里加组件、选中容器内的组件、改它的属性、
     删掉容器内的组件、删掉容器本身
"""
import allure
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
    # 画布断言：内边距现在直接按 px 生效
    expect(cp.widget_body).to_have_css('padding', f'{8 * cp.PADDING_UNIT_PX}px')


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
