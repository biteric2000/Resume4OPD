"""
logger_setup.py

日志模块：创建一个同时输出到控制台和日志文件的logger实例。

设计说明：
- logger命名为 "resume_processor"，与root logger及第三方库日志隔离
- 每次调用 init_logger 都会先【关闭并清空】该logger已有的handler再重新添加，
  保证多次调用不会导致日志重复打印，也不会导致文件句柄泄露（ResourceWarning）
- 日志级别为 INFO，即 INFO / WARNING / ERROR / CRITICAL 均会被记录
"""

import logging
import os
import sys


_LOGGER_NAME = "resume_processor"
_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def init_logger(log_file_path: str) -> logging.Logger:
    """
    创建并返回一个配置好的logger实例，同时输出到控制台和指定日志文件。

    :param log_file_path: 日志文件的完整路径（如果所在目录不存在会自动创建）
    :return: 配置完成的 logging.Logger 实例
    """
    # 若目录不存在则自动创建
    log_dir = os.path.dirname(os.path.abspath(log_file_path))
    if log_dir and not os.path.isdir(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(logging.INFO)

    # 先逐个关闭已有handler底层的文件句柄，再清空列表，
    # 避免重复调用时产生 ResourceWarning（文件句柄泄露）
    for old_handler in logger.handlers[:]:
        old_handler.close()
        logger.removeHandler(old_handler)

    formatter = logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT)

    # 控制台输出
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件输出（追加模式，utf-8编码）
    file_handler = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 防止日志向上冒泡到root logger导致控制台重复打印
    logger.propagate = False

    return logger