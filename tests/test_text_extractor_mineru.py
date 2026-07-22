"""
test_text_extractor_mineru.py

text_extractor_mineru 模块的独立测试脚本。

使用前准备：
    请在本脚本同目录下的 test_pdfs 文件夹中放入以下文件
    （如果模块4测试时已准备过 sample_image.pdf，可直接复用）：

      1. sample_image.pdf —— 至少1份图片型/扫描版PDF（内容完全无法选中复制文字）

    如果该文件不存在，脚本会跳过测试并给出提示，不会崩溃。

    注意事项：
      - 请确保运行本脚本前已激活正确的虚拟环境（即安装了MinerU的那个环境）
      - 首次调用MinerU可能涉及模型加载，耗时会明显长于后续调用，请耐心等待
      - MinerU处理过程通常耗时较长（几十秒到几分钟不等，视PDF页数和GPU情况），
        脚本会打印耗时统计，方便你了解实际处理速度

运行方式：
    python test_text_extractor_mineru.py
"""

import os
import shutil
import time

from text_extractor_mineru import extract_text_via_mineru, MinerUProcessError


_TEST_PDF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_pdfs")
_WORK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_mineru_work_dir")


def test_extract_image_pdf_via_mineru():
    """核对：调用MinerU处理一份真实图片型PDF，打印提取文本、warning列表和耗时"""
    pdf_path = os.path.join(_TEST_PDF_DIR, "sample_image.pdf")

    print("【测试用例】调用MinerU处理 sample_image.pdf")

    if not os.path.isfile(pdf_path):
        print(f"  ⚠️  跳过：测试文件不存在，请放置到 {pdf_path}\n")
        return

    # 每次测试前清理旧的work_dir，避免残留文件干扰"输出文件定位逻辑"的验证
    if os.path.isdir(_WORK_DIR):
        shutil.rmtree(_WORK_DIR)

    print(f"  PDF路径: {pdf_path}")
    print(f"  MinerU输出目录: {_WORK_DIR}")
    print("  开始调用MinerU，请耐心等待（首次调用可能涉及模型加载，耗时较长）...\n")

    start_time = time.time()

    try:
        text_content, warnings = extract_text_via_mineru(
            pdf_path, _WORK_DIR, timeout_seconds=600
        )
    except MinerUProcessError as e:
        elapsed = time.time() - start_time
        print(f"  ❌ 处理失败，耗时 {elapsed:.1f} 秒")
        print(f"  异常信息: {e}\n")
        return

    elapsed = time.time() - start_time
    print(f"  ✅ 处理完成，总耗时: {elapsed:.1f} 秒\n")

    print(f"  提取文本总长度: {len(text_content)} 字符")
    print("  ----- 以下是提取到的完整文本内容 -----")
    print(text_content)
    print("  ----- 提取文本内容结束 -----\n")

    print(f"  捕获到的warning数量: {len(warnings)}")
    if warnings:
        print("  ----- warning列表 -----")
        for i, w in enumerate(warnings, 1):
            print(f"    {i}. {w}")
        print("  ----- warning列表结束 -----")
    print("\n  ✅ 请人工核对：1) 文本内容是否与PDF实际内容基本一致（OCR效果）；")
    print("               2) 上方是否有打印'实际使用的输出文件路径'相关报错，")
    print("                  如有找不到文件的报错，请将work_dir实际目录结构反馈\n")


def main():
    test_extract_image_pdf_via_mineru()

    print("=" * 50)
    print("测试运行完毕，请人工核对以上OCR提取内容是否符合预期。")


if __name__ == "__main__":
    main()