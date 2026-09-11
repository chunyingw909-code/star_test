import allure
import pytest
from playwright.sync_api import expect



class ClickActionCases:
    """「点击事件」的共用用例集。

    文本 / 图表 / 表格 三个组件都有这组属性，行为完全一样，所以只写一份，
    组件的测试文件里继承一次就长在自己的 story 下：

        from testcases.editor.click_action_cases import ClickActionCases

        class TestChartClickAction(ClickActionCases):
            widget_fixture = 'free_chart_page'
            story = '自由布局-图表组件'
            marker_prop = 'prop_title'

    要求组件的页面对象有：prop_click_action（点击事件下拉）、
    prop_click_target（点击目标输入框），以及 marker_prop 指的那个属性。

    ⚠️ 只覆盖【单击】。属性面板里还有 双击事件 / 阈值触发 / 悬停事件 / 输入变化
       这几个，实测都不触发（双击只是被当成两次单击，弹的还是单击配的那条消息），
       系统没做完，不写。单击的动作里也只有【弹窗提示】和【跳转 URL】可用，
       其余（刷新数据 / 显示弹窗 / 组件联动）不稳定，同样不写。

    统一规律：编辑态点组件【不触发】（编辑态点是为了选中它），预览态点【才触发】。
    """

    widget_fixture = None    # 子类必填：组件 fixture 名
    story = None             # 子类必填：allure story
    marker_prop = None       # 子类必填：拿哪个属性给组件写唯一文案，好在预览态认出它

    @pytest.fixture
    def widget(self, request):
        """取到组件页面对象并选中画布上的组件（属性面板才会出来）。"""
        wp = request.getfixturevalue(self.widget_fixture)
        wp.click_widget()
        wp.prop_click_action.wait_for(state='visible')
        return wp

    def _mark(self, title):
        """allure 分类只能在运行时定，因为 story 来自子类。"""
        allure.dynamic.feature('界面编辑器')
        allure.dynamic.story(self.story)
        allure.dynamic.title(f'[点击事件] {title}')
        allure.dynamic.severity(allure.severity_level.CRITICAL)

    def _tag_widget(self, widget, text):
        """给组件写一段唯一文案，预览态靠它把组件认出来。"""
        getattr(widget, self.marker_prop).fill(text)
        widget.page.wait_for_timeout(400)

    # ==================== 弹窗提示 ====================

    def test_click_action_alert(self, widget):
        self._mark('弹窗提示：编辑态点不弹，预览态点才弹出配置的文案')
        page = widget.page
        ed = widget.editor
        tag, message = 'CLICK-ALERT-TAG', 'HELLO-FROM-CLICK'

        self._tag_widget(widget, tag)
        widget.pick_option(widget.prop_click_action, '弹窗提示')
        widget.prop_click_target.fill(message)
        # 右侧断言
        expect(widget.prop_click_action).to_have_text('弹窗提示')
        expect(widget.prop_click_target).to_have_value(message)

        popups = []
        page.on('dialog', lambda d: (popups.append((d.type, d.message)), d.accept()))

        # 编辑态：点组件只是选中它，不该触发
        widget.canvas_widgets().first.click(force=True)
        page.wait_for_timeout(1200)
        assert popups == [], f'编辑态点组件不该弹窗，实际弹了 {popups}'

        # 预览态：点组件才触发
        ed.enter_preview()
        page.get_by_text(tag).first.click(force=True)
        page.wait_for_timeout(1500)
        assert popups, '预览态点组件应弹出提示，实际一个都没有'
        kind, text = popups[0]
        assert kind == 'alert', f'应是浏览器原生提示，实际是 {kind}'
        assert text == message, f'弹窗内容应是配置的文案，实际是 {text!r}'

    # ==================== 跳转 URL ====================

    def test_click_action_open_url(self, widget):
        self._mark('跳转 URL：编辑态点不跳，预览态点才新开标签页')
        page = widget.page
        ed = widget.editor
        tag, target = 'CLICK-URL-TAG', 'https://example.com/abc'

        self._tag_widget(widget, tag)
        widget.pick_option(widget.prop_click_action, '跳转 URL')
        widget.prop_click_target.fill(target)
        # 右侧断言
        expect(widget.prop_click_action).to_have_text('跳转 URL')
        expect(widget.prop_click_target).to_have_value(target)

        opened = []
        page.context.on('page', lambda pg: opened.append(pg))

        # 编辑态：不跳、不开新标签
        url_before = page.url
        widget.canvas_widgets().first.click(force=True)
        page.wait_for_timeout(1200)
        assert page.url == url_before, f'编辑态点组件不该跳转，URL 变成了 {page.url}'
        assert opened == [], f'编辑态不该开新标签页，实际开了 {[pg.url for pg in opened]}'

        # 预览态：新开一个标签页，当前页不动
        ed.enter_preview()
        url_before = page.url
        page.get_by_text(tag).first.click(force=True)
        page.wait_for_timeout(2000)
        assert page.url == url_before, f'当前页不该跳走，实际变成 {page.url}'
        assert len(opened) == 1, f'应新开 1 个标签页，实际 {len(opened)} 个'
        assert opened[0].url.startswith(target), \
            f'新标签页地址应是配置的 {target}，实际是 {opened[0].url}'
        opened[0].close()

    # ==================== 没配点击事件 ====================

    def test_click_action_default_none(self, widget):
        self._mark('默认没配点击事件，预览态点组件没有任何反应')
        page = widget.page
        ed = widget.editor
        tag = 'NO-ACTION-TAG'

        self._tag_widget(widget, tag)
        # 右侧断言：没配动作时，点击目标也是空的
        expect(widget.prop_click_target).to_have_value('')

        popups, opened = [], []
        page.on('dialog', lambda d: (popups.append(d.message), d.accept()))
        page.context.on('page', lambda pg: opened.append(pg))

        ed.enter_preview()
        url_before = page.url
        page.get_by_text(tag).first.click(force=True)
        page.wait_for_timeout(1500)

        assert popups == [], f'没配点击事件不该弹窗，实际 {popups}'
        assert opened == [], f'没配点击事件不该开新标签页，实际 {[pg.url for pg in opened]}'
        assert page.url == url_before, f'没配点击事件不该跳转，实际 {page.url}'
