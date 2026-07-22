"""
test_llm_analyzer.py

llm_analyzer 模块的独立测试脚本。

运行方式：
    python test_llm_analyzer.py
"""

from llm_analyzer import call_llm_analysis


def test_disabled_case():
    """测试1：enabled=False（默认场景），应静默返回None，不打印任何提示"""
    print("【测试1】enabled=False（默认场景）")

    config = {
        "enabled": False,
        "api_endpoint": "",
        "api_key": "",
        "model_name": "",
    }

    print("  调用中（预期不应有任何[llm_analyzer]提示信息打印出来）：")
    result = call_llm_analysis("这是一段测试文本", config)

    print(f"  返回值: {result!r}")
    assert result is None, f"enabled=False时应返回None，实际返回: {result!r}"
    print("  ✅ PASS：返回值为None，符合预期\n")


def test_enabled_case():
    """测试2：enabled=True（未来预留场景），应打印提示信息，且仍返回None"""
    print("【测试2】enabled=True（未来预留场景，当前仍未真正实现）")

    config = {
        "enabled": True,
        "api_endpoint": "https://example.com/api/v1/chat",
        "api_key": "sk-test-fake-key",
        "model_name": "test-model-v1",
    }

    print("  调用中（预期应看到下方出现一行[llm_analyzer]提示信息）：")
    result = call_llm_analysis("这是一段测试文本", config)

    print(f"  返回值: {result!r}")
    assert result is None, f"enabled=True时（占位阶段）也应返回None，实际返回: {result!r}"
    print("  ✅ PASS：返回值为None，且上方应已打印提示信息，请人工核对\n")


def test_missing_enabled_key():
    """测试3：容错性验证——如果配置字典中缺失enabled键，应视为False处理，不报错"""
    print("【测试3】配置字典中缺失'enabled'键（容错性验证）")

    incomplete_config = {
        "api_endpoint": "",
        "api_key": "",
        "model_name": "",
    }

    result = call_llm_analysis("这是一段测试文本", incomplete_config)

    print(f"  返回值: {result!r}")
    assert result is None, f"缺失enabled键时应视为False并返回None，实际返回: {result!r}"
    print("  ✅ PASS：缺失enabled键时未报错，且正确视为False处理\n")


def main():
    test_disabled_case()
    test_enabled_case()
    test_missing_enabled_key()

    print("=" * 50)
    print("全部测试通过 ✅")
    print("\n请重点人工核对：【测试1】的调用过程中，控制台上方是否【没有】出现")
    print("任何[llm_analyzer]开头的提示信息；而【测试2】的调用过程中，")
    print("控制台上方是否【确实出现了】一行[llm_analyzer]提示信息。")


if __name__ == "__main__":
    main()