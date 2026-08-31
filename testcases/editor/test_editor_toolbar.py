import allure
from playwright.sync_api import expect

from pages.editor.editor_page import EditorPage
from pages.editor.template_page import TemplateDialog
from pages.editor.flow_page import FlowEditor


# ==================== 右抽屉：编辑管理 / 版本管理 ====================

@allure.feature('界面编辑器')
@allure.story('工具栏入口')
@allure.title('右抽屉有「编辑管理」「版本管理」两个 tab，默认在编辑管理')
@allure.severity(allure.severity_level.NORMAL)
def test_edit_manage_and_version_tabs(grid_layout_page):
    ed = EditorPage(grid_layout_page.page)
    expect(ed.edit_manage_tab).to_be_visible()
    expect(ed.version_manage_tab).to_be_visible()
    expect(ed.edit_manage_tab).to_have_attribute('aria-selected', 'true')

    ed.version_manage_tab.click()
    expect(ed.version_manage_tab).to_have_attribute('aria-selected', 'true')
    expect(ed.page.get_by_role('button', name='发布新版本')).to_be_visible()
    expect(ed.page.get_by_role('button', name='回滚编辑')).to_be_visible()

    ed.edit_manage_tab.click()
    expect(ed.page_props_marker).to_be_visible()   # 切回 Page 属性


# ==================== 模板：保存当前为模板 ====================

@allure.feature('界面编辑器')
@allure.story('工具栏入口')
@allure.title('模板弹框有「保存当前为模板」按钮')
@allure.severity(allure.severity_level.NORMAL)
def test_template_save_current_button(free_layout_page):
    td = TemplateDialog(free_layout_page.page).open()
    expect(td.save_current_button).to_be_visible()
    td.save_current_button.click()          # 现状：空画布下点它没有可见反馈
    expect(td.dialog).to_be_visible()       # 至少不崩、弹框还在
    td.cancel()


# ==================== 发布 ====================

@allure.feature('界面编辑器')
@allure.story('工具栏入口')
@allure.title('点「发布」弹出「发布看板」，列出开发/预发布/生产三个环境')
@allure.severity(allure.severity_level.CRITICAL)
def test_publish_dialog(free_layout_page):
    ed = EditorPage(free_layout_page.page)
    ed.publish_button.click()
    expect(ed.publish_dialog).to_be_visible()
    for env in ['开发环境', '预发布', '生产环境']:
        expect(ed.publish_dialog).to_contain_text(env)
    ed.publish_dialog.get_by_role('button', name='关闭').click()
    expect(ed.publish_dialog).to_have_count(0)


# ==================== 流程（可视化流程编排）====================

@allure.feature('界面编辑器')
@allure.story('工具栏入口')
@allure.title('点「流程」打开可视化流程编排，事件/条件/动作三类节点面板都在')
@allure.severity(allure.severity_level.CRITICAL)
def test_flow_editor_opens(free_layout_page):
    fe = FlowEditor(free_layout_page.page).open()
    expect(fe.title).to_be_visible()
    expect(fe.flow).to_be_visible()
    for group, items in FlowEditor.NODE_TYPES.items():
        expect(fe.page.get_by_text(group, exact=True).first).to_be_visible()
        for it in items:
            expect(fe.palette_item(it).first).to_be_visible()
    fe.save_and_close()


@allure.feature('界面编辑器')
@allure.story('工具栏入口')
@allure.title('流程里点左侧节点类型可往画布加节点')
@allure.severity(allure.severity_level.CRITICAL)
def test_flow_add_nodes(free_layout_page):
    fe = FlowEditor(free_layout_page.page).open()
    n0 = fe.nodes().count()
    fe.add_node('Click')
    fe.add_node('Alert')
    expect(fe.nodes()).to_have_count(n0 + 2)
    fe.save_and_close()


@allure.feature('界面编辑器')
@allure.story('工具栏入口')
@allure.title('[现状] 流程节点点击（单击/双击）弹不出配置面板')
@allure.severity(allure.severity_level.NORMAL)
def test_flow_node_not_configurable(free_layout_page):
    # ⚠️ 现状记录：节点点了没有配置面板/抽屉/右键菜单，无法给节点绑定
    # 具体组件、设置 Alert 文案 / 阈值等 → 流程画出来也不产生行为。功能未完成。
    # TODO(bug) 期望：点节点应弹出该节点类型的配置项。
    fe = FlowEditor(free_layout_page.page).open()
    fe.add_node('Alert')
    node = fe.nodes().last
    before = fe.page.locator('input:visible, textarea:visible').count()
    node.click()
    fe.page.wait_for_timeout(400)
    node.dblclick()
    fe.page.wait_for_timeout(400)
    after = fe.page.locator('input:visible, textarea:visible').count()
    assert after == before, f'现状应无配置项出现，before={before} after={after}'
    fe.save_and_close()
