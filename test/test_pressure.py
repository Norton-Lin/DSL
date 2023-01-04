"""
压力测试
"""
from threading import Thread
import unittest
import json
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from app import app


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_pressure(self, index):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIn("token", json_data)
        token = json_data["token"]

        response = self.client.get(
            "/register",
            query_string={
                "username": f"test{index}",
                "password": f"test{index}",
                "token": token,
            },
        )
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIn("token", json_data)
        token = json_data["token"]

        for i in range(1, 10):
            response = self.client.get(
                "/send", query_string={"msg": "改名", "token": token}
            )
            self.assertEqual(response.status_code, 200)
            json_data = json.loads(response.data)
            self.assertIn("msg", json_data)
            self.assertEqual(json_data["msg"][0], "请输入新用户名，不超过30个字符")

            response = self.client.get(
                "/send", query_string={"msg": f"test_user{index}", "token": token}
            )
            self.assertEqual(response.status_code, 200)
            json_data = json.loads(response.data)
            self.assertIn("msg", json_data)
            self.assertEqual(json_data["msg"][0], f"您的新用户名为test_user{index}")
            self.assertEqual(json_data["msg"][1], f"你好，test_user{index}")

    def test_connect(self):
        pool = []
        number = 100
        for i in range(number):
            pool.append(Thread(target=self.test_pressure, args=[i]))
            pool[-1].start()
        for i in range(number):
            pool[i].join()


if __name__ == "__main__":
    unittest.main()
