import re

from pages.editor.common_style_props import CommonStyleMixin
from pages.editor.free_layout_page import FreeLayoutPage


class FreeGaugePage(CommonStyleMixin, FreeLayoutPage):
    """仪表盘组件（自由布局）。

    ⚠️ 只有【标题 / 单位 / 最小值 / 最大值 / 尺寸】在画布上看得出来，其余是摆设：
       当前值、阈值(警告,危险) —— 只影响 echarts 内部绘制，暂不测
       卫星 ID、字段路径       —— 绑遥测数据用的，现在连不上真实数据，暂不测
    等能连上真实数据再补。
    """

    def __init__(self, page):
        super().__init__(page)
        # 属性面板：面板顶部是组件名的 heading
        self.prop_panel = page.get_by_role('heading', name='仪表盘', exact=True)
        self.prop_title = page.get_by_label('标题', exact=True)
        self.prop_min = page.get_by_label('最小值', exact=True)
        self.prop_max = page.get_by_label('最大值', exact=True)
        self.prop_unit = page.get_by_label('单位', exact=True)
        self.prop_size = page.get_by_label('尺寸 (px)', exact=True)

        # 画布上的仪表盘
        self.widget = self.canvas_widgets().first
        # 「Range: 0–100 V● LIVE」这行文字，最小值 / 最大值 / 单位都体现在这里
        self.widget_range = self.widget.get_by_text('Range:', exact=False)
        # echarts 那块，尺寸作用在它身上
        self.widget_chart = self.widget.locator('.echarts-for-react').first
        # 标题画在 echarts canvas 里，读不到文字，只能靠像素指纹
        self.widget_canvas = self.widget.locator('canvas').first

    def range_text(self):
        """画布 Range 那行拆成 {'min','max','unit'}。文案形如 "Range: 10–50 kW● LIVE"。"""
        raw = self.widget_range.inner_text()
        m = re.search(r'Range:\s*([\d.-]+)[–-]([\d.-]+)\s*(\S+?)●', raw)
        assert m, f'Range 文案没解析出来：{raw!r}'
        return {'min': m.group(1), 'max': m.group(2), 'unit': m.group(3)}

    def chart_size(self):
        """echarts 那块的渲染宽高，四舍五入 (w, h)。尺寸属性生效的结果。"""
        box = self.widget_chart.bounding_box()
        return (round(box['width']), round(box['height'])) if box else (0, 0)
