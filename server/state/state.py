"""
 * @file state.py
 * @author LinZhi
 * @brief 状态模块
        定义客服机器人状态机
 * @version 0.1
 * @date 2022-11-28
 * @copyright Copyright (c) 2022
"""

from typing import Optional
from storm.locals import Store
from storm.properties import Unicode, Int, Float
from pyparsing import ParseException

from server.state.action import (
    Action,
    ExitAction,
    GotoAction,
    UpdateAction,
    SpeakAction,
)
from server.state.service import Service
from server.user.user_state import UserState, VariableSet
from server.database.database import Database
from server.state.judgement import (
    ContainJudgement,
    LengthJudgement,
    TypeJudgement,
    EqualJudgement,
)
from server.parser.parser import Parser
from server.util.GrammarException import GrammarException


class StateMachine(object):
    """状态机。

    :ivar states: 状态集合。
    :ivar db: 数据库
    :ivar speak_action: 状态默认的speak语句集合。
    :ivar service: 状态的条件分支集合。
    :ivar default: 状态的默认分支。
    :ivar wait: 状态的超时转移分支。
    """

    def __init__(self, file: str, path: str) -> None:
        """

        :param file: 脚本文件路径
        :param path: 数据库文件路径
        """
        try:
            result = Parser.analyse_file(file)
        except ParseException as e:
            raise GrammarException(e.__str__(), [e.line])
        self.states: list[str] = []
        self.db = Database(path)
        verified: list[bool] = []
        self.speak_action: list[list[Action]] = []
        self.service: list[list[Service]] = []
        self.default: list[list[Action]] = []
        self.wait: list[dict[int, list[Action]]] = []
        self.basic = result[0]
        self.create_db = False
        self.db_name = str(self.basic[1][1])  # 对应脚本数据库表
        if str(self.basic[2][1]) == "True":
            self.create_db = True
        create_table_statement = [
            "CREATE TABLE " + self.db_name + "(username TEXT PRIMARY KEY, password TEXT"
        ]  # 建表语句
        # 处理变量定义和状态集
        for definition in result:
            if definition[0] == "Var:":  # 处理变量定义
                for clause in definition[1]:
                    if VariableSet.type.get(clause[0]) is not None:
                        raise GrammarException("变量命名冲突", clause)
                    if clause[1] == "Int":
                        setattr(VariableSet, clause[0][1:], Int(default=clause[2]))
                        VariableSet.type[clause[0][1:]] = "Int"
                        create_table_statement.append(f"{clause[0][1:]} INT")
                    elif clause[1] == "Real":
                        setattr(
                            VariableSet, clause[0][1:], Float(default=clause[2])
                        )
                        VariableSet.type[clause[0][1:]] = "Real"
                        create_table_statement.append(f"{clause[0][1:]} REAL")
                    elif clause[1] == "Text":
                        setattr(
                            VariableSet,
                            clause[0][1:],
                            Unicode(default=clause[2][1:-1]),
                        )
                        VariableSet.type[clause[0][1:]] = "Text"
                        create_table_statement.append(f"{clause[0][1:]} TEXT")
            elif definition[0] == "State:":  # 处理状态定义
                if definition[1] not in self.states:
                    self.states.append(definition[1])  # 将状态名加入状态集
                    if len(definition[2]) == 0:
                        verified.append(False)
                    else:
                        verified.append(True)
                else:
                    raise GrammarException("状态命名冲突", definition[:1])

        if "Begin" not in self.states:
            raise GrammarException("没有起始状态", [])
        else:
            beign_index = self.states.index("Begin")
            if verified[beign_index]:
                raise GrammarException("初始化状态必须不为Verified", [])
            verified[beign_index] = verified[0]
            verified[0] = False
            self.states[beign_index] = self.states[0]
            self.states[0] = "Begin"

        # 建立数据库
        if self.create_db:
            with self.db.lock:
                store = Store(self.db.database)
                store.execute(",".join(create_table_statement) + ")")
                store.add(VariableSet("Guest", ""))  # 创建默认的访客用户
                store.commit()
                store.close()

        state_index = -1
        # 处理各个分支和动作
        for definition in result:
            if definition[0] != "State:":
                continue
            state_index += 1

            # Speak子句
            self.speak_action.append([])
            if len(definition[3]) != 0:
                self.construct_action(
                    definition[3], self.speak_action[-1], state_index, verified, None
                )

            # Case子句
            self.service.append([])
            if len(definition[4]) != 0:
                for case_list in definition[4]:
                    value_check = "Text"
                    if case_list[1] == "Length":
                        self.service[-1].append(
                            Service(LengthJudgement(case_list[2], case_list[3]))
                        )
                    elif case_list[1] == "Contain:":
                        self.service[-1].append(
                            Service(ContainJudgement(case_list[2][1:-1]))
                        )
                    elif case_list[1] == "Type":
                        self.service[-1].append(Service(TypeJudgement(case_list[2])))
                        if case_list[2] == "Int" or case_list[2] == "Real":
                            value_check = case_list[2]
                    elif case_list[1][0] == '"' and case_list[1][-1] == '"':
                        self.service[-1].append(
                            Service(EqualJudgement(case_list[1][1:-1]))
                        )

                    self.construct_action(
                        case_list[-1],
                        self.service[-1][-1].actions,
                        state_index,
                        verified,
                        value_check,
                    )

            # Default子句
            self.default.append([])
            self.construct_action(
                definition[5][1], self.default[-1], state_index, verified, "Text"
            )

            # Timeout子句
            self.wait.append(dict())
            if len(definition[6]) != 0:
                for timeout_list in definition[6]:
                    self.wait[-1][timeout_list[1]] = []
                    self.construct_action(
                        timeout_list[-1],
                        self.wait[-1][timeout_list[1]],
                        state_index,
                        verified,
                        None,
                    )

    def construct_action(
        self,
        message: list,
        target: list[Action],
        index: int,
        logined: list[bool],
        value_check: Optional[str],
    ) -> None:
        """构建一个动作列表。

        :param message: 语法树信息，包含一系列动作。
        :param target: 存储动作列表。
        :param index: 状态编号。
        :param logined: 状态是否需要登录验证。
        :param value_check: 校验修改值类型。
        """
        for language in message:
            if language[0] == "Exit":
                target.append(ExitAction())
            elif language[0] == "Goto":
                if language[1] not in self.states:
                    raise GrammarException("Goto状态不存在", language)
                target.append(
                    GotoAction(
                        self.states.index(language[1]),
                        logined[self.states.index(language[1])],
                    )
                )
            elif language[0] == "Update:":
                if not logined[index]:
                    raise GrammarException("不能在非验证的状态执行Update语句", language)
                target.append(
                    UpdateAction(language[1][1:], language[2], language[3], value_check)
                )
            elif language[0] == "Speak:":
                target.append(SpeakAction(language[1]))

    def speak(self, user_state: UserState) -> list[str]:
        """
        输出某个状态的回复 动作。

        :param user_state: 用户状态。
        :return: 回复信息。
        """
        response: list[str] = []
        for action in self.speak_action[user_state.state]:
            action.exec(user_state, response, "", self.db)
        return response

    def state_transform(self, user_state: UserState, msg: str) -> list[str]:
        """
        状态转移。

        :param user_state: 用户状态
        :param msg: 用户输入。
        :return: 回复信息列表。
        """
        response: list[str] = []
        for case in self.service[user_state.state]:
            if case.judgement.check(msg):
                for action in case.actions:
                    action.exec(user_state, response, msg, self.db)
                if user_state.state != -1:  # 新状态的speak动作
                    response += self.speak(user_state)
                return response
        for action in self.default[user_state.state]:
            action.exec(user_state, response, msg, self.db)
        if user_state.state != -1:  # 新状态的speak动作
            response += self.speak(user_state)
        return response

    def timeout_transform(
        self, user_state: UserState, now_seconds: int
    ) -> (list[str], bool, bool):
        """超时转移。

        :param user_state: 用户状态。
        :param now_seconds: 用户未执行操作的秒数。
        :return: 输出的字符串列表、是否需要结束会话、是否转移到新的状态。
        """
        response: list[str] = []
        with user_state.lock:
            last_seconds = user_state.last_time
            user_state.last_time = now_seconds
        old_state = user_state.state
        for timeout_sec in self.wait[user_state.state].keys():
            if last_seconds < timeout_sec <= now_seconds:  # 检查字典的键是否在时间间隔内
                for action in self.wait[user_state.state][timeout_sec]:
                    action.exec(user_state, response, "", self.db)
                if old_state != user_state.state:  # 如果旧状态和新状态不同，执行新状态的speak动作
                    if user_state.state != -1:
                        response += self.speak(user_state)
                    break
        return response, user_state.state == -1, old_state != user_state.state


if __name__ == "__main__":
    try:
        #   m = StateMachine("../../grammar.txt", "../../dsl.db")
        m = StateMachine("../../test/parser/case1.txt", "../../dsl.db")
        print(m.basic)
        print(m.states)
        print(m.speak_action)
        print(m.service)
        print(m.default)
        print(m.wait)
    except GrammarException as err:
        print(" ".join([str(item) for item in err.context]))
        print("GrammarException: ", err.msg)
