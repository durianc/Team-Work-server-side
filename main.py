from sanic import Sanic
from sanic.response import file
import json
import mimetypes
import ssl
import brotli
app=Sanic(__name__)
app.static('/', './static')
with open('./static/index.html', 'rb') as fp:  # 读入前端的文件，具体是什么根据你们的工作填入，此处抽象化
    html = fp.read()

house = {}  # 房间字典，存放对战房间的信息
@app.middleware("response")
async def set_correct_content_type(request, response):
    if response.file:
        mime_type, encoding = mimetypes.guess_type(response.file.name)
        if mime_type:
            response.headers["Content-Type"] = mime_type
        if encoding:
            response.headers["Content-Encoding"] = encoding



# @app.middleware('response')
# async def set_mime_types_and_encoding(request, response):
#     if response.file and response.file.name:
#         if response.file.name.endswith('.br'):
#             response.headers['Content-Encoding'] = 'br'
#             response.headers['Content-Type'] = 'application/octet-stream'
#         elif response.file.name.endswith('.data.unityweb') or \
#              response.file.name.endswith('.wasm.code.unityweb') or \
#              response.file.name.endswith('.wasm.framework.unityweb'):
#             response.headers['Content-Type'] = 'application/octet-stream'
#         elif response.file.name.endswith('.json'):
#             response.headers['Content-Type'] = 'application/json'
#         elif response.file.name.endswith('.js'):
#             response.headers['Content-Type'] = 'application/javascript'
#         elif response.file.name.endswith('.html'):
#             response.headers['Content-Type'] = 'text/html'


@app.route('/')
async def index(request):
    return await file('./static/index.html')

@app.websocket('/game')
async def game(request, ws):
    # 处理WebSocket连接
    await ws.accept()
    # 处理游戏逻辑
    while True:
        event = await ws.recv()
        data = json.loads(event)
        if data['type'] == 'EnterRoom':
            # 处理进入房间逻辑
            room_id = data['room']
            user_id = data['id']
            if room_id not in house:
                house[room_id] = {
                    'players': {},
                    'cards': {},  # 存储卡牌数据
                    'game_state': {},  # 存储游戏状态数据
                    'sends': {},  # 存储每个玩家的WebSocket连接
                }
            room = house[room_id]
            if user_id not in room['players']:
                room['players'][user_id] = {
                    'ws': ws,
                    'cards_in_hand': [],  # 玩家手中的卡牌
                }
            # 发送初始化房间状态给客户端
            await ws.send(json.dumps({
                'type': 'InitializeRoomState',
                'players': list(room['players'].keys()),
                'cards': room['cards'],
                'game_state': room['game_state'],
            }))

        elif data['type'] == 'DropPiece':
            # 处理放置卡牌逻辑
            room_id = data['room']
            user_id = data['id']
            card_id = data['card_id']
            position = data['position']
            room = house[room_id]
            if user_id not in room['players']:
                # 如果用户不是房间内的玩家之一，不允许放置卡牌
                continue
            if card_id not in room['cards']:
                # 如果卡牌不存在，不允许放置卡牌
                continue
            player = room['players'][user_id]
            if card_id not in player['cards_in_hand']:
                # 如果玩家手中没有该卡牌，不允许放置卡牌
                continue
            # 处理放置卡牌的逻辑
            # ...
            # 更新游戏状态
            room['game_state']['board'][position] = card_id
            # 移除玩家手中的卡牌
            player['cards_in_hand'].remove(card_id)
            # 向房间内的所有玩家发送更新后的游戏状态
            for player_id, player_data in room['players'].items():
                await player_data['ws'].send(json.dumps({
                    'type': 'GameStateUpdate',
                    'game_state': room['game_state'],
                }))

        elif data['type'] == 'UseCard':
            # 处理使用卡牌逻辑
            room_id = data['room']
            user_id = data['id']
            card_id = data['card_id']
            room = house[room_id]
            if user_id not in room['players']:
                # 如果用户不是房间内的玩家之一，不允许使用卡牌
                continue
            player = room['players'][user_id]
            if card_id not in player['cards_in_hand']:
                # 如果玩家手中没有该卡牌，返回失败结果给前端
                response = {
                    'type': 'CardUsed',
                    'card_id': card_id,
                    'result': 'failure',
                }
            else:
                # 处理使用卡牌的逻辑
                # ...
                # 返回成功结果给前端
                response = {
                    'type': 'CardUsed',
                    'card_id': card_id,
                    'result': 'success',
                }
            await ws.send(json.dumps(response))
            # 处理其他类型的消息
            # ...

ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain("cert.pem", keyfile="key.pem")
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=60001)
