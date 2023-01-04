"""
脚本解析模块测试
"""
import os
import unittest
from pyparsing import ParseException
import sys
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from server.parser.parser import Parser

current_path = os.path.split(os.path.realpath(__file__))[0]


class TestParser(unittest.TestCase):
    def test_analyse_file(self):
        """
        analyse_file函数测试
        :return:
        """

        with open(
                os.path.join(current_path, "parser\\result1.txt"), "r", encoding="utf-8"
        ) as f:
            result = f.readline().strip()
            self.assertEqual(repr(Parser.analyse_file("parser/case1.txt")), result)
        """
        with self.assertRaises(ParseException):
            Parser.analyse_file("parser/case1.txt"),
        """
        with open(
                os.path.join(current_path, "parser\\result2.txt"), "r", encoding="utf-8"
        ) as f:
            result = f.readline().strip()
            self.assertEqual(repr(Parser.analyse_file("parser/case2.txt")), result)
        with self.assertRaises(ParseException):
            Parser.analyse_file("parser/case3.txt"),
        with self.assertRaises(ParseException):
            Parser.analyse_file("parser/case4.txt"),
        with self.assertRaises(ParseException):
            Parser.analyse_file("parser/case5.txt"),


if __name__ == "__main__":
    unittest.main()
