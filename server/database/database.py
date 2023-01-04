"""
 * @file database.py
 * @author LinZhi
 * @brief 数据库模块
        定义脚本语言定义的用户数据信息的数据库
 * @version 0.1
 * @date 2022-11-28
 * @copyright Copyright (c) 2022
"""
import os
from threading import Lock
from storm import database


class Database(object):
    """
    数据库类
    定义对应用户信息数据库
    :ivar database 数据库对象
    :ivar lock 数据库访问互斥锁
    """

    def __init__(self, path) -> None:
        """
        初始化数据库。

        :param path: 数据库路径。
        """
        directory, file_name = os.path.split(path)
        if file_name in os.listdir(directory):
            os.remove(path)
        self.database = database.create_database("sqlite:" + path)
        self.lock = Lock()
