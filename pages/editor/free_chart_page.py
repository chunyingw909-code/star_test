from pages.editor.free_layout_page import FreeLayoutPage


class FreeChartPage(FreeLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        # 属性面板
        self.prop_panel = page.locator('.MuiBox-root', has_text='ChartWidget').last
        self.prop_title = page.get_by_label('标题')
        self.prop_chart_type = page.locator('.MuiFormControl-root', has_text='图表类型').get_by_role('combobox')
        self.prop_satellite_id = page.get_by_label('卫星 ID')
        self.prop_x_field = page.get_by_label('X 轴字段')
        self.prop_y_field = page.get_by_label('Y 轴字段 (逗号分隔)')
        self.prop_series_name = page.get_by_label('系列名称 (逗号分隔)')
        self.prop_series_color = page.get_by_label('系列颜色 (逗号分隔)')
        self.prop_theme = page.locator('.MuiFormControl-root', has_text='主题').get_by_role('combobox')
        self.prop_legend_position = page.locator('.MuiFormControl-root', has_text='图例位置').get_by_role('combobox')

    def legend_radio(self, value):
        return self.page.locator('.MuiBox-root.css-0', has_text='显示图例').get_by_label(value)

    def tooltip_radio(self, value):
        return self.page.locator('.MuiBox-root.css-0', has_text='显示提示').get_by_label(value)

    def zoom_radio(self, value):
        return self.page.locator('.MuiBox-root.css-0', has_text='数据缩放').get_by_label(value)