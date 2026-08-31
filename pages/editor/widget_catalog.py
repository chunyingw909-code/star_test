"""内置组件清单（唯一数据源）。

同一份 12 个组件，被三处引用并各自校验：
- 自由布局「添加组件」菜单
- 栅格布局左侧组件库（按分类）
- Plugin Manager 表格（显示名 / Type / 分类）

顺序即自由布局菜单 / Plugin Manager 表格里的顺序。
"""

WIDGETS = [
    {'label': '文本',      'type': 'TextWidget',       'category': '文本'},
    {'label': '容器',      'type': 'ContainerWidget',  'category': '布局'},
    {'label': '占位',      'type': 'SpacerWidget',     'category': '布局'},
    {'label': '图表',      'type': 'ChartWidget',      'category': '图表'},
    {'label': '表格',      'type': 'TableWidget',      'category': '表格'},
    {'label': '仪表盘',    'type': 'GaugeWidget',      'category': '工业监控'},
    {'label': '状态灯',    'type': 'StatusIndicator',  'category': '工业监控'},
    {'label': '指示牌',    'type': 'IndicatorCard',    'category': '工业监控'},
    {'label': '输入框',    'type': 'InputWidget',      'category': '表单'},
    {'label': '下拉框',    'type': 'SelectWidget',     'category': '表单'},
    {'label': '数值输入',  'type': 'NumberWidget',     'category': '表单'},
    {'label': '故障关系图', 'type': 'FaultGraphWidget', 'category': '工业监控'},
]

LABELS = [w['label'] for w in WIDGETS]
TYPES = [w['type'] for w in WIDGETS]


def by_category():
    """{分类: [显示名, ...]}，分类按首次出现顺序。"""
    out = {}
    for w in WIDGETS:
        out.setdefault(w['category'], []).append(w['label'])
    return out


CATEGORIES = list(by_category())
