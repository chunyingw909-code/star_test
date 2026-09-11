from pages.editor.common_style_props import CommonStyleMixin
from pages.editor.free_layout_page import FreeLayoutPage


class FreeStatusPage(CommonStyleMixin, FreeLayoutPage):
    """状态灯组件（自由布局）。三个工业控件里，这个是真能反映数据的。

    能测的：标签、四种状态颜色、尺寸、显示标签开关、告警闪烁开关。

    ⚠️ 不测的：
       状态文字 —— 映射是坏的（填"警告"画布反而显示"危险"），别改它，
                  默认停在"正常"就行
       卫星 ID、字段路径 —— 绑遥测数据用的，现在连不上真实数据
    """

    def __init__(self, page):
        super().__init__(page)
        self.prop_panel = page.get_by_role('heading', name='状态灯', exact=True)
        self.prop_label = page.get_by_label('标签', exact=True)
        self.prop_normal_color = page.get_by_label('正常颜色', exact=True)
        self.prop_warning_color = page.get_by_label('警告颜色', exact=True)
        self.prop_danger_color = page.get_by_label('危险颜色', exact=True)
        self.prop_offline_color = page.get_by_label('离线颜色', exact=True)
        self.prop_size = page.get_by_label('尺寸 (px)', exact=True)
        # 每个颜色都是「色块 + 十六进制文本框」一对，色块见基类 color_swatch 说明
        self.prop_normal_color_swatch = self.color_swatch('正常颜色')

        # 画布上的状态灯
        self.widget = self.canvas_widgets().first
        # 标签文字
        self.widget_label = self.widget.locator('span.MuiTypography-caption').first

    # ---------- 是 / 否 单选 ----------
    def show_label_radio(self, value):
        return self.page.locator('.MuiBox-root.css-0', has_text='显示标签').get_by_label(value)

    def blink_radio(self, value):
        return self.page.locator('.MuiBox-root.css-0', has_text='告警闪烁').get_by_label(value)

    # 灯珠：组件里第一个「圆形 + 有背景色」的 div（删除按钮是 button，会被 div 过滤掉）。
    # class 是 emotion 哈希名不稳定，按计算样式在组件内部找。
    _FIND_LAMP = """el => {
        for (const n of el.querySelectorAll('div')) {
            const cs = getComputedStyle(n);
            if (!cs.borderRadius.includes('50%')) continue;
            if (cs.backgroundColor === 'rgba(0, 0, 0, 0)') continue;
            const r = n.getBoundingClientRect();
            return { bg: cs.backgroundColor, w: Math.round(r.width), h: Math.round(r.height) };
        }
        return null;
    }"""

    def _lamp(self):
        info = self.widget.evaluate(self._FIND_LAMP)
        assert info, '组件里没找到灯珠（圆形有色的 div）'
        return info

    def lamp_size(self):
        """灯珠渲染宽高 (w, h)。尺寸属性生效的结果。"""
        info = self._lamp()
        return (info['w'], info['h'])
