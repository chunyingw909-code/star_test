from pages.editor.free_layout_page import FreeLayoutPage


class FreeTablePage(FreeLayoutPage):
    """表格组件（自由布局）。

    没有通用样式那一组（上下左右边距 / 圆角 / 透明度），所以不 mixin CommonStyleMixin。

    ⚠️ 「保存绑定」后的第一帧：取数请求的排序字段还没重算，卡在 "satellite"
       （占位表头第三列「卫星」的内部字段名），真表没这列 → 后端报
       「排序字段不存在...当前为模拟数据」，画布是 1 行占位。
       只是这一帧的事：画面一重新渲染（点表头 / 切预览再切回 / ...）就正常了。
       自动化跑得快会撞上，手动基本看不到。绑完 unstick_sort() 点一下表头推过去。

    ⚠️ 表格默认（没绑数据源时）画布上是【占位表头】故障编码/等级/卫星/时间/状态 +
       「未绑定数据源」+「暂无数据」+ 0 of 0，不是演示数据。

    ⚠️ 「关闭分页」在小数据集上会显示全部行（不丢），但有 200 行上限，
       更大的表关掉分页也只渲染前 200 行。
    """

    # 没绑数据源时画布上的占位表头
    PLACEHOLDER_HEADERS = ['故障编码', '等级', '卫星', '时间', '状态']
    # 画布上的状态标签
    UNBOUND_HINT = '未绑定数据源'
    BOUND_HINT = '已登记数据源'
    MOCK_HINT = '数据源不可用'
    # 绑定弹窗里的两种「没选全」提示
    BIND_NEED_TABLE_HINT = '请先选择数据源、Schema 和数据表'
    BIND_NEED_COLUMN_HINT = '请至少选择一个展示列'
    # 关闭分页时最多渲染多少行
    UNPAGED_ROW_CAP = 200
    # 单击事件：只有单击的弹窗提示 / 跳转 URL 生效，双击及其余动作不触发（同图表）

    def __init__(self, page):
        super().__init__(page)

        # ==================== 右侧属性面板 ====================
        self.prop_panel = page.get_by_role('heading', name='表格', exact=True)
        self.prop_title = page.get_by_label('标题', exact=True)
        # 数字框（「每页行数」页面上另有个同名隐藏元素，只认 spinbutton 角色）
        self.prop_page_size = page.get_by_role('spinbutton', name='每页行数', exact=True)
        self.prop_max_height = page.get_by_label('最大高度', exact=True)
        self.prop_refresh_interval = page.get_by_label('刷新间隔 (s)', exact=True)
        # 单击事件（共用用例集 ClickActionCases 要用这两个名字）
        self.prop_click_action = page.locator('.MuiFormControl-root', has_text='点击事件').get_by_role('combobox')
        self.prop_click_target = page.get_by_label('点击目标 (URL 或消息)')

        # ==================== 数据绑定弹窗 ====================
        # 表格只支持关系型，弹窗里没有「数据来源」顶层选择器，直接就是
        # 关系型数据源 → Schema → 数据表 三级级联
        self.bind_button = page.get_by_role('button', name='配置数据绑定')
        self.bind_dialog = page.get_by_role('dialog')
        self.bind_dialog_cancel = self.bind_dialog.get_by_role('button', name='取消')
        self.bind_dialog_preview = self.bind_dialog.get_by_role('button', name='预览真实数据')
        self.bind_dialog_save = self.bind_dialog.get_by_role('button', name='保存绑定')
        # 「编辑态允许展示的总体列范围」——一排列勾选框，选完表才出现，至少勾一个才能保存
        self.bind_column_checkboxes = self.bind_dialog.locator('input[type="checkbox"]')
        self.bind_need_table_hint = self.bind_dialog.get_by_text(self.BIND_NEED_TABLE_HINT, exact=True)
        self.bind_need_column_hint = self.bind_dialog.get_by_text(self.BIND_NEED_COLUMN_HINT, exact=True)
        self.bind_preview_table = self.bind_dialog.locator('table')

        # ==================== 画布上的表格 ====================
        self.widget = self.canvas_widgets().first
        self.widget_title = self.widget.locator('span.MuiTypography-caption').first
        self.widget_unbound_chip = self.widget.get_by_text(self.UNBOUND_HINT, exact=True)
        self.widget_bound_chip = self.widget.get_by_text(self.BOUND_HINT, exact=True)
        self.widget_mock_chip = self.widget.get_by_text(self.MOCK_HINT, exact=True)
        # 没有数据时 tbody 里那一行「暂无数据」占位
        self.widget_empty_hint = self.widget.get_by_text('暂无数据', exact=True)
        # 绑定后才出现的两个按钮
        self.clear_binding_button = page.get_by_role('button', name='清除绑定')
        self.column_menu_button = page.get_by_role('button', name='列显示')
        # 表格滚动容器（最大高度作用在它上面）
        self.widget_table_container = self.widget.locator('.MuiTableContainer-root')
        # 分页控件
        self.widget_pager = self.widget.locator('.MuiTablePagination-root')

    # ==================== 定位（要带参数的写成方法）====================

    def sort_radio(self, value):
        """「启用排序」的「是 / 否」单选。value 传 '是' / '否'。"""
        return self.page.locator('.MuiBox-root.css-0', has_text='启用排序').get_by_label(value)

    def pagination_radio(self, value):
        """「启用分页」的「是 / 否」单选。value 传 '是' / '否'。"""
        return self.page.locator('.MuiBox-root.css-0', has_text='启用分页').get_by_label(value)

    def widget_headers(self):
        """画布表头文字列表。绑定前是占位表头，绑定后是真实列名。"""
        return self.widget.locator('thead th').all_inner_texts()

    def widget_sort_labels(self):
        """表头上的排序按钮（启用排序时每列一个）。"""
        return self.widget.locator('.MuiTableSortLabel-root')

    def widget_row_count(self):
        """当前画布上渲染的【真实数据】行数。
        没数据时 tbody 里有一行「暂无数据」占位，那行不算。"""
        rows = self.widget.locator('tbody tr')
        if self.widget_empty_hint.count() > 0:
            return 0
        return rows.count()

    def widget_filter(self, header_name):
        """某一列的筛选框，按表头名，如 widget_filter('id')。"""
        return self.widget.get_by_placeholder(f'筛选 {header_name}')

    def widget_column_values(self, header_name):
        """某一列 tbody 的全部单元格文字。按表头名动态找列序号。"""
        headers = self.widget_headers()
        idx = headers.index(header_name) + 1
        return self.widget.locator(f'tbody tr td:nth-child({idx})').all_inner_texts()

    def bind_field(self, label):
        """绑定弹窗里某个下拉（级联的，按 label 精确取不按顺序取）。"""
        return (self.bind_dialog.locator('.MuiFormControl-root')
                .filter(has=self.page.locator(f'label:text-is("{label}")'))
                .get_by_role('combobox').first)

    def column_menu_checkbox(self, column_name):
        """「列显示」弹出菜单里某一列的勾选框（菜单是 Popover，role=menu）。"""
        return (self.page.get_by_role('menu')
                .locator('label')
                .filter(has=self.page.get_by_text(column_name, exact=True))
                .locator('input[type="checkbox"]'))

    # ==================== 绑定弹窗操作 ====================

    def open_bind_dialog(self):
        self.bind_button.click()
        self.bind_dialog.wait_for(state='visible')
        self.page.wait_for_timeout(800)          # 等弹窗动画 + 数据源下拉加载

    def close_bind_dialog(self):
        self.bind_dialog_cancel.click()
        self.bind_dialog.wait_for(state='hidden')

    def bind_options(self, label, timeout_ms=10000):
        """点开绑定弹窗里某个下拉，返回 (下拉, 选项文案列表)。菜单停在打开状态。"""
        combobox = self.bind_field(label)
        combobox.wait_for(state='visible')
        combobox.click()
        try:
            self.page.get_by_role('option').first.wait_for(state='visible', timeout=timeout_ms)
        except Exception:
            pass
        return combobox, self.page.get_by_role('option').all_inner_texts()

    def bind_choose(self, label, name):
        """在绑定弹窗某个下拉选中一项，并等下一级刷出来。"""
        cb = self.bind_field(label)
        cb.wait_for(state='visible')
        cb.click()
        self.page.get_by_role('option', name=name, exact=True).click()
        self.page.wait_for_timeout(2000)

    def bind_pick_table(self):
        """走到「选完数据表」：把【每个数据源】都试一遍，每个数据源下【每个 Schema】
        都试一遍，用上第一张底下真有表的。不写死任何库表名，两个数据源也好、
        五个也好，一个一个试到有为止。
        返回一路选中的 {数据源, Schema, 数据表}。
        """
        _, sources = self.bind_options('关系型数据源')
        assert sources, '「关系型数据源」下拉里一个可选项都没有，后端没登记数据源？'
        self.page.keyboard.press('Escape')
        self.page.wait_for_timeout(400)

        for source in sources:
            self.bind_choose('关系型数据源', source)
            self.bind_field('Schema').wait_for(state='visible', timeout=10000)

            _, schemas = self.bind_options('Schema')
            self.page.keyboard.press('Escape')
            self.page.wait_for_timeout(400)
            if not schemas:
                continue

            for schema in schemas:
                self.bind_choose('Schema', schema)
                _, tables = self.bind_options('数据表')
                if tables:
                    self.page.get_by_role('option').first.click()
                    self.page.wait_for_timeout(2000)
                    return {'数据源': source, 'Schema': schema, '数据表': tables[0]}
                self.page.keyboard.press('Escape')
                self.page.wait_for_timeout(400)

        raise AssertionError(f'这些数据源 {sources} 底下的所有 Schema 都没有表')

    def check_all_bind_columns(self):
        """把「允许展示的列范围」全勾上（一个不勾保存不了）。返回勾了几个。"""
        n = self.bind_column_checkboxes.count()
        assert n > 0, '选完表之后应该列出可勾的列'
        for i in range(n):
            self.bind_column_checkboxes.nth(i).check()
            self.page.wait_for_timeout(120)
        return n

    def bind_first_available(self):
        """从头走到尾并保存：选表 → 全勾列 → 保存 → 等弹窗关掉。
        返回 bind_pick_table 的结果。
        注意：保存后画布因为硬编码排序 bug 会先落到「模拟数据」，
        要真实数据得再 unstick_sort() 一下。"""
        chosen = self.bind_pick_table()
        self.check_all_bind_columns()
        self.bind_dialog_save.click()
        self.bind_dialog.wait_for(state='hidden', timeout=20000)
        self.page.wait_for_timeout(2000)
        return chosen

    # ==================== 画布操作 ====================

    def unstick_sort(self):
        """点第一列的排序表头，把「保存绑定后第一帧」（排序字段还卡在 satellite）
        推过去，让真实数据出来。点完等画布出现「已登记数据源」。"""
        self.widget_sort_labels().first.click()
        self.widget_bound_chip.wait_for(state='visible', timeout=15000)
        self.page.wait_for_timeout(1000)

    def sort_by(self, header_name):
        """点某一列的排序表头。"""
        headers = self.widget_headers()
        idx = headers.index(header_name)
        self.widget_sort_labels().nth(idx).click()
        self.page.wait_for_timeout(1500)

    def filter_column(self, header_name, text):
        """在某列的筛选框里输入内容并等结果稳定。"""
        self.widget_filter(header_name).fill(text)
        self.page.wait_for_timeout(1500)

    def total_rows(self):
        """从分页控件的「1–20 of N」里解析出总行数 N。"""
        import re
        text = self.widget_pager.inner_text()
        m = re.search(r'of\s+([\d,]+)', text)
        assert m, f'分页控件文字里没找到「of N」：{text!r}'
        return int(m.group(1).replace(',', ''))

    def open_column_menu(self):
        self.column_menu_button.click()
        self.page.get_by_role('menu').wait_for(state='visible')

    def toggle_column(self, column_name):
        """在「列显示」菜单里勾 / 取消某一列，然后关掉菜单。"""
        self.column_menu_checkbox(column_name).click()
        self.page.wait_for_timeout(1000)
        self.page.keyboard.press('Escape')
        self.page.wait_for_timeout(500)

    def clear_binding(self):
        """点「清除绑定」，画布恢复未绑定默认态。"""
        self.clear_binding_button.click()
        self.widget_unbound_chip.wait_for(state='visible', timeout=10000)
        self.page.wait_for_timeout(500)
