from pages.editor.grid_layout_page import GridLayoutPage


class GridContainerPage(GridLayoutPage):
    """容器组件（栅格布局）—— 带 data-puck-dropzone="...:children" 的嵌套投放区，
    可把其它组件拖进去；自带 列数 / 间距 / 背景 / 边框 / 内边距 / 最小高度 属性。"""

    def __init__(self, page):
        super().__init__(page)
        # 用 input[title=] 精确匹配：get_by_title('列数') 会被 '跨列数' 子串命中
        self.prop_col_span = page.locator('input[title="跨列数"]')
        self.prop_title = page.locator('input[title="标题"]')
        self.prop_columns = page.locator('input[title="列数"]')
        self.prop_gap = page.locator('input[title="间距 (px)"]')
        self.prop_bg_color = page.locator('input[title="背景色"]')
        self.prop_border_color = page.locator('input[title="边框色"]')
        self.prop_padding = page.locator('input[title="内边距"]')
        self.prop_min_height = page.locator('input[title="最小高度 (px)"]')

    def widget_grid(self, index=0):
        return self.canvas_widgets().nth(index).locator('div[style*="grid-template-columns"]').first

    def widget_grid_columns(self, index=0):
        return self.widget_grid(index).evaluate(
            "el => getComputedStyle(el).gridTemplateColumns.split(' ').filter(Boolean).length")

    def nested_dropzone(self, index=0):
        return self.canvas_widgets().nth(index).locator('[data-puck-dropzone$=":children"]')

    def drag_into_container(self, test_id_name, index=0):
        source = self.drawer_item(test_id_name)
        source.scroll_into_view_if_needed()
        dz = self.nested_dropzone(index)
        sb = source.bounding_box(); db = dz.bounding_box()
        self.page.mouse.move(sb['x'] + sb['width'] / 2, sb['y'] + sb['height'] / 2)
        self.page.mouse.down()
        self.page.mouse.move(sb['x'] + 5, sb['y'] + 5, steps=5)
        self.page.wait_for_timeout(100)
        self.page.mouse.move(db['x'] + db['width'] / 2, db['y'] + db['height'] / 2, steps=30)
        self.page.mouse.up()
        self.page.wait_for_timeout(500)
        self._dismiss_breakpoint_dialog()
