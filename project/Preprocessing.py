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
    # data_dir = 'data/wiki_data_tables/'
    # for filename in os.listdir(data_dir):
    #     with open(data_dir + filename) as json_file:
    #         json_data = json_file.read()
    #         molecule_data = json.loads(json_data)
    #         DATABASE[filename] = molecule_data
    # with open('data/database_raw.json', 'w') as json_file:
    #     json_file.write(json.dumps(DATABASE, separators=(',', ':'), sort_keys=True, indent=4))
    global DATABASE
    with open(filename) as data_file:
        DATABASE = json.loads(data_file.read())
        for key in DATABASE:
            new_key = key.replace('.json', '')
            DATABASE[new_key] = DATABASE.pop(key)


load_data('data/database_raw.json')
count_keys()
