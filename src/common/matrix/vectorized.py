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
    return sum(args)/len(args)      ## THIS SEEMS 4x FASTER THAN USING np.average
    #return np.average(args)

myAverageMatrix = np.vectorize(averageMatrix)


def sumMatrix(*args):
    """
    GET THE SUM OF THE MATRIX PROVIDED
    """
    return sum(args)


mySumMatrix = np.vectorize(sumMatrix)

