import yaml
import os


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
