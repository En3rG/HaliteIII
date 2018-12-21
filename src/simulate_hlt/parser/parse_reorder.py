import zstd
import json
import os
import heapq

"""
PLACE REPLAY FILE IN THIS DIRECTORY
WILL PARSE THE HLT AND GENERATE MOVES PER PLAYER TO SIMULATE GAME

REORDER SINCE ENGINE ONLINE DOESNT GENERATE SAME EVENT ORDER AS LOCAL ENGINE

ISSUE:  MY BOT ONLINE DOESNT MATCH LOCALLY
        SINCE I USED SETS, AND ITERATE THROUGH IT, ORDER OF SET COULD CHANGE!!!
"""
class Parse():
    def __init__(self):
        """
        WHEN SPAWNING "g" ENGINE ORDER IS:
        LOCAL:  PLAYER 0, 1, 2, 3
        ONLINE: PLAYER 3, 2, 0, 1
        """
        self.remap = {0:{}, 1:{}, 2:{}, 3:{}}       ## WILL CONTAIN MAP WHAT TO CHANGE SHIP IDs DUE TO EVENT/ORDER DIFFERENCE ONLINE AND LOCALLY
        self.heap = []
        ## USED TO GET WHICH PLAYER GETS THE SHIP ID FIRST, THIS IS THE LOCAL ENGINE ORDER
        self.local_order = {0:(0, 0),
                            1:(1, 1),
                            2:(2, 2),
                            3:(3, 3)}
        self.replay_filename = self.get_replay_filename()
        self.output_filename = "parsed.txt"
        self.data = self.load_hlt()
        self.get_moves_per_player()
        self.generate_run_game_bat()
        self.save_json(self.output_filename, self.data)


    def get_replay_filename(self):
        ## GET FILENAME OF .hlt IN CURRENT DIRECTORY
        for root, dirs, files in os.walk(os.getcwd()):
            for file in files:
                if file.endswith(".hlt"):
                    return file


    def load_hlt(self):
        """
        TAKES HLT FILE AND RETURNS IN JSON FORMAT
        """
        data = zstd.decompress(open(self.replay_filename, "rb").read())     ## DECOMPRESS HLT FILE (COMPRESSED JSON)
        data_json = json.loads(data.decode())                   ## LOAD JSON

        return data_json


    def save_json(self, output_file, data):
        """
        TAKES DATA IN JSON FORMAT AND WRITES INTO A FILE (FILENAME)
        """
        with open(output_file, 'w') as outfile:
            json.dump(data, outfile, indent=4)


    def generate_run_game_bat(self):
        """
        GENERATE run_game.bat

        halite.exe --replay-directory replays/ -vvv --height 32 --width 32 --seed XXXXXXXXX "python v2/MyBot.py" "python MyBot.py"
        """
        width = self.data['production_map']['width']
        height = self.data['production_map']['height']
        seed = self.data['map_generator_seed']
        num_players = self.data['number_of_players']

        if num_players == 2:
            command = "halite.exe --replay-directory replays/ -vvv --height {} --width {} --seed {} \"python simulate_p0.py\" \"python simulate_p1.py\"".format(height, width, seed)

        elif num_players == 4:
            command = "halite.exe --replay-directory replays/ -vvv --height {} --width {} --seed {} \"python simulate_p0.py\" \"python simulate_p1.py\" \"python simulate_p2.py\" \"python simulate_p3.py\"".format(height, width, seed)

        with open('../run_game.bat', 'w') as outfile:
            outfile.write(command)


    def get_moves_per_player(self):
        """
        PARSE JSON TO GET EACH PLAYERS MOVES PER TURN
        """

        command_moves, num_players = self.get_player_names()

        for i, full_frames in enumerate(self.data['full_frames']):
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
            for player_id in range(num_players):
                self.get_moves_this_turn(full_frames['moves'].get(str(player_id)),
                                        player_id,
                                        command_moves)

            ## BELOW IS TO GENERATE THE REMAP DICTIONARY
            online_order = {}
            local_order = {}
            while self.heap:
                for event in full_frames['events']:
                    if event.get('type') == "spawn":
                        ship_id = event.get('id')
                        owner_id = event.get('owner_id')
                        id, player_id = heapq.heappop(self.heap)

                        print("Online: ship_id {} owner_id {} heap: id {} player_id {}".format(ship_id, owner_id, id, player_id))

                        online_order[owner_id] = ship_id
                        local_order[player_id] = ship_id

            print("online_order: {}".format(online_order))
            print("local_order: {}".format(local_order))
            for player_id, ship_id in online_order.items():
                self.remap[player_id][ship_id] = local_order[player_id]

            self.heap = []

        for id in range(num_players):
            self.save_json("../moves/p{}.txt".format(id), command_moves[id])


    def get_player_names(self):
        command_moves = {}

        for player in self.data['players']:
            id = player['player_id']
            name = player['name']
            command_moves[id] = [name]

        return command_moves, len(command_moves)


    def get_moves_this_turn(self, player_data, player_id, command_moves):
        """
        PARSES MOVES THIS TURN, ADD TO COMMAND_MOVES_PX
        """
        current_turn_commands = []

        if player_data:
            for move in player_data:
                if move.get('type') == "g": ## SPAWNING SHIP
                    current_turn_commands.append("g")
                    ## HEAP IS USED TO GET WHICH PLAYER GETS THE NEW SHIP FIRST
                    heapq.heappush(self.heap, self.local_order[player_id])

                elif move.get('type') == "m": ## MOVING SHIP
                    remap_id = self.remap[player_id][move.get('id')]
                    current_turn_commands.append("m {} {}".format(remap_id, move.get('direction')))

                elif move.get('type') == "c": ## BUILDING DOCK
                    remap_id = self.remap[player_id][move.get('id')]
                    current_turn_commands.append("c {}".format(remap_id))

        command_moves[player_id].append(current_turn_commands)


start = Parse()




