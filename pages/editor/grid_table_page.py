from pages.editor.grid_layout_page import GridLayoutPage


class GridTablePage(GridLayoutPage):
    # 演示表格当前的表头（中文）与列序号（1 起）
    DEMO_HEADERS = ['故障编码', '等级', '卫星', '时间', '状态']
    DEMO_COLUMNS = {'故障编码': 1, '等级': 2, '卫星': 3, '时间': 4, '状态': 5}
    DEMO_ROW_COUNT = 24
    FILTER_PLACEHOLDERS = ['筛选 故障编码', '筛选 等级', '筛选 卫星', '筛选 时间', '筛选 状态']
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
        self.prop_heading = page.get_by_role('heading', name='表格', exact=True)
        # 输入框（grid 用 title 定位）。跨列数已从表格属性面板移除。
        self.prop_title = page.get_by_title('标题')
        self.prop_page_size = page.get_by_title('每页行数')
        self.prop_max_height = page.get_by_title('最大高度')
        self.prop_refresh_interval = page.get_by_title('刷新间隔 (s)')
        self.bind_button = page.get_by_role('button', name='配置数据绑定')
        self.bind_dialog = page.get_by_role('dialog')
        self.bind_dialog_save = self.bind_dialog.get_by_role('button', name='保存绑定')
        # 交互事件里的「点击目标 (URL 或消息)」输入框
        self.prop_click_target = page.get_by_title('点击目标 (URL 或消息)')

    # ---------- 单选（grid：原生 input 被样式层遮挡，点外层 label；断言用 input） ----------
    def _radio(self, name, value):
        bool_val = 'true' if value == '是' else 'false'
        return self.page.locator(f'//input[@name="{name}" and @value=\'{{"value":{bool_val}}}\']')

    def _radio_label(self, name, value):
        return self._radio(name, value).locator('xpath=..')

    def sort_radio(self, value):
        return self._radio('enableSorting', value)

    def sort_label(self, value):
        return self._radio_label('enableSorting', value)

    def pagination_radio(self, value):
        return self._radio('enablePagination', value)

    def pagination_label(self, value):
        return self._radio_label('enablePagination', value)

    # 交互事件下拉（原生 select）
    def event_select(self, title):
        return self.page.get_by_title(title)

    # ---------- 画布上的表格 ----------
    def _widget(self, index=0):
        return self.canvas_widgets().nth(index)

    def widget_thead(self, index=0):
        return self._widget(index).locator('thead')

    def widget_sort_labels(self, index=0):
        return self._widget(index).locator('.MuiTableSortLabel-root')

    # 点击第 col_idx 列的排序按钮。
    # grid 编辑态画布很窄，排序按钮常在视口外，普通 .click() 会超时。
    # 排序按钮是 role=button、tabindex=0，用 focus + 空格键激活，不受视口位置限制。
    def click_sort(self, col_idx, index=0):
        label = self.widget_sort_labels(index).nth(col_idx)
        label.focus()
        self.page.keyboard.press(' ')

    def widget_table_container(self, index=0):
        return self._widget(index).locator('.MuiTableContainer-root')

    def widget_filter(self, placeholder, index=0):
        return self._widget(index).get_by_placeholder(placeholder)

    def widget_row_count(self, index=0):
        return self._widget(index).locator('tbody tr').count()

    def widget_column_values(self, col, index=0):
        n = self.DEMO_COLUMNS[col] if isinstance(col, str) else col
        return self._widget(index).locator(f'tbody tr td:nth-child({n})').all_inner_texts()

    def open_bind_dialog(self):
        self.bind_button.click()
        self.bind_dialog.wait_for(state='visible')

    def close_bind_dialog(self):
        self.bind_dialog.get_by_role('button', name='取消').click()
        self.bind_dialog.wait_for(state='hidden')
