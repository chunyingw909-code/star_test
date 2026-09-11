"""数字输入框的公用检查 —— 右边那对上下箭头。

页面上凡是 type=number 的输入框，浏览器都会在右侧画一对上下箭头（spinner），
点上箭头 +step、下箭头 -step。项目里到处都有这种框（界面编辑器的字号 / 列数 /
边距，遥测的自定义倍速，等等），所以检查逻辑放在这里公用。

⚠️ 那对箭头是浏览器画的伪元素（::-webkit-inner-spin-button），DOM 里没有对应
   节点，定位不到、也点不着（实测按坐标点输入框右边缘无效，值纹丝不动）。
   键盘的 ↑ ↓ 走的是同一套 step 逻辑，是箭头的等价操作，用它来驱动。
   「箭头存在」则从三件事确认：type=number、有 step、伪元素没被 CSS 藏掉。

用法 —— 在任何有数字输入框的用例里加一行：

    from common.number_input import check_number_spinner

    check_number_spinner(free_text_page.prop_font_size, start='24')

需要顺带校验画布跟着变，就传 after（每次值变化后回调一次，参数是当前值字符串）：

    text_el = free_text_page.canvas_widgets().first.locator('p')
    check_number_spinner(free_text_page.prop_font_size, start='24',
                         after=lambda v: expect(text_el).to_have_css('font-size', v + 'px'))
"""
from playwright.sync_api import expect


def assert_has_spinner(number_input):
    """断言这个框后面带浏览器原生的上下箭头，返回它的 step（字符串）。"""
    expect(number_input, '应该是 type=number 的数字框，浏览器才会画上下箭头') \
        .to_have_attribute('type', 'number')

    step = number_input.get_attribute('step')
    assert step not in (None, ''), '数字框没有 step 属性，浏览器不会画上下箭头'

    hidden = number_input.evaluate("""el => {
        const cs = getComputedStyle(el, '::-webkit-inner-spin-button');
        const ap = cs.webkitAppearance || cs.appearance;
        return ap === 'none' || cs.display === 'none' || cs.opacity === '0';
    }""")
    assert not hidden, '上下箭头被 CSS 藏掉了（appearance:none / display:none / opacity:0）'
    return step


def _fmt(value, step):
    """按 step 的精度把数值格式化成输入框里会显示的样子。"""
    if float(step).is_integer():
        return str(int(round(value)))
    text = f'{value:.10f}'.rstrip('0').rstrip('.')
    return text or '0'


def check_number_spinner(number_input, start=None, after=None, settle_ms=400):
    """一行覆盖上下箭头：箭头在 + 上一下加一个 step + 下一下减回来。

    start：从哪个值开始试。别传 min / max 上的值，到边界了按箭头不会动。
           框里本来是空的（比如通用样式那几个）就必须传。
    after：可选，每次值变化后回调，用来顺带断言画布，签名 after(当前值字符串)。
    """
    step_attr = assert_has_spinner(number_input)
    step = float(step_attr)
    page = number_input.page

    if start is not None:
        number_input.fill(str(start))
        page.wait_for_timeout(settle_ms)

    raw = number_input.input_value()
    assert raw != '', '数字框是空的，请用 start= 指定一个起始值再检查上下箭头'
    begin = float(raw)

    lo, hi = number_input.get_attribute('min'), number_input.get_attribute('max')
    if hi not in (None, ''):
        assert begin + step <= float(hi), f'起始值 {raw} 加一个 step 就超出上限 {hi}，换个 start'
    if lo not in (None, ''):
        assert begin >= float(lo), f'起始值 {raw} 已经低于下限 {lo}'

    # 上箭头：+1 个 step
    up = _fmt(begin + step, step_attr)
    number_input.press('ArrowUp')
    page.wait_for_timeout(settle_ms)
    expect(number_input, f'按一下上箭头，应该从 {raw} 变成 {up}').to_have_value(up)
    if after:
        after(up)

    # 下箭头：-1 个 step，回到起点
    back = _fmt(begin, step_attr)
    number_input.press('ArrowDown')
    page.wait_for_timeout(settle_ms)
    expect(number_input, f'按一下下箭头，应该从 {up} 回到 {back}').to_have_value(back)
    if after:
        after(back)
