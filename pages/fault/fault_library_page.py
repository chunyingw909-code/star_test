class FaultLibraryPage:
    """故障/预案库的「模块外壳」——顶部导航 Tab「故障/预案库」+ 6 个子标签
    （目录 / 预案库 / 快速定位 / 定位历史 / 故障注入 / 管理）。

    只负责「进入模块 + 在 6 个子标签间切换」。子标签的内容各自建 page 对象（目前是
    FaultCatalogPage=目录、FaultDetailPage=详情），都不继承本类——它们不做子标签切换。
    对应用例见 testcases/fault/test_fault_library.py。
    """

    TABS = ['目录', '预案库', '快速定位', '定位历史', '故障注入', '管理']

    def __init__(self, page):
        self.page = page
        # 顶部导航「界面编辑器 / 故障/预案库 / 卫星遥测」是一组 MUI Tab
        self.nav_entry = self.page.get_by_role('tab', name='故障/预案库', exact=True)
        # 进入模块的标志元素：子标签「目录」（进本模块不改 URL，靠子标签出现来判断）
        self.breadcrumb = self.tab('目录')
        # 头像菜单也是进入独立路由版「故障管理」的入口
        self.user_menu_button = self.page.get_by_title('用户菜单')
        self.fault_management_menu_item = self.page.get_by_role('menuitem', name='故障管理')

    def open(self):
        """点顶部「故障/预案库」Tab，等子标签渲染出来。"""
        self.nav_entry.click()
        self.tab('目录').wait_for(state='visible')
        self.page.wait_for_load_state('networkidle')
        return self

    def tab(self, name):
        """某个子标签的 locator（role=tab）。exact=True：否则「预案库」会连顶部
        「故障/预案库」Tab 一起命中（子串匹配）。"""
        return self.page.get_by_role('tab', name=name, exact=True)

    def open_tab(self, name):
        """点某个子标签。不在这里写死等待——由调用方的 expect(...) 自动等待到位。"""
        self.tab(name).click()

    def open_management_from_user_menu(self):
        """从右上角头像菜单进入独立路由版「故障管理」。"""
        self.user_menu_button.click()
        self.fault_management_menu_item.click()
        self.page.wait_for_url('**/zh-CN/fault/admin')
        self.page.get_by_role('heading', name='故障库管理').wait_for(state='visible')
