"""
辅助函数
"""
import os
import re
from datetime import datetime, timedelta
from pathlib import Path


def resolve_env_vars(config):
    """递归解析配置中的 ${ENV_VAR} 环境变量占位符"""
    if isinstance(config, dict):
        return {k: resolve_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [resolve_env_vars(item) for item in config]
    elif isinstance(config, str):
        pattern = re.compile(r'\$\{([^}]+)\}')
        def _replace(match):
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))
        return pattern.sub(_replace, config)
    return config


def format_date(date_str: str = None, format_str: str = "%Y-%m-%d") -> str:
    """格式化日期"""
    if date_str is None:
        return datetime.now().strftime(format_str)
    return date_str

def parse_date(date_str: str) -> datetime:
    """解析日期字符串"""
    formats = ["%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"无法解析日期: {date_str}")

def ensure_dir(path: str) -> Path:
    """确保目录存在"""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

def get_date_range(start_date: str, end_date: str):
    """获取日期范围内的所有日期"""
    start = parse_date(start_date)
    end = parse_date(end_date)

    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return dates

def truncate_text(text: str, max_length: int = 50) -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
