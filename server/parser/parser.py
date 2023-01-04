"""
 * @file parser.py
 * @author LinZhi
 * @brief 解析器模块
        脚本语言分析器
    包含词法分析与语法分析
    借助pyparsing实现
 * @version 0.1
 * @date 2022-11-28
 * @copyright Copyright (c) 2022
"""
import pyparsing as pp


class Parser(object):
    """
    脚本语言分析类
    根据脚本语言文件，构造脚本语言文法
    """

    const_num = pp.Regex("[-+]?[0-9]+").set_parse_action(lambda tokens: int(tokens[0]))
    real_num = pp.Regex("[-+]?[0-9]*\\.?[0-9]+([eE][-+]?[0-9]+)?").set_parse_action(
        lambda tokens: float(tokens[0])
    )
    const_string = pp.quoted_string('"')

    var = pp.Combine("$" + pp.Regex("[0-9A-Za-z_]+"))
    one_var_define = pp.Group(
        var
        + (
            (pp.Keyword("Int") + const_num)
            ^ (pp.Keyword("Real") + real_num)
            ^ (pp.Keyword("Text") + const_string)
        )
    )
    vars_define = pp.Group(pp.Keyword("Var:") + pp.Group(pp.OneOrMore(one_var_define)))

    judge_length = pp.Keyword("Length") + pp.oneOf("< > <= >= =") + const_num
    judge_contain = pp.Keyword("Contain:") + const_string
    judge_type = pp.Keyword("Type") + (pp.Keyword("Int") ^ pp.Keyword("Real"))
    judge_equal = const_string
    judgement = judge_length ^ judge_contain ^ judge_type ^ judge_equal

    exit_action = pp.Group(pp.Keyword("Exit"))
    goto_action = pp.Group(pp.Keyword("Goto") + pp.Word(pp.alphas))
    set_action = pp.Group(
        pp.Keyword("Update:")
        + var
        + (
            (
                (pp.Keyword("Add") ^ pp.Keyword("Sub") ^ pp.Keyword("Set"))
                + (real_num ^ pp.Keyword("Input"))
            )
            ^ (pp.Keyword("Set") + (const_string ^ pp.Keyword("Input")))
        )
    )
    content = var ^ const_string
    speak_action = pp.Group(
        pp.Keyword("Speak:")
        + pp.Group(
            (content + pp.ZeroOrMore("+" + content)).set_parse_action(
                lambda tokens: tokens[0::2]
            )
        )
    )
    speak_input = pp.Group(
        pp.Keyword("Speak:")
        + pp.Group(
            (
                (content ^ pp.Keyword("Input"))
                + pp.ZeroOrMore("+" + (content ^ pp.Keyword("Input")))
            ).set_parse_action(lambda tokens: tokens[0::2])
        )
    )

    service = pp.Group(
        pp.Keyword("Service:")
        + judgement
        + pp.Group(
            pp.ZeroOrMore(set_action ^ speak_input) + pp.Opt(exit_action ^ goto_action)
        )
    )
    default = pp.Group(
        pp.Keyword("Default:")
        + pp.Group(
            pp.ZeroOrMore(set_action ^ speak_input) + pp.Opt(exit_action ^ goto_action)
        )
    )
    wait = pp.Group(
        pp.Keyword("Wait:")
        + const_num
        + pp.Group(
            pp.ZeroOrMore(set_action ^ speak_action) + pp.Opt(exit_action ^ goto_action)
        )
    )

    state_define = pp.Group(
        pp.Keyword("State:")
        + pp.Word(pp.alphas)
        + pp.Group(pp.Opt(pp.Keyword("Logined")))
        + pp.Group(pp.ZeroOrMore(speak_action))
        + pp.Group(pp.ZeroOrMore(service))
        + default
        + pp.Group(pp.ZeroOrMore(wait))
    )
    basic = pp.Group(
        pp.Keyword("Basic:")
        + pp.Group(pp.Keyword("Name:") + pp.Word(pp.alphas))
        + pp.Group(pp.Keyword("Database:") + pp.Word(pp.alphas))
    )
    language = basic + pp.ZeroOrMore(state_define ^ vars_define)

    @staticmethod
    def analyse_file(file: str) -> list[pp.ParseResults]:
        """
        brief 解析一个脚本，脚本存储在文件中

        :param file: 文件名。
        :return: 解析脚本得到的语法树，以列表形式返回，根据列表嵌套层数构成树状结构
        """
        result = []
        result += Parser.language.parse_file(file, parse_all=True).as_list()
        return result


if __name__ == "__main__":
    try:
        print(Parser.analyse_file("../../grammar.txt"))
    except pp.ParseException as err:
        print(err.explain())
