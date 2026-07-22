"""
exceptions.py

项目公共自定义异常类模块。

设计说明：
    PDFReadError 会被"PDF类型判断模块"(pdf_type_checker.py)和
    "文本提取模块-原生文本层"(text_extractor_native.py)同时使用，
    为避免循环import和重复定义，单独抽出到本文件，两个模块都从这里import。
"""


class PDFReadError(Exception):
    """表示PDF文件无法正常打开或读取（如加密、损坏、文件不存在等情况）。"""
    pass