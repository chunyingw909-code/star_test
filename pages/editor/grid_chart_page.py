from pages.editor.grid_layout_page import GridLayoutPage


class GridChartPage(GridLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        # 输入框
        self.prop_title = page.get_by_title('标题')
        self.prop_chart_type = page.get_by_title('图表类型')
        self.prop_data_source = page.get_by_title('卫星 ID')
        self.prop_x_field = page.get_by_title('X 轴字段')
        self.prop_y_fields = page.get_by_title('Y 轴字段 (逗号分隔)')
        self.prop_series_names = page.get_by_title('系列名称 (逗号分隔)')
        self.prop_series_colors = page.get_by_title('系列颜色 (逗号分隔)')
        # 主题用 get_by_label 避免和主题切换按钮冲突
        self.prop_theme = page.get_by_label('主题')
        self.prop_legend_position = page.get_by_title('图例位置')
        self.prop_warning_line = page.get_by_title('警告线')
        self.prop_danger_line = page.get_by_title('危险线')
        self.prop_line_width = page.get_by_title('线宽')
        self.prop_fill_opacity = page.get_by_title('填充透明度')
        self.prop_max_points = page.get_by_title('最大点数')

    # ----- 图例 -----
    def legend_radio(self, value):
        bool_val = 'true' if value == '是' else 'false'
        return self.page.locator(f'//input[@name="showLegend" and @value=\'{{"value":{bool_val}}}\']')

    def legend_label(self, value):
        return self.legend_radio(value).locator('xpath=..')

    # ----- 提示 -----
    def tooltip_radio(self, value):
        bool_val = 'true' if value == '是' else 'false'
        return self.page.locator(f'//input[@name="showTooltip" and @value=\'{{"value":{bool_val}}}\']')

    def tooltip_label(self, value):
        return self.tooltip_radio(value).locator('xpath=..')

    # ----- 数据缩放 -----
    def zoom_radio(self, value):
        bool_val = 'true' if value == '是' else 'false'
        return self.page.locator(f'//input[@name="showDataZoom" and @value=\'{{"value":{bool_val}}}\']')

    def zoom_label(self, value):
        return self.zoom_radio(value).locator('xpath=..')