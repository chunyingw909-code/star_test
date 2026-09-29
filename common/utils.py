import os
import time

import yaml


def wait_until_stable(page, read_fn, quiet_ms=400, timeout_ms=4000, poll_ms=80):
    """轮询 read_fn()，直到它的返回值连续 quiet_ms 不再变化（或到 timeout_ms 上限）。

    用于筛选 / 搜索 / 排序这类「没有 loading 态、又有 WebSocket 让 networkidle 不可靠」的
    客户端更新——等内容真正稳定，比写死 sleep 靠谱。read_fn 返回可比较的值（如某列文本列表）。
    """
    deadline = time.time() + timeout_ms / 1000
    last, last_change = object(), time.time()
    while time.time() < deadline:
        cur = read_fn()
        now = time.time()
        if cur != last:
            last, last_change = cur, now
        elif (now - last_change) * 1000 >= quiet_ms:
            return
        page.wait_for_timeout(poll_ms)


def project_root():
    """项目根目录的绝对路径（本文件在 <root>/common/utils.py，往上两级即根）。"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resolve_path(*parts):
    """把「相对项目根」的路径片段拼成绝对路径。

    不管在哪个目录启动 pytest，结果都指向同一个位置。
    例：resolve_path('screenshots', 'baseline')
        resolve_path('config/config.yaml')
    """
    return os.path.join(project_root(), *parts)


def read_yaml(file_path):
    with open(resolve_path(file_path), 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def read_secrets():
    """读 config/secrets.yaml（账号密码，不进 git，见 .gitignore）。
    结构：accounts.<role>.username / .password，例：accounts.admin.username。
    本地没有这个文件时报清楚的错，别让用例掉进一堆无关的 FileNotFoundError 堆栈里。"""
    path = resolve_path('config/secrets.yaml')
    if not os.path.exists(path):
        raise FileNotFoundError(
            'config/secrets.yaml 不存在——这个文件不提交 git，需要本地自己放一份 '
            '（accounts.<role>.username / .password 结构）')
    return read_yaml('config/secrets.yaml')


def fault_root(page):
    """故障/预案库内嵌 Tab 版本（主壳内点子标签进）外层套了 data-testid=fault-catalog-root；
    同样内容的独立路由版（比如 /fault/history、/fault/inject，头像菜单「故障管理」或直接
    改 URL 进）没有这层包裹，其余 DOM 一致。两种入口共用同一批定位符时，root 用这个：
    有就用它兜底子树查询，没有就退化到整个 page（内容本来就没别的东西会撞）。"""
    root = page.get_by_test_id('fault-catalog-root')
    return root if root.count() else page


def api_fetch(page, url, method='GET', body=None):
    """同源 fetch，自动带上 localStorage 里的 sarsat_token（Bearer）。

    页面里真实点击触发的请求会自动带这个 token（前端自己的 fetch 封装加的），但用例
    里为了直接建 / 删测试数据、在 page.evaluate 里手写的裸 fetch 不会——没有登录态的
    环境（如 185）localStorage 里没有这个键，header 就不加，原本能直接过的请求不受
    影响；需要登录的环境（如 222）不带这个 token 会 403。给用例接口建 / 清数据用，
    不用各处重复写鉴权逻辑。返回解析后的 JSON（无响应体时返回 None）。"""
    return page.evaluate(
        """async ({url, method, body}) => {
            const token = localStorage.getItem('sarsat_token');
            const headers = {'Content-Type': 'application/json'};
            if (token) headers['Authorization'] = `Bearer ${token}`;
            const res = await fetch(url, {
                method, headers, body: body !== null ? JSON.stringify(body) : undefined,
            });
            const text = await res.text();
            return text ? JSON.parse(text) : null;
        }""",
        {'url': url, 'method': method, 'body': body},
    )


def api_status(page, url, method='GET', body=None):
    """跟 api_fetch 一样自动带 sarsat_token，但只要 HTTP 状态码——给「这个接口该不该
    拦住当前登录角色」这类权限用例用，不关心响应体具体内容。"""
    return page.evaluate(
        """async ({url, method, body}) => {
            const token = localStorage.getItem('sarsat_token');
            const headers = {'Content-Type': 'application/json'};
            if (token) headers['Authorization'] = `Bearer ${token}`;
            const res = await fetch(url, {
                method, headers, body: body !== null ? JSON.stringify(body) : undefined,
            });
            return res.status;
        }""",
        {'url': url, 'method': method, 'body': body},
    )
