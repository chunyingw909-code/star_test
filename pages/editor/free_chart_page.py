from pages.editor.free_layout_page import FreeLayoutPage


class FreeChartPage(FreeLayoutPage):
    # 图表类型 / 主题 / 图例位置 下拉的选项文案
    CHART_TYPES = ['折线', '柱状', '饼图']
    THEMES = ['深色', '浅色']
    LEGEND_POSITIONS = ['底部', '顶部', '左侧']
    # 交互事件下拉：{面板里的字段标签: [可选项文案]}
    EVENT_SELECTS = {
        '点击事件': ['无', '弹窗提示', '跳转 URL', '刷新数据', '显示弹窗', '组件联动'],
        '双击事件': ['无', '弹窗提示', '跳转 URL'],
        '阈值触发': ['无', '弹窗提示', '刷新数据'],
        '悬停事件': ['无', '弹窗提示'],
        '输入变化': ['无', '刷新数据'],
        '定时触发': ['无', '刷新数据'],
    }

    def __init__(self, page):
        super().__init__(page)
        # 属性面板：自由布局下面板顶部是组件名的 heading（"图表"）
        self.prop_panel = page.get_by_role('heading', name='图表', exact=True)
        # 输入框
        self.prop_title = page.get_by_label('标题', exact=True)
        self.prop_warning_line = page.get_by_label('警告线', exact=True)
        self.prop_danger_line = page.get_by_label('危险线', exact=True)
        self.prop_line_width = page.get_by_label('线宽', exact=True)
        self.prop_fill_opacity = page.get_by_label('填充透明度', exact=True)
        # MUI 下拉（点开后选项是 role=option）
        self.prop_chart_type = page.locator('.MuiFormControl-root', has_text='图表类型').get_by_role('combobox')
        self.prop_theme = page.locator('.MuiFormControl-root', has_text='主题').get_by_role('combobox')
        self.prop_legend_position = page.locator('.MuiFormControl-root', has_text='图例位置').get_by_role('combobox')
        # 数据绑定：内联字段没了，改成按钮弹对话框
        self.bind_button = page.get_by_role('button', name='配置数据绑定')
        self.bind_dialog = page.get_by_role('dialog')
        self.bind_dialog_save = self.bind_dialog.get_by_role('button', name='保存绑定')

    # 交互事件下拉（MUI Select）
    def event_select(self, label):
        return self.page.locator('.MuiFormControl-root', has_text=label).get_by_role('combobox')

    # ----- 是/否 单选：显示图例 / 显示提示 / 数据缩放 -----
    def legend_radio(self, value):
        return self.page.locator('.MuiBox-root.css-0', has_text='显示图例').get_by_label(value)

    def tooltip_radio(self, value):
        return self.page.locator('.MuiBox-root.css-0', has_text='显示提示').get_by_label(value)

    def zoom_radio(self, value):
        return self.page.locator('.MuiBox-root.css-0', has_text='数据缩放').get_by_label(value)

    # 点开某个 MUI 下拉并选中一项
    def pick_option(self, combobox, name):
        combobox.click()
        self.page.get_by_role('option', name=name, exact=True).click()

    # 画布上图表的 echarts canvas
    def widget_canvas(self, index=0):
        return self.canvas_widgets().nth(index).locator('canvas')

    # 打开 / 关闭「配置数据绑定」对话框
    def open_bind_dialog(self):
        self.bind_button.click()
        self.bind_dialog.wait_for(state='visible')

    def close_bind_dialog(self):
        self.bind_dialog.get_by_role('button', name='取消').click()
        self.bind_dialog.wait_for(state='hidden')
