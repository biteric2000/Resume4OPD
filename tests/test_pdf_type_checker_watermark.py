"""
test_pdf_type_checker_watermark.py

专门测试水印过滤功能：验证"图片型PDF+水印文本超过阈值"这种边界场景，
在传入watermark_strings后能被正确识别为图片型。

说明：
    本脚本会用PyMuPDF动态生成两份测试PDF：
    1. 一份只包含水印文本、无实际内容的"伪图片型"PDF（模拟你遇到的故障场景）
    2. 一份包含真实简历文本+同样水印的"真正文本型"PDF（确保过滤水印后，
       真实文本型PDF依然能被正确识别为文本型，不会被误伤）
    生成的PDF会保留在test_output目录下，方便你打开实际查看。

运行方式：
    python test_pdf_type_checker_watermark.py
"""

import os

import fitz

from pdf_type_checker import is_image_based_pdf


_TEST_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
_WATERMARK = "77a2a110dba8a1581HJ-2Nu-GVZZwYm2UPuaWOGhm_XVPhJi2Q~~"
_CHAR_THRESHOLD = 50


def _create_pdf_with_text(file_path: str, text: str) -> None:
    """生成一份只包含指定文本的单页PDF，用于模拟测试场景"""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text, fontsize=10)
    doc.save(file_path)
    doc.close()


def test_watermark_only_should_be_image_based():
    """场景1：PDF仅包含水印文本（无实际简历内容），字符数超过阈值，
    但传入watermark_strings过滤后，应正确识别为图片型"""
    print("【场景1】仅含水印文本的PDF（模拟真实故障场景）")

    pdf_path = os.path.join(_TEST_OUTPUT_DIR, "watermark_only.pdf")
    # 水印字符串本身长度约53字符，超过阈值50，模拟"误判"场景
    _create_pdf_with_text(pdf_path, _WATERMARK)
    print(f"  测试文件: {pdf_path}")
    print(f"  水印字符串长度: {len(_WATERMARK)}（阈值: {_CHAR_THRESHOLD}）")

    # 不传watermark_strings：应误判为文本型（复现故障）
    result_without_filter = is_image_based_pdf(pdf_path, char_threshold=_CHAR_THRESHOLD)
    print(f"  不启用水印过滤时的判断结果: is_image_based={result_without_filter}"
          f"（预期False，即会误判为文本型，复现故障）")
    assert result_without_filter is False, "未启用水印过滤时，应复现误判为文本型的故障"

    # 传入watermark_strings：应正确识别为图片型
    result_with_filter = is_image_based_pdf(
        pdf_path,
        char_threshold=_CHAR_THRESHOLD,
        watermark_strings=[_WATERMARK],
    )
    print(f"  启用水印过滤后的判断结果: is_image_based={result_with_filter}"
          f"（预期True，即修复后应正确识别为图片型）")
    assert result_with_filter is True, "启用水印过滤后，应正确识别为图片型"

    print("  ✅ PASS：水印过滤功能生效，故障场景已修复\n")


def test_real_text_with_watermark_should_stay_text_based():
    """场景2：PDF包含真实简历文本+水印，过滤水印后仍应正确识别为文本型
    （确保水印过滤不会误伤真正的文本型PDF）"""
    print("【场景2】真实文本+水印混合的PDF（确保不误伤正常文本型PDF）")

    pdf_path = os.path.join(_TEST_OUTPUT_DIR, "real_text_with_watermark.pdf")
    real_content = (
        "姓名：测试候选人\n"
        "工作经验：5年AI全栈开发经验，熟悉Python、React、大模型应用开发。\n"
        "教育背景：某大学计算机科学与技术专业。\n"
    )
    full_text = real_content + _WATERMARK
    _create_pdf_with_text(pdf_path, full_text)
    print(f"  测试文件: {pdf_path}")

    result_with_filter = is_image_based_pdf(
        pdf_path,
        char_threshold=_CHAR_THRESHOLD,
        watermark_strings=[_WATERMARK],
    )
    print(f"  启用水印过滤后的判断结果: is_image_based={result_with_filter}"
          f"（预期False，即真实文本型PDF不应被误伤）")
    assert result_with_filter is False, "过滤水印后，真实文本型PDF应仍被正确识别为文本型"

    print("  ✅ PASS：水印过滤未误伤真正的文本型PDF\n")


def main():
    os.makedirs(_TEST_OUTPUT_DIR, exist_ok=True)

    test_watermark_only_should_be_image_based()
    test_real_text_with_watermark_should_stay_text_based()

    print("=" * 50)
    print("全部测试通过 ✅")
    print(f"\n生成的测试PDF保留在: {_TEST_OUTPUT_DIR}")
    print("可自行打开查看，确认PDF内容与预期一致。")


if __name__ == "__main__":
    main()