"""
回复动作测试
"""
import os
import unittest
import sys

current_path = os.path.split(os.path.realpath(__file__))[0]
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from server.state.state import *


class TestSpeakAction(unittest.TestCase):
    def test_exec(self):
        db = Database(os.path.join(current_path, "dsl.db"))
        VariableSet.test1 = Int(default=0)
        VariableSet.test2 = Float(default=0.0)
        VariableSet.test3 = Unicode(default="default")
        VariableSet.type["test1"] = "Int"
        VariableSet.type["test2"] = "Real"
        VariableSet.type["test3"] = "Text"
        store = Store(db.database)
        store.execute(
            "CREATE TABLE robot (username TEXT PRIMARY KEY, password TEXT, test1 INTEGER, test2 REAL, test3 TEXT)")
        store.commit()
        store.close()

        user_state = UserState()
        user_state.register("test", "", db)

        action = SpeakAction(["\"2020211472\"", "\"林志\"", "Input", "$username", "$test1"])
        result = []
        action.exec(user_state, result, "是我", db)
        self.assertEqual(["2020211472林志是我test0"], result)

        with self.assertRaises(GrammarException):
            SpeakAction(["$vvv"])

        os.remove(os.path.join(current_path, "dsl.db"))


if __name__ == '__main__':
    unittest.main()
