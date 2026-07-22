"""
test_summary_file_initializer.py

summary_file_initializer 模块的独立测试脚本。

说明：
    本脚本会在当前目录下创建一个固定的 test_output 文件夹（不使用临时目录、
    不会自动清理），生成的测试文件会保留在磁盘上，方便你运行结束后
    直接用文件管理器/文本编辑器打开实际核对文件内容和换行格式，
    确认无误后可自行手动删除该文件夹。

运行方式：
    python test_summary_file_initializer.py
"""

import os

from summary_file_initializer import init_summary_file


_TEST_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")


def test_basic_init():
    """测试1：基本调用，验证文件内容与prompt_text一致，且自动创建父目录"""
    test_prompt_text = (
        "你是一个简历信息提取助手，请根据以下简历内容提取姓名、电话、"
        "教育背景、工作经历等关键信息，并按指定格式输出。"
    )

    summary_file_path = os.path.join(
        _TEST_OUTPUT_DIR, "sub_dir", "简历汇总文本_测试.txt"
    )

    print("【测试用例】基本调用，写入提示词文本")
    print(f"  文件路径: {summary_file_path}")
    print(f"  传入的prompt_text: {test_prompt_text}")

    # 调用前先确认父目录（sub_dir）确实不存在，用于验证"自动创建目录"逻辑
    assert not os.path.isdir(os.path.dirname(summary_file_path)), (
        "测试前置条件有误：sub_dir 目录应该尚不存在"
    )

    init_summary_file(summary_file_path, test_prompt_text)

    # 断言1：父目录已被自动创建
    assert os.path.isdir(os.path.dirname(summary_file_path)), (
        "父目录应已被自动创建，但实际不存在！"
    )

    # 断言2：文件确实已生成
    assert os.path.isfile(summary_file_path), "汇总文件应已生成，但实际不存在！"

    # 读取文件内容，核对是否与预期一致（prompt_text + 一个换行符）
    with open(summary_file_path, "r", encoding="utf-8") as f:
        actual_content = f.read()

    expected_content = test_prompt_text + "\n"

    print(f"  文件实际内容（repr形式，可看清换行符）: {actual_content!r}")
    print(f"  期望内容（repr形式）: {expected_content!r}")

    assert actual_content == expected_content, (
        f"文件内容与预期不一致！\n"
        f"  期望: {expected_content!r}\n"
        f"  实际: {actual_content!r}"
    )
    print("  ✅ PASS：文件内容与预期一致\n")


def test_overwrite_existing_file():
    """测试2：验证覆盖式写入——文件已存在旧内容时，再次调用应完全覆盖而非追加"""
    summary_file_path = os.path.join(_TEST_OUTPUT_DIR, "简历汇总文本_覆盖测试.txt")

    print("【测试用例】覆盖式写入验证")

    # 先写入一段"旧内容"
    init_summary_file(summary_file_path, "这是旧的提示词内容，应该被完全覆盖。")

    # 再写入新内容
    new_prompt_text = "这是新的提示词内容。"
    init_summary_file(summary_file_path, new_prompt_text)

    with open(summary_file_path, "r", encoding="utf-8") as f:
        actual_content = f.read()

    expected_content = new_prompt_text + "\n"

    print(f"  文件实际内容: {actual_content!r}")
    print(f"  期望内容（新内容，不含旧内容残留）: {expected_content!r}")

    assert actual_content == expected_content, (
        "文件内容应被完全覆盖为新内容，但实际检测到旧内容残留或格式不符！"
    )
    print("  ✅ PASS：覆盖式写入验证通过（无旧内容残留）\n")


def main():
    os.makedirs(_TEST_OUTPUT_DIR, exist_ok=True)

    test_basic_init()
    test_overwrite_existing_file()

    print("=" * 50)
    print("全部测试通过 ✅")
    print(f"\n生成的测试文件保留在磁盘上，你可以直接打开查看：")
    print(f"  {_TEST_OUTPUT_DIR}")
    print("（本脚本不会自动清理该目录，确认无误后可自行手动删除）")


if __name__ == "__main__":
    main()