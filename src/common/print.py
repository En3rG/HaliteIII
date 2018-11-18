import numpy as np
import logging


def print_matrix(name, matrix):
    """
    PRINTS ENTIRE MATRIX FOR TESTING PURPOSES

    :param name: TEXT TO PRINT
    :param matrix: MATRIX TO PRINT
    :return:
    """
    np.set_printoptions(threshold=np.inf, linewidth=np.inf)         ## SET NUMPY PRINT THRESHOLD TO INFINITY
    logging.debug("Print matrix {}: {}".format(name, matrix))
    np.set_printoptions(threshold=10)                               ## SET NUMPY PRINT THRESHOLD TO 10


def print_heading(text):
    """
    PRINT TEXT AS HEADING

    :param text:
    :return:
    """
    logging.debug("---------------------------------------")
    logging.debug("{}".format(text))
    logging.debug("---------------------------------------")