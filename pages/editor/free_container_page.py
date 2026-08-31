from pages.editor.free_layout_page import FreeLayoutPage


class FreeContainerPage(FreeLayoutPage):
    """容器组件（自由布局）—— 可往里嵌套其它组件的布局盒子，
    自带 CSS grid 列数 / 间距 / 背景 / 边框 / 内边距 / 最小高度 等样式属性。"""

    def __init__(self, page):
        super().__init__(page)
        self.prop_panel = page.locator('.MuiBox-root', has_text='ContainerWidget').last
        self.prop_title = page.get_by_label('标题', exact=True)
        self.prop_columns = page.get_by_label('列数', exact=True)
        self.prop_gap = page.get_by_label('间距 (px)', exact=True)
        self.prop_bg_color = page.get_by_label('背景色', exact=True)
        self.prop_border_color = page.get_by_label('边框色', exact=True)
        self.prop_padding = page.get_by_label('内边距', exact=True)
        self.prop_min_height = page.get_by_label('最小高度 (px)', exact=True)

    # 画布上容器内部的 grid（列数/间距作用在它上面）
    def widget_grid(self, index=0):
        return self.canvas_widgets().nth(index).locator('div[style*="grid-template-columns"]').first

    def widget_grid_columns(self, index=0):
        """容器内部 grid 的列轨道数 —— "列数" 属性生效的结果。"""
        return self.widget_grid(index).evaluate(
            "el => getComputedStyle(el).gridTemplateColumns.split(' ').filter(Boolean).length")

    # 容器外框（背景色/边框色/内边距/最小高度作用在它上面）
    def widget_title_text(self, index=0):
        return self.canvas_widgets().nth(index).locator('span.MuiTypography-caption').first
