"""文本组件。

⚠️ 以下属性【故意不写用例】，系统这边还不稳定，写了也是天天红：
      数据源、字段路径          —— 取不到真实数据
      警告阈值、危险阈值        —— 依赖上面两个，配了也不生效
      正常颜色、警告颜色、危险颜色 —— 同上，是配合阈值用的三态色
   等这几样稳了再补，补的位置就在本文件里，参照「颜色修改」那一节的写法。

⚠️ 「点击事件」下拉有 6 个选项，实测只有【弹窗提示】和【跳转 URL】是可用的，
   其余（刷新数据 / 显示弹窗 / 组件联动）不稳定，本文件只覆盖前两个。

⚠️ 颜色的调色盘是【浏览器自带的】，不是系统做的。点色块弹出的那个窗口
   （大色块、色相拉条、吸管、RGB/HEX 切换）不在页面 DOM 里，自动化碰不到，
   只能手工测。详见「颜色修改」那一节开头。

⚠️ 边界值（非法颜色、超范围数字等）目前只要求【不崩溃】，不断言具体回落值 ——
   系统还没成熟到能定这些行为。
"""
import allure
import pytest
from playwright.sync_api import expect

from pages.editor.editor_page import EditorPage
from common.number_input import check_number_spinner
from testcases.editor.click_action_cases import ClickActionCases
from testcases.editor.common_style_cases import CommonStyleCases


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('添加文本组件后画布出现组件，默认标题为"标题"')
@allure.severity(allure.severity_level.BLOCKER)
def test_text_default(free_text_page):
    free_text_page.click_widget()
    # 画布断言
    expect(free_text_page.canvas_widgets()).to_have_count(1)
    expect(free_text_page.canvas_widgets().first).to_contain_text('标题')


# ==================== 属性面板 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('点击组件，属性面板显示默认值')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_select_shows_properties(free_text_page):
    free_text_page.click_widget()
    expect(free_text_page.prop_panel).to_be_visible()
    # 右侧断言
    expect(free_text_page.prop_content).to_have_value('标题')
    expect(free_text_page.prop_font_size).to_have_value('24')
    expect(free_text_page.prop_color).to_have_value('#ffffff')
    # 画布断言
    text_el = free_text_page.widget_text()
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('点击画布空白区域，属性面板隐藏')
@allure.severity(allure.severity_level.NORMAL)
def test_text_click_blank_hides_properties(free_text_page):
    free_text_page.click_widget()
    expect(free_text_page.prop_panel).to_be_visible()
    free_text_page.click_canvas_blank()
    expect(free_text_page.prop_panel).to_be_hidden()


# ==================== 内容修改 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('修改内容为"卫星遥测监控大屏"')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_modify_content(free_text_page):
    free_text_page.click_widget()
    free_text_page.prop_content.fill('卫星遥测监控大屏')
    # 右侧断言
    expect(free_text_page.prop_content).to_have_value('卫星遥测监控大屏')
    # 画布断言
    text_el = free_text_page.widget_text()
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    expect(free_text_page.canvas_widgets().first).to_contain_text('卫星遥测监控大屏')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('清空内容，画布上不显示文字')
@allure.severity(allure.severity_level.NORMAL)
def test_text_clear_content(free_text_page):
    free_text_page.click_widget()
    free_text_page.prop_content.fill('')
    # 右侧断言
    expect(free_text_page.prop_content).to_have_value('')
    # 画布断言
    text_el = free_text_page.widget_text()
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    expect(free_text_page.canvas_widgets().first).not_to_contain_text('标题')


# ==================== 颜色修改 ====================
# 颜色属性是一对控件：左边一个色块，右边一个十六进制文本框，两边互相同步。
#
# ⚠️ 色块点开后弹出的是「浏览器自带的调色盘」——那里面的大色块拖拽、色相拉条、
#    吸管取色、RGB/HEX 格式切换，全都不在页面 DOM 里（点开前后页面元素数一个不变，
#    页面也没有 EyeDropper 接口），Playwright 没有任何办法碰到它们，测不了。
#    这里能覆盖到的是：色块本身的状态，以及「选完色之后」的结果——
#    给色块直接 fill() 一个颜色，等同于用户在调色盘里选完点确定，应用照样收得到。


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('颜色默认白色：文本框、色块、画布三处一致')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_color_default(free_text_page):
    free_text_page.click_widget()
    # 右侧断言
    expect(free_text_page.prop_color).to_have_value('#ffffff')
    expect(free_text_page.prop_color_swatch).to_have_value('#ffffff')
    # 画布断言
    text_el = free_text_page.widget_text()
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('在文本框写入十六进制 #127313，色块与画布同步')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_color_hex_input(free_text_page):
    free_text_page.click_widget()
    free_text_page.prop_color.fill('#127313')
    # 右侧断言
    expect(free_text_page.prop_color).to_have_value('#127313')
    expect(free_text_page.prop_color_swatch).to_have_value('#127313')
    # 画布断言
    text_el = free_text_page.widget_text()
    expect(text_el).to_have_css('color', 'rgb(18, 115, 19)')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('修改颜色为红色 #E74C3C')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_modify_color(free_text_page):
    free_text_page.click_widget()
    free_text_page.prop_color.fill('#E74C3C')
    # 右侧断言
    expect(free_text_page.prop_color).to_have_value('#E74C3C')
    expect(free_text_page.prop_color_swatch).to_have_value('#e74c3c')
    # 画布断言
    text_el = free_text_page.widget_text()
    expect(text_el).to_have_css('color', 'rgb(231, 76, 60)')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('font-weight', '700')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('修改颜色为浅蓝色 #4fc3f7')
@allure.severity(allure.severity_level.NORMAL)
def test_text_color_light_blue(free_text_page):
    free_text_page.click_widget()
    free_text_page.prop_color.fill('#4fc3f7')
    # 右侧断言
    expect(free_text_page.prop_color).to_have_value('#4fc3f7')
    expect(free_text_page.prop_color_swatch).to_have_value('#4fc3f7')
    # 画布断言
    text_el = free_text_page.widget_text()
    expect(text_el).to_have_css('color', 'rgb(79, 195, 247)')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('font-weight', '700')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('颜色恢复为白色 #ffffff')
@allure.severity(allure.severity_level.NORMAL)
def test_text_color_recover(free_text_page):
    free_text_page.click_widget()
    free_text_page.prop_color.fill('#E74C3C')
    free_text_page.prop_color.fill('#ffffff')
    # 右侧断言
    expect(free_text_page.prop_color).to_have_value('#ffffff')
    expect(free_text_page.prop_color_swatch).to_have_value('#ffffff')
    # 画布断言
    text_el = free_text_page.widget_text()
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('font-weight', '700')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('文本框填大写十六进制 {value}，色块归一成小写，画布按该色渲染')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize('value, swatch, rgb', [
    ('#ABCDEF', '#abcdef', 'rgb(171, 205, 239)'),
    ('#FF8800', '#ff8800', 'rgb(255, 136, 0)'),
])
def test_text_color_uppercase_hex(free_text_page, value, swatch, rgb):
    free_text_page.click_widget()
    free_text_page.prop_color.fill(value)
    # 右侧断言：文本框保留用户写的大写，色块统一成小写
    expect(free_text_page.prop_color).to_have_value(value)
    expect(free_text_page.prop_color_swatch).to_have_value(swatch)
    # 画布断言
    expect(free_text_page.widget_text()).to_have_css('color', rgb)


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('文本框填非法颜色 {value} 不会把页面点崩')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize('value', ['abcdef', '#12', '#12345', 'zzz', '#GGGGGG'])
def test_text_color_invalid_does_not_crash(free_text_page, value):
    # 系统还不成熟，非法值具体回落成什么颜色不做约定（实测是退回白色，但不断言）。
    # 这里只保证：填了非法值不报错、不白屏，组件和属性面板都还在，还能改回正常颜色。
    free_text_page.click_widget()
    free_text_page.prop_color.fill(value)
    free_text_page.page.wait_for_timeout(600)

    # 右侧断言：面板还在，输入的内容原样留着
    expect(free_text_page.prop_panel).to_be_visible()
    expect(free_text_page.prop_color).to_have_value(value)
    # 画布断言：组件还在，文字还在
    expect(free_text_page.canvas_widgets()).to_have_count(1)
    expect(free_text_page.widget_text()).to_contain_text('标题')

    # 还能改回正常颜色
    free_text_page.prop_color.fill('#127313')
    expect(free_text_page.prop_color_swatch).to_have_value('#127313')
    expect(free_text_page.widget_text()).to_have_css('color', 'rgb(18, 115, 19)')


@allure.title('色块是原生调色盘的入口：type=color、title="打开调色盘"、可点')
@allure.severity(allure.severity_level.NORMAL)
def test_text_color_swatch_is_native_picker_entry(free_text_page):
    # 点开之后的调色盘是浏览器自己的窗口，不在页面 DOM 里，测不到。
    # DOM 层能确认的只有：这个入口存在、类型对、可点、初值跟文本框一致。
    free_text_page.click_widget()
    swatch = free_text_page.prop_color_swatch
    expect(swatch).to_be_visible()
    expect(swatch).to_be_enabled()
    expect(swatch).to_have_attribute('type', 'color')
    expect(swatch).to_have_attribute('title', '打开调色盘')
    expect(swatch).to_have_value('#ffffff')

    # 点它不会往页面里插任何东西（调色盘是浏览器级窗口）
    page = free_text_page.page
    before = page.locator('body *').count()
    swatch.click()
    page.wait_for_timeout(800)
    assert page.locator('body *').count() == before, '点色块后页面 DOM 不应有变化'


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('通过色块选色 {value}（等同在调色盘里选完），文本框与画布同步')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('value, rgb', [
    ('#127313', 'rgb(18, 115, 19)'),
    ('#3366cc', 'rgb(51, 102, 204)'),
    ('#000000', 'rgb(0, 0, 0)'),
])
def test_text_color_set_via_swatch(free_text_page, value, rgb):
    free_text_page.click_widget()
    free_text_page.prop_color_swatch.fill(value)
    # 右侧断言：色块自己 + 旁边的文本框都跟上
    expect(free_text_page.prop_color_swatch).to_have_value(value)
    expect(free_text_page.prop_color).to_have_value(value)
    # 画布断言
    expect(free_text_page.widget_text()).to_have_css('color', rgb)


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('色块与文本框来回改，两边始终一致')
@allure.severity(allure.severity_level.NORMAL)
def test_text_color_swatch_and_text_stay_in_sync(free_text_page):
    free_text_page.click_widget()
    text_el = free_text_page.widget_text()

    # 文本框改 -> 色块跟
    free_text_page.prop_color.fill('#127313')
    expect(free_text_page.prop_color_swatch).to_have_value('#127313')
    expect(text_el).to_have_css('color', 'rgb(18, 115, 19)')

    # 色块改 -> 文本框跟
    free_text_page.prop_color_swatch.fill('#ff8800')
    expect(free_text_page.prop_color).to_have_value('#ff8800')
    expect(text_el).to_have_css('color', 'rgb(255, 136, 0)')

    # 再用文本框改回来
    free_text_page.prop_color.fill('#ffffff')
    expect(free_text_page.prop_color_swatch).to_have_value('#ffffff')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')


# ==================== 字号修改 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('字号调大为48')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_increase_font_size(free_text_page):
    free_text_page.click_widget()
    free_text_page.prop_font_size.fill('48')
    # 右侧断言
    expect(free_text_page.prop_font_size).to_have_value('48')
    # 画布断言
    text_el = free_text_page.widget_text()
    expect(text_el).to_have_css('font-size', '48px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    # 上下箭头：上一下 +1、下一下 -1，画布跟着变
    check_number_spinner(
        free_text_page.prop_font_size, start='48',
        after=lambda v: expect(text_el).to_have_css('font-size', f'{v}px'))


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('字号调小为8')
@allure.severity(allure.severity_level.NORMAL)
def test_text_decrease_font_size(free_text_page):
    free_text_page.click_widget()
    free_text_page.prop_font_size.fill('8')
    # 右侧断言
    expect(free_text_page.prop_font_size).to_have_value('8')
    # 画布断言
    text_el = free_text_page.widget_text()
    expect(text_el).to_have_css('font-size', '8px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('字号从48恢复为24')
@allure.severity(allure.severity_level.NORMAL)
def test_text_font_size_recover(free_text_page):
    free_text_page.click_widget()
    free_text_page.prop_font_size.fill('48')
    free_text_page.prop_font_size.fill('24')
    # 右侧断言
    expect(free_text_page.prop_font_size).to_have_value('24')
    # 画布断言
    text_el = free_text_page.widget_text()
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    # 上下箭头
    check_number_spinner(
        free_text_page.prop_font_size, start='24',
        after=lambda v: expect(text_el).to_have_css('font-size', f'{v}px'))


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('字号到上下限（8 / 120）后，再按箭头不会越界')
@allure.severity(allure.severity_level.NORMAL)
def test_text_font_size_clamps_at_limits(free_text_page):
    free_text_page.click_widget()
    size = free_text_page.prop_font_size
    expect(size).to_have_attribute('min', '8')
    expect(size).to_have_attribute('max', '120')

    size.fill('120')
    size.press('ArrowUp')
    free_text_page.page.wait_for_timeout(400)
    expect(size, '到上限 120 再按上箭头不该继续加').to_have_value('120')

    size.fill('8')
    size.press('ArrowDown')
    free_text_page.page.wait_for_timeout(400)
    expect(size, '到下限 8 再按下箭头不该继续减').to_have_value('8')


# ==================== 单位修改 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('设置单位为"V"')
@allure.severity(allure.severity_level.NORMAL)
def test_text_set_unit(free_text_page):
    free_text_page.click_widget()
    free_text_page.prop_unit.fill('V')
    # 右侧断言
    expect(free_text_page.prop_unit).to_have_value('V')
    # 画布断言
    text_el = free_text_page.widget_text()
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    expect(free_text_page.canvas_widgets().first).to_contain_text('V')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('清空单位')
@allure.severity(allure.severity_level.NORMAL)
def test_text_unit_clear(free_text_page):
    free_text_page.click_widget()
    free_text_page.prop_unit.fill('V')
    free_text_page.prop_unit.fill('')
    # 右侧断言
    expect(free_text_page.prop_unit).to_have_value('')
    # 画布断言
    text_el = free_text_page.widget_text()
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')
    expect(free_text_page.canvas_widgets().first).not_to_contain_text('V')


# ==================== 对齐方式 ====================
# 下拉框类的属性走数据驱动：选项列表写在页面对象里（FreeTextPage.ALIGNS），
# 一个用例把所有选项跑一遍。不拆成一个选项一条 —— 每条都要重开浏览器、进编辑器、
# 加组件，3 个选项就多花 30 秒，而选项之间互不影响，本来就是同一个交互重复 N 次。
# 断言消息里带上是哪个选项，失败定位不比拆开差。真碰到某个选项不稳，再单独拎出来。

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('对齐方式逐项切换（左 / 居中 / 右），画布对齐跟着变')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_align_all_options(free_text_page):
    free_text_page.click_widget()
    row = free_text_page.widget_text_row()

    for label, justify in free_text_page.ALIGNS.items():
        free_text_page.pick_option(free_text_page.prop_align, label)
        # 右侧断言
        expect(free_text_page.prop_align, f'对齐下拉应显示 {label}').to_have_text(label)
        # 画布断言：对齐作用在包文字那一层的 justify-content 上
        expect(row, f'对齐选 {label} 时画布应是 {justify}').to_have_css('justify-content', justify)


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('对齐方式改完再改回默认「左」，画布复原')
@allure.severity(allure.severity_level.NORMAL)
def test_text_align_recover_to_left(free_text_page):
    free_text_page.click_widget()
    row = free_text_page.widget_text_row()

    free_text_page.pick_option(free_text_page.prop_align, '右')
    expect(free_text_page.prop_align).to_have_text('右')
    expect(row).to_have_css('justify-content', 'flex-end')

    free_text_page.pick_option(free_text_page.prop_align, '左')
    # 右侧断言
    expect(free_text_page.prop_align).to_have_text('左')
    # 画布断言
    expect(row).to_have_css('justify-content', 'flex-start')
    text_el = free_text_page.widget_text()
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')


# ==================== 图标 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('图标逐项切换（无 / 信息 / 警告 / 告警），画布图标跟着换')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_icon_all_options(free_text_page):
    free_text_page.click_widget()
    icons = free_text_page.ICONS

    for label, testid in icons.items():
        free_text_page.pick_option(free_text_page.prop_icon, label)
        if testid is None:
            # 选「无」：下拉显示空，画布上一个业务图标都不该有
            for other in (t for t in icons.values() if t):
                expect(free_text_page.widget_icon(other),
                       f'图标选「无」时画布不该有 {other}').to_have_count(0)
        else:
            # 右侧断言
            expect(free_text_page.prop_icon, f'图标下拉应显示 {label}').to_have_text(label)
            # 画布断言：只出现这一个图标，别的都不在
            expect(free_text_page.widget_icon(testid),
                   f'图标选 {label} 时画布应出现 {testid}').to_have_count(1)
            for other in (t for t in icons.values() if t and t != testid):
                expect(free_text_page.widget_icon(other),
                       f'图标选 {label} 时不该同时有 {other}').to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('图标默认为「无」，画布上不带图标')
@allure.severity(allure.severity_level.NORMAL)
def test_text_icon_default_none(free_text_page):
    free_text_page.click_widget()
    for testid in (t for t in free_text_page.ICONS.values() if t):
        expect(free_text_page.widget_icon(testid),
               f'默认不该有 {testid}').to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('图标选中后再改回「无」，画布图标消失')
@allure.severity(allure.severity_level.NORMAL)
def test_text_icon_recover_to_none(free_text_page):
    free_text_page.click_widget()
    free_text_page.pick_option(free_text_page.prop_icon, '警告')
    expect(free_text_page.widget_icon('WarningIcon')).to_have_count(1)

    free_text_page.pick_option(free_text_page.prop_icon, '无')
    # 画布断言
    expect(free_text_page.widget_icon('WarningIcon')).to_have_count(0)
    # 文字本身不受影响
    expect(free_text_page.widget_text()).to_contain_text('标题')


# ==================== 字重 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('切换字重为正常 (400)')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_weight_normal(free_text_page):
    free_text_page.click_widget()
    free_text_page.prop_weight.click()
    free_text_page.page.get_by_role('option', name='正常').click()
    # 右侧断言
    expect(free_text_page.prop_weight).to_have_text('正常')
    # 画布断言
    text_el = free_text_page.widget_text()
    expect(text_el).to_have_css('font-weight', '400')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('切换字重为粗体 (700)')
@allure.severity(allure.severity_level.NORMAL)
def test_text_weight_bold(free_text_page):
    free_text_page.click_widget()
    free_text_page.prop_weight.click()
    free_text_page.page.get_by_role('option', name='粗体').click()
    # 右侧断言
    expect(free_text_page.prop_weight).to_have_text('粗体')
    # 画布断言
    text_el = free_text_page.widget_text()
    expect(text_el).to_have_css('font-weight', '700')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('切换字重为中等 (500)')
@allure.severity(allure.severity_level.NORMAL)
def test_text_weight_medium(free_text_page):
    free_text_page.click_widget()
    free_text_page.prop_weight.click()
    free_text_page.page.get_by_role('option', name='中等').click()
    # 右侧断言
    expect(free_text_page.prop_weight).to_have_text('中等')
    # 画布断言
    text_el = free_text_page.widget_text()
    expect(text_el).to_have_css('font-weight', '500')
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')


# ==================== 绑定模式 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('切换绑定模式为静态')
@allure.severity(allure.severity_level.NORMAL)
def test_text_binding_mode_static(free_text_page):
    free_text_page.click_widget()
    free_text_page.prop_binding_mode.click()
    free_text_page.page.get_by_role('option', name='静态').click()
    # 右侧断言
    expect(free_text_page.prop_binding_mode).to_have_text('静态')
    # 画布断言
    text_el = free_text_page.widget_text()
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')


@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('切换绑定模式为动态')
@allure.severity(allure.severity_level.NORMAL)
def test_text_binding_mode_dynamic(free_text_page):
    free_text_page.click_widget()
    free_text_page.prop_binding_mode.click()
    free_text_page.page.get_by_role('option', name='动态').click()
    # 右侧断言
    expect(free_text_page.prop_binding_mode).to_have_text('动态')
    # 画布断言
    text_el = free_text_page.widget_text()
    expect(text_el).to_have_css('font-size', '24px')
    expect(text_el).to_have_css('color', 'rgb(255, 255, 255)')
    expect(text_el).to_have_css('font-weight', '700')


# ==================== 删除 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('删除文本组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_delete(free_text_page):
    expect(free_text_page.canvas_widgets()).to_have_count(1)
    free_text_page.delete_widget()
    expect(free_text_page.canvas_widgets()).to_have_count(0)


# ==================== 组合修改 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-文本组件')
@allure.title('同时修改内容、颜色、字号、单位、对齐、字重')
@allure.severity(allure.severity_level.CRITICAL)
def test_text_combined(free_text_page):
    free_text_page.click_widget()
    # 修改多个属性
    free_text_page.prop_content.fill('综合测试文本')
    free_text_page.prop_color.fill('#4fc3f7')  # 浅蓝
    free_text_page.prop_font_size.fill('36')
    free_text_page.prop_unit.fill('kW')
    # 对齐方式改为居中
    free_text_page.prop_align.click()
    free_text_page.page.get_by_role('option', name='居中').click()
    # 字重改为粗体
    free_text_page.prop_weight.click()
    free_text_page.page.get_by_role('option', name='粗体').click()
    # 右侧断言
    expect(free_text_page.prop_content).to_have_value('综合测试文本')
    expect(free_text_page.prop_color).to_have_value('#4fc3f7')
    expect(free_text_page.prop_font_size).to_have_value('36')
    expect(free_text_page.prop_unit).to_have_value('kW')
    expect(free_text_page.prop_align).to_have_text('居中')
    expect(free_text_page.prop_weight).to_have_text('粗体')
    # 画布断言
    text_el = free_text_page.widget_text()
    expect(text_el).to_have_css('font-size', '36px')
    expect(text_el).to_have_css('color', 'rgb(79, 195, 247)')
    expect(text_el).to_have_css('font-weight', '700')
    expect(free_text_page.canvas_widgets().first).to_contain_text('综合测试文本')
    expect(free_text_page.canvas_widgets().first).to_contain_text('kW')


# ==================== 通用样式（共用用例集）====================
# 上/下/左/右边距 · 圆角 · 透明度 —— 用例写在 common_style_cases.py，这里只挂上去

class TestTextCommonStyle(CommonStyleCases):
    widget_fixture = 'free_text_page'
    story = '自由布局-文本组件'


# ==================== 点击事件（共用用例集）====================
# 单击 → 弹窗提示 / 跳转 URL —— 用例写在 click_action_cases.py，这里只挂上去

class TestTextClickAction(ClickActionCases):
    widget_fixture = 'free_text_page'
    story = '自由布局-文本组件'
    marker_prop = 'prop_content'
