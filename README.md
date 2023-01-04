# DSL

一个应用于在线机器人的脚本语言及其解释器，配有相应客户端及数据库。

## 特性

- 基于有限状态自动机的应答逻辑。
- 自定义用户变量，持久化访问。
- 基于 PyParsing的解释器。
- 基于 storm & SQLite 的 数据库
- 用户注册/登录，`JWT` 鉴权。
- PyQt5 & QtQuick 实现的客户端。
- Restful 接口设计风格

## 模块划分
client :            客户端程序
server :            服务端Model层
doc :               实验文档
test :              测试
app.py :            服务端Controller层
grammar.txt :       测试脚本文法
dsl.db :            数据库
requirements.txt :  项目依赖
test.sh :           测试集合

 
## 用户指南
安装依赖：

```
pip install -r requirements.txt
```

启动服务端：

```
python -m flask run 
可选: --host -- port
```

启动客户端：

```
cd client
python main.py
```
启动测试集合

```
./test.sh
```

启动单独测试

```
cd test
python -m test_parser
python -m test_speak_action
python -m test_update_action
python -m test_user_state
python -m test_state
python -m test_app
python -m test_pressure
```