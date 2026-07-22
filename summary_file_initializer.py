"""
summary_file_initializer.py

汇总文件初始化模块：创建汇总txt文件，并写入开头的提示词文本，
作为后续各份简历文本追加内容的开头部分。
"""

import os


def init_summary_file(summary_file_path: str, prompt_text: str) -> None:
    """
    以覆盖式写入模式创建汇总txt文件，写入prompt_text并换行。

    :param summary_file_path: 汇总txt文件的完整路径
    :param prompt_text: 要写入文件开头的提示词文本
    :return: None
    """
    parent_dir = os.path.dirname(summary_file_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    with open(summary_file_path, "w", encoding="utf-8") as f:
        f.write(prompt_text)
        f.write("\n")