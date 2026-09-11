class JsonViewMixin:
    """UI可视 / <>JSON 视图切换（自由布局 GridStack 画布上方那一对按钮）。

    宿主类需提供：
      self.ui_visual_button  —— 「UI可视」按钮
      self.json_button       —— 「<>JSON」按钮
      self.json_editor       —— JSON 模式下的 <textarea>
      self.canvas            —— 当前布局的画布
    """

    def switch_to_json(self):
        self.json_button.first.click()
        self.json_editor.first.wait_for(state='visible')

    def switch_to_ui(self):
        self.ui_visual_button.first.click()
        self.canvas.wait_for(state='visible')

    def active_view(self):
        """'ui' / 'json' —— 以 JSON 编辑区是否可见判断（比按钮 class 稳）。"""
        return 'json' if self.json_editor.first.is_visible() else 'ui'

    def json_text(self):
        return self.json_editor.first.input_value()

    def set_json(self, text):
        """整段替换 JSON 编辑区内容。"""
        self.json_editor.first.fill(text)
