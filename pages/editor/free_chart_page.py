from common.canvas_pixels import fingerprint
from pages.editor.free_layout_page import FreeLayoutPage


class FreeChartPage(FreeLayoutPage):
    """图表组件（自由布局）。

    注意图表【没有】通用样式那一组属性（上下左右边距 / 圆角 / 透明度），
    面板里就没有这几个框，所以不 mixin CommonStyleMixin。

    只放实际有用例的定位和操作。双击 / 阈值 / 悬停 / 输入变化 这几个事件不生效，
    用例不写，这里也不留定位，原因见图表的测试文件开头。
    """

    # 三个下拉的选项（顺序即面板里的顺序）
    CHART_TYPES = ['折线', '柱状', '饼图']
    THEMES = ['深色', '浅色']
    LEGEND_POSITIONS = ['底部', '顶部', '左侧']
    # 三组「是 / 否」单选，以及各自的默认档
    SWITCHES = {'显示图例': '是', '显示提示': '是', '数据缩放': '否'}
    # 「定时触发」下拉的选项。注意选中「无」之后下拉【显示为空】，不显示「无」两个字
    # ——「无」对应的是空值，跟没选过一个样。事件类下拉（点击事件等）都是这个规律。
    TIMER_ACTIONS = ['无', '刷新数据']
    NONE_OPTION = '无'          # 这一项选中后下拉显示空
    NONE_DISPLAY = '​'    # 空值时下拉里那个占位的零宽字符
    # 每种图表类型在数据绑定弹窗上的副标题（弹窗字段一样，副标题跟着类型走）
    CHART_TYPE_SUBTITLES = {
        '折线': '折线图（连续时序）',
        '柱状': '柱状图（同单位比较）',
        '饼图': '饼图（分类统计）',
    }
    # 「数据来源」下拉里灰掉那项的判定方式：选项上带 aria-disabled。
    # 具体有几种来源、叫什么，用例里不写死，下拉里有什么就遍历什么。
    # 数据绑定对话框里「统计方式」的选项
    AGGREGATIONS = ['不统计', '计数', '求和', '平均', '最小', '最大']
    # 画布上的状态文案：没绑数据源 / 绑好了
    UNBOUND_HINT = '演示数据（未绑定数据源）'
    BOUND_HINT = '已登记数据源'
    # 点预览时可能出的两种提示
    BIND_NEED_TABLE_HINT = '请先选择数据源、Schema 和数据表'   # 连表都还没选
    BIND_INVALID_HINT = '当前表或字段不适合该图表类型'         # 表选了但横轴/数值字段没选全

    def __init__(self, page):
        super().__init__(page)

        # ==================== 右侧属性面板 ====================
        # 面板顶部是组件名的 heading
        self.prop_panel = page.get_by_role('heading', name='图表', exact=True)
        self.prop_title = page.get_by_label('标题', exact=True)
        # 三个 MUI 下拉（选项是 role=option，用基类的 pick_option 选）
        self.prop_chart_type = page.locator('.MuiFormControl-root', has_text='图表类型').get_by_role('combobox')
        self.prop_theme = page.locator('.MuiFormControl-root', has_text='主题').get_by_role('combobox')
        self.prop_legend_position = page.locator('.MuiFormControl-root', has_text='图例位置').get_by_role('combobox')
        # 四个数字框
        self.prop_warning_line = page.get_by_label('警告线', exact=True)
        self.prop_danger_line = page.get_by_label('危险线', exact=True)
        self.prop_line_width = page.get_by_label('线宽', exact=True)
        self.prop_fill_opacity = page.get_by_label('填充透明度', exact=True)
        # 定时刷新：选了「刷新数据」之后填间隔秒数
        self.prop_timer_action = page.locator('.MuiFormControl-root', has_text='定时触发').get_by_role('combobox')
        self.prop_timer_interval = page.get_by_label('定时间隔 (s)', exact=True)
        # 单击事件（共用用例集 ClickActionCases 要用这两个名字）
        self.prop_click_action = page.locator('.MuiFormControl-root', has_text='点击事件').get_by_role('combobox')
        self.prop_click_target = page.get_by_label('点击目标 (URL 或消息)')

        # ==================== 数据绑定对话框 ====================
        self.bind_button = page.get_by_role('button', name='配置数据绑定')
        self.bind_dialog = page.get_by_role('dialog')
        self.bind_dialog_cancel = self.bind_dialog.get_by_role('button', name='取消')
        self.bind_dialog_preview = self.bind_dialog.get_by_role('button', name='预览真实数据')
        self.bind_dialog_save = self.bind_dialog.get_by_role('button', name='保存绑定')
        # 「数值字段」是一排勾选框，选了表之后才出现
        self.bind_value_fields = self.bind_dialog.locator('input[type="checkbox"]')
        # 点「预览真实数据」之后对话框里出现的结果表格
        self.bind_preview_table = self.bind_dialog.locator('table')
        # 点预览时的两种提示
        self.bind_need_table_hint = self.bind_dialog.get_by_text(self.BIND_NEED_TABLE_HINT, exact=True)
        self.bind_invalid_hint = self.bind_dialog.get_by_text(self.BIND_INVALID_HINT, exact=True)
        # 弹窗副标题那一行「当前图表类型：xxx」
        self.bind_dialog_subtitle = self.bind_dialog.get_by_text('当前图表类型', exact=False)

        # ==================== 画布上的图表 ====================
        self.widget = self.canvas_widgets().first
        # 图表左上角的标题文字
        self.widget_title = self.widget.locator('span.MuiTypography-caption').first
        # 没绑数据源时画布上的状态文案
        self.widget_unbound_chip = self.widget.get_by_text(self.UNBOUND_HINT, exact=True)
        # 绑好之后画布上的状态标签，以及真正出图的那块 echarts 画布
        self.widget_bound_chip = self.widget.get_by_text(self.BOUND_HINT, exact=True)
        self.widget_canvas = self.widget.locator('canvas')

    # ==================== 定位（要带参数的只能写成方法）====================

    def switch_radio(self, group, value):
        """三组「是 / 否」单选里的某一个。group 取 SWITCHES 的键，value 是 '是' / '否'。
        这几组单选没有 label，只能先按分组标题圈出最内层的那个盒子再取。"""
        return (self.page.locator('.MuiBox-root')
                .filter(has_text=group).last
                .get_by_label(value, exact=True))

    def bind_field(self, label):
        """数据绑定对话框里某个下拉。对话框是级联的，选了上一级下一级才出现，
        所以按 label 精确取，不按顺序取。"""
        return (self.bind_dialog.locator('.MuiFormControl-root')
                .filter(has=self.page.locator(f'label:text-is("{label}")'))
                .get_by_role('combobox').first)

    def bind_input(self, label):
        """数据绑定对话框里某个输入框（如「最大数据点数」）。"""
        return (self.bind_dialog.locator('.MuiFormControl-root')
                .filter(has=self.page.locator(f'label:text-is("{label}")'))
                .locator('input').first)

    # ==================== 操作 ====================

    def open_bind_dialog(self):
        """打开「配置数据绑定」对话框。"""
        self.bind_button.click()
        self.bind_dialog.wait_for(state='visible')

    def close_bind_dialog(self):
        """点「取消」关掉数据绑定对话框。"""
        self.bind_dialog_cancel.click()
        self.bind_dialog.wait_for(state='hidden')

    def bind_options(self, label, timeout_ms=8000):
        """点开对话框里某个下拉，返回 (下拉, 选项文案列表)。菜单会停在打开状态，
        调用方要么接着 choose 一项，要么自己 Escape 关掉。"""
        combobox = self.bind_field(label)
        combobox.click()
        listbox = self.page.locator('[role="listbox"]:visible').last
        try:
            listbox.wait_for(state='visible', timeout=timeout_ms)
            listbox.get_by_role('option').first.wait_for(state='visible', timeout=timeout_ms)
        except Exception:
            return combobox, []
        return combobox, listbox.get_by_role('option').all_inner_texts()

    def bind_choose(self, label, name):
        """在对话框里某个下拉选中一项，并等下一级字段刷出来。"""
        current = self.bind_field(label).inner_text().strip()
        if current == name:
            return
        _, names = self.bind_options(label)
        assert name in names, f'「{label}」当前选项里没有 {name!r}：{names}'
        self.page.locator('[role="listbox"]:visible').last \
            .get_by_role('option', name=name, exact=True).click()
        self.page.wait_for_timeout(1500)

    def canvas_fingerprint(self):
        """绑好数据源、真出图之后，采一张画布的像素指纹。
        echarts 画在 canvas 上，DOM 里读不出主题 / 图例位置这些，只能看像素。
        怎么用见 common/canvas_pixels.py。"""
        return fingerprint(self.widget_canvas.first)

    def bind_dialog_field_labels(self):
        """当前弹窗里所有配置字段的名字。切换数据来源后字段会整组换掉，
        用例拿它做前后对比，不用写死每种来源各有哪些字段。"""
        return [t.strip() for t in self.bind_dialog.locator('label').all_inner_texts()]

    def bind_source_options(self):
        """数据来源下拉的所有选项，返回 [(名字, 是不是灰的), ...]，读完就把菜单关掉。"""
        _, names = self.bind_options('数据来源')
        result = [(n, self.page.get_by_role('option', name=n, exact=True)
                   .get_attribute('aria-disabled') == 'true') for n in names]
        self.page.keyboard.press('Escape')
        self.page.wait_for_timeout(400)
        return result

    def hover_chart(self):
        """把鼠标移到图中间。提示框（tooltip）只有悬停时才画出来，要测它就得真 hover。"""
        box = self.widget_canvas.first.bounding_box()
        self.page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
        self.page.wait_for_timeout(800)

    def unhover_chart(self):
        """把鼠标从图上移开，让提示框消失。"""
        box = self.widget_canvas.first.bounding_box()
        self.page.mouse.move(box['x'] - 60, box['y'] - 60)
        self.page.wait_for_timeout(800)

    def bind_pick_table(self):
        """把绑定对话框走到「选完数据表」这一步：数据源 → Schema → 数据表。

        每步都选第一个可用项，不写死具体库表名，换个环境也能跑；Schema 逐个试，
        直到找到底下真有表的那个（实测默认那个 public 是空的）。
        返回一路选中的 {数据源, Schema, 数据表}。
        """
        chosen = {}

        _, sources = self.bind_options('关系型数据源')
        assert sources, '「关系型数据源」下拉里一个可选项都没有，后端没登记数据源？'
        chosen['数据源'] = sources[0]
        self.page.get_by_role('option').first.click()
        self.page.wait_for_timeout(1500)

        _, schemas = self.bind_options('Schema')
        assert schemas, '「Schema」下拉里一个可选项都没有'

        # 当前环境的 public 没有可绑定表，而且这个 MUI 级联框在选中空
        # Schema 后无法再次展开。把常见的空 public 放到最后，优先尝试业务 Schema。
        schemas = [schema for schema in schemas if schema != 'public'] + \
                  [schema for schema in schemas if schema == 'public']

        for index, schema in enumerate(schemas):
            # 第一次读取 Schema 选项时菜单已经打开，直接选；关闭后再次打开在
            # 单 Schema 环境下偶尔拿不到选项。只有后续尝试才重新打开菜单。
            if index == 0:
                self.page.locator('[role="listbox"]:visible').last \
                    .get_by_role('option', name=schema, exact=True).click()
                self.page.wait_for_timeout(1500)
            else:
                self.bind_choose('Schema', schema)
            _, tables = self.bind_options('数据表')
            if tables:
                chosen['Schema'] = schema
                chosen['数据表'] = tables[0]
                self.page.get_by_role('option').first.click()
                self.page.wait_for_timeout(2000)
                return chosen
            self.page.keyboard.press('Escape')
            self.page.wait_for_timeout(400)

        raise AssertionError(f'这些 Schema 底下都没有表：{schemas}')

    def bind_pick_fields(self):
        """接着上一步：选横轴字段 + 把数值字段【全部勾上】（一个不勾保存不生效）。

        为什么全勾而不是勾第一个：这张表里三个数值字段只有一个真有数据，
        另外两个整列都是 0。只勾第一个的话图上就是一条贴着底的直线，
        警告线 / 危险线 / 填充透明度这些改了都看不出效果，等于白测。
        全勾就一定包含有数据的那个。
        返回选中的横轴字段。
        """
        _, axes = self.bind_options('横轴字段')
        assert axes, '「横轴字段」下拉里一个可选项都没有'
        self.page.get_by_role('option').first.click()
        self.page.wait_for_timeout(1200)

        count = self.bind_value_fields.count()
        assert count > 0, '选完表之后应该列出可选的数值字段'
        for i in range(count):
            self.bind_value_fields.nth(i).check()
            self.page.wait_for_timeout(250)
        return axes[0]

    def bind_first_available(self):
        """把数据绑定从头走到尾并保存，等画布真的出图。
        返回一路选中的东西 {数据源, Schema, 数据表, 横轴字段}，用例要断言就用它。
        """
        chosen = self.bind_pick_table()
        chosen['横轴字段'] = self.bind_pick_fields()

        self.bind_dialog_save.click()
        self.bind_dialog.wait_for(state='hidden', timeout=20000)
        self.widget_canvas.first.wait_for(state='visible', timeout=20000)
        return chosen
