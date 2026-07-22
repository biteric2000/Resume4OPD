"""
test_clipboard_helper.py

clipboard_helper模块的独立测试脚本。

运行方式：
    python test_clipboard_helper.py

验证方式：
    脚本运行后会打印提示，请你在任意文本框（如记事本、微信输入框）
    中按 Ctrl+V 粘贴，肉眼确认粘贴出来的内容与脚本中写的测试文本一致。
"""

from clipboard_helper import copy_text_to_clipboard


def main():
    test_text = (
        "这是一段剪贴板测试文本。\n"
        "包含中文、英文English、数字12345，\n"
        "以及多行内容，用于验证复制到剪贴板功能是否正常。"
    )

    print("测试文本内容：")
    print("-" * 40)
    print(test_text)
    print("-" * 40)

    success = copy_text_to_clipboard(test_text)

    if success:
        print("\n✅ 已调用复制接口，返回成功。")
        print("请现在打开任意文本框，按 Ctrl+V 粘贴，核对内容是否与上方测试文本完全一致。")
    else:
        print("\n❌ 复制失败，请检查是否已安装pyperclip（pip install pyperclip）。")


if __name__ == "__main__":
    main()