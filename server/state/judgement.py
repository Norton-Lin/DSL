"""
 * @file judgement.py
 * @author LinZhi
 * @brief 判断模块
        定义脚本语言定义各服务的执行条件判断
 * @version 0.1
 * @date 2022-11-28
 * @copyright Copyright (c) 2022
"""
from abc import abstractmethod, ABCMeta


class Judgement(metaclass=ABCMeta):
    """条件判断抽象基类。"""

    @abstractmethod
    def check(self, check_string: str) -> bool:
        """判断是否满足条件。

        :param check_string: 需要判断的字符串。
        :return: 如果满足条件，返回True；否则返回False。
        """
        pass


class LengthJudgement(Judgement):
    """长度判断条件，判断用户输入是否满足长度限制。

    :ivar op: 判断运算符，可以为 ``<``、``>``、``<=``、``>=``、``=`` 其中之一。
    :ivar length: 长度。
    """

    def __init__(self, op: str, length: int) -> None:
        self.op = op
        self.length = length

    def __repr__(self) -> str:
        return f"Length {self.op} {self.length}"

    def check(self, check_string: str) -> bool:
        """
        :param 同Judgement.exec
        :return 同Judgement.exec
        """
        if self.op == "<":
            return len(check_string) < self.length
        elif self.op == ">":
            return len(check_string) > self.length
        elif self.op == "<=":
            return len(check_string) <= self.length
        elif self.op == ">=":
            return len(check_string) >= self.length
        elif self.op == "=":
            return len(check_string) == self.length


class ContainJudgement(Judgement):
    """字符串包含判断条件，判断用户输入是否包含给定串。

    :ivar string: 包含的字符串。
    """

    def __init__(self, string: str) -> None:
        self.string = string

    def __repr__(self) -> str:
        return f"Contain {self.string}"

    def check(self, check_string: str) -> bool:
        """
        :param 同Judgement.exec
        :return 同Judgement.exec
        """
        return self.string in check_string


class TypeJudgement(Judgement):
    """字符串字面值类型判断，判断用户输入是否是某种类型。

    :ivar type: 类型
    """

    def __init__(self, type_: str) -> None:
        self.type = type_

    def __repr__(self) -> str:
        return f"Type {self.type}"

    def check(self, check_string: str) -> bool:
        """
        :param 同Judgement.exec
        :return 同Judgement.exec
        """
        if self.type == "Int":
            return check_string.isdigit()
        elif self.type == "Real":
            try:
                float(check_string)
                return True
            except ValueError:
                return False


class EqualJudgement(Judgement):
    """字符串相等判断，判断用户输入是否和某一个串完全相等。

    :ivar string: 字符串。
    """

    def __init__(self, string: str) -> None:
        self.string = string

    def __repr__(self) -> str:
        return f"Equal {self.string}"

    def check(self, check_string: str) -> bool:
        """
        :param 同Judgement.exec
        :return 同Judgement.exec
        """
        return check_string.strip() == self.string.strip()
