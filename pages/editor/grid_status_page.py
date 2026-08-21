from pages.editor.grid_layout_page import GridLayoutPage


class GridStatusPage(GridLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        self.prop_col_span = page.get_by_title('跨列数')
        self.prop_label = page.get_by_title('标签')
        self.prop_status_text = page.get_by_title('状态文字')
        self.prop_normal_color = page.get_by_title('正常颜色')
        self.prop_warning_color = page.get_by_title('警告颜色')
        self.prop_danger_color = page.get_by_title('危险颜色')
        self.prop_offline_color = page.get_by_title('离线颜色')
        self.prop_size = page.get_by_title('尺寸 (px)')
        self.prop_data_source = page.get_by_title('卫星 ID')
        self.prop_field_path = page.get_by_title('字段路径')
        self.prop_refresh_mode = page.get_by_title('刷新模式')
        self.prop_error_fallback = page.get_by_title('出错时')
        self.prop_click_action = page.get_by_title('点击事件')
        self.prop_click_target = page.get_by_title('点击目标 (URL 或消息)')
        self.prop_dblclick_action = page.get_by_title('双击事件')
        self.prop_dblclick_target = page.get_by_title('双击目标')
        self.prop_threshold_action = page.get_by_title('阈值触发')
        self.prop_threshold_target = page.get_by_title('阈值消息')
        self.prop_hover_action = page.get_by_title('悬停事件')
        self.prop_hover_target = page.get_by_title('悬停消息')

    # 显示标签
    def show_label_radio(self, value):
        bool_val = 'true' if value == '是' else 'false'
        return self.page.locator(f'//input[@name="showLabel" and @value=\'{{\"value\":{bool_val}}}\']')

    def show_label_label(self, value):
        return self.show_label_radio(value).locator('xpath=..')

    # 告警闪烁
    def blink_radio(self, value):
        bool_val = 'true' if value == '是' else 'false'
        return self.page.locator(f'//input[@name="blinkOnWarning" and @value=\'{{\"value\":{bool_val}}}\']')

    def blink_label(self, value):
        return self.blink_radio(value).locator('xpath=..')

    # 画布上的标签文字
    def widget_label_text(self, index=0):
        return self.canvas_widgets().nth(index).locator('span.MuiTypography-caption').first

    # 画布上的状态文字
    def widget_status_text(self, index=0):
        return self.canvas_widgets().nth(index).locator('span.MuiTypography-caption').nth(1)