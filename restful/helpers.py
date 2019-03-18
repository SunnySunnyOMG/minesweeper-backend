from rest_framework import permissions
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.db.models import Q
import random
MINE = -1
FLAG = 10
MINE = -1
UNKNOWN = 9

def is_in_map(x, y, size_x, size_y):
    return x >= 0 and x < size_x and y >= 0 and y < size_y


def check(x, y, size_x, size_y, map_data):
    map_data[y][x] = MINE

    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if i == 0 and j == 0:
                continue
            dx = x + i
            dy = y + j
            if is_in_map(dx, dy, size_x, size_y) and map_data[dy][dx] != MINE:
                map_data[dy][dx] += 1


# get the game map and save the data to a 2-D array
def gen_map_data(size_x, size_y, mine_num):
    # data type conversion
    size_x, size_y, mine_num = int(size_x), int(size_y), int(mine_num)
    # array length
    map_size = size_x * size_y

    # judge edge case
    if map_size < mine_num:
        return False

    # generate mines
    mine_pos = random.sample(range(map_size), mine_num)

    # generate 2-d map
    map_data = [[0]*size_x for _ in range(size_y)]

    # check numbers
    for pos in mine_pos:
        x = pos % size_x
        y = pos // size_x
        check(x, y, size_x, size_y, map_data)

    return map_data

# gen initial snapshot
def init_map_snapshot(size_x, size_y):
    return [[UNKNOWN]*int(size_x) for _ in range(int(size_y))]

class ReadCreateAndPatchOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in ('GET', 'HEAD', 'OPTIONS', 'POST', 'PATCH')

class CreateOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method == 'POST'


def fill(snapshot, map_data, x, y, size_x, size_y):
    if is_in_map(x, y, size_x, size_y):
        # exit conditon
        if map_data[y][x] > 0 or snapshot[y][x] != UNKNOWN:
            if snapshot[y][x] == UNKNOWN or snapshot[y][x] == FLAG:
                snapshot[y][x] = map_data[y][x]
            return
        # fill
        snapshot[y][x] = map_data[y][x]
        # recursive search
        fill(snapshot, map_data, x - 1, y, size_x, size_y)
        fill(snapshot, map_data, x + 1, y, size_x, size_y)
        fill(snapshot, map_data, x, y - 1, size_x, size_y)
        fill(snapshot, map_data, x, y + 1, size_x, size_y)


def update_snapshot_of_game(map_data, snapshot, x, y, is_flag):
    size_x = len(map_data[0])
    size_y = len(map_data)

    # if is a inlegal input, do nothing
    if not is_in_map(x, y, size_x, size_y):
        print('do nothing, input is out of valid area')
        return snapshot

    # if mark as a flag
    if is_flag:
        if snapshot[y][x] == FLAG:
            snapshot[y][x] = UNKNOWN
        else:
            snapshot[y][x] = FLAG
        return snapshot

    # if hit on a place near a mine, return the num
    if map_data[y][x] > 0:
        snapshot[y][x] = map_data[y][x]
        return snapshot

    # if hit on a safe area, fill the area and return new snapshot
    if map_data[y][x] == 0:

        fill(snapshot, map_data, x, y, size_x, size_y)
        return snapshot

def is_lose(map_data, x, y):
    return map_data[y][x] == MINE

def is_win(snapshot, map_data, x, y): 
    size_x = len(map_data[0])
    size_y = len(map_data)

    for i in range(size_x):
        for j in range(size_y):
            if snapshot[j][i] == UNKNOWN:
              return False
            if snapshot[j][i] == FLAG and map_data[j][i] != MINE:
              return False
    
    return True

