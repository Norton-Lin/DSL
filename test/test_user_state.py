"""
用户状态测试
"""
import unittest
import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from server.state.state import *
from server.database.database import Database
from server.util.LoginExcepiton import LoginException

current_path = os.path.split(os.path.realpath(__file__))[0]

db = Database(os.path.join(current_path, "dsl.db"))


class TestDatabase(unittest.TestCase):
    def setUp(self):
        store = Store(db.database)
        store.execute(
            "CREATE TABLE robot (username TEXT PRIMARY KEY, password TEXT)")
        store.commit()
        store.close()

    def tearDown(self):
        os.remove(os.path.join(current_path, "dsl.db"))


class TestUserState(TestDatabase):
    def test_register(self):
        user_state = UserState()
        self.assertTrue(user_state.register("test1", "test1", db))
        self.assertEqual(user_state.username, "test1", db)
        self.assertTrue(user_state.have_login)

    def test_login(self):
        user_state = UserState()
        user_state.register("test2", "test2", db)
        user_state = UserState()
        self.assertFalse(user_state.login("test2", "tt", db))
        self.assertFalse(user_state.login("233", "233", db))
        self.assertTrue(user_state.login("test2", "test2", db))
        self.assertEqual(user_state.username, "test2", db)
        self.assertTrue(user_state.have_login)


class TestLengthJudgement(unittest.TestCase):
    def test_check(self):
        judgement = LengthJudgement("<", 3)
        self.assertTrue(judgement.check(""))
        self.assertFalse(judgement.check("aaa"))
        condition = LengthJudgement(">=", 5)
        self.assertTrue(condition.check("aaaaa"))
        self.assertFalse(condition.check("bb"))


class TestContainJudgement(unittest.TestCase):
    def test_check(self):
        judgement = ContainJudgement("")
        self.assertTrue(judgement.check("a string"))
        judgement = ContainJudgement(" ")
        self.assertTrue(judgement.check("a string"))
        judgement = ContainJudgement("b")
        self.assertFalse(judgement.check("a string"))


class TestTypeJudgement(unittest.TestCase):
    def test_check(self):
        judgement = TypeJudgement("Int")
        self.assertTrue(judgement.check("3"))
        self.assertFalse(judgement.check("3.3"))
        self.assertFalse(judgement.check("s"))
        judgement = TypeJudgement("Real")
        self.assertTrue(judgement.check("3"))
        self.assertTrue(judgement.check("3.3"))
        self.assertFalse(judgement.check("s"))


class TestEqualJudgement(unittest.TestCase):
    def test_check(self):
        judgement = EqualJudgement("string")
        self.assertTrue(judgement.check("string"))
        self.assertFalse(judgement.check(""))


class TestExitAction(TestDatabase):
    def test_exec(self):
        action = ExitAction()
        user_state = UserState()
        action.exec(user_state, [], "", db)
        self.assertEqual(user_state.state, -1)


class TestGotoAction(TestDatabase):
    def test_exec(self):
        action = GotoAction(2, False)
        user_state = UserState()
        action.exec(user_state, [], "", db)
        self.assertEqual(user_state.state, 2)
        action = GotoAction(2, True)
        user_state.state = 1
        with self.assertRaises(LoginException):
            action.exec(user_state, [], "", db)
        user_state.have_login = True
        action.exec(user_state, [], "", db)
        self.assertEqual(user_state.state, 2)


if __name__ == '__main__':
    unittest.main()
