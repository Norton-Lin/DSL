"""
 * @file user_manage.py
 * @author LinZhi
 * @brief 用户管理模块。
        管理用户的连接、登录、注册和超时释放，采用JWT令牌进行鉴权。
 * @version 0.1
 * @date 2022-11-28
 * @copyright Copyright (c) 2022
"""
import time
from typing import Optional
from threading import Lock, Timer
import jwt
from server.state.state import UserState
from server.database.database import Database


class User(object):
    """用户类。

    :ivar timer: 计时器，根据设定时间，释放用户对象
    :ivar state: 用户状态。
    :ivar username: 用户名。
    """

    def __init__(self, username: str) -> None:
        self.timer = None
        self.state = UserState()
        self.username = username


class UserManage(object):
    """用户管理类。

    :ivar users: 从用户名映射到User对象的字典。
    :ivar lock: 互斥访问 users 字典的互斥锁。
    :ivar key: JWT加密密钥。
    """

    def __init__(self, key: str) -> None:
        self.users: dict[str, User] = dict()
        self.lock = Lock()
        self.key = key

    def jwt_encode(self, username: str) -> str:
        """JWT令牌编码。

        :param username: 用户名。
        :return: JWT令牌。
        """
        return jwt.encode({"username": username}, self.key, algorithm="HS256")

    def jwt_decode(self, token: str) -> User:
        """JWT令牌解码。

        :param token: JWT令牌。
        :return: 如果解码成功，并且用户存在，则返回对应的User对象。
        :raises jwt.InvalidTokenError: 当解码失败或者用户名不存在时触发。
        """
        username = jwt.decode(token, self.key, algorithms="HS256").get("username")
        if username is None or username not in self.users.keys():
            raise jwt.InvalidTokenError
        self.users[username].timer.cancel()
        self.users[username].timer = Timer(300, self.timeout, username)  # 重设超时计时器
        return self.users[username]

    def connect(self) -> (User, str):
        """处理新客户端连接到服务器的请求。

        :return: User对象和JWT令牌。
        """
        username = f"Guest_{time.time_ns()}"
        with self.lock:
            self.users[username] = User(username)
            self.users[username].timer = Timer(300, self.timeout, username)  # 初始化超时计时器
        return self.users[username], self.jwt_encode(username)

    def login(self, user: User, username: str, password: str, db: Database) -> Optional[str]:
        """处理登录请求。

        :param db: 数据库对象
        :param user: 客户端对应的User对象。
        :param username: 登录的用户名。
        :param password: 登录的密码。
        :return: 如果登录成功,返回新JWT令牌。否则返回None。
        """
        old_username = user.username
        if not self.users[old_username].state.login(username, password, db):  # 登录失败，用户名或密码错误
            return None
        if self.users.get(username, None) is not None:  # 用户已经登录。
            return None
        with self.lock:
            self.users[username] = self.users[old_username]  # 用户名改变，移动User对象到新位置
            self.users[username].username = username
            del self.users[old_username]
        return self.jwt_encode(username)

    def register(self, user: User, username: str, password: str, db: Database) -> Optional[str]:
        """处理注册请求。

        :param db: 数据库对象
        :param user: 客户端对应的 User对象。
        :param username: 注册的用户名。
        :param password: 注册的密码。
        :return: 如果注册成功，返回新JWT令牌。否则返回None。
        """
        old_username = user.username
        if not self.users[old_username].state.register(username, password, db):  # 注册失败
            return None
        with self.lock:
            self.users[username] = self.users[old_username]  # 用户名改变，移动User对象到新位置
            self.users[username].username = username
            del self.users[old_username]
        return self.jwt_encode(username)

    def timeout(self, username: str) -> None:
        """超时状态处理函数。

        :param username: 超时的用户名。
        """
        with self.lock:
            self.users[username].timer.cancel()
            del self.users[username]  # 释放User对象。
