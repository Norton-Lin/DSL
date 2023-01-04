from .CommonException import CommonException


class LoginException(CommonException):
    """
    表示未登录用户试图访问需登录操作

    :ivar msg: 错误消息。
    :ivar context: 错误上下文。
    """

    def __init__(self, msg: str, context: list[str]) -> None:
        self.msg = msg
        self.context = context
