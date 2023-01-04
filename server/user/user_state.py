"""
 * @file user_state.py
 * @author LinZhi
 * @brief 用户状态模块。
        定义用户状态和指定脚本语言变量集
 * @version 0.1
 * @date 2022-11-28
 * @copyright Copyright (c) 2022
"""
from threading import Lock

from storm.properties import Unicode
from storm.store import Store

from server.database.database import Database


class VariableSet(object):
    """脚本语言变量集，与数据库关联。

    采用storm作为ORM，除了 type(基础属性)之外各个类属性关联到数据库表中的一列，实例中的相关属性关联到元组的对应属性。
    用户的基础属性包括用户名和密码，其他属性则通过 ``setattr`` 动态添加。

    :cvar type: 表中各列的类型。
    :cvar username: 用户名
    :cvar password: 密码
    :ivar username: 用户名
    :ivar password： 密码
    """
    __storm_table__ = 'robot'
    type = {"username": "Text", "password": "Text"}
    username = Unicode(primary=True)
    password = Unicode()

    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password


class UserState(object):
    """用户状态类

    :ivar state: 用户在状态机中所处的状态。
    :ivar have_login: 用户是否已经登录。
    :ivar last_time: 距离用户上次发送消息过去的秒数。
    :ivar lock: 互斥锁。
    :ivar username: 用户名。
    """

    def __init__(self) -> None:
        self.state = 0
        self.have_login = False
        self.last_time = 0
        self.lock = Lock()
        self.username = "Guest"

    def register(self, username: str, password: str, db: Database) -> bool:
        """注册新用户。

        首先在数据库中查找用户是否存在，如果不存在，则向数据库中添加一个新用户，并且更新用户名和登录信息。

        :param db: 数据库对象
        :param username: 用户名。
        :param password: 密码。
        :return: 如果注册成功，返回True；否则返回False。
        """
        with db.lock:
            store = Store(db.database)
            if store.get(VariableSet, username) is not None:  # 用户已经存在
                store.close()
                return False
            with self.lock:
                self.username = username
                variable_set = VariableSet(username, password)
                self.have_login = True
            store.add(variable_set)  # 添加新的行
            store.commit()
            store.close()
            return True

    def login(self, username: str, password: str, db: Database) -> bool:
        """用户登录。

        在数据库中查找用户信息，并且验证密码是否正确。

        :param db:
        :param username: 用户名。
        :param password: 密码。
        :return: 如果登录成功，返回True；否则返回False。
        """
        if username == "Guest":  # 不能登录访客用户
            return False

        with db.lock:
            store = Store(db.database)
            variable_set = store.get(VariableSet, username)
            if variable_set is None:  # 用户不存在
                store.close()
                return False
            if variable_set.password == password:
                with self.lock:
                    self.username = username
                    self.have_login = True
                store.close()
                return True
            store.close()
            return False
