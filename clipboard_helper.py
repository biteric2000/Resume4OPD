"""
clipboard_helper.py

剪贴板辅助模块：将指定文本内容复制到系统剪贴板。

设计说明：
    依赖第三方库pyperclip（需提前 pip install pyperclip）。
    若该库未安装或复制过程中出现任何异常，本模块不会抛出异常
    导致主流程中断，仅返回False并由调用方决定如何提示用户。
"""


def copy_text_to_clipboard(text: str) -> bool:
    """
    将text复制到系统剪贴板。

    :param text: 待复制的文本内容
    :return: True表示复制成功；False表示复制失败（如库未安装、
             或运行环境不支持剪贴板操作），此时调用方应自行
             打印提示，引导用户手动打开文件复制。
    """
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except ImportError:
        print(
            "⚠️  未安装pyperclip库，无法自动复制到剪贴板。"
            "如需启用此功能，请运行: pip install pyperclip"
        )
        return False
    except Exception as e:
        print(f"⚠️  复制到剪贴板时发生错误（不影响文件已正常生成）：{e}")
        return False