"""占位组件 —— 在画布上占一块空。

⚠️ 以下属性【故意不写用例】，系统这边不生效：
      占位列数    —— 改了画布没有任何变化
      高度 (px)   —— 同上，不生效
   这两个一去掉，占位就只剩通用样式那一组属性能测了。
   等开发修好再补，补的位置就在本文件里。
"""
import allure
from playwright.sync_api import expect

from testcases.editor.common_style_cases import CommonStyleCases


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-占位组件')
@allure.title('添加占位后画布出现组件')
@allure.severity(allure.severity_level.BLOCKER)
def test_spacer_added_to_canvas(free_spacer_page):
    # 画布断言
    expect(free_spacer_page.canvas_widgets()).to_have_count(1)


# ==================== 删除 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-占位组件')
@allure.title('删除占位组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_spacer_delete(free_spacer_page):
    expect(free_spacer_page.canvas_widgets()).to_have_count(1)
    free_spacer_page.delete_widget()
    # 画布断言
    expect(free_spacer_page.canvas_widgets()).to_have_count(0)


# ==================== 通用样式（共用用例集）====================
# 上/下/左/右边距 · 圆角 · 透明度 —— 用例写在 common_style_cases.py，这里只挂上去

class TestSpacerCommonStyle(CommonStyleCases):
    widget_fixture = 'free_spacer_page'
    story = '自由布局-占位组件'
