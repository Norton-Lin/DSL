"""
更新动作测试
"""
import os
import unittest
from storm.properties import Int, Float, Unicode
from storm.store import Store
import sys
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from server.database.database import Database
from server.state.action import UpdateAction
from server.user.user_state import VariableSet, UserState
from server.util.GrammarException import GrammarException

current_path = os.path.split(os.path.realpath(__file__))[0]


class TestUpdateAction(unittest.TestCase):
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

        action = UpdateAction("test1", "Set", 1, None)
        action.exec(user_state, [], "", db)
        store = Store(db.database)
        self.assertEqual(store.get(VariableSet, "test").test1, 1)
        store.close()

        action = UpdateAction("test1", "Add", 1, "Int")
        action.exec(user_state, [], "", db)
        store = Store(db.database)
        self.assertEqual(store.get(VariableSet, "test").test1, 2)
        store.close()

        action = UpdateAction("test2", "Sub", 1.5, "Real")
        action.exec(user_state, [], "", db)
        store = Store(db.database)
        self.assertEqual(store.get(VariableSet, "test").test2, -1.5)
        store.close()

        action = UpdateAction("test2", "Set", "Input", "Real")
        action.exec(user_state, [], "2.2", db)
        store = Store(db.database)
        self.assertEqual(store.get(VariableSet, "test").test2, 2.2)
        store.close()

        action = UpdateAction("test3", "Set", "\"测试\"", None)
        action.exec(user_state, [], "", db)
        store = Store(db.database)
        self.assertEqual(store.get(VariableSet, "test").test3, "测试")
        store.close()

        action = UpdateAction("test3", "Set", "Input", "Text")
        action.exec(user_state, [], "testing", db)
        store = Store(db.database)
        self.assertEqual(store.get(VariableSet, "test").test3, "testing")
        store.close()

        with self.assertRaises(GrammarException):
            UpdateAction("test1", "Set", "Input", "Text")
        with self.assertRaises(GrammarException):
            UpdateAction("test1", "Set", "Input", "Real")
        with self.assertRaises(GrammarException):
            UpdateAction("test1", "Set", 2.2, None)
        with self.assertRaises(GrammarException):
            UpdateAction("test2", "Set", "Input", "Text")
        with self.assertRaises(GrammarException):
            UpdateAction("test2", "Set", "\"12\"", None)
        with self.assertRaises(GrammarException):
            UpdateAction("test3", "Add", "\"12\"", None)
        with self.assertRaises(GrammarException):
            UpdateAction("test3", "Set", "Input", None)
        with self.assertRaises(GrammarException):
            UpdateAction("test4", "Set", "", None)

        os.remove(os.path.join(current_path, "dsl.db"))


if __name__ == '__main__':
    unittest.main()
