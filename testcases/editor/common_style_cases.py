import allure
import pytest
from playwright.sync_api import expect

from pages.editor.common_style_props import CommonStyleMixin


class CommonStyleCases:
    """「通用样式」属性（上/下/左/右边距 · 圆角 · 透明度）的共用用例集。

    这一组属性在 10 个组件上完全一样（图表 / 表格 没有），用例只写这一份，
    每个组件的测试文件里继承一次就长在自己的 story 下、独立跑独立报：

        from testcases.editor.common_style_cases import CommonStyleCases

        class TestTextCommonStyle(CommonStyleCases):
            widget_fixture = 'free_text_page'
            story = '自由布局-文本组件'

    要求：该组件的页面对象已经 mixin 了 CommonStyleMixin。
    新增组件时，页面对象加 mixin + 测试文件加这 3 行即可，不用抄用例。
    """

    widget_fixture = None    # 子类必填：组件 fixture 名，如 'free_text_page'
    story = None             # 子类必填：allure story，跟该文件其它用例保持一致

    @pytest.fixture
    def widget(self, request):
        """按名字取该组件的 fixture，并选中画布上的组件（属性面板才会出来）。"""
        wp = request.getfixturevalue(self.widget_fixture)
        wp.click_widget()
        wp.prop_margin_top.wait_for(state='visible')
        return wp

    def _mark(self, title):
        """allure 分类只能在运行时定，因为 story 来自子类。"""
        allure.dynamic.feature('界面编辑器')
        allure.dynamic.story(self.story)
        allure.dynamic.title(f'[通用样式] {title}')
        allure.dynamic.severity(allure.severity_level.NORMAL)

    # ==================== 默认状态 ====================

    def test_common_style_fields_default(self, widget):
        self._mark('6 个字段都在，默认为空，取值范围正确')
        for name, (label, lo, hi, step) in CommonStyleMixin.COMMON_STYLE_FIELDS.items():
            el = widget.common_style_input(name)
            expect(el, f'{label} 应该在属性面板里').to_be_visible()
            expect(el, f'{label} 默认应为空').to_have_value('')
            expect(el).to_have_attribute('min', lo)
            expect(el).to_have_attribute('max', hi)
            expect(el).to_have_attribute('step', step)
        # 画布断言：没设之前不带外边距、不透明、默认圆角
        box = widget.widget_style_box()
        expect(box).to_have_css('margin', CommonStyleMixin.DEFAULT_MARGIN)
        expect(box).to_have_css('border-radius', CommonStyleMixin.DEFAULT_RADIUS)
        expect(box).to_have_css('opacity', CommonStyleMixin.DEFAULT_OPACITY)

    # ==================== 边距 ====================

    def test_common_style_margins_apply(self, widget):
        self._mark('四个边距写入后画布同步')
        widget.set_common_style(margin_top=12, margin_right=24,
                                margin_bottom=16, margin_left=20)
        # 右侧断言
        expect(widget.prop_margin_top).to_have_value('12')
        expect(widget.prop_margin_right).to_have_value('24')
        expect(widget.prop_margin_bottom).to_have_value('16')
        expect(widget.prop_margin_left).to_have_value('20')
        # 画布断言（CSS 简写顺序：上 右 下 左）
        expect(widget.widget_style_box()).to_have_css('margin', '12px 24px 16px 20px')

    # ==================== 圆角 / 透明度 ====================

    def test_common_style_radius_and_opacity_apply(self, widget):
        self._mark('圆角与透明度写入后画布同步')
        widget.set_common_style(radius=9, opacity=0.5)
        # 右侧断言
        expect(widget.prop_radius).to_have_value('9')
        expect(widget.prop_opacity).to_have_value('0.5')
        # 画布断言
        box = widget.widget_style_box()
        expect(box).to_have_css('border-radius', '9px')
        expect(box).to_have_css('opacity', '0.5')
