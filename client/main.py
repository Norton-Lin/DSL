"""
 * @file main.py
 * @author LinZhi
 * @brief 
        客户端模块
 * @version 0.1
 * @date 2022-11-28
 * @copyright Copyright (c) 2022
"""

import sys
from threading import Timer, Lock
import json.decoder
from typing import Optional

import requests
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine, QQmlListProperty

server_address = "http://127.0.0.1:5000"


class Message(QObject):
    """
    消息类。
    :ivar msg: 消息内容。
    :ivar author: 消息发送方，0表示客服，1表示用户。
    """

    def __init__(self, msg: str, author: int, parent=None) -> None:
        super().__init__(parent)
        self._msg = msg
        self._author = author

    @pyqtProperty("QString", constant=True)
    def get_msg(self) -> str:
        return self._msg

    @pyqtProperty(int, constant=True)
    def get_author(self) -> int:
        return self._author


class Client(QObject):
    """
    客户端模型。与QML交互。
    :ivar message: 消息列表。
    :ivar lock: 互斥锁。
    :ivar token: 令牌。
    :ivar logined: 是否已经登录。
    :ivar timer: 超时计时器，监测用户闲置时间。
    :ivar time_count: 用户闲置时间计数器。
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.message = []
        self.lock = Lock()

        self.token: Optional[str] = None
        self.logined = False
        self.timer: Optional[Timer] = None
        self.time_count: Optional[int] = None
        self.connect()

    def __del__(self) -> None:
        if self.timer is not None:
            self.timer.cancel()

    message_changed = pyqtSignal()

    @pyqtProperty(QQmlListProperty, notify=message_changed)
    def get_message(self) -> QQmlListProperty:
        """
        获取信息列表
        :return: 信息列表
        """
        return QQmlListProperty(Message, self, self.message)

    def append_message(self, msg: Message) -> None:
        """
        在信息列表后追加信息
        :param msg: 新信息
        :return:
        """
        self.message.append(msg)
        self.message_changed.emit()

    @pyqtSlot("QString")
    def send_message(self, msg: str) -> None:
        """
        发送请求
        :param msg: 请求信息
        """
        if self.token is None:
            self.connect()
            if self.token is None:
                return

        if len(msg.strip()) == 0:  # 消息为空
            return
        self.append_message(Message(msg, 1))

        with self.lock:  # 重设计时器
            self.time_count = 0
        self.timer.cancel()
        self.timer = Timer(5, self.timeout)
        self.timer.start()

        try:
            # 向/send 发送get请求
            r = requests.get(
                server_address + "/send", params={"token": self.token, "msg": msg}
            )
            if r.status_code == 401:
                self.append_message(Message("需要登录，请点击右上角登录", 0))
                return
            elif r.status_code == 403:
                self.append_message(Message("服务器拒绝请求，请重启客户端", 0))
                self.timer.cancel()
                return
            elif r.status_code != 200:  # 其他错误
                raise requests.exceptions.ConnectionError()
            for msg in r.json().get("msg"):
                self.append_message(Message(msg, 0))
            if r.json().get("exit"):
                self.append_message(Message("退出成功！", 0))
                self.append_message(Message("输入任意信息开始对话", 0))
                self.token = None
                self.logined = False
                self.timer.cancel()
        except requests.exceptions.ConnectionError:
            self.append_message(Message("服务器异常，请稍后重试", 0))
        except (KeyError, json.decoder.JSONDecodeError):
            self.append_message(Message("反馈消息异常，请稍后重试", 0))

    @pyqtSlot("QString", "QString")
    def login(self, username: str, password: str) -> None:
        """
        用户注册
        :param username: 用户名
        :param password: 密码
        """
        if self.token is None:
            self.connect()
            if self.token is None:
                self.append_message(Message("服务器异常，请稍后重试", 0))
                return
        try:
            r = requests.get(
                server_address + "/login",
                params={"token": self.token, "username": username, "password": password},
            )
            if r.status_code == 403:
                self.append_message(Message("服务器拒绝请求，请重启客户端", 0))
                self.timer.cancel()
                return
            elif r.status_code != 200:
                raise requests.exceptions.ConnectionError()
            if r.json().get("token") is None:
                self.append_message(Message("登录失败，用户名或密码无效", 0))
                return
            self.token = r.json().get("token")
            self.append_message(Message("登录成功！", 0))
        except requests.exceptions.ConnectionError:
            self.append_message(Message("服务器异常，请稍后重试", 0))
        except (KeyError, json.decoder.JSONDecodeError):
            self.append_message(Message("反馈消息异常，请稍后重试", 0))

    @pyqtSlot("QString", "QString")
    def register(self, username: str, password: str) -> None:
        """
        用户注册
        :param username: 用户名
        :param password: 密码
        """
        if self.token is None:
            self.connect()
            if self.token is None:
                self.append_message(Message("服务器异常，请稍后重试", 0))
                return
        try:
            r = requests.get(
                server_address + "/register",
                params={"token": self.token, "username": username, "password": password},
            )
            if r.status_code == 403:
                self.append_message(Message("服务器拒绝请求，请重启客户端", 0))
                self.timer.cancel()
                return
            elif r.status_code != 200:
                raise requests.exceptions.ConnectionError()
            if r.json().get("token") is None:
                self.append_message(Message("注册失败，用户名冲突", 0))
                return
            self.token = r.json().get("token")
            self.append_message(Message("注册并登录成功", 0))
        except requests.exceptions.ConnectionError:
            self.append_message(Message("服务器异常，请稍后重试", 0))
        except (KeyError, json.decoder.JSONDecodeError):
            self.append_message(Message("反馈消息异常，请稍后重试", 0))

    def connect(self) -> None:
        """
        与服务端建立连接
        """
        try:
            r = requests.get(server_address)
            if r.status_code != 200:
                raise requests.exceptions.ConnectionError()
            self.token = r.json().get("token")
            for msg in r.json().get("msg"):
                self.append_message(Message(msg, 0))
            self.time_count = 0
            self.timer = Timer(5, self.timeout)
            self.timer.start()
        except requests.exceptions.ConnectionError:
            self.append_message(Message("服务器异常，请稍后重试", 0))
        except KeyError:
            self.append_message(Message("反馈消息异常，请稍后重试", 0))

    def timeout(self) -> None:
        """
        用户无操作计时检查
        """
        with self.lock:
            self.time_count += 5
        self.timer = Timer(5, self.timeout)
        self.timer.start()

        try:
            r = requests.get(
                server_address + "/echo",
                params={"token": self.token, "seconds": self.time_count},
            )
            if r.status_code == 401:
                self.append_message(Message("需要登录，请点击右上角登录", 0))
                return
            elif r.status_code == 403:
                self.append_message(Message("服务器拒绝请求，请重启客户端", 0))
                self.timer.cancel()
                return
            elif r.status_code != 200:
                raise requests.exceptions.ConnectionError()
            if r.json().get("reset"):
                with self.lock:
                    self.time_count = 0
            for msg in r.json().get("msg"):
                self.append_message(Message(msg, 0))
            if r.json().get("exit"):
                self.append_message(Message("退出成功！", 0))
                self.append_message(Message("输入任意信息开始对话", 0))
                self.token = None
                self.logined = False
                self.timer.cancel()
        except requests.exceptions.ConnectionError:
            self.append_message(Message("服务器异常，请稍后重试", 0))
        except (KeyError, json.decoder.JSONDecodeError):
            self.append_message(Message("反馈消息异常，请稍后重试", 0))


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    client = Client()
    engine.rootContext().setContextProperty("client", client)
    engine.load("main.qml")
    app.exec()
    client.__del__()
