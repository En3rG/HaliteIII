import numpy as np
import logging


def print_matrix(text, matrix):
    """
    PRINTS ENTIRE MATRIX FOR TESTING PURPOSES

    :param text: TEXT TO PRINT
    :param matrix: MATRIX TO PRINT
    :return:
    """
    np.set_printoptions(threshold=np.inf, linewidth=np.inf)         ## SET NUMPY PRINT THRESHOLD TO INFINITY
    logging.debug("Print matrix {}: {}".format(text, matrix))
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