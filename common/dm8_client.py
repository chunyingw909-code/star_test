"""Read-only access to the local DM8 instance used for database-backed tests."""

import atexit
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml

from common.utils import resolve_path


class Dm8Unavailable(RuntimeError):
    """The machine does not have the local DB test configuration or JDBC driver."""


_BUILD_DIR = None


def _settings():
    path = Path(resolve_path('config/dm8.local.yaml'))
    if not path.exists():
        raise Dm8Unavailable(f'缺少本地达梦配置：{path}')
    with path.open(encoding='utf-8') as file:
        settings = yaml.safe_load(file) or {}
    missing = {'host', 'port', 'username', 'password'} - settings.keys()
    if missing:
        raise Dm8Unavailable(f'达梦本地配置缺少：{", ".join(sorted(missing))}')
    return settings


def _driver_jar():
    configured = os.getenv('DM8_JDBC_JAR')
    default = Path.home() / (
        'AppData/Roaming/DBeaverData/drivers/maven/maven-central/com.dameng/'
        'DmJdbcDriver18-8.1.3.62.jar'
    )
    path = Path(configured) if configured else default
    if not path.is_file():
        raise Dm8Unavailable(f'找不到达梦 JDBC 驱动：{path}')
    return path


def _compiled_tool():
    global _BUILD_DIR
    if _BUILD_DIR:
        return _BUILD_DIR
    build_dir = Path(tempfile.mkdtemp(prefix='star-test-dm8-'))
    source = Path(resolve_path('tools/Dm8Read.java'))
    try:
        subprocess.run(
            ['javac', '-encoding', 'UTF-8', '-cp', str(_driver_jar()), '-d', str(build_dir), str(source)],
            check=True, capture_output=True, text=True,
        )
    except FileNotFoundError as error:
        shutil.rmtree(build_dir, ignore_errors=True)
        raise Dm8Unavailable('找不到 Java，无法使用达梦 JDBC 驱动') from error
    except subprocess.CalledProcessError as error:
        shutil.rmtree(build_dir, ignore_errors=True)
        raise Dm8Unavailable(f'编译达梦只读工具失败：{error.stderr.strip()}') from error
    _BUILD_DIR = build_dir
    return build_dir


@atexit.register
def _clean_compiled_tool():
    if _BUILD_DIR:
        shutil.rmtree(_BUILD_DIR, ignore_errors=True)


def fetch_rows(sql):
    """Execute one SELECT and return result rows keyed by the actual column labels."""
    if not sql.lstrip().lower().startswith('select'):
        raise ValueError('DM8 test client only permits SELECT statements')

    settings = _settings()
    env = os.environ | {
        'DM8_HOST': str(settings['host']),
        'DM8_PORT': str(settings['port']),
        'DM8_USER': settings['username'],
        'DM8_PASSWORD': settings['password'],
    }
    classpath = os.pathsep.join((str(_compiled_tool()), str(_driver_jar())))
    try:
        completed = subprocess.run(
            ['java', '-Dfile.encoding=UTF-8', '-cp', classpath, 'Dm8Read', sql],
            check=True, capture_output=True, text=True, encoding='utf-8', env=env,
        )
    except FileNotFoundError as error:
        raise Dm8Unavailable('找不到 Java，无法使用达梦 JDBC 驱动') from error
    except subprocess.CalledProcessError as error:
        raise Dm8Unavailable(f'达梦只读查询失败：{error.stderr.strip()}') from error

    lines = completed.stdout.splitlines()
    if not lines:
        return []
    headers = lines[0].split('\t')
    return [dict(zip(headers, line.split('\t'))) for line in lines[1:]]


def fault_plan_with_fault(name=None):
    """Read a guaranteed plan→fault pair, optionally by an exact plan name."""
    name_filter = ''
    if name is not None:
        escaped_name = name.replace("'", "''")
        name_filter = f' AND "name" = \'{escaped_name}\''
    plans = fetch_rows(
        'SELECT "id", "faultId", "name", "expectedResult", "steps", "simSceneId" '
        'FROM SARSAT_SCHED."fault_plans" WHERE "faultId" IS NOT NULL '
        f'{name_filter} ORDER BY "createdAt" DESC FETCH FIRST 1 ROW ONLY'
    )
    if not plans:
        raise Dm8Unavailable('fault_plans 中没有可关联到故障的预案')
    plan = plans[0]
    fault_id = plan['faultId'].replace("'", "''")
    faults = fetch_rows(
        'SELECT "id", "faultCode", "faultName" '
        f'FROM SARSAT_SCHED."fault_catalog" WHERE "id" = \'{fault_id}\''
    )
    if not faults:
        raise Dm8Unavailable(f'预案 {plan["id"]} 的 faultId 在 fault_catalog 中不存在')
    return plan | faults[0]
