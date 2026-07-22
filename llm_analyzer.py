"""
llm_analyzer.py

大模型调用占位模块：本次不实现实际的API调用逻辑，仅预留未来功能接口，
保证主流程调用方式提前固定下来，后续接入真实大模型时无需改动上层代码。
"""

from typing import Optional


def call_llm_analysis(text: str, llm_api_config: dict) -> Optional[str]:
    """
    调用大模型对文本进行分析（当前为占位实现，尚未接入真实API）。

    未来实现说明：
        如果要接入真实的大模型API调用，只需要替换本函数【内部】的实现逻辑
        （例如改为使用 requests/httpx 等库，根据
        llm_api_config["api_endpoint"]、llm_api_config["api_key"]、
        llm_api_config["model_name"] 发起真实HTTP请求，将响应结果解析后
        作为字符串返回），函数的输入参数和返回值类型保持不变，
        上层调用代码完全不需要任何修改。

    :param text: 待分析的文本内容（如已脱敏的简历文本）
    :param llm_api_config: 大模型API配置字典，参考模块1配置结构，
                            应包含以下键："enabled"、"api_endpoint"、
                            "api_key"、"model_name"
    :return: 当前阶段始终返回 None（无论enabled为True还是False）：
             - enabled为False时：静默返回None，不做任何输出
             - enabled为True时：打印提示信息说明功能尚未实现，然后返回None
             - 均不会抛出异常，确保主流程不会因本占位功能而中断
    """
    if not llm_api_config.get("enabled", False):
        return None

    print(
        "[llm_analyzer] 提示：大模型调用功能尚未实现（当前为占位模块）。"
        f" 配置中已启用（enabled=True），但暂不会发起实际API请求。"
        f" 配置的model_name为：{llm_api_config.get('model_name')}"
    )
    return None