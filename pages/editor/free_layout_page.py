class FreeLayoutPage:
    COMPONENT_NAMES = [
        '文本', '容器', '占位', '图表', '表格', '仪表盘',
        '状态灯', '指示牌', '输入框', '下拉框', '数值输入', '故障关系图',
    ]

    def __init__(self, page):
        self.page = page
        # 工具按钮
        self.ui_visual_button = page.get_by_role('button', name='UI可视')
        self.json_button = page.get_by_role('button', name='<>JSON')
        self.add_component_button = page.get_by_role('button', name='添加组件')
        # 添加组件菜单
        self.menu = page.get_by_role('menu')
        # 画布
        self.canvas = page.locator('.react-grid-layout')

    # 根据名字获取添加组件菜单中的某一项
    def component_item(self, name):
        return self.page.get_by_role('menuitem', name=name)

    # 获取画布上所有组件
    def canvas_widgets(self):
        return self.canvas.locator('.react-grid-item')

    # 点击画布上第index个组件，点了右侧才出属性面板
    def click_widget(self, index=0):
        self.canvas_widgets().nth(index).click()

    # 先hover让删除按钮出现，再点击删除
    def delete_widget(self, index=0):
        widget = self.canvas_widgets().nth(index)
        widget.hover()
        widget.get_by_test_id('CloseIcon').click()

    # 点击画布空白处，取消选中组件
    def click_canvas_blank(self):
        self.canvas.click(position={'x': 1, 'y': 1})