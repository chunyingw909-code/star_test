from pages.editor.common_style_props import CommonStyleMixin
from pages.editor.free_layout_page import FreeLayoutPage


class FreeIndicatorPage(CommonStyleMixin, FreeLayoutPage):
    """指示牌组件（自由布局）。

    ⚠️ 只有【标签 / 单位 / 图标】在画布上看得出来，其余现在都是摆设：
       数值、警告阈值、危险阈值、小数位 —— 画布上数值一直显示 "—"（拿不到数据）
       显示状态                     —— 配套的状态趋势也没做好
       卫星 ID、字段路径             —— 绑遥测数据用的，现在连不上真实数据
    等能连上真实数据再补。
    """

    # 图标选项 -> 画布上那个图标的 data-testid（实测出来的，CPU 对应的是 MemoryIcon）
    ICONS = {'CPU': 'MemoryIcon', '内存': 'StorageIcon', '网络': 'NetworkCheckIcon',
             '速度': 'SpeedIcon', '温度': 'ThermostatIcon'}

    def __init__(self, page):
        super().__init__(page)
        self.prop_panel = page.get_by_role('heading', name='指示牌', exact=True)
        self.prop_label = page.get_by_label('标签', exact=True)
        self.prop_unit = page.get_by_label('单位', exact=True)
        self.prop_icon = page.locator('.MuiFormControl-root', has_text='图标').get_by_role('combobox')

        # 画布上的指示牌
        self.widget = self.canvas_widgets().first
        # 标签（第一段 caption）
        self.widget_label = self.widget.locator('span.MuiTypography-caption').first
        # 单位（数值后面那段 body 文字）
        self.widget_unit = self.widget.locator('p.MuiTypography-body1').nth(1)

    def widget_icon(self, testid):
        """画布上那个图标。testid 取自 ICONS，如 'StorageIcon'。"""
        return self.widget.locator(f'svg[data-testid="{testid}"]')
