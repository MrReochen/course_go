# -*- coding: utf-8 -*-
import numpy as np
from conf import conf

SIZE = conf['SIZE']
SWAP_INDEX = [1, 0, 3, 2, 5, 4, 7, 6, 9, 8]

def index2coord(index):
    y = index // SIZE
    x = index - SIZE * y
    return x, y

def coord2index(x, y):
    return y * SIZE + x

def legal_moves(board):
    # Occupied places
    mask1 = board[0,:,:,0].reshape(-1) != 0
    mask2 = board[0,:,:,1].reshape(-1) != 0
    mask = mask1 + mask2

    # Ko situations
    ko_mask = ((board[0,:,:,2] - board[0,:,:,0]))
    if (ko_mask == 1).sum() == 1:
        mask += (ko_mask == 1).reshape(-1)

    # Pass is legal after 30 stones on the board
    if (np.sum(board[0, :, :, 0]) + np.sum(board[0, :, :, 1]) >= 30):
        mask = np.append(mask, 0)
    else:
        mask = np.append(mask, 1)
    return mask

def get_real_board(board):
    player = board[0,0,0,-1]
    if player == 1:
        real_board = board[0,:,:,0] - board[0,:,:,1]
    else:
        real_board = board[0,:,:,1] - board[0,:,:,0]
    return real_board

def _show_board(board, policy):
    real_board = get_real_board(board)
    if policy is not None:
        index = policy.argmax()
        x, y = index2coord(index)

    color = "B" if board[0][0][0][-1] == 1 else "W"
    string = "To play: %s\n" % color
    for j, row in enumerate(real_board):
        for i, c in enumerate(row):
            if c == 1:
                string += u"○ "
            elif c == -1:
                string += u"● "
            elif policy is not None and i == x and j == y:
                string += u"X "
            else:
                string += u". "
        string += "\n"
    if policy is not None and y == SIZE:
        string += "Pass policy"
    return string

def show_board(board, policy=None, history=1):
    results = []
    for i in reversed(range(history)):
        tmp_board = np.copy(board)
        tmp_board = tmp_board[:,:,:,i:]
        if i % 2 == 1:
            tmp_board[:,:,:,-1] *= -1
        results.append(_show_board(tmp_board, policy))
    return "\n".join(results)


dxdys = [(1, 0), (-1, 0), (0, 1), (0, -1)]
def capture_group(x, y, real_board, group=None):
    if group is None:
        group = [(x, y)]

    c = real_board[y][x]
    for dx, dy in dxdys:
        nx = x + dx
        ny = y + dy
        if (nx, ny) in group:
            continue
        if not(0 <= nx < SIZE and 0 <= ny < SIZE):
            continue
        dc = real_board[ny][nx]
        if dc == 0:
            return None
        elif dc == c:
            group.append( (nx, ny) )
            group = capture_group(nx, ny, real_board, group=group)
            if group == None:
                return None
    return group

def take_stones(x, y, board):
    real_board = get_real_board(board)
    _player = 1 if board[0,0,0,-1] == 1 else -1
    for dx, dy in dxdys:  # We need to check capture
        nx = x + dx
        ny = y + dy
        if not(0 <= nx < SIZE and 0 <= ny < SIZE):
            continue
        if real_board[ny][nx] == 0:
            continue
        if real_board[ny][nx] == _player:
            continue
        group = capture_group(nx, ny, real_board)
        if group:
            for _x, _y in group:
                assert board[0,_y,_x,1] == 1
                board[0,_y,_x,1] = 0
                real_board[_y][_x] = 0
    for dx, dy in dxdys + [(0, 0)]:  # We need to check self sucide.
        nx = x + dx
        ny = y + dy
        if not(0 <= nx < SIZE and 0 <= ny < SIZE):
            continue
        if real_board[ny][nx] == 0:
            continue
        if real_board[ny][nx] != _player:
            continue
        group = capture_group(nx, ny, real_board)
        if group:
            for _x, _y in group:
                # Sucide
                assert board[0,_y,_x,0] == 1
                board[0,_y,_x,0] = 0
                real_board[_y][_x] = 0

    return board


def make_play(x, y, board):
    player = board[0,0,0,-1]
    board[:,:,:,2:10] = board[:,:,:,0:8]
    if y != SIZE:
        assert board[0,y,x,1] == 0
        assert board[0,y,x,0] == 0
        board[0,y,x,0] = 1  # Careful here about indices
        board = take_stones(x, y, board)
    else:
        # "Skipping", player
        pass
    # swap_players
    board[:,:,:,range(10)] = board[:,:,:,SWAP_INDEX]
    player = -1 if player == 1 else 1
    board[:,:,:,-1] = player
    return board, player

def _color_adjoint(i, j, color, board):
    # TOP
    SIZE1 = len(board)
    SIZE2 = len(board[0])
    if i > 0 and board[i-1][j] == 0:
        board[i-1][j] = color
        _color_adjoint(i - 1, j, color, board)
    # BOTTOM
    if i < SIZE1 - 1 and board[i+1][j] == 0:
        board[i+1][j] = color
        _color_adjoint(i + 1, j, color, board)
    # LEFT
    if j > 0 and board[i][j - 1] == 0:
        board[i][j - 1] = color
        _color_adjoint(i, j - 1, color, board)
    # RIGHT
    if j < SIZE2 - 1 and board[i][j + 1] == 0:
        board[i][j + 1] = color
        _color_adjoint(i, j + 1, color, board)
    return board

def color_board(real_board, color):
    board = np.copy(real_board)
    for i, row in enumerate(board):
        for j, v in enumerate(row):
            if v == color:
                _color_adjoint(i, j, color, board)
    return board


def get_winner(board):
    real_board = get_real_board(board)
    points =  _get_points(real_board)
    black = points.get(1, 0) + points.get(2, 0)
    white = points.get(-1, 0) + points.get(-2, 0) + conf['KOMI']
    if black > white:
        return 1, black, white
    elif black == white:
        return 0, black, white
    else:
        return -1, black, white

def _get_points(real_board):
    colored1 = color_board(real_board,  1)
    colored2 = color_board(real_board, -1)
    total = colored1 + colored2
    unique, counts = np.unique(total, return_counts=True)
    points = dict(zip(unique, counts))
    return points


def game_init():
    board = np.zeros((1, SIZE, SIZE, 11), dtype=np.int32)
    player = 1
    board[:,:,:,-1] = player
    return board, player
