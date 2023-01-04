class CommonException(Exception):
    """
    公共异常类
    :ivar status 状态码
    :ivar msg 异常信息
    """

    def __init__(self, exception: Exception = None):
        """
        :param exception: 异常信息
        ：
        """
        super().__init__()
        self.status = 500
        self.msg = str(exception if exception else "服务器内部错误")

    def __str__(self):
        return self.msg
