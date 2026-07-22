"""
test_output_structure.py

output_structure 模块的独立测试脚本。

运行方式：
    python test_output_structure.py
"""

import os
import shutil
import tempfile

from output_structure import create_output_structure


def print_result_and_verify(result: dict, label: str):
    """打印返回字典内容，并实际检查磁盘上对应目录/路径是否符合预期"""
    print(f"【{label}】返回结果：")
    for key, value in result.items():
        print(f"  {key}: {value}")

    print(f"  磁盘核对：")
    for dir_key in ("base_dir", "pdf_dir", "txt_dir"):
        exists = os.path.isdir(result[dir_key])
        status = "✅ 存在" if exists else "❌ 不存在"
        print(f"    {dir_key} 实际是否存在: {status}")
        assert exists, f"{dir_key} 应该已被创建，但实际不存在！"

    # summary_file_path 和 log_file_path 本模块不应创建文件，只返回路径
    for file_key in ("summary_file_path", "log_file_path"):
        exists = os.path.isfile(result[file_key])
        status = "不存在（符合预期，本模块不创建文件）" if not exists else "❌ 意外地已存在"
        print(f"    {file_key} 实际是否存在: {status}")
        assert not exists, f"{file_key} 不应被本模块创建，但实际已存在文件！"

    print()


def test_basic_creation(tmp_output_folder: str):
    """测试1：基本调用，使用自动生成的当前时间时间戳"""
    result = create_output_structure(tmp_output_folder)
    print_result_and_verify(result, "测试1：自动生成时间戳")
    return result


def test_timestamp_conflict(tmp_output_folder: str):
    """
    测试2：连续两次调用传入相同的timestamp，模拟时间戳冲突场景，
    验证第二次调用会自动加上_2后缀，且不会报错。
    """
    fixed_timestamp = "202607301158"

    result1 = create_output_structure(tmp_output_folder, timestamp=fixed_timestamp)
    print_result_and_verify(result1, "测试2-第1次调用（固定timestamp）")

    result2 = create_output_structure(tmp_output_folder, timestamp=fixed_timestamp)
    print_result_and_verify(result2, "测试2-第2次调用（相同timestamp，应自动加_2后缀）")

    # 断言第二次的base_dir确实带有_2后缀，且与第一次不是同一个目录
    assert result1["base_dir"] != result2["base_dir"], (
        "两次调用应生成不同的目录（第二次应加序号后缀），但实际路径相同！"
    )
    assert result2["base_dir"].endswith("_2"), (
        f"第二次调用的base_dir应以'_2'结尾，实际为：{result2['base_dir']}"
    )
    print(f"  ✅ 冲突处理验证通过：")
    print(f"     第1次目录: {result1['base_dir']}")
    print(f"     第2次目录: {result2['base_dir']}\n")

    # 顺便验证第3次调用会加_3后缀，确保序号递增逻辑正确
    result3 = create_output_structure(tmp_output_folder, timestamp=fixed_timestamp)
    assert result3["base_dir"].endswith("_3"), (
        f"第三次调用的base_dir应以'_3'结尾，实际为：{result3['base_dir']}"
    )
    print(f"  ✅ 第3次调用也正确加了'_3'后缀: {result3['base_dir']}\n")


def test_auto_create_output_folder():
    """测试3：output_folder本身不存在时，能自动创建（包括多层父目录）"""
    tmp_parent = tempfile.mkdtemp()
    try:
        non_existent_output_folder = os.path.join(tmp_parent, "a", "b", "c_output")
        assert not os.path.isdir(non_existent_output_folder)

        result = create_output_structure(non_existent_output_folder, timestamp="202607301200")
        print_result_and_verify(result, "测试3：output_folder多层父目录自动创建")

        assert os.path.isdir(non_existent_output_folder), "output_folder本身应已被自动创建"
    finally:
        shutil.rmtree(tmp_parent, ignore_errors=True)


def main():
    tmp_output_folder = tempfile.mkdtemp()
    print(f"本次测试使用的临时output_folder: {tmp_output_folder}\n")

    try:
        test_basic_creation(tmp_output_folder)
        test_timestamp_conflict(tmp_output_folder)
        test_auto_create_output_folder()

        print("=" * 50)
        print("全部测试通过 ✅")
        print(f"\n如需人工肉眼核对目录结构，可在清理前查看：{tmp_output_folder}")
        print("（本脚本运行结束后会自动清理该临时目录）")
    finally:
        shutil.rmtree(tmp_output_folder, ignore_errors=True)


if __name__ == "__main__":
    main()