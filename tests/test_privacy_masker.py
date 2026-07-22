"""
test_privacy_masker.py

privacy_masker 模块的独立测试脚本。

设计说明：
    本脚本对每个测试用例都会【打印输入文本和处理后的输出文本】，
    方便你直接肉眼核对替换是否符合预期；同时每个用例都带有assert断言，
    自动判断结果是否正确，最终打印 "全部测试通过" 或明确指出哪个用例失败。

运行方式：
    python test_privacy_masker.py
"""

from privacy_masker import mask_privacy_info


_PHONE_PLACEHOLDER = "[出于隐私保护，已删去]"
_EMAIL_PLACEHOLDER = "[出于隐私保护，已删去]"


def run_case(case_name: str, input_text: str, expected_output: str) -> None:
    """运行单个测试用例，打印输入输出，并断言结果与期望一致"""
    actual_output = mask_privacy_info(
        input_text,
        phone_placeholder=_PHONE_PLACEHOLDER,
        email_placeholder=_EMAIL_PLACEHOLDER,
    )

    print(f"【测试用例】{case_name}")
    print(f"  输入: {input_text}")
    print(f"  输出: {actual_output}")

    assert actual_output == expected_output, (
        f"用例【{case_name}】失败！\n"
        f"  期望输出: {expected_output}\n"
        f"  实际输出: {actual_output}"
    )
    print("  结果: ✅ PASS\n")


def main():
    # 用例1：标准手机号，验证被正确替换
    run_case(
        case_name="标准手机号替换",
        input_text="联系电话：13312341234，请尽快联系。",
        expected_output=f"联系电话：{_PHONE_PLACEHOLDER}，请尽快联系。",
    )

    # 用例2：手机号被更长数字串包裹，验证不会误匹配
    # 构造一个18位身份证号，中间恰好嵌套一段符合"1[3-9]开头+9位数字"特征的11位子串
    # 身份证号: 110105 199001133112 34  (共18位，中间"19900113311"恰好是"1"开头的11位，
    # 但因为前后紧邻其他数字，不应被当作手机号处理)
    id_number = "110105199001133112" + "34"  # 20位数字串，人为构造，确保比11位长
    run_case(
        case_name="手机号被更长数字串包裹，不应误匹配",
        input_text=f"身份证号：{id_number}，请核对。",
        expected_output=f"身份证号：{id_number}，请核对。",  # 原样不变
    )

    # 用例3：多种格式邮箱地址，验证被正确替换
    run_case(
        case_name="多种格式邮箱替换",
        input_text="邮箱1: test@qq.com 邮箱2: test.name@company.co.cn",
        expected_output=f"邮箱1: {_EMAIL_PLACEHOLDER} 邮箱2: {_EMAIL_PLACEHOLDER}",
    )

    # 用例4：手机号和邮箱同时存在，验证两者都被处理，其余文本不受影响
    run_case(
        case_name="手机号与邮箱同时存在，其余文本不受影响",
        input_text="姓名：张三，电话：15912345678，邮箱：zhangsan@example.com，工作经验：5年。",
        expected_output=(
            f"姓名：张三，电话：{_PHONE_PLACEHOLDER}，"
            f"邮箱：{_EMAIL_PLACEHOLDER}，工作经验：5年。"
        ),
    )

    # 用例5：不包含任何手机号或邮箱，验证原文本原样返回
    run_case(
        case_name="不含隐私信息，原文本应原样返回",
        input_text="教育背景：某大学计算机科学与技术专业，本科学历。",
        expected_output="教育背景：某大学计算机科学与技术专业，本科学历。",
    )

    # 额外补充用例：手机号前后紧邻非数字字符（如中文、标点），应正常匹配替换
    run_case(
        case_name="手机号前后紧邻中文/标点，应正常替换",
        input_text="（手机号：13812345678）备用号码：18600001111。",
        expected_output=f"（手机号：{_PHONE_PLACEHOLDER}）备用号码：{_PHONE_PLACEHOLDER}。",
    )

    print("=" * 50)
    print("全部测试通过 ✅")


if __name__ == "__main__":
    main()