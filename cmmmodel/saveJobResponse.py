# -*- coding: utf-8 -*-

import sys


def saveModelResponse(arg1, arg2):
    """ save model response  """
    print("save model response")


if __name__ == "__main__":
    """ load data with data given by args """
    sys.argv.pop(0)
    saveModelResponse(**sys.argv)
