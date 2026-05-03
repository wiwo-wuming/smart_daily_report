"""
日志配置 - 统一日志格式和输出
"""
import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """配置全局日志

    Args:
        level: 日志级别 (DEBUG/INFO/WARNING/ERROR)
    """
    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)-7s %(name)-20s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(fmt)

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    # 避免重复添加 handler
    if not root_logger.handlers:
        root_logger.addHandler(handler)

    # 抑制第三方库的噪音日志
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
