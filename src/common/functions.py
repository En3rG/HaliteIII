from hlt.positionals import Direction
from src.common.matrix.functions import calculate_distance
from src.common.values import Matrix_val
import logging
import heapq

def get_adjacent_directions(direction):
    """
    GET ITS SIDE DIRECTIONS (NOT THE OPPOSITE THOUGH)
    """
    if direction == Direction.North:
        return [Direction.West, Direction.East]
    elif direction == Direction.East:
        return [Direction.North, Direction.South]
    elif direction == Direction.South:
        return [Direction.East, Direction.West]
    elif direction == Direction.West:
        return [Direction.South, Direction.North]


def a_star(matrix_path, matrix_cost, start_pos, goal_pos):
    """
    A* ALGORITHM TO GET THE BEST PATH FROM START TO GOAL
    CONSIDERING OBSTRUCTION AND COST ALONG THE WAY

    :param matrix_path:
    :param matrix_cost:
    :param start_pos:
    :param goal_pos:
    :return:
    """
    def heuristic(a, b, cost):
        """
        POINT SYSTEM BASED ON COST / DISTANCE
        DISTANCE, IF TAKEN THE SQRT
        ADDING SQUARED VALUE SINCE IF COST IS THE SAME, WILL GET HIGHER DISTANCE
        EXAMPLE: 1000/7 > 1000/9, WHERE 7 AND 9 ARE DISTANCES (WHICH IS NOT TRUE).  7 SHOULD BE A BETTER HEURISTIC
        """
        d = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)
        if d == 0: return 0
        else: return (cost / d) + (d ** 2)


    def isBadNeighbor(array, neighbor):
        """
        CHECKS IF THE NEIGHBOR IS WITHIN THE ARRAY BOUNDARIES
        OR IF THE NEIGHBOR IS AN OBSTRUCTION
        """
        if 0 <= neighbor[0] < array.shape[0] and 0 <= neighbor[1] < array.shape[1] \
                and array[neighbor[0]][neighbor[1]] == 0:
            return False
        else:
            ## OUTSIDE ARRAY Y OR X BOUNDARY
            ## OR ITS AN OBSTRUCTION (BAD/SKIP)
            return True

    start = (start_pos.y, start_pos.x)
    goal = (goal_pos.y, goal_pos.x)
    start_cost = matrix_cost[start_pos.y][start_pos.x]

    ## NEIGHBORS IN NORTH, EAST, SOUTH, WEST DIRECTIONS
    neighbors = [(-1, 0), (0, 1), (1, 0), (0, -1)]

    visited_cells = set()
    came_from = {}
    score_to_start = {start: 0}
    score = {start: heuristic(start, goal, start_cost)}             ## FULL SCORE OF EACH CELL OR COORD. FROM START TO GOAL
    myheap = []

    ## HEAP CONSIST OF SCORE, COORD
    heapq.heappush(myheap, (score[start], start))

    while myheap:
        curr_score, curr_cell = heapq.heappop(myheap)

        if curr_cell == goal:                                       ## GOAL REACHED, GET PATH
            data_cells = []
            while curr_cell in came_from:
                data_cells.append(curr_cell)
                curr_cell = came_from[curr_cell]
            data_cells.append(start)                                ## APPEND STARTING LOCATION
            return data_cells                                       ## START COORD WILL BE AT THE END, GOAL AT FIRST!

        visited_cells.add(curr_cell)

        for r, c in neighbors:
            neighbor_cell = (curr_cell[0] + r, curr_cell[1] + c)
            bad_neighbor = isBadNeighbor(matrix_path, neighbor_cell)

            if bad_neighbor:
                continue

            neighbor_cost = matrix_cost[neighbor_cell[0]][neighbor_cell[1]]
            curr_score_to_start = score_to_start[curr_cell] + heuristic(curr_cell, neighbor_cell, neighbor_cost)

            if neighbor_cell in visited_cells and curr_score_to_start >= score_to_start.get(neighbor_cell, 0):  ## 0 DEFAULT VALUE
                ## A BETTER SOLUTION EXIST TOWARDS THIS NEIGHBOR CELL
                continue

            ## IF A BETTER score_to_start IS FOUND FOR THAT NEIGHBOR COORD OR NEIGHBOR COORD NOT IN HEAP
            if curr_score_to_start < score_to_start.get(neighbor_cell, 0) or neighbor_cell not in (i[1] for i in myheap):
                came_from[neighbor_cell] = curr_cell                                                ## NEIGHBOR COORD CAME FROM CURRENT COORD
                score_to_start[neighbor_cell] = curr_score_to_start                                 ## NEIGHBOR DISTANCE FROM START
                score[neighbor_cell] = curr_score_to_start + heuristic(neighbor_cell, goal, 1000)   ## GSCORE PLUS DISTANCE TO GOAL
                heapq.heappush(myheap, (score[neighbor_cell], neighbor_cell))                       ## PUSH NEIGHBOR TO HEAP

    return []