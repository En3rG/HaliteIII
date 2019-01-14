from hlt.positionals import Direction
from src.common.values import MyConstants
from hlt.positionals import Position
from src.common.matrix.functions import calculate_distance
from src.common.values import Matrix_val
from src.common.print import print_matrix
import logging
import heapq


def get_goal_in_section(matrix_path, center_section, start, goal, directions):
    """
    GET POSITION OF GOAL IN SECTION, INSTEAD OF GOAL WHICH CAN BE PRETTY FAR

    :param matrix_path: PATH WITH OBSTRUCTIONS
    :param center_section: CENTER OF SECTION, WHERE A STAR WILL START
    :param start: ACTUAL START POSITION OF SHIP
    :param goal: ACTUAL GOAL POSITION OF SHIP
    :param directions: DIRECTIONS TOWARDS THE GOAL
    :return: POSITION OF THE GOAL IN THE SECTION
    """
    r = min(MyConstants.deposit.search_perimeter, abs(start.y - goal.y))
    c = min(MyConstants.deposit.search_perimeter, abs(start.x - goal.x))

    if Direction.North in directions:
        y = center_section.y - r
    else:
        y = center_section.y + r

    if Direction.West in directions:
        x = center_section.x - c
    else:
        x = center_section.x + c

    return Position(x, y)


def a_star(matrix_path, matrix_cost, start_pos, goal_pos, lowest_cost):
    """
    A* ALGORITHM TO GET THE BEST PATH FROM START TO GOAL
    CONSIDERING OBSTRUCTION AND COST ALONG THE WAY

    :param matrix_path:
    :param matrix_cost:
    :param start_pos:
    :param goal_pos:
    :return:
    """
    def heuristic(a, b, cost, lowest_cost):
        """
        :param a: POSITION A
        :param b: POSITION B
        :param cost: HALITE COST
        :param lowest_cost: IF TRUE, USE HEURISTIC WITH LOWEST HALITE, IF FALSE, FIND MOST EXPENSIVE PATH (HIGH HALITE)
        :return: POINTS
        """
        dy = abs(a[0] - b[0])
        dx = abs(a[1] - b[1])
        d = dx + dy

        if lowest_cost:
            ## OLD WAY
            # d = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)
            # if d == 0: return 0
            # else: return (cost / d) + (d ** 2)

            ## NEW WAY
            ## WEIGHTED TO PREVENT LONG CHEAP PATHS
            return (cost * 0.0015) + (d * 0.9985)
        else:
            if d == 0 or cost == 0:
                return 0
            else:
                ## DIVISION COSTS A LOT (TIMES OUT)
                #return -(cost / d)
                ## USING A DICTIONARY
                #ratio_d = data.myDicts.ratios[d]
                #return -(cost * ratio_d)

                return d / cost


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
    #score = {start: heuristic(start, goal, start_cost, lowest_cost)}                                                    ## FULL SCORE OF EACH CELL OR COORD. FROM START TO GOAL
    myheap = []

    ## HEAP CONSIST OF SCORE, COORD
    #heapq.heappush(myheap, (score[start], start))
    heapq.heappush(myheap, (score_to_start[start], start))


    while myheap:
        curr_score, curr_cell = heapq.heappop(myheap)

        if curr_cell == goal:                                                                                           ## GOAL REACHED, GET PATH
            data_cells = []
            while curr_cell in came_from:
                data_cells.append(curr_cell)
                curr_cell = came_from[curr_cell]
            data_cells.append(start)                                                                                    ## APPEND STARTING LOCATION
            return data_cells                                                                                           ## START COORD WILL BE AT THE END, GOAL AT FIRST!

        visited_cells.add(curr_cell)

        for r, c in neighbors:
            neighbor_cell = (curr_cell[0] + r, curr_cell[1] + c)
            bad_neighbor = isBadNeighbor(matrix_path, neighbor_cell)

            if bad_neighbor:
                continue

            neighbor_cost = matrix_cost[neighbor_cell[0]][neighbor_cell[1]]
            curr_score_to_start = score_to_start[curr_cell] + heuristic(curr_cell, neighbor_cell, neighbor_cost, lowest_cost)


            if neighbor_cell in visited_cells and curr_score_to_start >= score_to_start.get(neighbor_cell, 0):          ## 0 DEFAULT VALUE
                ## A BETTER SOLUTION EXIST TOWARDS THIS NEIGHBOR CELL
                continue

            ## IF A BETTER score_to_start IS FOUND FOR THAT NEIGHBOR COORD OR NEIGHBOR COORD NOT IN HEAP
            if curr_score_to_start < score_to_start.get(neighbor_cell, 0) or neighbor_cell not in (i[1] for i in myheap):
                came_from[neighbor_cell] = curr_cell                                                                    ## NEIGHBOR COORD CAME FROM CURRENT COORD
                score_to_start[neighbor_cell] = curr_score_to_start                                                     ## NEIGHBOR DISTANCE FROM START
                #score[neighbor_cell] = curr_score_to_start + heuristic(neighbor_cell, goal, 0, lowest_cost)            ## GSCORE PLUS DISTANCE TO GOAL
                #heapq.heappush(myheap, (score[neighbor_cell], neighbor_cell))                                          ## PUSH NEIGHBOR TO HEAP
                heapq.heappush(myheap, (score_to_start[neighbor_cell], neighbor_cell))  ## PUSH NEIGHBOR TO HEAP


    return []