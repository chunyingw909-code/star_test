"""读 <canvas> 的像素 —— option 读不到时才用。

图表优先走 common/echarts_option.py，断言「图画成了什么」。
像素指纹只能看出变了、变在哪块区域，留给仪表盘标题这种 option 不好对的场合。

⚠️ 别跟以前那个整页截图比对搞混。那个是拿图片文件做 SSIM，跟机器 / DPI / 有头无头
   强绑定，已经停用了。这里读的是画布自己的像素缓冲。

用法：
    from common.canvas_pixels import fingerprint, assert_changed

    before = fingerprint(图表.widget_canvas.first)
    ...改属性...
    after = fingerprint(图表.widget_canvas.first)
    assert_changed(before, after, '切换主题')
"""

# 九宫格编号：
#   0 1 2      左上 中上 右上
#   3 4 5      左中 正中 右中
#   6 7 8      左下 中下 右下
REGIONS = {
    'top': (0, 1, 2),
    'middle': (3, 4, 5),
    'bottom': (6, 7, 8),
    'left': (0, 3, 6),
    'center': (1, 4, 7),
    'right': (2, 5, 8),
}

# 取样：九宫格各自的平均颜色 + 整幅平均色 + 粗分后的颜色种类数
# （颜色种类衡量「画布上画了多少东西」，饼图那种五颜六色的会明显偏高）
_SAMPLE_JS = """
el => {
  const ctx = el.getContext('2d');
  const W = el.width, H = el.height;
  if (!W || !H) return null;
  const cells = [];
  for (let ry = 0; ry < 3; ry++) {
    for (let rx = 0; rx < 3; rx++) {
      const x = Math.floor(rx * W / 3), y = Math.floor(ry * H / 3);
      const w = Math.floor(W / 3), h = Math.floor(H / 3);
      const d = ctx.getImageData(x, y, w, h).data;
      let r = 0, g = 0, b = 0, n = 0;
      for (let i = 0; i < d.length; i += 4 * 7) { r += d[i]; g += d[i+1]; b += d[i+2]; n++; }
      cells.push([Math.round(r / n), Math.round(g / n), Math.round(b / n)]);
    }
  }
  const all = ctx.getImageData(0, 0, W, H).data;
  let R = 0, G = 0, B = 0, N = 0;
  const kinds = new Set();
  for (let i = 0; i < all.length; i += 4 * 11) {
    R += all[i]; G += all[i+1]; B += all[i+2]; N++;
    kinds.add((all[i] >> 4) + ',' + (all[i+1] >> 4) + ',' + (all[i+2] >> 4));
  }
  return { size: [W, H], cells,
           avg: [Math.round(R / N), Math.round(G / N), Math.round(B / N)],
           colors: kinds.size };
}
"""


def fingerprint(canvas, settle_ms=400, tries=25, stable_hits=3):
    """采一张像素指纹。会一直采到【连续 stable_hits 次一模一样】才返回。

    为什么要连着好几次都一样：echarts 换主题 / 换类型时有入场动画，刚绑完数据源
    的头几帧也还在画。只比连续两次很容易在动画的某个平台期上误判成「稳了」，
    采回来的指纹就跟稳定态对不上（实测表现为颜色种类偏高）。

    canvas：<canvas> 元素的 Locator（如 图表.widget_canvas.first）
    返回 {'size': [宽, 高], 'avg': [r,g,b], 'cells': [9 个 [r,g,b]], 'colors': 颜色种类数}
    """
    page = canvas.page
    page.wait_for_timeout(settle_ms)
    prev = canvas.evaluate(_SAMPLE_JS)
    assert prev is not None, '画布宽高是 0，图还没画出来'
    hits = 1
    for _ in range(tries):
        page.wait_for_timeout(settle_ms)
        cur = canvas.evaluate(_SAMPLE_JS)
        if cur == prev:
            hits += 1
            if hits >= stable_hits:
                return cur
        else:
            hits = 1
        prev = cur
    return prev


def brightness(rgb):
    """一个颜色的平均亮度（0~255）。"""
    return sum(rgb) / 3


def region_brightness(fp, region):
    """指纹里某块区域的平均亮度。region 取 REGIONS 的键，如 'top' / 'left'。"""
    idxs = REGIONS[region]
    return sum(brightness(fp['cells'][i]) for i in idxs) / len(idxs)


def is_changed(before, after):
    """两张指纹是不是不一样（九宫格或颜色种类有差别就算）。"""
    return before['cells'] != after['cells'] or before['colors'] != after['colors']


def assert_changed(before, after, what):
    """断言画布确实变了。"""
    assert is_changed(before, after), (
        f'{what} 之后画布应该有变化，但像素完全一样：'
        f'整幅平均={after["avg"]} 颜色种类={after["colors"]}')


def assert_same(before, after, what):
    """断言画布回到了原样（改回默认值之后用）。"""
    assert not is_changed(before, after), (
        f'{what} 之后画布应该跟之前一样，实际 '
        f'整幅平均 {before["avg"]}→{after["avg"]}、'
        f'颜色种类 {before["colors"]}→{after["colors"]}')
