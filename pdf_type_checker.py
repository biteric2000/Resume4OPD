"""
pdf_type_checker.py

PDF类型判断模块：判断一份PDF是"文本型"还是"图片型"。

判断原则：不以文字数量多寡判断，而是判断"是否存在有效文本层"。
    - 只要有任意一页字符数达到或超过阈值，整份PDF判定为文本型（返回False）
    - 只有全部页面字符数都低于阈值，才判定为图片型（返回True）

水印过滤说明：
    部分简历平台生成的"图片型"PDF，会在页面中嵌入一段不可见/无关的
    追踪水印文本，这段文本本身与简历内容无关。本模块提供公开函数
    strip_watermarks()，支持两种过滤方式：

    1. watermark_strings（精确字符串列表）：
       适合完全不规律、无法归纳模板的水印，逐条精确删除。

    2. watermark_patterns（正则表达式列表）：
       适合"有固定外形特征"的水印，例如该平台水印的通用外形为：
           一长串连续无空格的字母/数字/下划线/短横线，并以两个
           波浪号"~~"结尾
       对应正则： [0-9A-Za-z_-]{20,}~~

    两种方式可以同时配置、同时生效，互不冲突。

    【重要】strip_watermarks()被设计为公开函数（而非模块私有函数），
    是因为它不仅要在本模块内部用于"类型判断前的字符数统计"，
    更要在resume_processor.py主流程中，被应用到【真正提取出来、
    即将写入文件的文本内容】上，确保水印真正从最终输出中被清除，
    而不仅仅是在类型判断这一个孤立环节里被临时过滤。
"""

import re

import fitz  # PyMuPDF

from exceptions import PDFReadError


def strip_watermarks(
    text: str,
    watermark_strings: list = None,
    watermark_patterns: list = None,
) -> str:
    """
    从text中移除所有已知的水印内容（精确字符串+正则模式），返回净化后的文本。

    本函数为公开函数，可在任何需要清除水印的场景下调用——
    不仅限于PDF类型判断，也应用于最终写入文件/汇总/剪贴板的文本内容。

    :param text: 原始文本
    :param watermark_strings: 需要精确移除的水印字符串列表（可为空）
    :param watermark_patterns: 需要按正则表达式移除的水印模式列表（可为空）
    :return: 移除水印后的文本
    """
    cleaned_text = text

    if watermark_strings:
        for watermark in watermark_strings:
            if watermark:
                cleaned_text = cleaned_text.replace(watermark, "")

    if watermark_patterns:
        for pattern in watermark_patterns:
            if pattern:
                try:
                    cleaned_text = re.sub(pattern, "", cleaned_text)
                except re.error:
                    # 配置文件里正则写错了，不应导致整个程序崩溃，
                    # 忽略这一条无效正则，继续处理其余的过滤规则
                    continue

    return cleaned_text


def is_image_based_pdf(
    pdf_path: str,
    char_threshold: int = 50,
    watermark_strings: list = None,
    watermark_patterns: list = None,
) -> bool:
    """
    判断PDF是否为图片型（即全部页面均无有效可提取文本层）。

    :param pdf_path: PDF文件路径
    :param char_threshold: 每页字符数阈值，低于此值视为该页"几乎没有可提取文本"
    :param watermark_strings: 已知的水印精确字符串列表，会在统计字符数
                               之前从每页文本中先剔除掉。默认为None（不过滤）
    :param watermark_patterns: 已知的水印正则表达式列表。默认为None（不过滤）
    :return: True表示图片型（需走OCR分支），False表示文本型（可直接用PyMuPDF提取）
    :raises PDFReadError: 当PDF无法正常打开或读取时抛出（如加密、损坏、文件不存在），
                           异常信息中包含原始文件路径和具体原因
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise PDFReadError(
            f"PDF文件无法打开：{pdf_path}，原因：{e}"
        ) from e

    try:
        if doc.is_encrypted:
            raise PDFReadError(
                f"PDF文件已加密，无法读取：{pdf_path}"
            )

        for page_index in range(doc.page_count):
            try:
                page = doc.load_page(page_index)
                page_text = page.get_text()
            except Exception as e:
                raise PDFReadError(
                    f"PDF文件读取页面内容失败：{pdf_path}，"
                    f"第{page_index + 1}页，原因：{e}"
                ) from e

            cleaned_page_text = strip_watermarks(
                page_text, watermark_strings, watermark_patterns
            )

            char_count = len(cleaned_page_text.strip())
            if char_count >= char_threshold:
                return False

        return True
    finally:
        doc.close()