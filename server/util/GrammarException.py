from .CommonException import CommonException


class GrammarException(CommonException):
    """表示脚本语言的语法错误。

    :ivar msg: 错误消息。
    :ivar context: 错误上下文。
    """

    def __init__(self, msg: str, context: list[str]) -> None:
        self.msg = msg
        self.context = context
