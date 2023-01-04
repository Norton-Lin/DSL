"""
 * @file action.py
 * @author LinZhi
 * @brief 动作模块
        定义客服机器人的各种动作操作
 * @version 0.1
 * @date 2022-11-28
 * @copyright Copyright (c) 2022
"""
from abc import abstractmethod, ABCMeta
from typing import Union, Optional
from storm.store import Store
from server.database.database import Database
from server.util.GrammarException import GrammarException
from server.user.user_state import UserState, VariableSet
from server.util.LoginExcepiton import LoginException


class Action(metaclass=ABCMeta):
    """
    动作抽象基类。

    """

    @abstractmethod
    def exec(self, user_state: UserState, response: list[str], request: str, db: Database) -> None:
        """执行一个动作。

        :param db:数据库对象
        :param user_state: 用户状态对象
        :param response: 回复信息。
        :param request: 用户请求信息。
        """
        pass


class ExitAction(Action):
    """
    退出动作，结束一个会话。

    """

    def __repr__(self):
        return "Exit"

    def exec(self, user_state: UserState, response: list[str], request: str, db: Database) -> None:
        """
        执行退出动作 -- 用户状态置为 -1

        :param  同动作抽象基类 Action.exec
        """
        with user_state.lock:
            user_state.state = -1


class GotoAction(Action):
    """状态转移动作，转移到一个新状态。

    :ivar next: 将转移到的状态。
    :ivar logined: 新状态是否需要登录验证。
    """

    def __init__(self, next_state: int, logined: bool) -> None:
        self.next = next_state
        self.logined = logined

    def __repr__(self):
        return f"Goto {self.next}"

    def exec(self, user_state: UserState, response: list[str], request: str, db: Database) -> None:
        """
        执行跳转动作 -- 修改用户状态

        :param  同动作抽象基类 Action.exec
        :exception LoginException 未登录用户访问需登录操作，将抛出登录异常
        """
        if not user_state.have_login and self.logined:
            raise LoginException("需要登录", [])
        with user_state.lock:
            user_state.state = self.next


class UpdateAction(Action):
    """更新用户变量动作。

    :ivar variable: 变量名。
    :ivar op: 更新操作类型，可以是 ``Add``、``Sub``、``Set`` 之一。
    :ivar value: 更新的值，可为字符串常量、数字常量、用户输入
    :ivar value_check: 对动作进行类型检查，查看更新值是否符合类型
    """

    def __init__(self, variable: str, op: str, value: Union[str, int, float], value_check: Optional[str]) -> None:
        """

        :param variable: 变量名
        :param op: 更新操作类型
        :param value: 更新值
        :param value_check: 更新值类型检查
        :exception GrammarException 存在语法错误
        """
        if VariableSet.type.get(variable) is None:
            raise GrammarException(f"{variable} 变量名不存在", ["Update", variable, op, value])
        if VariableSet.type[variable] == "Int":  # 变量类型为整数
            if value == "Input":
                if value_check != "Int":  # 整数类型检查
                    raise GrammarException("用户输入数据不为 整数!", ["Update", variable, op, value])
            elif not (isinstance(value, float) or isinstance(value, int)) or int(value) != value:  # 字面值必须是整数
                raise GrammarException("更新动作操作数不为 整数！", ["Update", variable, op, int(value)])
        elif VariableSet.type[variable] == "Real":  # 变量类型为实数
            if value == "Input":
                if not (value_check == "Real" or value_check == "Int"):  # 必须进行整数或者浮点数类型检查
                    raise GrammarException("用户输入数据不为 实数!", ["Update", variable, op, value])
            elif not isinstance(value, float):  # 字面值必须是浮点数
                raise GrammarException("更新动作操作数不为 浮点数!", ["Update", variable, op, value])
        elif VariableSet.type[variable] == "Text":
            if value == "Input":
                if value_check is None:  # 必须进行类型检查
                    raise GrammarException("用户输入数据不为 字符串!", ["Update", variable, op, value])
            if not isinstance(value, str):  # 字面值必须是字符串
                raise GrammarException("更新动作操作数不为 字符串!", ["Update", variable, op, value])
            if op != "Set":  # 字符串只能进行Set操作
                raise GrammarException("该更新动作 必须为Set方法", ["Update", variable, op, value])

        self.variable = variable
        self.op = op
        self.value = value

    def __repr__(self) -> str:
        return f"Update {self.variable} {self.op} {self.value}"

    def exec(self, user_state: UserState, response: list[str], request: str, db: Database) -> None:
        """
        执行数据修改动作

        :param  同动作抽象基类 Action.exec
        """
        with db.lock:
            store = Store(db.database)
            variable_set: VariableSet = store.get(VariableSet, user_state.username)  # 得到用户的变量集
            if self.op == "Add":
                value = getattr(variable_set, self.variable)
                if self.value == "Input":  # 根据用户输入处理值
                    if VariableSet.type[self.variable] == "Int":
                        setattr(variable_set, self.variable, value + int(request))
                    elif VariableSet.type[self.variable] == "Real":
                        setattr(variable_set, self.variable, value + float(request))
                else:
                    setattr(variable_set, self.variable, value + self.value)
            elif self.op == "Sub":
                value = getattr(variable_set, self.variable)
                if self.value == "Input":  # 根据用户输入处理值
                    if VariableSet.type[self.variable] == "Int":
                        setattr(variable_set, self.variable, value - int(request))
                    elif VariableSet.type[self.variable] == "Real":
                        setattr(variable_set, self.variable, value - float(request))
                else:
                    setattr(variable_set, self.variable, value - self.value)
            elif self.op == "Set":
                if self.value == "Input":  # 根据用户输入处理值
                    if VariableSet.type[self.variable] == "Int":
                        setattr(variable_set, self.variable, int(request))
                    elif VariableSet.type[self.variable] == "Real":
                        setattr(variable_set, self.variable, float(request))
                    elif VariableSet.type[self.variable] == "Text":
                        setattr(variable_set, self.variable, request)
                else:
                    if VariableSet.type[self.variable] == "Text":
                        setattr(variable_set, self.variable, self.value[1:-1])
                    else:
                        setattr(variable_set, self.variable, self.value)
            store.commit()
            store.close()


class SpeakAction(Action):
    """产生回复动作。

    :ivar contents: 回复内容列表。
    """

    def __init__(self, contents: list[str]) -> None:
        self.contents = contents
        for content in self.contents:
            if content[0] == '$':
                if VariableSet.type.get(content[1:]) is None:
                    raise GrammarException(f"{content[1:]} 变量名不存在", ["Speak"] + contents)

    def __repr__(self) -> str:
        return "Speak " + " + ".join(self.contents)

    def exec(self, user_state: UserState, response: list[str], request: str, db: Database) -> None:
        """
        执行客服回复动作

        :param  同动作抽象基类 Action.exec
        """
        res = ""
        with db.lock:
            for content in self.contents:
                if content[0] == '$':  # 输出信息为变量
                    store = Store(db.database)
                    variable_set = store.get(VariableSet, user_state.username)
                    res += str(getattr(variable_set, content[1:]))
                    store.close()
                elif content[0] == '"' and content[-1] == '"':   # 输出信息为字符串
                    res += content[1:-1]
                elif content == "Input":   # 输出信息为用户输入
                    res += request
        response.append(res)
