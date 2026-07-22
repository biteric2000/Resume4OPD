"""
config_loader.py

配置加载模块：负责读取JSON格式的配置文件，进行必填字段校验，
并为可选字段填充默认值。

特别说明：
- llm_prompt_text（提示词全文）不直接写在JSON配置文件中，而是通过
  llm_prompt_file 字段指定一个txt文件名（该文件需与config.json放在
  同一目录下），程序会自动读取该文件内容，并将读取结果存入返回字典的
  "llm_prompt_text" 键中，供后续模块直接使用。
  这样设计是为了避免长文本、特殊字符（引号、换行等）写入JSON时
  导致解析失败或转义困难。

- 必填字段（缺失时抛出 ConfigError）：
    input_folder, output_folder, llm_prompt_file, separator_template
- 可选字段（缺失时自动填充默认值，不报错）：
    phone_placeholder, email_placeholder, image_pdf_char_threshold, llm_api_config
"""

import json
import os
from typing import Any


class ConfigError(Exception):
    """配置文件相关错误的自定义异常。"""
    pass


# 必填字段列表（注意：llm_prompt_file 是文件名指针，而非提示词正文本身）
_REQUIRED_FIELDS = [
    "input_folder",
    "output_folder",
    "llm_prompt_file",
    "separator_template",
]

# 可选字段的默认值
_DEFAULT_PHONE_PLACEHOLDER = "[出于隐私保护，已删去]"
_DEFAULT_EMAIL_PLACEHOLDER = "[出于隐私保护，已删去]"
_DEFAULT_IMAGE_PDF_CHAR_THRESHOLD = 50

_DEFAULT_LLM_API_CONFIG = {
    "enabled": False,
    "api_endpoint": "",
    "api_key": "",
    "model_name": "",
}


def _load_prompt_text_from_file(config_path: str, prompt_filename: str) -> str:
    """
    根据 config.json 的路径，拼接出同目录下的提示词txt文件路径并读取其内容。

    :param config_path: 配置文件路径（用于定位同目录）
    :param prompt_filename: 提示词txt文件名（仅文件名，不含目录）
    :return: 文件内容（字符串）
    :raises ConfigError: 文件不存在或读取失败时抛出，说明具体路径和原因
    """
    config_dir = os.path.dirname(os.path.abspath(config_path))
    prompt_path = os.path.join(config_dir, prompt_filename)

    if not os.path.isfile(prompt_path):
        raise ConfigError(
            f"提示词文件不存在：{prompt_path}"
            f"（请确认该文件与config.json位于同一目录，且文件名与"
            f"配置中 llm_prompt_file 字段一致）"
        )

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        raise ConfigError(
            f"提示词文件读取失败：{prompt_path}，错误详情：{e}"
        ) from e


def load_config(config_path: str) -> dict:
    """
    读取指定路径的JSON配置文件，校验必填字段，读取提示词txt文件内容，
    并为可选字段填充默认值。

    :param config_path: 配置文件路径
    :return: 校验并补全默认值后的配置字典。其中 "llm_prompt_text" 键
             的内容来自 llm_prompt_file 指向的txt文件，可直接被后续
             模块使用，无需再关心它原本是从文件读取而来。
    :raises ConfigError: 当文件不存在、JSON解析失败、顶层结构非字典，
                          缺少必填字段，或提示词txt文件不存在/读取失败时抛出，
                          异常信息中会说明具体原因。
    """
    if not os.path.isfile(config_path):
        raise ConfigError(f"配置文件不存在：{config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config: Any = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(
            f"配置文件JSON格式解析失败：{config_path}，错误详情：{e}"
        ) from e
    except OSError as e:
        raise ConfigError(
            f"配置文件读取失败：{config_path}，错误详情：{e}"
        ) from e

    if not isinstance(config, dict):
        raise ConfigError(
            f"配置文件内容格式错误：期望顶层为JSON对象（字典），"
            f"实际为 {type(config).__name__}"
        )

    # 校验必填字段
    missing_fields = [field for field in _REQUIRED_FIELDS if field not in config]
    if missing_fields:
        raise ConfigError(
            f"配置文件缺少必填字段：{', '.join(missing_fields)}"
        )

    # 读取提示词txt文件内容，存入 llm_prompt_text 键
    config["llm_prompt_text"] = _load_prompt_text_from_file(
        config_path, config["llm_prompt_file"]
    )

    # 填充可选字段默认值（已存在的字段保持用户提供的值不变）
    config.setdefault("phone_placeholder", _DEFAULT_PHONE_PLACEHOLDER)
    config.setdefault("email_placeholder", _DEFAULT_EMAIL_PLACEHOLDER)
    config.setdefault("image_pdf_char_threshold", _DEFAULT_IMAGE_PDF_CHAR_THRESHOLD)

    # 处理 llm_api_config 预留字段：与默认结构合并，用户提供的子字段优先
    llm_api_config = config.get("llm_api_config")
    if not isinstance(llm_api_config, dict):
        llm_api_config = {}
    merged_llm_config = dict(_DEFAULT_LLM_API_CONFIG)
    merged_llm_config.update(llm_api_config)
    config["llm_api_config"] = merged_llm_config

    return config