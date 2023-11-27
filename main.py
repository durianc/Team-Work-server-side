from sanic import Sanic
from sanic.response import file
from collections import defaultdict
import json

app = Sanic(__name__)
app.static('/', './static')
with open('./static/index.html', 'rb') as fp:
    html = fp.read()

house = {}
@app.route('/')
def index(request):
    return file('static/index.html')

# 一个存储房间和玩家状态的字典
rooms = defaultdict(lambda: {"players": {}, "game_state": {}})


def generate_room_id():
    for room_number in range(1, 13):  # 遍历1到12的房间号码
        room_id = str(room_number)
        if not is_room_full(room_id):
            return room_id
    return None  # 所有房间都满了
def is_room_full(room_id):
    return len(rooms[room_id]["players"]) >= 2

def generate_user_id(room_id):
    # 如果房间是空的，返回 "0"
    if len(rooms[room_id]["players"]) == 0:
        return "0"
    # 如果房间有一个玩家，返回 "1"
    elif len(rooms[room_id]["players"]) == 1:
        return "1"
    # 超过两个玩家则是异常情况
    else:
        raise ValueError("Room is already full")

@app.websocket('/game', name='game_without_room_id')
@app.websocket('/game/<room_id>', name='game_with_room_id')
async def game(request, ws, room_id=None):
    # 如果没有提供 room_id，为用户分配一个房间
    if room_id is None:
        room_id = generate_room_id()
        if room_id is None:
            await ws.send(json.dumps({"type": "Error", "message": "All rooms are full"}))
            await ws.close(code=1000)
            return

        # 新房间可能需要在这里初始化
        if room_id not in rooms:
            rooms[room_id] = {"players": {}, "game_state": {}}

    try:
        user_id = generate_user_id(room_id)
    except ValueError:
        await ws.send(json.dumps({"type": "Error", "message": "Room is full"}))
        await ws.close(code=1000)
        return

        # 如果成功生成 user_id，我们继续加入房间
    room = rooms[room_id]
    room["players"][user_id] = ws

    # 向用户发送其ID和房间ID
    await ws.send(json.dumps({"type": "UserInfo", "room_id": room_id, "user_id": user_id }))
    # 监听玩家的消息
    while True:
        data = await ws.recv()
        print(data)
        # message = json.loads(data)
        #
        # # 根据消息类型处理游戏逻辑
        # if message["type"] == "Action":
        #     # 更新游戏状态
        #     pass  # 替换为具体的游戏逻辑代码
        #
        # # 广播更新后的游戏状态给房间内的所有玩家
        # for player_id, player_ws in room["players"].items():
        #     if player_ws != ws:  # 不要将消息发送回来源玩家
        #         await player_ws.send(json.dumps({
        #             "type": "Update",
        #             "game_state": room["game_state"]
        #         }))


# 运行服务端
if __name__ == '__main__':
    app.run(host='10.133.42.136', port=60001,debug=True)

# 启用单进程模式后，你可以更容易地查看任何启动错误，因为所有错误都将直接输出到控制台
# if __name__ == '__main__':
#     app.run(host='172.20.10.3', port=60001, debug=True, single_process=True)
