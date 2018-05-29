import json
from queue import Queue
from model import load_best_model
from collections import OrderedDict
import numpy as np
from conf import conf
from datetime import datetime
from engine import ModelEngine
from play import (
game_init, make_play
)

global start_time, time_limit

class Utils:
    @staticmethod
    def json_input():
        raw = input()
        obj = json.loads(raw, object_pairs_hook=OrderedDict)
        return OrderedDict(obj)

    @staticmethod
    def json_output(obj):
        raw = json.dumps(obj)
        print(raw)

def main():
    global start_time, time_limit
    start_time = datetime.now()
    time_limit = 11.6

    raw = Utils.json_input()
    request = raw['requests']

    model = load_best_model()

    board, player = game_init()
    if not (request['x']==-2 and request['y']==-2):
        board, player = make_play(request['x'] - 1, request['y'] - 1, board)

    if player == 1:
        color = 'B'
    else:
        color = 'W'

    engine = ModelEngine(model, conf['MCTS_SIMULATIONS'], board)
    x, y, _, _, _, _, _ = engine.genmove(color)
    response = {}
    response['x'], response['y'] = x + 1, y + 1
    if y == conf['SIZE']:
        response['x'], response['y'] = -1, -1
    Utils.json_output({'response': response})
    print(">>>BOTZONE_REQUEST_KEEP_RUNNING<<<")
    time_limit = 3.6

    while True:
        try:
            start_time = datetime.now()
            raw = Utils.json_input()
            request = raw['requests']
            if not(request['x']==-1 and request['y']==-1):
                engine.play('B', request['x'] - 1, request['y'] - 1, update_tree=True)
            x, y, _, _, _, _, _ = engine.genmove(color)
            response = {}
            response['x'], response['y'] = x + 1, y + 1
            if y == conf['SIZE']:
                response['x'], response['y'] = -1, -1
            Utils.json_output({'response': response})
            print(">>>BOTZONE_REQUEST_KEEP_RUNNING<<<")
        except json.JSONDecodeError:
            break


if __name__ == '__main__':
    main()
