"""
manual_check_logger.py

手动核对脚本：在你指定的真实目录下生成一个日志文件，写入几条示例消息，
然后回读并打印文件内容，供你肉眼确认"正常使用场景下，日志文件确实生成、
内容确实正确"——而非仅依赖自动化测试的断言结果。

运行方式：
    python manual_check_logger.py "C:/resumehelper/logs/demo.log"
    如果不传参数，默认写入 C:/resumehelper/logs/demo.log
"""

import os
import sys

from logger_setup import init_logger


def main():
    log_file_path = (
        sys.argv[1] if len(sys.argv) > 1 else "C:/resumehelper/logs/demo.log"
    )

    print(f"即将初始化logger，日志文件路径：{log_file_path}\n")
    print("--- 以下是控制台实时日志输出 ---")

    logger = init_logger(log_file_path)
    logger.info("程序启动，这是一条正常的INFO日志示例")
    logger.warning("这是一条WARNING日志示例，比如MinerU处理时的非阻断提示")
    logger.error("这是一条ERROR日志示例，比如某个PDF处理失败的原因说明")

    # 主动关闭handler，确保文件内容已完全刷盘，方便立即回读
    for handler in logger.handlers[:]:
        handler.close()

    print("--- 控制台实时日志输出结束 ---\n")

    if os.path.isfile(log_file_path):
        print(f"✅ 日志文件已成功生成：{log_file_path}\n")
        print("--- 以下是回读到的日志文件完整内容 ---")
        with open(log_file_path, "r", encoding="utf-8") as f:
            print(f.read())
        print("--- 日志文件内容结束 ---")
    else:
        print(f"❌ 日志文件未生成，请检查：{log_file_path}")


if __name__ == "__main__":
    main()