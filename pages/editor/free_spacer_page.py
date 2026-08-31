from pages.editor.free_layout_page import FreeLayoutPage


class FreeSpacerPage(FreeLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        self.prop_panel = page.locator('.MuiBox-root', has_text='SpacerWidget').last
        self.prop_columns = page.get_by_label('占位列数', exact=True)
        self.prop_height = page.get_by_label('高度 (px)', exact=True)

    # 画布上真正的占位盒（高度作用在它的 min-height 上）
    def widget_spacer_box(self, index=0):
        return self.canvas_widgets().nth(index).locator('.MuiBox-root').last
