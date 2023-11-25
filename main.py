from sanic import Sanic
from sanic.response import file

import json

app = Sanic(__name__)
app.static('/', './static')
with open('./static/index.html', 'rb') as fp:
    html = fp.read()

house = {}

# 增加一个列表用于存储房间号
rooms = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

@app.route('/')
def index(request):
    return file('static/index.html')


@app.websocket('/game/<room_id>')
async def feed(request, ws, room_id):
    while True:
        data = 'Hello from the server!'
        print('Sending: ' + data)
        await ws.send(data)

        # 接收消息
        data = await ws.recv()

        # 如果数据是bytes类型，则解码为str
        if isinstance(data, bytes):
            data = data.decode('utf-8')  # 或者使用你期望的字符集

        print('Received: ' + data)
# async def game(request, ws, room_id):  # 使用 `async` 定义异步函数
#     user_id = request.args.get('id')
#
#     if not user_id:
#         return
#
#     if room_id not in rooms:
#         return
#
#     if room_id not in house:
#         house[room_id] = {
#             'players': {},
#             'pieces': [],
#             'sends': [],
#         }
#
#     room = house[room_id]
#     if user_id not in room['players']:
#         room['players'][user_id] = {
#             'ws': ws,
#             'ready': False,
#         }
#     await ws.send('Hello!')
    # await ws.send(json.dumps({  # 使用 `await` 等待异步操作完成
    #     'type': 'InitializeRoomState',
    #     'pieces': room['pieces'],
    #     'players': list(room['players'].keys()),
    #     'ready': all(player['ready'] for player in room['players'].values()),
    # }))
    #
    # for player_id, player_data in room['players'].items():
    #     if player_id != user_id:
    #         await player_data['ws'].send(json.dumps({  # 使用 `await` 等待异步操作完成
    #             'type': 'AddPlayer',
    #             'ready': all(player['ready'] for player in room['players'].values()),
    #         }))
    #
    # while True:
    #     event = await ws.recv()  # 使用 `await` 等待异步操作完成
    #     data = json.loads(event)
    #     if data['type'] == 'DropPiece':
    #         room['pieces'].append((data['x'], data['y']))
    #         for player_id, player_data in room['players'].items():
    #             if player_id != user_id:
    #                 await player_data['ws'].send(json.dumps({  # 使用 `await` 等待异步操作完成
    #                     'type': 'DropPiece',
    #                     'x': data['x'],
    #                     'y': data['y'],
    #                 }))
    #     elif data['type'] == 'SetPlayerReady':
    #         player_data = room['players'][user_id]
    #         player_data['ready'] = True
    #         await ws.send(json.dumps({  # 使用 `await` 等待异步操作完成
    #             'type': 'PlayerReady',
    #             'ready': all(player['ready'] for player in room['players'].values()),
    #         }))
    #
    #         for player_id, player_data in room['players'].items():
    #             if player_id != user_id:
    #                 await player_data['ws'].send(json.dumps({  # 使用 `await` 等待异步操作完成
    #                     'type': 'AddPlayer',
    #                     'ready': all(player['ready'] for player in room['players'].values()),
    #                 }))



if __name__ == '__main__':
    app.run(host='10.133.28.55', port=60001,debug=True)