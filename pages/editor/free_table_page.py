from pages.editor.free_layout_page import FreeLayoutPage


class FreeTablePage(FreeLayoutPage):
    # 演示表格当前的表头（中文）与列序号（1 起）
    DEMO_HEADERS = ['故障编码', '等级', '卫星', '时间', '状态']
    DEMO_COLUMNS = {'故障编码': 1, '等级': 2, '卫星': 3, '时间': 4, '状态': 5}
    # 演示数据共 24 行 SIM-0001 ~ SIM-0024，画布表格按每页 20 行分页
    DEMO_ROW_COUNT = 24
    DEMO_PAGE_SIZE = 20
    # 每列的筛选框 placeholder
    FILTER_PLACEHOLDERS = ['筛选 故障编码', '筛选 等级', '筛选 卫星', '筛选 时间', '筛选 状态']
    # 交互事件下拉：{字段标签: [可选项文案]}
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
        # 属性面板：面板顶部是组件名 heading（"表格"）
        self.prop_panel = page.get_by_role('heading', name='表格', exact=True)
        # 输入框
        self.prop_title = page.get_by_label('标题', exact=True)
        self.prop_page_size = page.get_by_label('每页行数', exact=True)
        self.prop_max_height = page.get_by_label('最大高度', exact=True)
        self.prop_refresh_interval = page.get_by_label('刷新间隔 (s)', exact=True)
        # 数据绑定按钮 + 对话框（原「数据源 ID / 列定义 JSON」内联字段已移除）
        self.bind_button = page.get_by_role('button', name='配置数据绑定')
        self.bind_dialog = page.get_by_role('dialog')
        self.bind_dialog_save = self.bind_dialog.get_by_role('button', name='保存绑定')

    # ----- 是/否 单选：启用排序 / 启用分页 -----
    def sort_radio(self, value):
        return self.page.locator('.MuiBox-root.css-0', has_text='启用排序').get_by_label(value)

    def pagination_radio(self, value):
        return self.page.locator('.MuiBox-root.css-0', has_text='启用分页').get_by_label(value)

    # 交互事件下拉（MUI Select）
    def event_select(self, label):
        return self.page.locator('.MuiFormControl-root', has_text=label).get_by_role('combobox')

    def pick_option(self, combobox, name):
        combobox.click()
        self.page.get_by_role('option', name=name, exact=True).click()

    # ---------- 画布上的表格 ----------
    def _widget(self, index=0):
        return self.canvas_widgets().nth(index)

    def widget_thead(self, index=0):
        return self._widget(index).locator('thead')

    # 列排序按钮（启用排序时每列一个）
    def widget_sort_labels(self, index=0):
        return self._widget(index).locator('.MuiTableSortLabel-root')

    # 表格滚动容器（最大高度作用在它上面）
    def widget_table_container(self, index=0):
        return self._widget(index).locator('.MuiTableContainer-root')

    # 某个筛选输入框（按 placeholder，如 '筛选 卫星'）
    def widget_filter(self, placeholder, index=0):
        return self._widget(index).get_by_placeholder(placeholder)

    def widget_row_count(self, index=0):
        return self._widget(index).locator('tbody tr').count()

    # 读取某一列 tbody 的全部文本；col 可传列名或 1 起的序号
    def widget_column_values(self, col, index=0):
        n = self.DEMO_COLUMNS[col] if isinstance(col, str) else col
        return self._widget(index).locator(f'tbody tr td:nth-child({n})').all_inner_texts()

    def open_bind_dialog(self):
        self.bind_button.click()
        self.bind_dialog.wait_for(state='visible')

    def close_bind_dialog(self):
        self.bind_dialog.get_by_role('button', name='取消').click()
        self.bind_dialog.wait_for(state='hidden')
