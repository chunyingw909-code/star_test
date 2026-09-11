from pages.editor.common_style_props import CommonStyleMixin
from pages.editor.free_layout_page import FreeLayoutPage


class FreeSpacerPage(CommonStyleMixin, FreeLayoutPage):
    """占位组件（自由布局）—— 用来在画布上占一块空。

    面板里的「占位列数」和「高度 (px)」都不生效，用例不写，这里也不留定位，
    原因见占位的测试文件开头。实际能测的只剩通用样式那一组，那组的定位在
    CommonStyleMixin 里，所以这个类自己不需要再加任何东西。
    """
