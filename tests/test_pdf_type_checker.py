"""
test_pdf_type_checker.py

pdf_type_checker 模块的独立测试脚本。

使用前准备：
    请在本脚本同目录下创建一个名为 test_pdfs 的文件夹，
    并放入以下3份真实PDF文件（文件名必须完全一致）：

      1. sample_text.pdf      —— 纯文本可选中的PDF（如用Word/WPS导出的简历）
                                  预期判断结果：False（文本型）
      2. sample_image.pdf     —— 纯扫描图片版PDF（如用手机拍照扫描后转成PDF、
                                  或用扫描仪生成的、内容完全无法选中复制的PDF）
                                  预期判断结果：True（图片型）
      3. sample_encrypted.pdf —— 一份设置了打开密码的加密PDF
                                  预期结果：抛出 PDFReadError 异常

    如果某份文件暂时没有准备好，脚本会自动跳过该项测试并给出提示，
    不会导致整个脚本崩溃中断，你可以先跑通已准备好的部分。

运行方式：
    python test_pdf_type_checker.py
"""

import os

from pdf_type_checker import is_image_based_pdf
from exceptions import PDFReadError


_TEST_PDF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_pdfs")


def run_case(filename: str, expected_result_desc: str, expect_exception: bool = False):
    """运行单个测试用例：打印实际结果，供人工核对是否与预期一致"""
    pdf_path = os.path.join(_TEST_PDF_DIR, filename)

    print(f"【测试用例】{filename}")
    print(f"  预期结果: {expected_result_desc}")

    if not os.path.isfile(pdf_path):
        print(f"  ⚠️  跳过：测试文件不存在，请放置到 {pdf_path}\n")
        return

    try:
        result = is_image_based_pdf(pdf_path, char_threshold=50)
        if expect_exception:
            print(f"  ❌ FAIL：预期应抛出PDFReadError，但实际正常返回了结果：{result}\n")
        else:
            print(f"  实际结果: is_image_based_pdf() = {result}")
            print(f"  ✅ 请人工核对上方实际结果是否与预期一致\n")
    except PDFReadError as e:
        if expect_exception:
            print(f"  实际结果: 按预期抛出 PDFReadError")
            print(f"  异常信息: {e}")
            print(f"  ✅ PASS\n")
        else:
            print(f"  ❌ FAIL：未预期的异常：{e}\n")


def main():
    if not os.path.isdir(_TEST_PDF_DIR):
        print(f"⚠️  测试目录不存在：{_TEST_PDF_DIR}")
        print("请先创建该目录并放入测试PDF文件后再运行本脚本。")
        return

    run_case(
        filename="sample_text.pdf",
        expected_result_desc="False（文本型，因为PyMuPDF能提取到足够文本）",
        expect_exception=False,
    )

    run_case(
        filename="sample_image.pdf",
        expected_result_desc="True（图片型，因为所有页面都几乎没有可提取文本）",
        expect_exception=False,
    )

    run_case(
        filename="sample_encrypted.pdf",
        expected_result_desc="抛出 PDFReadError（因为PDF已加密无法读取）",
        expect_exception=True,
    )

    print("=" * 50)
    print("全部测试用例运行完毕，请人工核对以上每一项实际结果是否符合预期。")


if __name__ == "__main__":
    main()