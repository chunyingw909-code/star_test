from pages.editor.free_layout_page import FreeLayoutPage


class FreeGaugePage(FreeLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        # 属性面板
        self.prop_panel = page.locator('.MuiBox-root', has_text='GaugeWidget').first
        # 核心字段
        self.prop_title = page.get_by_label('标题')
        self.prop_min = page.get_by_label('最小值')
        self.prop_max = page.get_by_label('最大值')
        self.prop_value = page.get_by_label('当前值')
        self.prop_unit = page.get_by_label('单位')
        self.prop_thresholds = page.get_by_label('阈值 (警告,危险)')
        self.prop_size = page.get_by_label('尺寸 (px)')
        # 数据绑定
        self.prop_data_source = page.get_by_label('卫星 ID')
        self.prop_field_path = page.get_by_label('字段路径')
        # 下拉框（MUI Select）
        self.prop_refresh_mode = page.locator('.MuiFormControl-root', has_text='刷新模式').get_by_role('combobox')
        self.prop_error_fallback = page.locator('.MuiFormControl-root', has_text='出错时').get_by_role('combobox')
        self.prop_click_action = page.locator('.MuiFormControl-root', has_text='点击事件').get_by_role('combobox')
        self.prop_dblclick_action = page.locator('.MuiFormControl-root', has_text='双击事件').get_by_role('combobox')
        self.prop_threshold_action = page.locator('.MuiFormControl-root', has_text='阈值触发').get_by_role('combobox')
        self.prop_hover_action = page.locator('.MuiFormControl-root', has_text='悬停事件').get_by_role('combobox')
        self.prop_input_action = page.locator('.MuiFormControl-root', has_text='输入变化').get_by_role('combobox')
        self.prop_timer_action = page.locator('.MuiFormControl-root', has_text='定时触发').get_by_role('combobox')
        # 事件目标
        self.prop_click_target = page.get_by_label('点击目标 (URL 或消息)')
        self.prop_dblclick_target = page.get_by_label('双击目标')
        self.prop_threshold_target = page.get_by_label('阈值消息')
        self.prop_hover_target = page.get_by_label('悬停消息')
        self.prop_refresh_interval = page.get_by_label('刷新间隔 (s)')
        self.prop_timer_interval = page.get_by_label('定时间隔 (s)')
        self.prop_condition_expr = page.get_by_label('条件表达式 (JSON)')

    def gauge_chart(self, index=0):
        return self.canvas_widgets().nth(index).locator('.echarts-for-react')

    def gauge_caption(self, index=0):
        return self.canvas_widgets().nth(index).locator('span.MuiTypography-caption').first