"""
output_structure.py

输出目录结构创建模块：按时间戳创建本次运行所需的目录结构。

目录结构：
    output_folder/
      └── 简历汇总_{timestamp}/          (主子目录，若冲突则自动加_2/_3...后缀)
            ├── pdf/                     (成功转换的PDF备份目录)
            ├── txt/                     (每个PDF对应的独立txt目录)
            ├── 简历汇总文本_{timestamp}.txt   (仅返回路径，不在本模块创建)
            └── 处理日志_{timestamp}.log       (仅返回路径，不在本模块创建)
"""

import os
from datetime import datetime


def _generate_timestamp() -> str:
    """生成 YYYYMMDDHHmm 格式的时间戳字符串"""
    return datetime.now().strftime("%Y%m%d%H%M")


def _resolve_available_base_dir(output_folder: str, timestamp: str) -> str:
    """
    在output_folder下，为主子目录名 "简历汇总_{timestamp}" 解决命名冲突。

    若该目录已存在，依次尝试追加 _2, _3... 后缀，直到找到一个尚不存在的目录名。

    :return: 最终确定使用的主子目录【绝对路径】（此时该目录尚未创建，
             仅返回一个确认可用的路径，由调用方负责实际创建）
    """
    base_name = f"简历汇总_{timestamp}"
    candidate_path = os.path.join(output_folder, base_name)

    if not os.path.isdir(candidate_path):
        return os.path.abspath(candidate_path)

    suffix_index = 2
    while True:
        candidate_name = f"{base_name}_{suffix_index}"
        candidate_path = os.path.join(output_folder, candidate_name)
        if not os.path.isdir(candidate_path):
            return os.path.abspath(candidate_path)
        suffix_index += 1


def create_output_structure(output_folder: str, timestamp: str = None) -> dict:
    """
    在output_folder下创建本次运行所需的目录结构。

    :param output_folder: 输出结果的根目录（若不存在会自动创建，包括多层父目录）
    :param timestamp: 时间戳字符串，格式YYYYMMDDHHmm；若为None则自动生成当前时间
    :return: 字典，包含以下键（均为绝对路径字符串）：
             "base_dir"、"pdf_dir"、"txt_dir"、"summary_file_path"、"log_file_path"
             其中 summary_file_path 和 log_file_path 仅为路径字符串，
             本函数不会创建这两个文件本身。
    """
    if timestamp is None:
        timestamp = _generate_timestamp()

    # 确保output_folder本身存在（包括多层不存在的父目录）
    os.makedirs(output_folder, exist_ok=True)

    base_dir = _resolve_available_base_dir(output_folder, timestamp)
    pdf_dir = os.path.join(base_dir, "pdf")
    txt_dir = os.path.join(base_dir, "txt")

    os.makedirs(base_dir, exist_ok=False)
    os.makedirs(pdf_dir, exist_ok=False)
    os.makedirs(txt_dir, exist_ok=False)

    summary_file_path = os.path.abspath(
        os.path.join(base_dir, f"简历汇总文本_{timestamp}.txt")
    )
    log_file_path = os.path.abspath(
        os.path.join(base_dir, f"处理日志_{timestamp}.log")
    )

    return {
        "base_dir": base_dir,
        "pdf_dir": pdf_dir,
        "txt_dir": txt_dir,
        "summary_file_path": summary_file_path,
        "log_file_path": log_file_path,
    }