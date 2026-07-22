"""
text_extractor_native.py

文本型PDF提取模块：使用PyMuPDF逐页提取PDF的文本层内容并拼接。

仅适用于"文本型"PDF（即已通过pdf_type_checker.is_image_based_pdf判定为
False的PDF）。只提取文本层，不处理PDF中嵌入的图片内容。
"""

import fitz  # PyMuPDF

from exceptions import PDFReadError


def extract_text_native(pdf_path: str) -> str:
    """
    逐页提取PDF的文本层内容，按页码顺序拼接为一个完整字符串。

    :param pdf_path: PDF文件路径
    :return: 拼接后的完整文本内容（各页之间用单个换行符\n分隔）
    :raises PDFReadError: 当PDF无法正常打开或读取时抛出（如加密、损坏、
                           文件不存在等），异常信息中包含原始文件路径和具体原因
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

        page_texts = []
        for page_index in range(doc.page_count):
            try:
                page = doc.load_page(page_index)
                page_text = page.get_text()
            except Exception as e:
                raise PDFReadError(
                    f"PDF文件读取页面内容失败：{pdf_path}，"
                    f"第{page_index + 1}页，原因：{e}"
                ) from e

            page_texts.append(page_text)

        return "\n".join(page_texts)
    finally:
        doc.close()