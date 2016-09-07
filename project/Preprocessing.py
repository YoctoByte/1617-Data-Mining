import os
import json


DATABASE = dict()


def count_keys():
    keys = dict()
    for molecule in DATABASE:
        for key in DATABASE[molecule]:
            if key in keys:
                keys[key] += 1
            else:
                keys[key] = 1
    keys_sorted = sorted(keys.items(), key=lambda tup: tup[1])
    print('number of molecules: ' + str(len(DATABASE)))
    print(keys_sorted)


def load_data(filename):
    global DATABASE
    with open(filename) as data_file:
        DATABASE = json.loads(data_file.read())
        for key in DATABASE:
            new_key = key.replace('.json', '')
            DATABASE[new_key] = DATABASE.pop(key)


load_data('data/database_raw.json')
count_keys()
