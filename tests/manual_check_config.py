"""
manual_check_config.py

手动核对脚本：读取你实际环境中的 config.json 和提示词txt文件，
将加载结果完整打印到控制台，供人工肉眼核对内容是否符合预期。

与 test_config_loader.py 的区别：
    test_config_loader.py 使用临时目录中"自己造的"测试数据，
    验证代码逻辑本身是否正确，跑完即清理，不涉及你的真实文件。
    本脚本则直接读取你指定的真实config.json路径，方便你确认
    "我自己准备的配置文件、提示词文件到底有没有被正确加载"。

运行方式：
    python manual_check_config.py "C:/resumehelper/config.json"
    如果不传参数，默认读取 C:/resumehelper/config.json
"""

import json
import sys

from config_loader import load_config, ConfigError


def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "C:/resumehelper/config.json"

    print(f"正在读取配置文件：{config_path}\n")

    try:
        config = load_config(config_path)
    except ConfigError as e:
        print("❌ 配置加载失败，ConfigError：")
        print(f"   {e}")
        sys.exit(1)

    print("✅ 配置加载成功！以下是完整解析结果：\n")

    # 单独把提示词文本高亮打印出来，因为它是从外部txt文件读入的，最需要重点核对
    print("--- llm_prompt_text（从提示词txt文件读取的内容）---")
    print(config.get("llm_prompt_text"))
    print("--- 提示词内容结束 ---\n")

    print("--- 完整配置字典（JSON格式打印，便于查看全部字段）---")
    print(json.dumps(config, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()