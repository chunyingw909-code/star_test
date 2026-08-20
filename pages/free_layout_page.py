# 页面编辑器-自由布局
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
        # 添加组件后有组件的那个容器 画布
        self.canvas = page.locator('.react-grid-layout')
        # 添加组件后弹出来的菜单
        self.menu = page.get_by_role('menu')

    # 获取画布所有组件 数数量/取某一个
    def canvas_widgets(self):
        return self.canvas.locator('.react-grid-item')

    # 点第几个组件 右侧出现属性
    def click_widget(self, index=0):
        self.canvas_widgets().nth(index).click()

    # 鼠标在组件上 显示删除后点击
    def delete_widget(self, index=0):
        widget = self.canvas_widgets().nth(index)
        widget.hover()
        widget.get_by_test_id('CloseIcon').click()

    # 点空白处 隐藏属性
    def click_canvas_blank(self):
        self.canvas.click(position={'x': 1, 'y': 1})

    def component_item(self, name):
        return self.page.get_by_role('menuitem', name=name)