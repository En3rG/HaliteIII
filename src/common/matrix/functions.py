import numpy as np
from hlt.positionals import Position
from src.common.values import MyConstants, Matrix_val, Inequality
import logging


def shift_matrix(y_shift, x_shift, matrix):
    """
    SHIFT (ROLL) MATRIX GIVEN X & Y

    :param x_shift:
    :param y_shift:
    :param matrix:
    :return:
    """
    return np.roll(np.roll(matrix, shift=x_shift, axis=1), shift=y_shift, axis=0)


def get_distance_matrix(start_tuple, height, width):
    """
    GENERATES A TABLE WITH ACTUAL DISTANCES FROM START PROVIDED

    WARNING!!! THIS TIMES OUT WHEN USED ON A 64x64 MAP (WHEN USED PER CELL DISTANCE CALCULATION)

    OBSOLETE, NO LONGER USED

    :param start_tuple: START IN TUPLE
    :param height: HEIGHT OF THE MAP
    :param width: WIDTH OF THE MAP
    :return: DISTANCE MATRIX
    """
    ## USING NUMPY (VECTORIZED), MUCH FASTER

    ## CANT USE THIS, CALCULATES DISTANCE FROM POINT TO POINT (ALLOWS DIAGONAL MOVEMENT)
    # matrix = np.zeros((height, width), dtype=np.float16)
    # indexes = [(y, x) for y, row in enumerate(matrix) for x, val in enumerate(row)]
    # to_points = np.array(indexes)
    # start_point = np.array([curr_section[0], curr_section[1]])
    # distances = np.linalg.norm(to_points - start_point, ord=2, axis=1.)
    #
    # return distances.reshape((height, width))

    start = Position(start_tuple[1], start_tuple[0])  ## REMEMBER Position(x, y)
    distance_matrix = np.zeros((height, width), dtype=np.int16)

    for y in range(height):
        for x in range(width):
            destination = Position(x, y)
            distance_matrix[y][x] = calculate_distance(start, destination, height, width)

    return distance_matrix


def calculate_distance(start, destination, height, width):
    """
    UPDATED FROM hlt.game_map.calculate distance

    Compute the Manhattan distance between two locations.
    Accounts for wrap-around.
    :param source: The source from where to calculate
    :param target: The target to where calculate
    :return: The distance between these items
    """
    resulting_position = abs(start - destination)
    return min(resulting_position.x, width - resulting_position.x) + \
           min(resulting_position.y, height - resulting_position.y)


def get_values_matrix(seek_value, matrix, condition):
    """
    GET SPECIFIC VALUES IN MATRIX PROVIDED, GIVEN INEQUALITY CONDITION

    :param seek_value:
    :param matrix:
    :param condition:
    :return: LIST OF VALUES
    """

    if condition == Inequality.EQUAL:
        r, c = np.where(matrix == seek_value)
    elif condition == Inequality.GREATERTHAN:
        r, c = np.where(matrix > seek_value)
    elif condition == Inequality.LESSTHAN:
        r, c = np.where(matrix < seek_value)
    else:
        raise NotImplemented

    ## EXTRACT CORRESPONDING VALUES
    return matrix[r, c]


def get_coord_closest(seek_val, value_matrix, distance_matrix):
    """
    GET CLOSESTS seek_val FROM MATRIX PROVIDED

    :param seek_val: VALUE WE ARE LOOKING FOR
    :param value_matrix: MATRIX WITH VALUES
    :param distance_matrix: MATRIX THAT REPRESENTS ITS DISTANCE
    :return: COORD, MIN DISTANCE, VALUE WITH MINIMUM DISTANCE
    """
    ## GET ROW, COL INDICES FOR THE CONDITION
    r, c = np.where(value_matrix == seek_val)

    ## EXTRACT CORRESPONDING VALUES OF DISTANCES
    distances = distance_matrix[r, c]

    if len(distances) >= 1:
        min_distance = distances.min()

        ## GET INDICES (INDEXABLE INTO r,c) CORRESPONDING TO LOWEST DISTANCE
        ld_indx = np.flatnonzero(distances == min_distance)

        ## GETTING CLOSEST seek_val, MAX NOT NECESSARY??
        ## GET MAX INDEX (BASED OFF v) OUT OF THE SELECTED INDICES
        max_idx = value_matrix[r[ld_indx], c[ld_indx]].argmax()

        ## INDEX INTO r,c WITH THE LOWEST DIST INDICES AND
        ## FROM THOSE SELECT MAXED ONE BASED OF VALUE
        return (r[ld_indx][max_idx], c[ld_indx][max_idx]), min_distance, value_matrix[r[ld_indx][max_idx], c[ld_indx][max_idx]]

    else:
        ## NO seek_val FOUND
        return None, None, None


def populate_manhattan(matrix, val, position, dist, cummulative=False):
    """
    POPULATE AREA IN MATRIX PROVIDED (BASED ON DISTANCE FROM ORIGIN OR LOC)

    LOOPS THROUGH EACH OF THE LOCATION ONE BY ONE (BASED ON DISTANCE)
    NO EXTRA LOCATION IS PART OF THE LOOP

    :param matrix: MATRIX TO BE POPULATED
    :param val: VALUE TO ADD IN MATRIX
    :param position: SHIP LOCATION
    :return:
    """
    size, size = matrix.shape
    for y in range(-dist, dist + 1):
        for x in range(-dist + abs(y), dist - abs(y) + 1):
            y_ = (y + position.y) % size
            x_ = (x + position.x) % size

            if cummulative:
                matrix[y_, x_] += val
            else:
                matrix[y_, x_] = val


def move_populate_manhattan(matrix, old_loc, new_loc, dist):
    """
    MOVE POPULATE AREA IN MATRIX PROVIDED FROM OLD LOC TO NEW LOC

    LOOPS THROUGH EACH OF THE LOCATION ONE BY ONE (BASED ON DISTANCE)
    NO EXTRA LOCATION IS PART OF THE LOOP

    ONLY MOVES VALUE '1', UNLIKE populate_manhattan, CAN TAKE ANY VAL

    :param matrix: MATRIX TO BE POPULATED
    :param old_loc: OLD LOCATION TO BE DEPOPULATED
    :param new_loc: NEW LOCATION TO BE POPULATED
    :param dist:
    :param cummulative:
    :return:
    """
    ## REMOVE FROM OLD LOCATION
    size, size = matrix.shape
    for y in range(-dist, dist + 1):
        for x in range(-dist + abs(y), dist - abs(y) + 1):
            y_ = (y + old_loc.y) % size
            x_ = (x + old_loc.x) % size

            matrix[y_, x_] -= 1 ## REMOVE VALUE

    ## ADD TO NEW LOCATION
    size, size = matrix.shape
    for y in range(-dist, dist + 1):
        for x in range(-dist + abs(y), dist - abs(y) + 1):
            y_ = (y + new_loc.y) % size
            x_ = (x + new_loc.x) % size

            matrix[y_, x_] += 1 ## ADD VALUE


def get_average_manhattan(matrix, loc, dist):
    """
    GET AVERAGE OF AREA IN THE MATRIX WITH CENTER LOCATION AND DISTANCE GIVEN

    :param matrix:
    :param loc: CENTER
    :param dist: DISTANCE AWAY FROM THE CENTER
    :return: AVERAGE
    """
    sum = 0
    num = 0
    size, size = matrix.shape
    for y in range(-dist, dist + 1):
        for x in range(-dist + abs(y), dist - abs(y) + 1):
            y_ = (y + loc.y) % size
            x_ = (x + loc.x) % size

            sum += matrix[y_, x_]
            num += 1

    return int(sum/num) ## FORCING TO INT FOR READABILITY (CHANGE LATER)


def get_position_highest_section(data):
    """
    GET POSITION OF HIGHEST SECTION

    OBSOLETE, NO LONGER USED

    :param data:
    :return: POSITION
    """
    section_coord = get_index_highest_val(data.matrix.sectioned.halite)
    destination = convert_section_coord(section_coord)

    return destination


def get_index_highest_val(matrix):
    """
    GET INDEX OF HIGHEST VALUE IN MATRIX

    :param matrix:
    :return: TUPLE (INDEX OF HIGHEST VALUE)
    """
    return np.unravel_index(np.argmax(matrix, axis=None), matrix.shape)


def convert_section_coord(section_coord):
    """
    CONVERT SECTION COORD TO POSITION IN GAME MAP

    :param section_coord: TUPLE
    :return: POSITION ON GAME MAP
    """
    section_y, section_x = section_coord[0], section_coord[1]
    x = section_x * MyConstants.SECTION_SIZE + MyConstants.SECTION_SIZE
    y = section_y * MyConstants.SECTION_SIZE + MyConstants.SECTION_SIZE

    return Position(x, y)


def get_n_largest_values(matrix, n):
    """
    :param n:
    :param matrix:
    :return: n LARGEST VALUES FROM MATRIX, AND ITS INDICES (AS NUMPY ARRAY)
    """
    ind = largest_indices(matrix, n)
    return matrix[ind], ind


def largest_indices(matrix, n):
    """Returns the n largest indices from a numpy array."""
    flat = matrix.flatten()
    indices = np.argpartition(flat, -n)[-n:]
    indices = indices[np.argsort(-flat[indices])]  ## SORT FROM HIGHEST TO LOWEST
    return np.unravel_index(indices, matrix.shape)


def get_n_smallest_values(matrix, n):
    """
    :param n:
    :param matrix:
    :return: n SMALLEST VALUES FROM MATRIX, AND ITS INDICES (AS NUMPY ARRAY)
    """
    ind = smallest_indices(matrix, n)
    return matrix[ind], ind


def smallest_indices(matrix, n):
    """Returns the n smallest indices from a numpy array."""
    flat = matrix.flatten()
    indices = np.argpartition(flat, n)[:n]
    return np.unravel_index(indices, matrix.shape)


def get_n_closest_masked(value_matrix, distance_matrix, mask_val, n):
    """
    RETURN INDICES OF CLOSEST DISTANCE AND ITS VALUES
    BASED ON MASKED VALUE MATRIX

    :param value_matrix:
    :param distance_matrix:
    :param mask_val:
    :param n:
    :return:
    """
    logging.debug("size value matrix: {}".format(value_matrix.shape))
    logging.debug("size distance matrix: {} ".format(distance_matrix.shape))
    mask = value_matrix == mask_val
    sorted_args = np.argpartition(distance_matrix[mask], n)[:n]
    sorted_dist = np.partition(distance_matrix[mask], n)[:n]
    indices = np.argwhere(mask)[sorted_args]
    return indices, sorted_dist


def get_sorted_distance_indices(val_matrix, dist_matrix):
    """
    RETURN SORTED ARGS OF THE DISTANCE MATRIX, BASED ON THE MASK
    MIGHT BE SLOW IF THE DATA SET IS LARGE (SORTING ENTIRE THING)
    FASTER TO DO ARGPARTITION IF ONLY NEED CLOSEST N
    """
    mask = val_matrix == 10
    return np.argwhere(mask)[dist_matrix[mask].argsort()]


def get_cell_averages(map_height, map_width, matrix):
    """
    GET CELL AVERAGES OF MATRIX PROVIDED

    :param matrix: MATRIX WHERE AVERAGES WILL BE BASED ON
    :return: MATRIX WITH CELL AVERAGES
    """
    ave_matrix = np.zeros((map_height, map_width), dtype=np.int16)

    for r in range(map_height):
        for c in range(map_width):
            loc = Position(c, r)  ## Position(x, y)
            ave_matrix[r][c] = get_average_manhattan(matrix, loc, MyConstants.AVERAGE_MANHATTAN_DISTANCE)

    return ave_matrix

