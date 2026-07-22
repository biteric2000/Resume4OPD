"""
test_text_extractor_native.py

text_extractor_native 模块的独立测试脚本。

使用前准备：
    请在本脚本同目录下的 test_pdfs 文件夹中放入以下文件
    （如果你在模块4测试时已经准备过 sample_text.pdf，可以直接复用同一份文件）：

      1. sample_text.pdf —— 至少1份文本型PDF（可选中复制文字的PDF）

    如果该文件不存在，脚本会跳过对应测试并给出提示，不会崩溃。

运行方式：
    python test_text_extractor_native.py
"""

import os

from text_extractor_native import extract_text_native
from exceptions import PDFReadError


_TEST_PDF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_pdfs")


def test_extract_real_text_pdf():
    """核对：提取一份真实文本型PDF的内容，打印全文供人工核对完整性/准确性/是否乱码"""
    pdf_path = os.path.join(_TEST_PDF_DIR, "sample_text.pdf")

    print("【测试用例】提取 sample_text.pdf 的文本内容")

    if not os.path.isfile(pdf_path):
        print(f"  ⚠️  跳过：测试文件不存在，请放置到 {pdf_path}\n")
        return

    try:
        extracted_text = extract_text_native(pdf_path)
    except PDFReadError as e:
        print(f"  ❌ 提取失败，抛出了未预期的PDFReadError：{e}\n")
        return

    print(f"  提取文本总长度：{len(extracted_text)} 字符")
    print("  ----- 以下是提取到的完整文本内容 -----")
    print(extracted_text)
    print("  ----- 提取文本内容结束 -----")
    print("  ✅ 请人工核对以上文本内容是否完整、准确、无乱码\n")


def test_file_not_found():
    """核对：传入不存在的文件路径，应正确抛出PDFReadError"""
    non_existent_path = os.path.join(_TEST_PDF_DIR, "does_not_exist.pdf")

    print("【测试用例】传入不存在的文件路径")
    print(f"  路径: {non_existent_path}")

    try:
        extract_text_native(non_existent_path)
        print("  ❌ FAIL：预期应抛出PDFReadError，但实际未抛出任何异常\n")
    except PDFReadError as e:
        print(f"  实际结果: 按预期抛出 PDFReadError")
        print(f"  异常信息: {e}")
        print("  ✅ PASS\n")


def main():
    test_extract_real_text_pdf()
    test_file_not_found()

    print("=" * 50)
    print("全部测试用例运行完毕，请人工核对以上文本提取内容部分是否符合预期。")


if __name__ == "__main__":
    main()