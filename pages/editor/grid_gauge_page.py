from pages.editor.grid_layout_page import GridLayoutPage


class GridGaugePage(GridLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        # 属性面板 —— 核心字段
        self.prop_col_span = page.get_by_title('跨列数')
        self.prop_title = page.get_by_title('标题')
        self.prop_min = page.get_by_title('最小值')
        self.prop_max = page.get_by_title('最大值')
        self.prop_value = page.get_by_title('当前值')
        self.prop_unit = page.get_by_title('单位')
        self.prop_thresholds = page.get_by_title('阈值 (警告,危险)')
        self.prop_size = page.get_by_title('尺寸 (px)')
        # 数据绑定
        self.prop_data_source = page.get_by_title('卫星 ID')
        self.prop_field_path = page.get_by_title('字段路径')
        # 下拉框
        self.prop_refresh_mode = page.get_by_title('刷新模式')
        self.prop_refresh_interval = page.get_by_title('刷新间隔 (s)')
        self.prop_error_fallback = page.get_by_title('出错时')
        # 事件
        self.prop_click_action = page.get_by_title('点击事件')
        self.prop_click_target = page.get_by_title('点击目标 (URL 或消息)')
        self.prop_dblclick_action = page.get_by_title('双击事件')
        self.prop_dblclick_target = page.get_by_title('双击目标')
        self.prop_threshold_action = page.get_by_title('阈值触发')
        self.prop_threshold_target = page.get_by_title('阈值消息')
        self.prop_hover_action = page.get_by_title('悬停事件')
        self.prop_hover_target = page.get_by_title('悬停消息')
        self.prop_input_action = page.get_by_title('输入变化')
        self.prop_timer_action = page.get_by_title('定时触发')
        self.prop_timer_interval = page.get_by_title('定时间隔 (s)')
        # 条件
        self.prop_condition_expr = page.get_by_title('条件表达式 (JSON)')

    # 画布上仪表盘的 echarts 容器
    def gauge_chart(self, index=0):
        return self.canvas_widgets().nth(index).locator('.echarts-for-react')

    # 画布上仪表盘的底部说明文字 Range: x–y unit
    def gauge_caption(self, index=0):
        return self.canvas_widgets().nth(index).locator('span.MuiTypography-caption').first