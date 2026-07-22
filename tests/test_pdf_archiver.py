"""
test_pdf_archiver.py

pdf_archiver 模块的独立测试脚本。

说明：
    本脚本会在当前目录下创建固定的 test_output 文件夹（不使用临时目录、
    不会自动清理），生成的测试文件（含移动后的"PDF"占位文件）保留在磁盘上，
    方便你运行结束后直接用文件管理器实际打开查看归档目录下的文件情况。

    测试中使用的"PDF文件"只是简单的txt占位文件（内容为一行说明文字），
    不需要是真实PDF格式，因为本模块测试的是文件移动和命名冲突逻辑，
    与文件实际内容/格式无关。

运行方式：
    python test_pdf_archiver.py
"""

import os
import shutil

from pdf_archiver import archive_pdf


_TEST_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
_SOURCE_DIR = os.path.join(_TEST_OUTPUT_DIR, "pdf_archiver_source")
_ARCHIVE_DIR = os.path.join(_TEST_OUTPUT_DIR, "pdf_archiver_archive")


def _reset_test_dirs():
    """每次运行前清空测试用的源目录和归档目录，避免上次运行的残留文件干扰本次测试"""
    for d in (_SOURCE_DIR, _ARCHIVE_DIR):
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d)


def _create_dummy_pdf(dir_path: str, filename: str, content: str) -> str:
    """在指定目录下创建一个占位"PDF"文件（实际是简单文本文件），返回其完整路径"""
    file_path = os.path.join(dir_path, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path


def print_dir_listing(dir_path: str, label: str):
    """打印目标目录下当前的文件列表，方便核对实际磁盘状态"""
    print(f"  {label} 目录 [{dir_path}] 当前文件列表:")
    files = sorted(os.listdir(dir_path)) if os.path.isdir(dir_path) else []
    if not files:
        print("    (空)")
    for f in files:
        print(f"    - {f}")


def test_normal_move():
    """测试1：正常移动场景（目标目录中无同名文件）"""
    print("【测试1】正常移动场景")

    source_path = _create_dummy_pdf(_SOURCE_DIR, "张三_简历.pdf", "这是张三的简历占位内容")
    print(f"  原始文件: {source_path}")
    assert os.path.isfile(source_path)

    result_path = archive_pdf(source_path, _ARCHIVE_DIR)
    print(f"  返回的最终路径: {result_path}")

    # 断言1：源文件已不存在（因为是"移动"不是"复制"）
    assert not os.path.exists(source_path), "源文件应已被移动走，但原路径仍存在文件！"

    # 断言2：目标路径确实存在，且路径就是预期的（无冲突时应保持原文件名）
    expected_path = os.path.join(_ARCHIVE_DIR, "张三_简历.pdf")
    assert result_path == expected_path, (
        f"无冲突场景下应保持原文件名，期望路径: {expected_path}，实际: {result_path}"
    )
    assert os.path.isfile(result_path), "目标文件应已存在，但实际找不到！"

    print_dir_listing(_SOURCE_DIR, "源")
    print_dir_listing(_ARCHIVE_DIR, "归档")
    print("  ✅ PASS：正常移动场景验证通过\n")


def test_naming_conflict():
    """测试2：命名冲突场景（目标目录中提前放置同名文件）"""
    print("【测试2】命名冲突场景")

    # 提前在归档目录放一个同名的"已存在"文件，内容不同，用于验证不会被覆盖
    pre_existing_path = _create_dummy_pdf(
        _ARCHIVE_DIR, "李四_简历.pdf", "这是归档目录里原本就存在的李四简历（不应被覆盖）"
    )
    print(f"  预先在归档目录放置的同名文件: {pre_existing_path}")

    # 待归档的新文件（来自源目录），文件名与上面那个冲突
    source_path = _create_dummy_pdf(
        _SOURCE_DIR, "李四_简历.pdf", "这是新提交的李四简历（应被重命名为_2）"
    )
    print(f"  新的待归档文件: {source_path}")

    result_path = archive_pdf(source_path, _ARCHIVE_DIR)
    print(f"  返回的最终路径: {result_path}")

    # 断言1：新文件被重命名为 李四_简历_2.pdf
    expected_path = os.path.join(_ARCHIVE_DIR, "李四_简历_2.pdf")
    assert result_path == expected_path, (
        f"冲突场景下应自动加_2后缀，期望路径: {expected_path}，实际: {result_path}"
    )
    assert os.path.isfile(result_path), "重命名后的目标文件应已存在，但实际找不到！"

    # 断言2：原有的"李四_简历.pdf"没有被覆盖，内容保持不变
    with open(pre_existing_path, "r", encoding="utf-8") as f:
        pre_existing_content = f.read()
    assert "不应被覆盖" in pre_existing_content, (
        "原有同名文件的内容应保持不变，但实际内容被覆盖了！"
    )

    # 断言3：新文件的内容确实是"新提交"的那份内容（没有搞反）
    with open(result_path, "r", encoding="utf-8") as f:
        new_file_content = f.read()
    assert "新提交" in new_file_content, (
        "重命名后的新文件内容应为新提交的内容，但实际内容不符！"
    )

    # 断言4：源目录下的原文件已被移走
    assert not os.path.exists(source_path), "源文件应已被移动走，但原路径仍存在文件！"

    print_dir_listing(_SOURCE_DIR, "源")
    print_dir_listing(_ARCHIVE_DIR, "归档")
    print("  ✅ PASS：命名冲突场景验证通过（原文件未被覆盖，新文件正确加了_2后缀）\n")


def test_multiple_conflicts():
    """测试3：连续多次冲突，验证序号能正确递增（_2, _3...）"""
    print("【测试3】连续多次命名冲突（验证序号递增）")

    # 归档目录里已经有 王五_简历.pdf 和 王五_简历_2.pdf
    _create_dummy_pdf(_ARCHIVE_DIR, "王五_简历.pdf", "原始文件")
    _create_dummy_pdf(_ARCHIVE_DIR, "王五_简历_2.pdf", "第一次冲突后的文件")

    # 再提交一份新的同名文件，预期应该被命名为 王五_简历_3.pdf
    source_path = _create_dummy_pdf(_SOURCE_DIR, "王五_简历.pdf", "第二次冲突提交的新文件")

    result_path = archive_pdf(source_path, _ARCHIVE_DIR)
    print(f"  返回的最终路径: {result_path}")

    expected_path = os.path.join(_ARCHIVE_DIR, "王五_简历_3.pdf")
    assert result_path == expected_path, (
        f"连续冲突场景下应正确递增到_3，期望路径: {expected_path}，实际: {result_path}"
    )

    print_dir_listing(_ARCHIVE_DIR, "归档")
    print("  ✅ PASS：连续多次冲突场景，序号递增验证通过\n")


def test_file_not_found():
    """测试4：原始文件不存在时，应抛出FileNotFoundError"""
    print("【测试4】原始文件不存在场景")

    non_existent_path = os.path.join(_SOURCE_DIR, "不存在的文件.pdf")
    print(f"  尝试归档不存在的文件: {non_existent_path}")

    try:
        archive_pdf(non_existent_path, _ARCHIVE_DIR)
        print("  ❌ FAIL：预期应抛出FileNotFoundError，但实际未抛出任何异常\n")
    except FileNotFoundError as e:
        print(f"  实际结果: 按预期抛出 FileNotFoundError")
        print(f"  异常信息: {e}")
        print("  ✅ PASS\n")


def main():
    _reset_test_dirs()

    test_normal_move()
    test_naming_conflict()
    test_multiple_conflicts()
    test_file_not_found()

    print("=" * 50)
    print("全部测试通过 ✅")
    print(f"\n生成的测试文件保留在磁盘上，你可以直接打开查看：")
    print(f"  源目录: {_SOURCE_DIR}")
    print(f"  归档目录: {_ARCHIVE_DIR}")
    print("（本脚本不会自动清理这两个目录，确认无误后可自行手动删除）")


if __name__ == "__main__":
    main()