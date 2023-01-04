"""
 * @file service.py
 * @author LinZhi
 * @brief 服务模块
        定义客服机器人的各种服务操作
 * @version 0.1
 * @date 2022-11-28
 * @copyright Copyright (c) 2022
"""
from server.state.action import Action
from server.state.judgement import Judgement


class Service(object):
    """条件分支。

    :ivar judgement: 条件。
    :ivar actions: 满足条件后执行的动作列表。
    """

    def __init__(self, judgement: Judgement) -> None:
        self.judgement = judgement
        self.actions: list[Action] = []

    def __repr__(self) -> str:
        return repr(self.judgement) + ": " + "; ".join([repr(i) for i in self.actions])
