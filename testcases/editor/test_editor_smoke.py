import allure
import pytest
from playwright.sync_api import expect

from pages.editor.template_page import TemplateDialog


# 稳定性冒烟：不逐个断属性，只把「容易把前端点崩」的编辑器操作串一遍，
# 每步之后做个快速体检（工具栏还在 / body 不空 / 没有错误边界文案）。
# 真正的「未捕获异常 / 白屏」由 conftest 的 fail_on_page_error 全局兜底。

TEMPLATES = list(TemplateDialog.TEMPLATES)


def _healthy(page):
    """快速体检：编辑器没被点崩。"""
    expect(page.get_by_test_id('dashboard-toolbar')).to_be_visible()
    txt = page.locator('body').inner_text()
    assert len(txt) > 200, f'疑似白屏：body 文本仅 {len(txt)} 字'
    for s in ('Something went wrong', 'Minified React error', '页面出错', '页面崩溃'):
        assert s not in txt, f'出现错误边界文案：{s!r}'


@allure.feature('界面编辑器')
@allure.story('稳定性冒烟')
@allure.title('套用模板「{tpl}」→ 预览往返 → 再套一次，不白屏不报错')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('tpl', TEMPLATES)
def test_template_then_preview_roundtrip(free_layout_page, tpl):
    ed = free_layout_page.editor
    TemplateDialog(ed.page).open().apply(tpl)
    expect(ed.page.get_by_text(TemplateDialog.TEMPLATES[tpl]).first).to_be_visible()

    ed.enter_preview()
    _healthy(ed.page)
    # 断言：模板内容在预览态照常渲染，没丢
    expect(ed.page.get_by_text(TemplateDialog.TEMPLATES[tpl]).first).to_be_visible()

    ed.exit_preview()
    _healthy(ed.page)

    # 同一个模板再套一次（覆盖自己），仍不崩
    TemplateDialog(ed.page).open().apply(tpl)
    _healthy(ed.page)
    expect(ed.page.get_by_text(TemplateDialog.TEMPLATES[tpl]).first).to_be_visible()


@allure.feature('界面编辑器')
@allure.story('稳定性冒烟')
@allure.title('套模板「综合遥测总览大屏」→ 预览 ↔ 编辑 ↔ JSON ↔ 新建，不白屏不报错')
@allure.severity(allure.severity_level.NORMAL)
def test_template_then_view_ops(free_layout_page):
    ed = free_layout_page.editor
    flp = free_layout_page
    TemplateDialog(ed.page).open().apply(TEMPLATES[0])

    ed.enter_preview();       _healthy(ed.page)
    ed.exit_preview();        _healthy(ed.page)
    flp.switch_to_json();     _healthy(ed.page)
    flp.switch_to_ui();       _healthy(ed.page)
    ed.click_new_and_confirm()
    ed.page.wait_for_timeout(800)
    _healthy(ed.page)
