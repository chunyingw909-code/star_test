from pages.editor.common_style_props import CommonStyleMixin
from pages.editor.free_layout_page import FreeLayoutPage


class FreeTextPage(CommonStyleMixin, FreeLayoutPage):
    # 「对齐」的三个选项 -> 画布上包文字那一层的 justify-content
    # （注意不是 p 自己的 text-align，p 的 text-align 三档都是 start）
    ALIGNS = {'左': 'flex-start', '居中': 'center', '右': 'flex-end'}
    # 「图标」的选项 -> 画布上出现的那个图标的 data-testid（'无' 表示不出图标）
    ICONS = {'无': None, '信息': 'InfoIcon', '警告': 'WarningIcon', '告警': 'NotificationsIcon'}
    # 「字重」的选项 -> 画布 font-weight
    WEIGHTS = {'正常': '400', '中等': '500', '粗体': '700'}

    def __init__(self, page):
        super().__init__(page)
        # 属性面板：面板顶部是组件名的 heading（面板里已经不再出现 TextWidget 这种类型名）
        self.prop_panel = page.get_by_role('heading', name='文本', exact=True)
        self.prop_content = page.get_by_label('内容')
        self.prop_font_size = page.get_by_label('字号')
        self.prop_color = page.get_by_label('颜色', exact=True)
        # 「颜色」左边那个色块（原生 <input type="color">）
        self.prop_color_swatch = self.color_swatch('颜色')
        self.prop_unit = page.get_by_label('单位')
        self.prop_weight = page.locator('.MuiFormControl-root', has_text='粗细').get_by_role('combobox')
        self.prop_align = page.locator('.MuiFormControl-root', has_text='对齐').get_by_role('combobox')
        self.prop_icon = page.locator('.MuiFormControl-root', has_text='图标').get_by_role('combobox')
        self.prop_binding_mode = page.locator('.MuiFormControl-root', has_text='绑定模式').get_by_role('combobox')
        # 交互事件（只有「弹窗提示」和「跳转 URL」是稳定可用的，见测试文件开头说明）
        self.prop_click_action = page.locator('.MuiFormControl-root', has_text='点击事件').get_by_role('combobox')
        self.prop_click_target = page.get_by_label('点击目标 (URL 或消息)')

    # ==================== 画布上的元素 ====================

    def widget_text(self, index=0):
        """画布上那段文字（<p>）。字号 / 颜色 / 字重都断在它身上。"""
        return self.canvas_widgets().nth(index).locator('p')

    def widget_text_row(self, index=0):
        """包着文字的那一层 —— 「对齐」作用在它的 justify-content 上。"""
        return self.widget_text(index).locator('xpath=..')

    def widget_icon(self, testid, index=0):
        """画布上那个图标。testid 取自 ICONS，如 'WarningIcon'。"""
        return self.canvas_widgets().nth(index).locator(f'svg[data-testid="{testid}"]')
