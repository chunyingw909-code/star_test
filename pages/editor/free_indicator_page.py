from pages.editor.common_style_props import CommonStyleMixin
from pages.editor.free_layout_page import FreeLayoutPage


class FreeIndicatorPage(CommonStyleMixin, FreeLayoutPage):
    """指示牌组件（自由布局），包括真实遥测数值与 LIVE 状态。"""

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
        self.widget_value = self.widget.locator('p.MuiTypography-body1').first
        # 单位（数值后面那段 body 文字）
        self.widget_unit = self.widget.locator('p.MuiTypography-body1').nth(1)
        self.widget_live = self.widget.get_by_text('● LIVE', exact=True)

    def widget_icon(self, testid):
        """画布上那个图标。testid 取自 ICONS，如 'StorageIcon'。"""
        return self.widget.locator(f'svg[data-testid="{testid}"]')

    def live_value(self):
        """画布正在显示的实时数值。"""
        return float(self.widget_value.inner_text())
