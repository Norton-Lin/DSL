"""
服务端测试
"""
import json
import unittest
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from app import app


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_connect(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("token", data)
        token = data["token"]

        response = self.client.get("/send", query_string={"msg": "123", "token": ""})
        self.assertEqual(response.status_code, 403)

        response = self.client.get("/send", query_string={"msg": "123"})
        self.assertEqual(response.status_code, 400)

        response = self.client.get("/send", query_string={"msg": "投诉", "token": token})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("msg", data)
        self.assertEqual(data["msg"][0], "请输入您的建议，不超过200个字符")

        response = self.client.get(
            "/echo", query_string={"seconds": 60, "token": token}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("msg", data)
        self.assertEqual(data["msg"][0], "您已经很久没有操作了，即将返回主菜单")

        response = self.client.get("/send", query_string={"msg": "改名", "token": token})
        self.assertEqual(response.status_code, 401)

        response = self.client.get(
            "/register",
            query_string={"username": "test1", "password": "test1", "token": token},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("token", data)
        token = data["token"]

        response = self.client.get("/send", query_string={"msg": "改名", "token": token})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("msg", data)
        self.assertEqual(data["msg"][0], "请输入新用户名，不超过30个字符")

        response = self.client.get(
            "/send", query_string={"msg": "test_user", "token": token}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("msg", data)
        self.assertEqual(data["msg"][0], "您的新用户名为test_user")
        self.assertEqual(data["msg"][1], "你好，test_user")

        response = self.client.get("/send", query_string={"msg": "退出", "token": token})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("exit", data)
        self.assertTrue(data["exit"])

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("token", data)
        token = data["token"]

        response = self.client.get(
            "/login",
            query_string={"username": "test1", "password": "test1", "token": token},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("token", data)


if __name__ == "__main__":
    unittest.main()
