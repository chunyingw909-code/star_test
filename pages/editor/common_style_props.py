class CommonStyleMixin:
    """组件属性面板底部那一组「通用样式」属性：上/下/左/右边距 · 圆角 · 透明度。

    12 个内置组件里有 10 个带这一组，字段名 / 取值范围 / 生效方式完全一致；
    图表(ChartWidget) 和 表格(TableWidget) 的面板里没有，别把它们 mixin 进来。

    生效目标是组件的外层包裹 div（.react-grid-item 里的第一个 MuiBox），
    见 widget_style_box()。默认值：面板里 6 个框都是空的，画布上表现为
    margin 0px / border-radius 4px / opacity 1。

    宿主类需提供（FreeLayoutPage 已有）：
      self.page            —— Page
      self.canvas_widgets() —— 画布上的组件集合
    """

    # 字段 key -> (面板标签, min, max, step)  —— 唯一数据源，用例直接遍历它
    COMMON_STYLE_FIELDS = {
        'margin_top':    ('上边距', '0', '64', '1'),
        'margin_bottom': ('下边距', '0', '64', '1'),
        'margin_left':   ('左边距', '0', '64', '1'),
        'margin_right':  ('右边距', '0', '64', '1'),
        'radius':        ('圆角',   '0', '32', '1'),
        'opacity':       ('透明度', '0', '1',  '0.05'),
    }
    # 画布上的默认表现（面板里 6 个框为空时）
    DEFAULT_MARGIN = '0px'
    DEFAULT_RADIUS = '4px'
    DEFAULT_OPACITY = '1'

    def __init__(self, page):
        super().__init__(page)
        self.prop_margin_top = page.get_by_label('上边距', exact=True)
        self.prop_margin_bottom = page.get_by_label('下边距', exact=True)
        self.prop_margin_left = page.get_by_label('左边距', exact=True)
        self.prop_margin_right = page.get_by_label('右边距', exact=True)
        self.prop_radius = page.get_by_label('圆角', exact=True)
        self.prop_opacity = page.get_by_label('透明度', exact=True)

    def common_style_input(self, name):
        """按 COMMON_STYLE_FIELDS 的 key 取输入框，如 common_style_input('radius')。"""
        return self.page.get_by_label(self.COMMON_STYLE_FIELDS[name][0], exact=True)

    def set_common_style(self, **values):
        """批量写入，key 同 COMMON_STYLE_FIELDS：
        set_common_style(margin_top=12, radius=9, opacity=0.5)
        """
        for name, v in values.items():
            self.common_style_input(name).fill(str(v))
        self.page.wait_for_timeout(300)

    def widget_style_box(self, index=0):
        """画布上真正吃这组样式的元素：组件外层包裹 div。"""
        return self.canvas_widgets().nth(index).locator('.MuiBox-root').first
