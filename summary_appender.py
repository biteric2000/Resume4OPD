"""
summary_appender.py

汇总文件追加写入模块：将单份PDF的处理结果（分隔符+文本内容）
以追加模式写入汇总txt文件。
"""


def append_to_summary(
    summary_file_path: str,
    pdf_filename: str,
    text_content: str,
    separator_template: str,
) -> None:
    """
    将单份PDF的处理结果追加写入汇总文件。

    :param summary_file_path: 汇总txt文件的完整路径（该文件应已由
                               init_summary_file 初始化，此函数只做追加）
    :param pdf_filename: 当前处理的PDF文件名，用于填入分隔符模板
    :param text_content: 该PDF提取并脱敏后的文本内容
    :param separator_template: 分隔符模板字符串，包含 {filename} 占位符，
                                如 "\n========== 简历: {filename} ==========\n"
    :return: None
    """
    separator_text = separator_template.format(filename=pdf_filename)

    with open(summary_file_path, "a", encoding="utf-8") as f:
        f.write(separator_text)
        f.write(text_content)
        f.write("\n")