import pickle
import os
from typing import Tuple, List

from iso4217 import Currency as cur

from definitions import ROOT_DIR


def bitify(s: str) -> str:
    """
    Returns the bit representation of string s
    :param s: string to turn into bits
    :return: bit representation of s
    """
    return ''.join(format(c, 'b') for c in bytearray(s, 'utf-8'))


def load_primes() -> List[int]:
    """
    Loads all the primes stored into the binary file
    :return: a list of primes
    """
    with open(os.path.join(ROOT_DIR, 'resources/primes.bin'), 'rb') as f:
        primes = pickle.load(f)
    return primes


def binary_search(array: List, element, start=0, end=None) -> Tuple[bool, int]:
    """
    Binary-searches element into array in indices between start and end
    :param array: array in which the search is performed
    :param element: the element to search
    :param start: the first index
    :param end: the last index
    :return:
        false: bool: True if elements in in array, False otherwise
        index: int: the index of the last visited element (array[index] is always < element if found is False
    """
    end = end if end is not None else len(array) - 1

    if start > end:
        return False, end

    mid = (start + end) // 2
    if element == array[mid]:
        return True, mid

    if element < array[mid]:
        return binary_search(array, element, start, mid - 1)
    else:
        return binary_search(array, element, mid + 1, end)


def validate_iso_code(code: str) -> bool:
    """
    Checks whether if code is a valid ISO-4217 standard code
    :param code: the code to check
    :return: True if code is a valid ISO-4217 standard code, False otherwise
    """
    return code in [currency.code for currency in cur]


def str2bool(v: str) -> bool:
    """
    Converts the v string into a boolean
    :param v: the string to convert
    :return: the boolean value corresponding to v
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
