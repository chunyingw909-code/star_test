from pages.editor.free_layout_page import FreeLayoutPage


class FreeStatusPage(FreeLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        self.prop_panel = page.locator('.MuiBox-root', has_text='StatusIndicator').first
        # 核心字段
        self.prop_label = page.get_by_label('标签')
        self.prop_status_text = page.get_by_label('状态文字')
        self.prop_normal_color = page.get_by_label('正常颜色')
        self.prop_warning_color = page.get_by_label('警告颜色')
        self.prop_danger_color = page.get_by_label('危险颜色')
        self.prop_offline_color = page.get_by_label('离线颜色')
        self.prop_size = page.get_by_label('尺寸 (px)')
        # 数据绑定
        self.prop_data_source = page.get_by_label('卫星 ID')
        self.prop_field_path = page.get_by_label('字段路径')
        # 下拉框
        self.prop_refresh_mode = page.locator('.MuiFormControl-root', has_text='刷新模式').get_by_role('combobox')
        self.prop_error_fallback = page.locator('.MuiFormControl-root', has_text='出错时').get_by_role('combobox')
        self.prop_click_action = page.locator('.MuiFormControl-root', has_text='点击事件').get_by_role('combobox')

    # 显示标签 单选
    def show_label_radio(self, value):
        return self.page.locator('.MuiBox-root.css-0', has_text='显示标签').get_by_label(value)

    # 告警闪烁 单选
    def blink_radio(self, value):
        return self.page.locator('.MuiBox-root.css-0', has_text='告警闪烁').get_by_label(value)

    # 画布上的标签文字
    def widget_label_text(self, index=0):
        return self.canvas_widgets().nth(index).locator('span.MuiTypography-caption').first

    # 画布上的状态文字
    def widget_status_text(self, index=0):
        return self.canvas_widgets().nth(index).locator('span.MuiTypography-caption').nth(1)