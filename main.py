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

@app.websocket('/game/<int:room_id>')
def game(request, ws, room_id):
    user_id = request.args.get('id')

    if not user_id:
        return

    if room_id not in rooms:
        return

    if room_id not in house:
        house[room_id] = {
            'players': {},
            'pieces': [],
            'sends': [],
        }

    room = house[room_id]
    if user_id not in room['players']:
        room['players'][user_id] = {
            'ws': ws,
            'ready': False,
        }

    ws.send(json.dumps({
        'type': 'InitializeRoomState',
        'pieces': room['pieces'],
        'players': list(room['players'].keys()),
        'ready': all(player['ready'] for player in room['players'].values()),
    }))

    for player_id, player_data in room['players'].items():
        if player_id != user_id:
            player_data['ws'].send(json.dumps({
                'type': 'AddPlayer',
                'ready': all(player['ready'] for player in room['players'].values()),
            }))

    while True:
        event = ws.recv()
        data = json.loads(event)
        if data['type'] == 'DropPiece':
            room['pieces'].append((data['x'], data['y']))
            for player_id, player_data in room['players'].items():
                if player_id != user_id:
                    player_data['ws'].send(json.dumps({
                        'type': 'DropPiece',
                        'x': data['x'],
                        'y': data['y'],
                    }))
        elif data['type'] == 'SetPlayerReady':
            player_data = room['players'][user_id]
            player_data['ready'] = True
            ws.send(json.dumps({
                'type': 'PlayerReady',
                'ready': all(player['ready'] for player in room['players'].values()),
            }))

            for player_id, player_data in room['players'].items():
                if player_id != user_id:
                    player_data['ws'].send(json.dumps({
                        'type': 'AddPlayer',
                        'ready': all(player['ready'] for player in room['players'].values()),
                    }))


if __name__ == '__main__':
    app.run(host='10.133.18.99', port=60001,debug=True)