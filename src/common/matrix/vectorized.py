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


def harvestCounter(x):
    """
    GIVEN A MATRIX OF HALITE AMOUNT, GET THE NUMBER OF TURNS IT'LL TAKE TO HARVEST
    IT UP TO THE DONT HARVEST POINT

    :param x: EACH NUMBER FROM THE ARRAY
    :return: NUMBER OF TURNS TO DEPLETE HALITE TO BE EQUAL OR BELOW DONT HARVEST POINT
    """
    counter = 0

    while x > (MyConstants.DONT_HARVEST_BELOW * 4):  ## MULTIPLIED BY 4 SINCE ITS THE HARVEST AMOUNT, TO GET HALITE AMOUNT
        x = x * 0.75    ## AMOUNT LEFT AFTER A TURN
        counter += 1

    return counter

myHarvestCounter = np.vectorize(harvestCounter)


def turnCounter(harvestTurns, distance):
    """
    :param harvestTurns:
    :param distance:
    :return: TOTAL NUMBER OF TURNS TO DEPLETE HALITE TO BELOW DONT HARVEST POINT
             PLUS TOTAL TIME TO GET TO/FROM SHIPYARD
    """
    return distance + harvestTurns + distance

myTurnCounter = np.vectorize(turnCounter)


def harvestArea(max_x, x):
    """
    POPULATE GOOD AREA TO HARVEST

    :param max_x:
    :param x:
    :return: 10 IF ITS A GOOD HARVEST AREA
    """
    if x > (MyConstants.HARVEST_AREA_PERCENT * max_x):
        return 0
    else:
        return 10 ## GOOD HARVEST AREA (10 SO ITS JUST EASIER TO DISTINGUISH FROM 0)

myHarvestArea = np.vectorize(harvestArea)


def bonusArea(harvest, influence):
    """
    POPULATE BONUS HARVEST

    :param harvest:
    :param influence:
    :return:
    """
    if influence >= MyConstants.INFLUENCED:
        return harvest * 2
    else:
        return 0

myBonusArea = np.vectorize(bonusArea)
