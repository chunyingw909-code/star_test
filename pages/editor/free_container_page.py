from pages.editor.common_style_props import CommonStyleMixin
from pages.editor.free_layout_page import FreeLayoutPage


class FreeContainerPage(CommonStyleMixin, FreeLayoutPage):
    """容器组件（自由布局）—— 能往里嵌套其它组件的盒子。

    只放实际有用例的定位和操作。列数 / 间距 / 最小高度 / children 这几个属性
    系统这边不生效，用例不写，所以这里也不留定位，原因见容器的测试文件开头。
    """

    # 「内边距」填的是 MUI 间距单位，不是像素：填 1 画布上是 8px，默认 8 就是 64px
    PADDING_UNIT_PX = 8

    def __init__(self, page):
        super().__init__(page)

        # ==================== 右侧属性面板 ====================
        # 面板顶部是组件名的 heading
        self.prop_panel = page.get_by_role('heading', name='容器', exact=True)
        self.prop_title = page.get_by_label('标题', exact=True)
        # 颜色是「色块 + 十六进制文本框」一对，色块见基类的 color_swatch 说明
        self.prop_bg_color = page.get_by_label('背景色', exact=True)
        self.prop_bg_color_swatch = self.color_swatch('背景色')
        self.prop_border_color = page.get_by_label('边框色', exact=True)
        self.prop_border_color_swatch = self.color_swatch('边框色')
        self.prop_padding = page.get_by_label('内边距', exact=True)

        # 选中容器【内部】的子组件时，右侧面板的两个标志：
        # 标题变成「文本（容器内）」这种，下面还有一行位置说明
        self.child_position_hint = page.get_by_text('容器内位置', exact=False)

        # ==================== 画布上的容器 ====================
        # 容器外壳（画布上那个可拖拽的格子）
        self.widget = self.canvas_widgets().first
        # 容器内框 —— 背景色 / 边框色 / 内边距 都作用在这一层
        self.widget_body = self.widget.locator('div.MuiBox-root').nth(1)
        # 容器左上角那行标题文字
        self.widget_title = self.widget.locator('span.MuiTypography-caption').first
        # 容器内部放子组件的槽位（一个 CSS grid）
        self.widget_slot = self.widget.locator('div[style*="grid-template-columns"]').first
        # 槽位里的子组件，一个子组件占一个直接子元素
        self.children = self.widget_slot.locator('> div')
        # 删除按钮：容器自己的 / 容器内子组件的，类名不同，别混
        self.delete_button = self.widget.locator('button.gridstack-remove')
        self.child_delete_button = self.widget.locator('button.gridstack-remove-child')

    # ==================== 定位（要带参数的只能写成方法）====================

    def child_panel_title(self, widget_name):
        """选中容器内子组件时，右侧面板顶部的标题，形如「文本（容器内）」。"""
        return self.page.get_by_role('heading', name=f'{widget_name}（容器内）', exact=True)

    # ==================== 操作 ====================

    def add_child(self, name):
        """往容器里加一个组件。
        先选中容器再点「添加组件」，新组件就落进容器内部而不是画布上。"""
        self.click_widget()
        self.add_component_button.click()
        self.component_item(name).click()
        self.page.wait_for_timeout(800)

    def select_child(self, index=0):
        """点选容器内第 index 个子组件，右侧切到它的属性面板。"""
        self.children.nth(index).click(force=True)
        self.page.wait_for_timeout(600)

    def delete_child(self, index=0):
        """删掉容器内第 index 个子组件（删除按钮要 hover 才出来）。"""
        self.children.nth(index).hover()
        self.child_delete_button.nth(index).click()
        self.page.wait_for_timeout(800)

    def delete_container(self):
        """删掉容器本身。
        不能用基类的 delete_widget：那个按 CloseIcon 定位，容器里的子组件也有
        CloseIcon，会一次命中多个，所以这里按容器自己的删除按钮类名来。"""
        self.widget.hover()
        self.delete_button.click()
        self.page.wait_for_timeout(800)
