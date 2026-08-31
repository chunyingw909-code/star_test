from pages.editor.grid_layout_page import GridLayoutPage


class GridChartPage(GridLayoutPage):
    # 图表类型 / 主题 / 图例位置 原生 <select> 的 {选项文案: value}
    CHART_TYPES = {'折线': '{"value":"line"}', '柱状': '{"value":"bar"}', '饼图': '{"value":"pie"}'}
    THEMES = {'深色': '{"value":"dark"}', '浅色': '{"value":"light"}'}
    LEGEND_POSITIONS = {'底部': '{"value":"bottom"}', '顶部': '{"value":"top"}', '左侧': '{"value":"left"}'}
    # 交互事件下拉：{字段 title: {选项文案: value}}
    EVENT_SELECTS = {
        '点击事件': {
            '无': '{"value":""}', '弹窗提示': '{"value":"alert"}', '跳转 URL': '{"value":"navigate"}',
            '刷新数据': '{"value":"refresh"}', '显示弹窗': '{"value":"modal"}', '组件联动': '{"value":"linkage"}',
        },
        '双击事件': {'无': '{"value":""}', '弹窗提示': '{"value":"alert"}', '跳转 URL': '{"value":"navigate"}'},
        '阈值触发': {'无': '{"value":""}', '弹窗提示': '{"value":"alert"}', '刷新数据': '{"value":"refresh"}'},
        '悬停事件': {'无': '{"value":""}', '弹窗提示': '{"value":"alert"}'},
        '输入变化': {'无': '{"value":""}', '刷新数据': '{"value":"refresh"}'},
        '定时触发': {'无': '{"value":""}', '刷新数据': '{"value":"refresh"}'},
    }

    def __init__(self, page):
        super().__init__(page)
        self.prop_heading = page.get_by_role('heading', name='图表', exact=True)
        # 输入框（grid 用 title 定位）
        self.prop_title = page.get_by_title('标题')
        self.prop_warning_line = page.get_by_title('警告线')
        self.prop_danger_line = page.get_by_title('危险线')
        self.prop_line_width = page.get_by_title('线宽')
        self.prop_fill_opacity = page.get_by_title('填充透明度')
        # 原生 <select>
        self.prop_chart_type = page.get_by_title('图表类型')
        self.prop_legend_position = page.get_by_title('图例位置')
        # 主题用 select[title] 精确定位，避开工具栏的「主题切换」按钮
        self.prop_theme = page.locator('select[title="主题"]')
        # 数据绑定按钮 + 对话框
        self.bind_button = page.get_by_role('button', name='配置数据绑定')
        self.bind_dialog = page.get_by_role('dialog')
        self.bind_dialog_save = self.bind_dialog.get_by_role('button', name='保存绑定')
        # 交互事件里的「点击目标 (URL 或消息)」输入框
        self.prop_click_target = page.get_by_title('点击目标 (URL 或消息)')

    # 交互事件下拉（原生 select）
    def event_select(self, title):
        return self.page.get_by_title(title)

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

    # 画布上图表的 echarts canvas
    def widget_canvas(self, index=0):
        return self.canvas_widgets().nth(index).locator('canvas')

    def open_bind_dialog(self):
        self.bind_button.click()
        self.bind_dialog.wait_for(state='visible')

    def close_bind_dialog(self):
        self.bind_dialog.get_by_role('button', name='取消').click()
        self.bind_dialog.wait_for(state='hidden')
