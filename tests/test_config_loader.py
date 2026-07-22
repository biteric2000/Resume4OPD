"""
test_config_loader.py

config_loader 模块的独立测试脚本。

运行方式：
    1. 确保 config_loader.py 与本文件位于同一目录下
    2. 直接运行： python test_config_loader.py
    3. 全部测试通过时会显示 OK，若有失败会明确指出哪个用例、哪一行断言失败
"""

import json
import os
import tempfile
import unittest

from config_loader import load_config, ConfigError


class TestConfigLoader(unittest.TestCase):

    def setUp(self):
        # 每个测试用例独享一个临时目录，测试结束后自动清理
        self._tmp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._tmp_dir.cleanup()

    def _write_file(self, filename: str, content: str) -> str:
        """辅助函数：在临时目录下写入指定内容的文件，返回完整路径。"""
        path = os.path.join(self._tmp_dir.name, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_valid_config(self):
        """测试合法配置+提示词txt文件能被正确加载，且可选字段被填充默认值"""
        # 提示词内容特意包含双引号、反斜杠、换行，验证不受JSON转义问题影响
        prompt_content = (
            '你是一名资深HR，请根据以下"简历"内容进行初筛。\n'
            '注意路径分隔符 C:\\resumes\\ 不需要转义处理。\n'
            '重点关注：教育背景、工作经历。'
        )
        self._write_file("llm_prompt.txt", prompt_content)

        valid_config = {
            "input_folder": "C:/resumes/input",
            "output_folder": "C:/resumes/output",
            "llm_prompt_file": "llm_prompt.txt",
            "separator_template": "========== 简历: {filename} ==========",
        }
        path = self._write_file(
            "valid_config.json", json.dumps(valid_config, ensure_ascii=False)
        )

        result = load_config(path)

        # 必填字段应原样保留
        self.assertEqual(result["input_folder"], valid_config["input_folder"])
        self.assertEqual(result["output_folder"], valid_config["output_folder"])
        self.assertEqual(result["separator_template"], valid_config["separator_template"])

        # 提示词内容应从txt文件正确读取，与原始内容完全一致（含特殊字符）
        self.assertEqual(result["llm_prompt_text"], prompt_content)

        # 可选字段应被填充为文档指定的默认值
        self.assertEqual(result["phone_placeholder"], "[出于隐私保护，已删去]")
        self.assertEqual(result["email_placeholder"], "[出于隐私保护，已删去]")
        self.assertEqual(result["image_pdf_char_threshold"], 50)
        self.assertEqual(
            result["llm_api_config"],
            {"enabled": False, "api_endpoint": "", "api_key": "", "model_name": ""},
        )

    def test_valid_config_with_custom_optional_fields(self):
        """测试用户自定义提供的可选字段值不会被默认值覆盖，未提供的子字段仍补默认值"""
        self._write_file("prompt.txt", "自定义提示词内容")

        custom_config = {
            "input_folder": "C:/resumes/input",
            "output_folder": "C:/resumes/output",
            "llm_prompt_file": "prompt.txt",
            "separator_template": "========== 简历: {filename} ==========",
            "phone_placeholder": "[手机号已隐藏]",
            "image_pdf_char_threshold": 80,
            "llm_api_config": {
                "enabled": True,
                "api_key": "sk-xxxx",
            },
        }
        path = self._write_file(
            "custom_config.json", json.dumps(custom_config, ensure_ascii=False)
        )

        result = load_config(path)

        self.assertEqual(result["llm_prompt_text"], "自定义提示词内容")
        self.assertEqual(result["phone_placeholder"], "[手机号已隐藏]")
        self.assertEqual(result["image_pdf_char_threshold"], 80)
        self.assertEqual(result["llm_api_config"]["enabled"], True)
        self.assertEqual(result["llm_api_config"]["api_key"], "sk-xxxx")
        # 用户未提供的子字段应仍补默认值
        self.assertEqual(result["llm_api_config"]["api_endpoint"], "")
        self.assertEqual(result["llm_api_config"]["model_name"], "")

    def test_missing_required_field(self):
        """测试缺少必填字段时抛出ConfigError，且异常信息中包含具体缺失的字段名"""
        incomplete_config = {
            "input_folder": "C:/resumes/input",
            "output_folder": "C:/resumes/output",
            # 缺少 llm_prompt_file 和 separator_template
        }
        path = self._write_file(
            "incomplete_config.json", json.dumps(incomplete_config, ensure_ascii=False)
        )

        with self.assertRaises(ConfigError) as ctx:
            load_config(path)

        error_message = str(ctx.exception)
        self.assertIn("llm_prompt_file", error_message)
        self.assertIn("separator_template", error_message)

    def test_prompt_file_not_found(self):
        """测试llm_prompt_file字段指向的txt文件实际不存在时，抛出ConfigError"""
        config_with_missing_prompt = {
            "input_folder": "C:/resumes/input",
            "output_folder": "C:/resumes/output",
            "llm_prompt_file": "does_not_exist_prompt.txt",
            "separator_template": "========== 简历: {filename} ==========",
        }
        path = self._write_file(
            "config_missing_prompt.json",
            json.dumps(config_with_missing_prompt, ensure_ascii=False),
        )

        with self.assertRaises(ConfigError) as ctx:
            load_config(path)

        self.assertIn("does_not_exist_prompt.txt", str(ctx.exception))

    def test_file_not_found(self):
        """测试传入不存在的文件路径时抛出ConfigError"""
        non_existent_path = os.path.join(self._tmp_dir.name, "does_not_exist.json")

        with self.assertRaises(ConfigError) as ctx:
            load_config(non_existent_path)

        self.assertIn(non_existent_path, str(ctx.exception))

    def test_invalid_json_format(self):
        """测试传入非合法JSON格式的文件时抛出ConfigError"""
        path = self._write_file("broken_config.json", "{ this is not valid json, ")

        with self.assertRaises(ConfigError):
            load_config(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)