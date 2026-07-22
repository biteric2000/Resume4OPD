"""
test_pdf_type_checker_watermark_pattern.py

验证watermark_patterns正则过滤功能：
    1. 确认已知的4条水印样本，全部能被正则正确匹配删除
    2. 【关键】构造一条"从未出现过的、全新随机ID"的水印（但符合同一模板），
       验证正则能自动识别，无需手动加入watermark_strings列表
    3. 确认正则不会误伤真实简历文本内容
"""

import re

from pdf_type_checker import _strip_watermarks


_WATERMARK_PATTERN = r"[0-9a-f]{16}1HJ-[0-9A-Za-z_-]{16}WOGhm_XVPhJi2Q~~"

_KNOWN_WATERMARKS = [
    "77a2a110dba8a1581HJ-2Nu-GVZZwYm2UPuaWOGhm_XVPhJi2Q~~",
    "28c33a2a234787761HJ-3N-7EVNSy424VvKdWOGhm_XVPhJi2Q~~",
    "c81da26d749977cb1HJ-3N6_EFBXxI2-UvOdWOGhm_XVPhJi2Q~~",
    "a201af095a41390c1HJ-3N6_EVdYxYm4UP6eWOGhm_XVPhJi2Q~~",
]

# 手动构造一条"全新"的、从未在配置文件中出现过的水印，
# 只是随机ID部分不同，用来验证正则的【泛化能力】
_NEVER_SEEN_WATERMARK = "f00dbeef1234abcd1HJ-9Zx_QwErTy56LmNoWOGhm_XVPhJi2Q~~"


def test_all_known_watermarks_match():
    print("【测试1】已知4条水印样本，逐条验证能否被正则匹配删除")
    for i, watermark in enumerate(_KNOWN_WATERMARKS, start=1):
        text_with_watermark = f"这是页面内容。{watermark}"
        cleaned = _strip_watermarks(
            text_with_watermark, watermark_patterns=[_WATERMARK_PATTERN]
        )
        print(f"  样本{i}: {watermark}")
        print(f"    过滤后: {cleaned!r}")
        assert watermark not in cleaned, f"样本{i}未被正确过滤"
    print("  ✅ PASS：4条已知水印全部被正确过滤\n")


def test_never_seen_watermark_still_matches():
    print("【测试2，关键测试】全新未见过的水印（同模板，随机ID不同）")
    print(f"  该水印从未出现在watermark_strings配置中: {_NEVER_SEEN_WATERMARK}")

    text_with_watermark = f"简历正文内容。{_NEVER_SEEN_WATERMARK}"
    cleaned = _strip_watermarks(
        text_with_watermark, watermark_patterns=[_WATERMARK_PATTERN]
    )
    print(f"  过滤后: {cleaned!r}")

    assert _NEVER_SEEN_WATERMARK not in cleaned, (
        "全新水印未被正则捕获，说明正则泛化能力不足"
    )
    print("  ✅ PASS：全新水印同样被正则自动识别并过滤，无需手动加入配置\n")


def test_real_content_not_affected():
    print("【测试3】确认正则不会误伤真实简历文本")
    real_text = (
        "姓名：测试候选人\n"
        "工作经验：5年AI全栈开发经验。\n"
        "项目编号：ABCD1234EFGH5678-测试项目\n"  # 故意构造一段容易混淆的文本
    )
    cleaned = _strip_watermarks(real_text, watermark_patterns=[_WATERMARK_PATTERN])
    print(f"  原文: {real_text!r}")
    print(f"  过滤后: {cleaned!r}")
    assert cleaned == real_text, "正则误伤了真实简历文本，需要检查正则精确度"
    print("  ✅ PASS：真实文本未被误伤\n")


def main():
    test_all_known_watermarks_match()
    test_never_seen_watermark_still_matches()
    test_real_content_not_affected()
    print("=" * 50)
    print("全部测试通过 ✅")
    print("\n结论：该正则表达式可以覆盖同模板的所有过去和未来水印实例，")
    print("以后遇到该平台生成的新水印ID，无需再手动修改config.json。")


if __name__ == "__main__":
    main()