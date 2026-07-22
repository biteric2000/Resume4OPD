"""
pdf_archiver.py

PDF归档移动模块：将成功处理完的PDF文件移动到备份目录，
并处理目标目录下的同名文件命名冲突。
"""

import os
import shutil


def _resolve_available_target_path(pdf_archive_dir: str, filename: str) -> str:
    """
    在pdf_archive_dir目录下，为filename解决同名文件命名冲突。

    若目标路径已存在同名文件，在文件名（不含扩展名部分）后依次追加
    _2, _3... 后缀，直到找到一个尚不存在的路径为止。

    :return: 最终确定使用的目标文件【完整路径】（该路径此时尚不存在，
             仅返回一个确认可用的路径，实际移动操作由调用方完成）
    """
    name_stem, extension = os.path.splitext(filename)
    candidate_path = os.path.join(pdf_archive_dir, filename)

    if not os.path.exists(candidate_path):
        return candidate_path

    suffix_index = 2
    while True:
        candidate_filename = f"{name_stem}_{suffix_index}{extension}"
        candidate_path = os.path.join(pdf_archive_dir, candidate_filename)
        if not os.path.exists(candidate_path):
            return candidate_path
        suffix_index += 1


def archive_pdf(pdf_path: str, pdf_archive_dir: str) -> str:
    """
    将pdf_path指向的文件移动到pdf_archive_dir目录下，自动处理同名冲突。

    :param pdf_path: 待移动的PDF文件路径
    :param pdf_archive_dir: 目标归档目录（若不存在会自动创建）
    :return: 移动后文件的最终完整路径
    :raises FileNotFoundError: 当pdf_path指向的文件不存在时抛出，
                                异常信息中说明具体原因
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(
            f"无法归档：原始PDF文件不存在，路径：{pdf_path}"
        )

    os.makedirs(pdf_archive_dir, exist_ok=True)

    filename = os.path.basename(pdf_path)
    target_path = _resolve_available_target_path(pdf_archive_dir, filename)

    shutil.move(pdf_path, target_path)

    return target_path