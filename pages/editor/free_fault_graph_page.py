from pages.editor.free_layout_page import FreeLayoutPage


class FreeFaultGraphPage(FreeLayoutPage):
    def __init__(self, page):
        super().__init__(page)
        self.prop_panel = page.locator('.MuiBox-root', has_text='FaultGraphWidget').last
        self.prop_fault_id = page.get_by_label('故障 ID', exact=True)

    # 画布上的组件
    def widget(self, index=0):
        return self.canvas_widgets().nth(index)
