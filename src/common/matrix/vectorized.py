import numpy as np
from src.common.values import MyConstants, Matrix_val, Inequality


def rounder(x):
    """
    SINCE np.round() DOESNT ALWAYS ROUND UP XX.5
    MAKING MY OWN FUNCTION THEN np.vectorize IT

    :param x: EACH NUMBER FROM THE ARRAY
    :return: CEIL OR FLOOR OF THAT NUMBER
    """
    if (x - int(x) >= 0.5):
        return np.ceil(x)
    else:
        return np.floor(x)

myRound = np.vectorize(rounder)


def bonusArea(harvest, influence):
    """
    POPULATE BONUS HARVEST

    :param harvest:
    :param influence:
    :return:
    """
    if influence >= MyConstants.influence.min_num:
        return harvest * 2
    else:
        return 0

myBonusArea = np.vectorize(bonusArea)


def minValueMatrix(*args):
    """
    GET THE SMALLEST VALUE IN THE GIVEN MATRICES

    USED POPULATE DISTANCES TO DOCKS/SHIPYARD GIVEN ALL DISTANCE MATRICES PER DOCKS/SHIPYARD
    """
    return min(args)

myMinValueMatrix = np.vectorize(minValueMatrix)


def maxValueMatrix(*args):
    """
    GET THE LARGEST VALUE IN THE GIVEN MATRICES
    """
    return max(args)

myMaxValueMatrix = np.vectorize(maxValueMatrix)


def sunkenShips(prev, now):
    """
    GET THE LOCATIONS OF SUNKEN SHIPS
    """
    if prev != now:
        return 1
    else:
        return 0

mySunkenShips = np.vectorize(sunkenShips)


def averageMatrix(*args):
    """
    GET THE AVERAGE OF THE MATRIX PROVIDED
    """
    #return sum(args)/len(args)
    return np.average(args)

myAverageMatrix = np.vectorize(averageMatrix)


## NO LONGER USED
# def harvestArea(max_x, x):
#     """
#     POPULATE GOOD AREA TO HARVEST
#
#     :param max_x:
#     :param x:
#     :return: 10 IF ITS A GOOD HARVEST AREA
#     """
#     if x > (MyConstants.HARVEST_AREA_PERCENT * max_x):
#         return 0
#     else:
#         return 10 ## GOOD HARVEST AREA (10 SO ITS JUST EASIER TO DISTINGUISH FROM 0)
#
# myHarvestArea = np.vectorize(harvestArea)


# def harvestCounter(x):
#     """
#     GIVEN A MATRIX OF HALITE AMOUNT, GET THE NUMBER OF TURNS IT'LL TAKE TO HARVEST
#     IT UP TO THE DONT HARVEST POINT
#
#     :param x: EACH NUMBER FROM THE ARRAY
#     :return: NUMBER OF TURNS TO DEPLETE HALITE TO BE EQUAL OR BELOW DONT HARVEST POINT
#     """
#     counter = 0
#
#     while x > (MyConstants.DONT_HARVEST_BELOW * 4):  ## MULTIPLIED BY 4 SINCE ITS THE HARVEST AMOUNT, TO GET HALITE AMOUNT
#         x = x * 0.75    ## AMOUNT LEFT AFTER A TURN
#         counter += 1
#
#     return counter
#
# myHarvestCounter = np.vectorize(harvestCounter)


# def turnCounter(harvestTurns, distance):
#     """
#     :param harvestTurns:
#     :param distance:
#     :return: TOTAL NUMBER OF TURNS TO DEPLETE HALITE TO BELOW DONT HARVEST POINT
#              PLUS TOTAL TIME TO GET TO/FROM SHIPYARD
#     """
#     return distance + harvestTurns + distance
#
# myTurnCounter = np.vectorize(turnCounter)