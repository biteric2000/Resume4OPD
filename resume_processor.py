"""
resume_processor.py

主流程调度模块：串联前面所有已独立测试通过的模块，
形成完整的简历PDF批量处理流程。

设计决策说明（重要，供你核对）：
    1. 失败容错：任意一份PDF在任意处理步骤失败，只跳过该文件，
       继续处理下一份，绝不中断整个程序。
    2. 失败的PDF文件保留在原始输入文件夹中不做任何移动，
       但会在【控制台】和【日志】中明确提示"该文件处理失败，
       仍保留在原始文件夹，请手动检查"。
    3. 只处理input_folder【顶层】的.pdf文件，不递归子文件夹。
    4. config.json路径默认固定为"本脚本同目录下的config.json"，
       同时保留命令行参数覆盖的能力。
    5. 每份PDF处理完毕后（脱敏之后），都会调用一次模块11的
       call_llm_analysis占位函数，为未来真正接入大模型提前接好调用点。
    6. 汇总文本文件（简历汇总文本_时间戳.txt）放在【output_folder根目录】下。
    7. 全部处理完成后，会自动将汇总文本文件的完整内容复制到系统剪贴板。
    8. 【本次修复】此前发现一个严重遗漏：watermark_strings/watermark_patterns
       配置的水印过滤，此前【只在is_image_based_pdf()内部用于类型判断时
       生效】，从未真正应用到实际提取出来、写入txt文件/汇总文件/剪贴板的
       文本内容上，导致水印依然原样出现在最终产物里。
       本次修复：在文本提取完成后（extract_text_native/extract_text_via_mineru
       之后），【立即】调用strip_watermarks()对text_content做一次净化，
       确保后续所有环节（隐私脱敏、写入txt、追加汇总、复制剪贴板）
       使用的都是已经去除水印的干净文本。
"""

import os
import sys
from datetime import datetime

from config_loader import load_config, ConfigError
from logger_setup import init_logger
from privacy_masker import mask_privacy_info
from exceptions import PDFReadError
from pdf_type_checker import is_image_based_pdf, strip_watermarks
from text_extractor_native import extract_text_native
from text_extractor_mineru import extract_text_via_mineru, MinerUProcessError
from output_structure import create_output_structure
from summary_file_initializer import init_summary_file
from summary_appender import append_to_summary
from pdf_archiver import archive_pdf
from llm_analyzer import call_llm_analysis
from clipboard_helper import copy_text_to_clipboard


_SCRIPT_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def _resolve_available_txt_path(txt_dir: str, pdf_filename: str) -> str:
    """
    在txt_dir目录下，为pdf_filename对应的txt文件名解决命名冲突。
    逻辑与pdf_archiver模块中的冲突处理方式保持一致：
    若同名文件已存在，依次尝试追加 _2, _3... 后缀。

    :return: 最终确定使用的txt文件【完整路径】（尚未创建该文件）
    """
    name_stem = os.path.splitext(pdf_filename)[0]
    candidate_path = os.path.join(txt_dir, f"{name_stem}.txt")

    if not os.path.exists(candidate_path):
        return candidate_path

    suffix_index = 2
    while True:
        candidate_path = os.path.join(txt_dir, f"{name_stem}_{suffix_index}.txt")
        if not os.path.exists(candidate_path):
            return candidate_path
        suffix_index += 1


def _list_top_level_pdfs(input_folder: str) -> list:
    """获取input_folder【顶层】所有以.pdf结尾的文件的完整路径列表（不递归子目录）"""
    pdf_paths = []
    for entry in sorted(os.listdir(input_folder)):
        full_path = os.path.join(input_folder, entry)
        if os.path.isfile(full_path) and entry.lower().endswith(".pdf"):
            pdf_paths.append(full_path)
    return pdf_paths


def _process_single_pdf(
    pdf_path: str,
    config: dict,
    dirs: dict,
    logger,
) -> None:
    """
    处理单份PDF的完整流程：类型判断→提取文本→净化水印→脱敏→
    保存独立txt→追加汇总→归档PDF。任何一步失败都会抛出异常，
    由上层调用方捕获并跳过。
    """
    pdf_filename = os.path.basename(pdf_path)

    watermark_strings = config.get("watermark_strings", [])
    watermark_patterns = config.get("watermark_patterns", [])

    # 步骤1：判断PDF类型（文本型/图片型），并过滤已知的平台水印字符串
    char_threshold = config["char_threshold"]
    is_image_based = is_image_based_pdf(
        pdf_path,
        char_threshold=char_threshold,
        watermark_strings=watermark_strings,
        watermark_patterns=watermark_patterns,
    )

    # 步骤2：根据类型选择提取方式
    if is_image_based:
        mineru_work_dir = os.path.join(
            dirs["base_dir"], "mineru_temp", os.path.splitext(pdf_filename)[0]
        )
        text_content, warnings = extract_text_via_mineru(
            pdf_path,
            work_dir=mineru_work_dir,
            timeout_seconds=config["mineru_timeout_seconds"],
        )
        for warning_line in warnings:
            logger.warning(f"[{pdf_filename}] MinerU警告: {warning_line}")
    else:
        text_content = extract_text_native(pdf_path)

    # 步骤2.5（本次修复的关键步骤）：净化水印
    # 必须在这里【真正应用】一次水印过滤，而不是只在is_image_based_pdf内部
    # 用于类型判断时临时生效——否则水印会原样保留在最终输出文本中。
    text_content = strip_watermarks(
        text_content,
        watermark_strings=watermark_strings,
        watermark_patterns=watermark_patterns,
    )

    # 步骤3：隐私脱敏
    masked_text = mask_privacy_info(
        text_content,
        phone_placeholder=config["phone_placeholder"],
        email_placeholder=config["email_placeholder"],
    )

    # 步骤4（预留接口）：调用大模型分析占位函数
    call_llm_analysis(masked_text, config["llm_api_config"])

    # 步骤5：保存为独立txt文件（处理命名冲突）
    txt_path = _resolve_available_txt_path(dirs["txt_dir"], pdf_filename)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(masked_text)

    # 步骤6：追加写入汇总文件
    append_to_summary(
        dirs["summary_file_path"],
        pdf_filename=pdf_filename,
        text_content=masked_text,
        separator_template=config["separator_template"],
    )

    # 步骤7：归档PDF原件到pdf_dir
    archive_pdf(pdf_path, dirs["pdf_dir"])


def run_resume_processing(config_path: str) -> None:
    """
    主流程入口：加载配置→创建输出目录→初始化日志→初始化汇总文件→
    遍历处理所有PDF→打印最终统计信息→自动复制汇总内容到剪贴板。

    :param config_path: config.json配置文件的完整路径
    :return: None
    """
    try:
        config = load_config(config_path)
    except ConfigError as e:
        print(f"❌ 配置加载失败，程序无法继续：{e}")
        return

    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    dirs = create_output_structure(config["output_folder"], timestamp=timestamp)

    output_folder = config["output_folder"]
    os.makedirs(output_folder, exist_ok=True)
    summary_filename = f"简历汇总文本_{timestamp}.txt"
    dirs["summary_file_path"] = os.path.join(output_folder, summary_filename)

    logger = init_logger(dirs["log_file_path"])
    logger.info("===== 简历批量处理流程启动 =====")
    logger.info(f"输出目录: {dirs['base_dir']}")
    logger.info(f"汇总文本文件路径（output根目录）: {dirs['summary_file_path']}")

    init_summary_file(dirs["summary_file_path"], config["llm_prompt_text"])

    input_folder = config["input_folder"]
    pdf_paths = _list_top_level_pdfs(input_folder)
    total_count = len(pdf_paths)
    logger.info(f"在输入目录 {input_folder} 顶层发现 {total_count} 份PDF文件")

    success_count = 0
    failed_items = []

    for pdf_path in pdf_paths:
        pdf_filename = os.path.basename(pdf_path)
        print(f"\n处理中: {pdf_filename} ...")
        logger.info(f"开始处理: {pdf_filename}")

        try:
            _process_single_pdf(pdf_path, config, dirs, logger)
        except (PDFReadError, MinerUProcessError) as e:
            reason = str(e)
            logger.error(f"[{pdf_filename}] 处理失败: {reason}")
            print(
                f"❌ [跳过] {pdf_filename} 处理失败：{reason}\n"
                f"   该文件仍保留在原始输入文件夹中，未被移动，请手动检查。"
            )
            failed_items.append((pdf_filename, reason))
            continue
        except Exception as e:
            reason = f"未预期的错误: {e}"
            logger.error(f"[{pdf_filename}] 处理失败: {reason}")
            print(
                f"❌ [跳过] {pdf_filename} 处理失败：{reason}\n"
                f"   该文件仍保留在原始输入文件夹中，未被移动，请手动检查。"
            )
            failed_items.append((pdf_filename, reason))
            continue

        success_count += 1
        logger.info(f"[{pdf_filename}] 处理成功")
        print(f"✅ {pdf_filename} 处理成功")

    failed_count = len(failed_items)

    summary_lines = [
        "\n" + "=" * 50,
        "处理完成，统计结果如下：",
        f"  共发现PDF文件: {total_count} 份",
        f"  成功处理: {success_count} 份",
        f"  失败: {failed_count} 份",
        f"  汇总文本文件位置: {dirs['summary_file_path']}",
    ]

    if failed_items:
        summary_lines.append("  失败文件列表（均仍保留在原始输入文件夹中，请手动检查）：")
        for filename, reason in failed_items:
            summary_lines.append(f"    - {filename}：{reason}")

    summary_text = "\n".join(summary_lines)
    print(summary_text)
    logger.info(summary_text)

    if success_count > 0:
        try:
            with open(dirs["summary_file_path"], "r", encoding="utf-8") as f:
                final_summary_content = f.read()
            copied = copy_text_to_clipboard(final_summary_content)
            if copied:
                print("\n📋 汇总内容已自动复制到剪贴板，可直接 Ctrl+V 粘贴给大模型使用。")
                logger.info("汇总内容已成功复制到剪贴板")
            else:
                print(f"\n请手动打开以下文件复制内容：\n  {dirs['summary_file_path']}")
        except Exception as e:
            print(f"\n⚠️  读取汇总文件用于复制到剪贴板时出错：{e}")
            print(f"请手动打开以下文件复制内容：\n  {dirs['summary_file_path']}")
    else:
        print("\n⚠️  本次没有成功处理任何文件，跳过复制到剪贴板。")

    logger.info("===== 简历批量处理流程结束 =====")


if __name__ == "__main__":
    _default_config_path = os.path.join(_SCRIPT_ROOT_DIR, "config.json")

    if len(sys.argv) > 1:
        _config_path = sys.argv[1]
    else:
        _config_path = _default_config_path

    print(f"使用配置文件: {_config_path}")
    run_resume_processing(_config_path)