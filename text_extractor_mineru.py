"""
text_extractor_mineru.py

图片型PDF的OCR提取模块：调用本地已部署的MinerU（vlm后端）命令行工具，
将PDF转换为文本/Markdown内容。

调用命令格式：mineru -p <PDF路径> -o <输出目录> -b vlm-engine
"""

import os
import subprocess
from typing import List, Tuple


class MinerUProcessError(Exception):
    """表示调用MinerU命令行处理PDF过程中发生的错误
    （命令未找到、执行超时、返回非0退出码、找不到输出结果文件等）。"""
    pass


def _run_mineru_command(
    pdf_path: str, work_dir: str, timeout_seconds: int
) -> subprocess.CompletedProcess:
    """执行mineru命令行调用，返回CompletedProcess对象（包含stdout/stderr/returncode）"""
    command = ["mineru", "-p", pdf_path, "-o", work_dir, "-b", "vlm-engine"]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as e:
        stdout_partial = e.stdout if e.stdout else "(无)"
        stderr_partial = e.stderr if e.stderr else "(无)"
        raise MinerUProcessError(
            f"MinerU处理超时（超过{timeout_seconds}秒）：{pdf_path}\n"
            f"超时前已捕获的stdout：{stdout_partial}\n"
            f"超时前已捕获的stderr：{stderr_partial}"
        ) from e
    except FileNotFoundError as e:
        raise MinerUProcessError(
            f"找不到mineru命令，请确认：\n"
            f"  1) 已正确安装MinerU；\n"
            f"  2) 当前运行本程序所用的虚拟环境已激活（与安装MinerU时使用的环境一致）；\n"
            f"  3) mineru命令确实在当前PATH中可用（可在命令行手动执行 'mineru --version' 验证）。\n"
            f"原始错误：{e}"
        ) from e

    if result.returncode != 0:
        raise MinerUProcessError(
            f"MinerU处理失败，退出码：{result.returncode}，PDF路径：{pdf_path}\n"
            f"stdout：{result.stdout}\n"
            f"stderr：{result.stderr}"
        )

    return result


def _extract_warnings(stdout: str, stderr: str) -> List[str]:
    """从stdout和stderr中提取所有包含"warning"关键字（不区分大小写）的行"""
    warnings: List[str] = []
    for stream_content in (stdout, stderr):
        if not stream_content:
            continue
        for line in stream_content.splitlines():
            if "warning" in line.lower():
                stripped_line = line.strip()
                if stripped_line:
                    warnings.append(stripped_line)
    return warnings


def _locate_output_file(work_dir: str, pdf_path: str) -> str:
    """
    在work_dir目录下递归查找MinerU生成的结果文件（.md或.txt）。

    定位策略（因MinerU不同版本/后端的输出目录结构可能不同，采用较宽松的匹配）：
        1. 递归收集work_dir下所有.md/.txt文件
        2. 优先选择文件名（不含后缀）与PDF文件名完全一致的文件
        3. 如果没有精确匹配但只找到唯一候选文件，直接使用该文件
        4. 如果有多个候选文件又无精确匹配，取最近修改时间的文件作为保底
        5. 如果一个候选文件都没找到，抛出MinerUProcessError并提示检查目录结构
    """
    pdf_stem = os.path.splitext(os.path.basename(pdf_path))[0]

    candidate_files = []
    for root, _dirs, files in os.walk(work_dir):
        for filename in files:
            if filename.lower().endswith((".md", ".txt")):
                candidate_files.append(os.path.join(root, filename))

    if not candidate_files:
        raise MinerUProcessError(
            f"MinerU命令执行成功（退出码0），但在输出目录中未找到任何.md/.txt结果文件："
            f"{work_dir}（PDF：{pdf_path}）。\n"
            f"请检查MinerU实际生成的目录结构是否与本模块的查找逻辑不匹配，"
            f"并将该目录下的实际文件树结构反馈给开发者以便调整定位逻辑。"
        )

    exact_matches = [
        f for f in candidate_files
        if os.path.splitext(os.path.basename(f))[0] == pdf_stem
    ]
    if exact_matches:
        return exact_matches[0]

    if len(candidate_files) == 1:
        return candidate_files[0]

    # 多个候选且无精确匹配，取最近修改的文件作为保底策略
    candidate_files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
    return candidate_files[0]


def extract_text_via_mineru(
    pdf_path: str, work_dir: str, timeout_seconds: int = 600
) -> Tuple[str, List[str]]:
    """
    调用本地MinerU（vlm后端）命令行工具，将图片型PDF转换为文本内容。

    :param pdf_path: 待处理PDF文件路径
    :param work_dir: MinerU输出目录（若不存在会自动创建）
    :param timeout_seconds: 命令执行超时时间（秒），默认600秒
    :return: (text_content, warnings) 元组
             text_content: 从MinerU生成的.md/.txt结果文件中读取的完整文本内容
             warnings: 从命令执行过程中的stdout/stderr里提取出的、
                       包含"warning"关键字（不区分大小写）的行组成的列表
    :raises MinerUProcessError: 命令未找到、执行超时、返回非0退出码、
                                 或找不到输出结果文件时抛出，异常信息中
                                 包含PDF路径和具体错误详情
    """
    os.makedirs(work_dir, exist_ok=True)

    result = _run_mineru_command(pdf_path, work_dir, timeout_seconds)
    warnings = _extract_warnings(result.stdout, result.stderr)

    output_file_path = _locate_output_file(work_dir, pdf_path)

    with open(output_file_path, "r", encoding="utf-8") as f:
        text_content = f.read()

    return text_content, warnings