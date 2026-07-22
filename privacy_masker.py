"""
privacy_masker.py

隐私信息脱敏模块：使用正则表达式识别并替换文本中的中国大陆手机号和邮箱地址。
"""

import re


# 手机号正则：
# (?<!\d) 负向后顾 —— 确保匹配起始处前面不是数字（避免从更长数字串中截取子串误判）
# 1[3-9]\d{2}      —— 号段+前2位，共3位
# [-\s]?           —— 可选的分隔符：短横线"-"或任意空白字符（空格），也可以没有分隔符
# \d{4}            —— 中间4位
# [-\s]?           —— 同上，可选分隔符
# \d{4}            —— 末尾4位
# (?!\d) 负向前瞻  —— 确保匹配结束处后面不是数字
# 该模式可同时兼容以下写法：
#   13012341234      （无分隔符，连续11位）
#   130-1234-1234    （短横线分隔）
#   177 1234 1234    （空格分隔）
#   130-1234 1234    （混合分隔符，也能兼容）
_PHONE_PATTERN = re.compile(r"(?<!\d)1[3-9]\d{2}[-\s]?\d{4}[-\s]?\d{4}(?!\d)")

# 邮箱正则：本地部分（字母/数字/常见符号）+ @ + 域名（可多级）+ 顶级域名（至少2个字母）
_EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


def mask_privacy_info(
    text: str,
    phone_placeholder: str = "[出于隐私保护，已删去]",
    email_placeholder: str = "[出于隐私保护，已删去]",
) -> str:
    """
    对文本中的中国大陆手机号和邮箱地址进行脱敏替换。

    :param text: 待处理的原始文本
    :param phone_placeholder: 手机号替换为的占位文本
    :param email_placeholder: 邮箱替换为的占位文本
    :return: 脱敏后的文本；如果原文本中不存在手机号或邮箱，原样返回
    """
    # 先处理邮箱，再处理手机号（两者特征互斥，顺序对结果无实际影响，此处仅为保守起见）
    masked_text = _EMAIL_PATTERN.sub(email_placeholder, text)
    masked_text = _PHONE_PATTERN.sub(phone_placeholder, masked_text)
    return masked_text