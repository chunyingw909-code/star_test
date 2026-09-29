"""显示 —— 不改内容，只改「怎么看」。

这里管：
  - 编辑 / 预览 切换；预览态里编辑器外壳全消失；预览态只读；往返后内容不丢
  - 三档屏幕分辨率（大屏 / HD / 平板）
  - 主题切换

工具栏级的东西（编辑/预览、分辨率、主题）统一用 free_xxx_page.editor 取，
不在每条用例里 new 一个 EditorPage。用例开头一行 `ed = free_layout_page.editor` 即可。

不归这里的：
  - 组件在画布上的行为 → test_canvas.py
  - 整份布局的新建 / 保存 / 模板 / 发布 / 版本 → test_layout_manage.py
"""
import allure
import pytest
from playwright.sync_api import expect

from pages.editor.editor_page import EditorPage

RES_KEYS = list(EditorPage.RESOLUTIONS)   # ['fullhd', 'hd', 'tablet']


# ==================== 编辑 / 预览 ====================

@allure.feature('界面编辑器')
@allure.story('显示-编辑与预览')
@allure.title('点击"预览"后切到预览态，点"编辑"切回编辑态（toggle 状态互斥）')
@allure.severity(allure.severity_level.CRITICAL)
def test_preview_toggle_button_state(free_layout_page):
    ed = free_layout_page.editor
    # 初始：编辑态
    expect(ed.edit_button).to_have_attribute('aria-pressed', 'true')
    expect(ed.preview_button).to_have_attribute('aria-pressed', 'false')
    # 切预览
    ed.preview_button.click()
    expect(ed.preview_button).to_have_attribute('aria-pressed', 'true')
    expect(ed.edit_button).to_have_attribute('aria-pressed', 'false')
    # 切回编辑
    ed.edit_button.click()
    expect(ed.edit_button).to_have_attribute('aria-pressed', 'true')
    expect(ed.preview_button).to_have_attribute('aria-pressed', 'false')


@allure.feature('界面编辑器')
@allure.story('显示-编辑与预览')
@allure.title('预览态下编辑器结构（画布 / 添加组件 / 保存 / 视图切换）全部隐藏')
@allure.severity(allure.severity_level.CRITICAL)
def test_preview_hides_editor_chrome(free_text_page):
    tp = free_text_page
    # 编辑态：编辑壳这些都在
    expect(tp.canvas).to_be_visible()
    expect(tp.canvas_widgets()).to_have_count(1)
    expect(tp.add_component_button).to_be_visible()
    expect(tp.save_button.first).to_be_visible()
    expect(tp.json_button.first).to_be_visible()
    expect(tp.gridstack_caption).to_be_visible()

    tp.editor.enter_preview()

    # 预览态：编辑壳全没了
    expect(tp.canvas).to_have_count(0)
    expect(tp.canvas_widgets()).to_have_count(0)
    expect(tp.add_component_button).to_have_count(0)
    expect(tp.save_button).to_have_count(0)
    expect(tp.json_button).to_have_count(0)
    expect(tp.gridstack_caption).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('显示-编辑与预览')
@allure.title('编辑态搭好的组件，预览态仍然渲染出来')
@allure.severity(allure.severity_level.CRITICAL)
def test_preview_renders_widget_content(free_text_page):
    tp = free_text_page
    tp.click_widget()
    tp.prop_content.fill('卫星遥测监控大屏')
    expect(tp.canvas_widgets().first).to_contain_text('卫星遥测监控大屏')

    tp.editor.enter_preview()

    # 预览里没有 .react-grid-item 编辑壳，但组件内容照常渲染
    expect(tp.canvas_widgets()).to_have_count(0)
    expect(tp.page.get_by_text('卫星遥测监控大屏')).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('显示-编辑与预览')
@allure.title('预览态下点击组件不会弹出属性面板（只读渲染）')
@allure.severity(allure.severity_level.NORMAL)
def test_preview_is_read_only(free_text_page):
    tp = free_text_page
    tp.click_widget()
    tp.prop_content.fill('只读渲染测试')
    tp.editor.enter_preview()

    # 预览态点组件：属性面板（「内容」输入框）不应出现
    tp.page.get_by_text('只读渲染测试').first.click(force=True)
    tp.page.wait_for_timeout(600)
    expect(tp.prop_content).to_have_count(0)


@allure.feature('界面编辑器')
@allure.story('显示-编辑与预览')
@allure.title('预览往返后回到编辑态，组件与内容都还在')
@allure.severity(allure.severity_level.CRITICAL)
def test_preview_back_to_edit_restores(free_text_page):
    tp = free_text_page
    tp.click_widget()
    tp.prop_content.fill('保留内容测试')

    tp.editor.enter_preview()
    expect(tp.canvas_widgets()).to_have_count(0)

    tp.editor.exit_preview()
    expect(tp.canvas).to_be_visible()
    expect(tp.add_component_button).to_be_visible()
    expect(tp.canvas_widgets()).to_have_count(1)
    expect(tp.canvas_widgets().first).to_contain_text('保留内容测试')


# ==================== 屏幕分辨率 ====================

@allure.feature('界面编辑器')
@allure.story('显示-屏幕分辨率')
@allure.title('默认分辨率是 fullhd')
@allure.severity(allure.severity_level.CRITICAL)
def test_default_resolution_is_fullhd(free_layout_page):
    ed = free_layout_page.editor
    expect(ed.resolution_button('fullhd')).to_have_attribute('aria-pressed', 'true')


@allure.feature('界面编辑器')
@allure.story('显示-屏幕分辨率')
@allure.title('切换分辨率：按钮状态互斥 + 画布宽度对应')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('key', RES_KEYS)
def test_set_resolution(free_layout_page, key):
    ed = free_layout_page.editor
    ed.set_resolution(key)
    expect(ed.resolution_button(key)).to_have_attribute('aria-pressed', 'true')
    for other in RES_KEYS:
        if other != key:
            expect(ed.resolution_button(other)).to_have_attribute('aria-pressed', 'false')
    assert abs(ed.canvas_width() - EditorPage.RESOLUTIONS[key]) <= 2, \
        f'{key} 期望画布宽 {EditorPage.RESOLUTIONS[key]}，实际 {ed.canvas_width()}'


@allure.feature('界面编辑器')
@allure.story('显示-屏幕分辨率')
@allure.title('分辨率在预览往返后保持')
@allure.severity(allure.severity_level.NORMAL)
def test_resolution_persists_across_preview(free_text_page):
    # 用带一个文本组件的画布：enter/exit_preview 依赖编辑壳里的组件挂载/卸载
    ed = free_text_page.editor
    ed.set_resolution('hd')
    ed.enter_preview()
    ed.exit_preview()
    expect(ed.resolution_button('hd')).to_have_attribute('aria-pressed', 'true')
    assert abs(ed.canvas_width() - EditorPage.RESOLUTIONS['hd']) <= 2


# ==================== 主题 ====================
# 主题切换：按钮 title 在「切换至浅色主题」/「切换至深色主题」之间翻。
# 在主页 URL 上，切换【有可见效果】—— MUI 的 Paper 类表面（属性面板、弹窗等）
# 背景色会在深色 rgb(19,47,76) 和浅色 rgb(255,255,255) 之间切。
# ⚠️ 但只要跳到别的路由（/fault、用户管理…），主题立刻被打回去 —— 见文件末尾的
#    TODO 用例。已提 bug。

def _paper_bg(page):
    """随便取一个 MUI Paper 表面的背景色（主题切换在这类元素上体现）。"""
    return page.evaluate("""() => {
        const el = document.querySelector('[class*="MuiPaper-root"]');
        return el ? getComputedStyle(el).backgroundColor : null;
    }""")


@allure.feature('界面编辑器')
@allure.story('显示-主题')
@allure.title('主题切换：按钮 title 往返翻转，且 Paper 表面深浅色跟着变')
@allure.severity(allure.severity_level.CRITICAL)
def test_theme_toggle(free_layout_page):
    ed = free_layout_page.editor
    page = ed.page

    # 默认深色
    assert ed.current_theme() == 'dark'
    dark_bg = _paper_bg(page)

    # 切到浅色
    ed.theme_toggle.click()
    page.wait_for_timeout(600)
    expect(ed.theme_toggle).to_have_attribute('title', '切换至深色主题')  # title 变了
    light_bg = _paper_bg(page)
    assert light_bg != dark_bg, f'切到浅色，Paper 背景应该变：{dark_bg} → {light_bg}'

    # 切回深色
    ed.theme_toggle.click()
    page.wait_for_timeout(600)
    expect(ed.theme_toggle).to_have_attribute('title', '切换至浅色主题')
    assert _paper_bg(page) == dark_bg, '切回深色，Paper 背景应该回到原来的深色'


@allure.feature('界面编辑器')
@allure.story('显示-主题')
@allure.title('主题选到浅色后，跳到别的路由（/fault）仍保持浅色')
@allure.severity(allure.severity_level.NORMAL)
def test_theme_persists_on_route_change(free_layout_page):
    from common.utils import read_yaml
    ed = free_layout_page.editor
    page = ed.page

    dark_bg = _paper_bg(page)
    ed.theme_toggle.click()          # 切成浅色
    page.wait_for_timeout(600)
    light_bg = _paper_bg(page)
    assert light_bg != dark_bg, '前提：切换在当前路由上是有效果的'

    # 真的换到 /fault 路由
    base = read_yaml('config/config.yaml')['url'].rstrip('/')
    page.goto(base + '/zh-CN/fault')
    page.wait_for_load_state('networkidle')

    # 主题是全局状态，进入真实路由后仍应保持浅色。
    assert _paper_bg(page) == light_bg, \
        f'跳路由后应保持浅色，实际 Paper 背景={_paper_bg(page)}'
