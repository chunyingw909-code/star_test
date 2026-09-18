"""插件注册清单与当前可添加组件清单。

Plugin Manager 仍登记 12 个组件；自由布局「添加组件」菜单目前只开放其中 8 个。
下线组件保留在插件注册表中，但不应出现在可添加菜单里。

顺序即 Plugin Manager 表格里的顺序。
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

RETIRED_TYPES = {'InputWidget', 'SelectWidget', 'NumberWidget', 'FaultGraphWidget'}
ACTIVE_WIDGETS = [w for w in WIDGETS if w['type'] not in RETIRED_TYPES]
ACTIVE_LABELS = [w['label'] for w in ACTIVE_WIDGETS]
