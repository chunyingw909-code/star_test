# 页面编辑器
class EditorPage:
    def __init__(self, page):
        self.page = page
        # 主题切换
        self.theme_toggle = page.get_by_test_id('dashboard-theme-toggle')
        # 大小屏切换
        self.fullhd_button = page.get_by_test_id('resolution-fullhd')
        self.hd_button = page.get_by_test_id('resolution-hd')
        self.tablet_button = page.get_by_test_id('resolution-tablet')
        # 工具栏
        self.editor_button = page.get_by_role('button', name='界面编辑器')
        self.edit_button = page.get_by_role('button', name='编辑', exact=True)
        self.preview_button = page.get_by_role('button', name='预览')
        self.free_layout_button = page.get_by_role('button', name='自由布局')
        self.grid_layout_button = page.get_by_role('button', name='栅格布局')
        self.template_button = page.get_by_role('button', name='模板')
        self.plugin_button = page.get_by_role('button', name='插件')
        self.flow_button = page.get_by_role('button', name='流程')
        self.new_button = page.get_by_role('button', name='新建')
        self.publish_button = page.get_by_role('button', name='发布')
        # 右侧栏
        self.edit_manage_button = page.get_by_text('编辑管理')
        self.version_manage_button = page.get_by_text('版本管理')