"""
test_summary_appender.py

summary_appender 模块的独立测试脚本。

说明：
    本脚本会在当前目录下创建固定的 test_output 文件夹（不使用临时目录、
    不会自动清理），生成的测试文件保留在磁盘上，方便你运行结束后
    直接用文本编辑器打开实际核对追加内容的分隔符格式是否清晰易读。

运行方式：
    python test_summary_appender.py
"""

import os

from summary_appender import append_to_summary


_TEST_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
_SEPARATOR_TEMPLATE = "\n========== 简历: {filename} ==========\n"


def main():
    os.makedirs(_TEST_OUTPUT_DIR, exist_ok=True)

    summary_file_path = os.path.join(_TEST_OUTPUT_DIR, "汇总追加测试.txt")

    # 每次运行前先清空旧文件，避免多次运行导致内容一直累加，干扰核对
    if os.path.isfile(summary_file_path):
        os.remove(summary_file_path)

    print(f"测试文件路径: {summary_file_path}\n")

    # 模拟第1份简历
    print("【第1次调用】追加张三的简历内容")
    append_to_summary(
        summary_file_path,
        pdf_filename="张三_简历.pdf",
        text_content="姓名：张三\n电话：[出于隐私保护，已删去]\n工作经验：5年后端开发。",
        separator_template=_SEPARATOR_TEMPLATE,
    )

    # 模拟第2份简历
    print("【第2次调用】追加李四的简历内容")
    append_to_summary(
        summary_file_path,
        pdf_filename="李四_简历.pdf",
        text_content="姓名：李四\n邮箱：[出于隐私保护，已删去]\n工作经验：3年前端开发。",
        separator_template=_SEPARATOR_TEMPLATE,
    )

    # 读取最终文件内容并完整打印
    with open(summary_file_path, "r", encoding="utf-8") as f:
        final_content = f.read()

    print("\n----- 最终文件完整内容（原样打印） -----")
    print(final_content)
    print("----- 文件内容结束 -----\n")

    print("----- 最终文件内容（repr形式，可看清所有换行符位置） -----")
    print(repr(final_content))
    print("----- repr结束 -----\n")

    # 基本断言：两份简历的关键内容都应出现在最终文件中
    assert "张三" in final_content, "张三的内容应出现在汇总文件中"
    assert "李四" in final_content, "李四的内容应出现在汇总文件中"
    assert "张三_简历.pdf" in final_content, "分隔符中应包含张三的PDF文件名"
    assert "李四_简历.pdf" in final_content, "分隔符中应包含李四的PDF文件名"

    # 断言两份内容出现的顺序正确（张三在前，李四在后）
    zhang_index = final_content.index("张三")
    li_index = final_content.index("李四")
    assert zhang_index < li_index, "张三的内容应先于李四的内容出现（追加顺序）"

    print("✅ 自动化断言全部通过")
    print(f"\n生成的测试文件保留在磁盘上，请直接打开查看：")
    print(f"  {summary_file_path}")
    print("请人工核对：两次追加内容之间的分隔符是否清晰、换行是否合理、无粘连或多余空行。")


if __name__ == "__main__":
    main()