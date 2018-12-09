import zstd
import json
import os

"""
PLACE REPLAY FILE IN THIS DIRECTORY
WILL PARSE THE HLT AND GENERATE MOVES PER PLAYER TO SIMULATE GAME
"""

def load_hlt(filename):
    """
    TAKES HLT FILE AND RETURNS IN JSON FORMAT
    """
    data = zstd.decompress(open(filename, "rb").read())     ## DECOMPRESS HLT FILE (COMPRESSED JSON)
    data_json = json.loads(data.decode())                   ## LOAD JSON

    return data_json


def save_json(filename, data):
    """
    TAKES DATA IN JSON FORMAT AND WRITES INTO A FILE (FILENAME)
    """
    with open(filename, 'w') as outfile:
        json.dump(data, outfile, indent=4)


def generate_run_game_bat(data):
    """
    GENERATE run_game.bat

    halite.exe --replay-directory replays/ -vvv --height 32 --width 32 --seed XXXXXXXXX "python v2/MyBot.py" "python MyBot.py"
    """
    width = data['production_map']['width']
    height = data['production_map']['height']
    seed = data['map_generator_seed']
    num_players = data['number_of_players']

    if num_players == 2:
        command = "halite.exe --replay-directory replays/ -vvv --height {} --width {} --seed {} \"python simulate_p0.py\" \"python simulate_p1.py\"".format(height, width, seed)

    elif num_players == 4:
        command = "halite.exe --replay-directory replays/ -vvv --height {} --width {} --seed {} \"python simulate_p0.py\" \"python simulate_p1.py\" \"python simulate_p2.py\" \"python simulate_p3.py\"".format(height, width, seed)

    with open('../run_game.bat', 'w') as outfile:
        outfile.write(command)


def get_moves_per_player(data):
    """
    PARSE JSON TO GET EACH PLAYERS MOVES PER TURN
    """
    def get_player_names(data):
        command_moves = {}

        for player in data['players']:
            id = player['player_id']
            name = player['name']
            command_moves[id] = [name]

        return command_moves, len(command_moves)


    def get_moves_this_turn(player_data, id, command_moves):
        """
        PARSES MOVES THIS TURN, ADD TO COMMAND_MOVES_PX
        """
        current_turn_commands = []

        if player_data:
            for move in player_data:
                if move.get('type') == "g": ## SPAWNING SHIP
                    current_turn_commands.append("g")

                elif move.get('type') == "m": ## MOVING SHIP
                    current_turn_commands.append("m {} {}".format(move.get('id'), move.get('direction')))

                elif move.get('type') == "c": ## BUILDING DOCK
                    current_turn_commands.append("c {}".format(move.get('id')))

        command_moves[id].append(current_turn_commands)


    def save_moves_json(filename, commands):
        """
        SAVES MOVES TO JSON FILE
        """
        save_json(filename, commands)


    command_moves, num_players = get_player_names(data)

    for i, full_frames in enumerate(data['full_frames']):
        """
            "moves": {},
            "entities": {},
            "cells": [],
            "deposited": {
                "0": 0,
                "1": 0
            },
            "events": [],
            "energy": {
                "0": 5000,
                "1": 5000
            }
        """
        print("At turn {}".format(i))
        for id in range(num_players):
            get_moves_this_turn(full_frames['moves'].get(str(id)),
                                id,
                                command_moves)

    for id in range(num_players):
        save_moves_json("../moves/p{}.txt".format(id), command_moves[id])


def get_filename():
    ## GET FILENAME OF .hlt IN CURRENT DIRECTORY
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith(".hlt"):
                return file


## MAIN
data = load_hlt(get_filename)
get_moves_per_player(data)
generate_run_game_bat(data)
save_json("parsed.txt",data)


