from pages.editor.free_layout_page import FreeLayoutPage


class FreeIndicatorPage(FreeLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        self.prop_panel = page.locator('.MuiBox-root', has_text='IndicatorCard').first
        # 核心字段
        self.prop_label = page.get_by_label('标签')
        self.prop_value = page.get_by_label('数值')
        self.prop_unit = page.get_by_label('单位')
        self.prop_warning_threshold = page.get_by_label('警告阈值')
        self.prop_danger_threshold = page.get_by_label('危险阈值')
        self.prop_icon = page.locator('.MuiFormControl-root', has_text='图标').get_by_role('combobox')
        self.prop_decimal = page.get_by_label('小数位')
        # 数据绑定
        self.prop_data_source = page.get_by_label('卫星 ID')
        self.prop_field_path = page.get_by_label('字段路径')
        # 下拉框
        self.prop_refresh_mode = page.locator('.MuiFormControl-root', has_text='刷新模式').get_by_role('combobox')
        self.prop_error_fallback = page.locator('.MuiFormControl-root', has_text='出错时').get_by_role('combobox')
        self.prop_click_action = page.locator('.MuiFormControl-root', has_text='点击事件').get_by_role('combobox')
        self.prop_threshold_action = page.locator('.MuiFormControl-root', has_text='阈值触发').get_by_role('combobox')
        self.prop_threshold_target = page.get_by_label('阈值消息')
        self.prop_click_target = page.get_by_label('点击目标 (URL 或消息)')

    # 显示状态 单选
    def show_status_radio(self, value):
        return self.page.locator('.MuiBox-root.css-0', has_text='显示状态').get_by_label(value)

    # 画布上的标签
    def widget_label_text(self, index=0):
        return self.canvas_widgets().nth(index).locator('span.MuiTypography-caption').first

    # 画布上的数值
    def widget_value_text(self, index=0):
        return self.canvas_widgets().nth(index).locator('p.MuiTypography-body1').first

    # 画布上的单位
    def widget_unit_text(self, index=0):
        return self.canvas_widgets().nth(index).locator('p.MuiTypography-body1').nth(1)

    # 画布上的状态文字 (NORMAL等)
    def widget_status_text(self, index=0):
        return self.canvas_widgets().nth(index).locator('span.MuiTypography-caption').nth(1)