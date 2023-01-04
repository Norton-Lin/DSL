"""
有限状态自动机测试
"""
import unittest
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from server.state.state import *
from server.util.LoginExcepiton import LoginException

current_path = os.path.split(os.path.realpath(__file__))[0]


class TestStateMachine(unittest.TestCase):
    def test_state(self):
        with self.assertRaises(GrammarException):
            StateMachine(os.path.join(current_path, "state/case1.txt"),
                         os.path.join(current_path, "../dsl.db"))
        with self.assertRaises(GrammarException):
            StateMachine(os.path.join(current_path, "state/case2.txt"),
                         os.path.join(current_path, "../dsl.db"))
        with self.assertRaises(GrammarException):
            StateMachine(os.path.join(current_path, "state/case3.txt"),
                         os.path.join(current_path, "../dsl.db"))

        m = StateMachine(os.path.join(current_path, "parser/case2.txt"), os.path.join(current_path, "../dsl.db"))
        with open(os.path.join(current_path, "state/result.txt"), "r") as f:
            line = f.readline().strip()
            self.assertEqual(line, repr(m.basic))
            line = f.readline().strip()
            self.assertEqual(line, repr(m.states))
            line = f.readline().strip()
            self.assertEqual(line, repr(m.speak_action))
            line = f.readline().strip()
            self.assertEqual(line, repr(m.service))
            line = f.readline().strip()
            self.assertEqual(line, repr(m.default))
            line = f.readline().strip()
            self.assertEqual(line, repr(m.wait))

        user_state = UserState()

        with self.assertRaises(LoginException):
            m.state_transform(user_state, "")

        user_state.register("test", "test", m.db)
        user_state.state = 2
        result = m.state_transform(user_state, "Test")
        self.assertEqual(result, ["用户timeoutTest"])
        store = Store(m.db.database)
        self.assertEqual(store.get(VariableSet, "test").billing, 1.0)
        self.assertEqual(store.get(VariableSet, "test").name, "Test")
        store.close()

        user_state.state = 2
        user_state.last_time = 7
        result = m.timeout_transform(user_state, 20)
        self.assertEqual(result, (["test1Test1.00"], False, True))
        self.assertEqual(user_state.state, 1)

        os.remove(os.path.join(current_path, "../dsl.db"))


if __name__ == '__main__':
    unittest.main()
