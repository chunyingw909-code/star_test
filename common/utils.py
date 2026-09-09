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
