"""故障关系图组件。

这个组件只有一个自己的属性：故障 ID —— 填一个真实故障的 UUID，它拿这个 ID
去调接口，把「故障模式 / 原因 / 影响 / 预案 / 规则」这张关系图画出来。
其余就是通用样式那一组（上/下/左/右边距、圆角、透明度）。

⚠️ 用户实测：填入故障 ID 后画布【有时】显示「加载关系图失败」而不出图，已提开发。
   「填 ID 渲染关系图」这条带 TODO(bug) 照常跑 —— 它挂了就是复现了那个 bug。
"""
import allure
from playwright.sync_api import expect

from testcases.editor.common_style_cases import CommonStyleCases


# ==================== 默认状态 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-故障关系图组件')
@allure.title('添加故障关系图后画布出现组件，未配置时提示"请配置故障ID"')
@allure.severity(allure.severity_level.BLOCKER)
def test_fault_graph_add(free_fault_graph_page):
    fp = free_fault_graph_page
    expect(fp.canvas_widgets()).to_have_count(1)
    # 画布断言：没填 ID 时的占位提示
    expect(fp.widget()).to_contain_text('请配置故障ID')


@allure.feature('界面编辑器')
@allure.story('自由布局-故障关系图组件')
@allure.title('点击组件，属性面板出现，故障 ID 默认空')
@allure.severity(allure.severity_level.CRITICAL)
def test_fault_graph_defaults(free_fault_graph_page):
    fp = free_fault_graph_page
    fp.click_widget()
    # 右侧断言
    expect(fp.prop_panel).to_be_visible()
    expect(fp.prop_fault_id).to_have_value('')


@allure.feature('界面编辑器')
@allure.story('自由布局-故障关系图组件')
@allure.title('点击画布空白区域，属性面板隐藏')
@allure.severity(allure.severity_level.NORMAL)
def test_fault_graph_panel_hides(free_fault_graph_page):
    fp = free_fault_graph_page
    fp.click_widget()
    expect(fp.prop_panel).to_be_visible()
    fp.click_canvas_blank()
    expect(fp.prop_panel).to_be_hidden()


# ==================== 绑定故障 ID ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-故障关系图组件')
@allure.title('填入真实故障 UUID，关系图渲染出来')
@allure.severity(allure.severity_level.CRITICAL)
def test_fault_graph_bind_id_renders(free_fault_graph_page, faults):
    # faults 这个 fixture 走 /api/fault/list 接口拿真实故障列表，取第一条的 UUID。
    # TODO(bug) 用户实测：填入故障 ID 后画布有时显示「加载关系图失败」而不出图，
    #           已提开发。这条用例挂了 == 复现了那个 bug。
    fp = free_fault_graph_page
    fp.click_widget()
    fp.prop_fault_id.fill(faults[0]['id'])
    widget = fp.widget()
    # 画布断言：关系图的几类节点都画出来了，没有报错文案
    for node in ('故障模式', '原因', '影响', '预案', '规则'):
        expect(widget).to_contain_text(node)
    expect(widget).not_to_contain_text('请配置故障ID')
    expect(widget).not_to_contain_text('加载关系图失败')


@allure.feature('界面编辑器')
@allure.story('自由布局-故障关系图组件')
@allure.title('填入不存在的故障 ID，画布提示"加载关系图失败"')
@allure.severity(allure.severity_level.NORMAL)
def test_fault_graph_bind_invalid_id(free_fault_graph_page):
    # 这条跟渲染无关：随便填个非 UUID，接口查不到，画布给出失败提示。
    fp = free_fault_graph_page
    fp.click_widget()
    fp.prop_fault_id.fill('not-a-real-fault-id')
    # 画布断言
    expect(fp.widget()).to_contain_text('加载关系图失败')


@allure.feature('界面编辑器')
@allure.story('自由布局-故障关系图组件')
@allure.title('清空故障 ID，画布回到"请配置故障ID"')
@allure.severity(allure.severity_level.NORMAL)
def test_fault_graph_clear_id(free_fault_graph_page):
    fp = free_fault_graph_page
    fp.click_widget()
    # 先随便填点东西让画布离开占位态
    fp.prop_fault_id.fill('not-a-real-fault-id')
    expect(fp.widget()).not_to_contain_text('请配置故障ID')

    fp.prop_fault_id.fill('')
    # 右侧断言
    expect(fp.prop_fault_id).to_have_value('')
    # 画布断言：回到占位提示
    expect(fp.widget()).to_contain_text('请配置故障ID')


# ==================== 删除 ====================

@allure.feature('界面编辑器')
@allure.story('自由布局-故障关系图组件')
@allure.title('删除故障关系图组件')
@allure.severity(allure.severity_level.CRITICAL)
def test_fault_graph_delete(free_fault_graph_page):
    fp = free_fault_graph_page
    expect(fp.canvas_widgets()).to_have_count(1)
    fp.delete_widget()
    expect(fp.canvas_widgets()).to_have_count(0)


# ==================== 通用样式（共用用例集）====================
# 上/下/左/右边距 · 圆角 · 透明度 —— 用例写在 common_style_cases.py，这里只挂上去

class TestFaultGraphCommonStyle(CommonStyleCases):
    widget_fixture = 'free_fault_graph_page'
    story = '自由布局-故障关系图组件'
