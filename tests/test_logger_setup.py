"""
test_logger_setup.py

logger_setup 模块的独立测试脚本。

运行方式：
    1. 确保 logger_setup.py 与本文件位于同一目录下
    2. 直接运行： python test_logger_setup.py
    3. 运行时会先在控制台看到几条实时打印的测试日志（用于人工肉眼核对格式），
       随后脚本会自动读取生成的日志文件内容并用断言核对，最终打印 OK 表示通过
"""

import os
import re
import shutil
import tempfile
import unittest

from logger_setup import init_logger


class TestLoggerSetup(unittest.TestCase):

    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._tmp_dir, ignore_errors=True)

    def test_log_messages_written_correctly(self):
        """测试INFO/WARNING/ERROR三种级别的日志都能正确写入文件，且格式包含时间戳和级别"""
        log_file_path = os.path.join(self._tmp_dir, "test.log")

        logger = init_logger(log_file_path)

        logger.info("这是一条INFO测试消息")
        logger.warning("这是一条WARNING测试消息")
        logger.error("这是一条ERROR测试消息")

        # 断言日志文件确实被创建
        self.assertTrue(os.path.isfile(log_file_path))

        with open(log_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 断言三条消息内容都存在
        self.assertIn("这是一条INFO测试消息", content)
        self.assertIn("这是一条WARNING测试消息", content)
        self.assertIn("这是一条ERROR测试消息", content)

        # 断言日志级别标签正确
        self.assertIn("[INFO]", content)
        self.assertIn("[WARNING]", content)
        self.assertIn("[ERROR]", content)

        # 断言每行都包含形如 "2026-07-18 10:42:00" 的时间戳格式
        timestamp_pattern = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
        lines = [line for line in content.strip().split("\n") if line.strip()]
        self.assertEqual(len(lines), 3, "应恰好有3行日志记录")
        for line in lines:
            self.assertRegex(line, timestamp_pattern)

    def test_auto_create_log_directory(self):
        """测试当日志文件所在目录不存在时，能自动创建该目录而不报错"""
        nested_dir = os.path.join(self._tmp_dir, "nested", "logs")
        log_file_path = os.path.join(nested_dir, "auto_created.log")

        self.assertFalse(os.path.isdir(nested_dir))

        logger = init_logger(log_file_path)
        logger.info("目录应已被自动创建")

        self.assertTrue(os.path.isdir(nested_dir))
        self.assertTrue(os.path.isfile(log_file_path))

    def test_repeated_init_does_not_duplicate_handlers(self):
        """测试多次调用init_logger不会导致同一条日志被重复打印/写入多份"""
        log_file_path = os.path.join(self._tmp_dir, "repeated.log")

        logger1 = init_logger(log_file_path)
        logger2 = init_logger(log_file_path)  # 模拟重复初始化

        logger2.info("只应出现一次的消息")

        with open(log_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        occurrences = content.count("只应出现一次的消息")
        self.assertEqual(occurrences, 1, "重复调用init_logger后，消息不应被重复写入")

        # 两次返回的应是同一个logger对象（同名logger在logging模块中是单例）
        self.assertIs(logger1, logger2)


if __name__ == "__main__":
    unittest.main(verbosity=2)