import numpy as np
from hlt.positionals import Position
from src.common.values import MyConstants, Matrix_val, Inequality
from src.common.print import print_matrix
from src.common.matrix.classes import Option
import logging

class Section():
    """
    GET A SECTION OF THE MATRIX PROVIDED
    GIVEN THE CENTER (POSITION) AND SIZE OF SECTION
    SECTION IS A SQUARE MATRIX
    ACTUAL SIZE OF SECTION IS ACTUALLY (SIZE * 2 + 1) by (SIZE * 2 + 1)

    :param matrix: ORIGINAL MATRIX
    :param position: CENTER OF THE SECTION
    :param size: SIZE OF THE SECTION TO BE EXTRACTED (FROM POSITION)
    :return: A MATRIX REPRESENTING THE SECTION EXTRACTED
    """
    def __init__(self, matrix, position, size):
        self.a = matrix
        self.position = position
        self.size = size

        self.matrix = self.get_section()
        self.center = Position(size, size)

    def get_section(self):

        h, w = self.a.shape
        rows = [i % h for i in range(self.position.y - self.size, self.position.y + self.size + 1)]
        cols = [i % w for i in range(self.position.x - self.size, self.position.x + self.size + 1)]

        return self.a[rows, :][:, cols]


def pad_around(matrix):
    """
    np.pad(matrix, [(1, 1), (1, 1)], mode='constant')
    WHERE 0 IS DEFAULT VALUE FOR CONSTANT

    WHERE SECOND ARGUMENT:
    [(0, 1), (0, 1)]
              ^^^^^^------ padding for second dimension
     ^^^^^^-------------- padding for first dimension

      ^------------------ no padding at the beginning of the first axis
          ^--------------- pad with one "value" at the end of the first axis.

    :param matrix:
    :return: MATRIX PADDED 0s AROUND
    """
    return np.pad(matrix, [(1, 1), (1, 1)], mode='constant')


def shift_matrix(y_shift, x_shift, matrix):
    """
    SHIFT (ROLL) MATRIX GIVEN X & Y

    :param x_shift: AMOUNT TO SHIFT IN X DIRECTION
    :param y_shift: AMOUNT TO SHIFT IN Y DIRECTION
    :param matrix: MATRIX TO BE SHIFTED
    :return: UPDATED MATRIX
    """
    return np.roll(np.roll(matrix, shift=x_shift, axis=1), shift=y_shift, axis=0)


def get_distance_matrix(start_tuple, data):
    """
    GENERATES A TABLE WITH ACTUAL DISTANCES FROM START PROVIDED

    WARNING!!! THIS TIMES OUT WHEN USED ON A 64x64 MAP (WHEN USED PER CELL DISTANCE CALCULATION)

    NOW JUST USED ONCE AS THE BASE, THEN USE SHIFT MATRIX

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

    height = data.game.game_map.height
    width = data.game.game_map.width

    start = Position(start_tuple[1], start_tuple[0])                                                                    ## REMEMBER Position(x, y)
    distance_matrix = np.zeros((height, width), dtype=np.int16)

    for y in range(height):
        for x in range(width):
            destination = Position(x, y)
            distance_matrix[y][x] = calculate_distance(start, destination, data)

    return distance_matrix


def calculate_distance(start, destination, data):
    """
    UPDATED FROM hlt.game_map.calculate distance

    Compute the Manhattan distance between two locations.
    Accounts for wrap-around.
    :param source: The source from where to calculate
    :param target: The target to where calculate
    :return: The distance between these items
    """
    height = data.game.game_map.height
    width = data.game.game_map.width

    resulting_position = abs(start - destination)
    return min(resulting_position.x, width - resulting_position.x) + \
           min(resulting_position.y, height - resulting_position.y)


def get_indices(seek_value, matrix, condition):
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

    return r, c


def get_coord_closest(seek_val, value_matrix, distance_matrix, condition):
    """
    GET CLOSESTS seek_val FROM MATRIX PROVIDED

    :param seek_val: VALUE WE ARE LOOKING FOR
    :param value_matrix: MATRIX WITH VALUES
    :param distance_matrix: MATRIX THAT REPRESENTS ITS DISTANCE
    :return: COORD, MIN DISTANCE, VALUE WITH MINIMUM DISTANCE
    """
    ## GET ROW, COL INDICES FOR THE CONDITION
    r, c = get_indices(seek_val, value_matrix, condition)

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


def get_manhattan(matrix, position, dist):
    """
    RETURN A SET OF VALUES FOUND IN THE GIVEN AREA/MANHATTAN BASED ON POSITION AND DIST
    """
    found_values = set()

    size, size = matrix.shape
    for y in range(-dist, dist + 1):
        for x in range(-dist + abs(y), dist - abs(y) + 1):
            y_ = (y + position.y) % size
            x_ = (x + position.x) % size

            found_values.add(matrix[y_, x_])

    return found_values


def count_manhattan(matrix, val, position, dist):
    """
    COUNT HOW MANY 'val' IS IN THE MATRIX, WITH THE GIVEN dist AND position

    :param matrix:
    :param val:
    :param position:
    :param dist:
    :return: NUMBER OF val OCCURENCES IN THE MATRIX, CENTERED AT POSITION WITH DIST GIVEN
    """
    count = 0

    size, size = matrix.shape
    for y in range(-dist, dist + 1):
        for x in range(-dist + abs(y), dist - abs(y) + 1):
            y_ = (y + position.y) % size
            x_ = (x + position.x) % size

            if matrix[y_, x_] == val:
                count += 1

    return count


def populate_manhattan(matrix, val, position, dist, option):
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

            if option == Option.REPLACE:
                matrix[y_, x_] = val
            elif option == Option.CUMMULATIVE:
                matrix[y_, x_] += val
            elif option == Option.MINIMUM:
                matrix[y_, x_] = min(val, matrix[y_, x_])
            elif option == Option.MAXIMUM:
                matrix[y_, x_] = max(val, matrix[y_, x_])


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

            matrix[y_, x_] -= 1                                                                                         ## REMOVE VALUE

    ## ADD TO NEW LOCATION
    size, size = matrix.shape
    for y in range(-dist, dist + 1):
        for x in range(-dist + abs(y), dist - abs(y) + 1):
            y_ = (y + new_loc.y) % size
            x_ = (x + new_loc.x) % size

            matrix[y_, x_] += 1                                                                                         ## ADD VALUE


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


def get_index_highest_val(matrix):
    """
    GET INDEX OF HIGHEST VALUE IN MATRIX

    :param matrix:
    :return: TUPLE (INDEX OF HIGHEST VALUE)
    """
    return np.unravel_index(np.argmax(matrix, axis=None), matrix.shape)


def get_coord_max_closest(value_matrix, distance_matrix):
    """
    GET VALUE AND INDEX OF THE HIGHEST VALUE IN THE MATRIX
    IF THERE ARE MULTIPLE HIGHEST VALUE, RETURN THE ONE WITH LEAST DISTANCE VALUE
    """
    max_value = np.nanmax(value_matrix)                                                                                 ## MAX VALUE.
                                                                                                                        ## USING NANMAX SINCE SOMETIMES THE VALUE MATRIX
                                                                                                                        ## WILL CONTAIN A NAN (WHEN 0 DIVIDED BY SOMETHING)
    r, c = np.where(value_matrix == max_value)                                                                          ## INDEXES OF WHERE MAX VALUE ARE
    distances = distance_matrix[r, c]                                                                                   ## VALUE OF DISTANCES WHERE MAX VALUES ARE LOCATED
    min_distance = distances.min()                                                                                      ## MIN DISTANCE VALUE
    ld_indx = np.flatnonzero(distances == min_distance)                                                                 ## INDEX OF MIN DISTANCE
    max_idx = value_matrix[r[ld_indx], c[ld_indx]].argmax()                                                             ## INDEX OF WHERE MAX VALUE & LEAST DISTANCE IS

    return max_value, (r[ld_indx][max_idx], c[ld_indx][max_idx])


def get_n_max_values(matrix):
    """
    GET n MAX VALUES
    RETURN MULTIPLE ITEMS IF THERE ARE MULTIPLE MAX VALUES (DUPLICATES)

    :param matrix:
    :return: VALUE AND INDEX
    """
    max_value = matrix.max()
    indexes = np.argwhere(matrix == max_value)

    return max_value, indexes


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
    indices = indices[np.argsort(-flat[indices])]                                                                       ## SORT FROM HIGHEST TO LOWEST
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


## NO LONGER USED
# def fill_circle(array, center, radius, value, cummulative=False, override_edges=None):
#     """
#     MASK A CIRCLE ON THE ARRAY
#
#     CURRENTLY NOT USED (DELETE LATER!!!!!)
#
#     :param array: ORIGINAL ARRAY
#     :param center: CENTER OF THE CIRCLE
#     :param radius: RADIUS OF THE CIRCLE
#     :param value: VALUE TO BE PLACED IN THE CIRCLE
#     :param cummulative: IF VALUE WILL BE ADDED TO EXISTING VALUE IN THAT INDEX
#     :param override_edges: IF A VALUE IS GIVEN, IT WILL HELP MAKE THE CIRCLE ROUNDER
#     :return: UPDATED ARRAY
#     """
#
#     height = array.shape[0]
#     width = array.shape[1]
#
#     ## y IS JUST AN ARRAY OF 1xY (ROWS)
#     ## x IS JUST AN ARRAY OF 1xX (COLS)
#     y, x = np.ogrid[-center.y:height - center.y, -center.x:width - center.x]
#     ## MASKS IS A HEIGHTxWIDTH ARRAY WITH TRUE INSIDE THE CIRCLE SPECIFIED
#
#     if override_edges:
#         mask = x * x + y * y <= radius * radius + radius * override_edges
#     else:
#         ## WHEN WANT TO BE MORE CIRCLE (DUE TO ROUNDING)
#         mask = x * x + y * y <= radius * radius
#
#     if cummulative:  ## VALUE KEEPS GETTING ADDED
#         array[mask] += value
#     else:
#         array[mask] = value
#
#     return array


# def convert_section_coord(section_coord):
#     """
#     CONVERT SECTION COORD TO POSITION IN GAME MAP
#
#     :param section_coord: TUPLE
#     :return: POSITION ON GAME MAP
#     """
#     section_y, section_x = section_coord[0], section_coord[1]
#     x = section_x * MyConstants.SECTION_SIZE + MyConstants.SECTION_SIZE
#     y = section_y * MyConstants.SECTION_SIZE + MyConstants.SECTION_SIZE
#
#     return Position(x, y)


# def get_position_highest_section(data):
#     """
#     GET POSITION OF HIGHEST SECTION
#
#     OBSOLETE, NO LONGER USED
#
#     :param data:
#     :return: POSITION
#     """
#     section_coord = get_index_highest_val(data.myMatrix.sectioned.halite)
#     destination = convert_section_coord(section_coord)
#
#     return destination