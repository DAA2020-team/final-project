import sys
sys.path.append('../final-project')

from typing import Tuple
import argparse

from data_structures.currency import Currency
from utils import get_decimal_places


def init_parameter():
    """
    Create argument parser.
    usage: main.py [-h] [-r R]
    Finds all combinations to change an amount.
    optional arguments:
      -h, --help  show this help message and exit
      -r R        the amount to change (default: 1.0)
    :return: input arguments
    """
    parser = argparse.ArgumentParser(description='Finds all combinations to change an amount.')
    parser.add_argument("-r", type=float, default=1.0, help="the amount to change (default: 1.0)")
    return parser.parse_args()


def add_den_usage(denomination, solution, max_solutions):
    new_solution = []
    for i, d in enumerate(solution):
        usages_per_denomination = dict(d)
        usages_per_denomination[denomination] += + 1
        new_solution.append(usages_per_denomination)
        if i >= max_solutions:
            new_solution.pop(0)
    return new_solution


def denominations_combinations(cur: Currency, amount: float, max_solutions=1_000) -> Tuple[int, list]:
    """
    This function returns the number of different ways that value given as parameter can be achieved
    by using all the possible comibinations of the denominations of the given currency.
    :param cur: currency to use
    :param amount: the total amount to be achieved
    :param max_solutions: the maximum number of solutions that must be returned. After 1_000, memory usage increases
    :return: the number of all the possible cominations of denominations that match the amount
    """
    amount = round(amount, 2)
    amount_decimal_places = get_decimal_places(amount)

    den_decimal_places = 0
    denominations = []
    unused_denominations = []
    for den in cur.iter_denominations():
        if den <= amount:
            den_decimal_places = max(den_decimal_places, get_decimal_places(round(den, 2)))  # max is needed
            denominations.append(round(den, 2))
        else:
            unused_denominations.append(den)

    if amount_decimal_places > den_decimal_places:
        # if the smallest denomination has less decimal places than the amount, then a solution does not exist
        return 0, []

    # the amount and the denominations are multiplied by the minimum possible value
    # e.g. if amount = 2.20 and den = [0.10, 0.20, 0.50] then everything is multiplied by 10^1
    amount = int(round(amount, 2) * (10 ** den_decimal_places))
    int_denonimations = [int(denomination * (10 ** den_decimal_places)) for denomination in denominations]
    int2real = {k: v for k, v in zip(int_denonimations, denominations)}

    # dynamic programmic solution
    base_sol = {denomination: 0 for denomination in denominations}
    sol = [[(0, [])] * (amount + 1) for _ in range(len(int_denonimations))]
    for i in range(len(int_denonimations)):
        for j in range(amount + 1):
            if j == 0:
                sol[i][j] = (1, [base_sol])  # base solution, take zero denominations
                continue
            if i == 0:
                if j % int_denonimations[i] == 0:
                    d_sol = dict(base_sol)
                    d_sol[int2real[int_denonimations[i]]] = j // int_denonimations[i]
                    sol[i][j] = (1, [d_sol])
                else:
                    sol[i][j] = (0, [])
                continue
            if j >= int_denonimations[i]:
                n_sol = sol[i - 1][j][0] + sol[i][j - int_denonimations[i]][0]
                d_sol = []
                d_sol += sol[i - 1][j][1][:]
                d_sol += add_den_usage(int2real[int_denonimations[i]], sol[i][j - int_denonimations[i]][1],
                                       max_solutions=max_solutions)
                sol[i][j] = (n_sol, d_sol[-max_solutions:])
            else:
                sol[i][j] = (sol[i - 1][j][0], sol[i - 1][j][1][:])
            sol[i-1][j] = (sol[i-1][j][0], [])  # Memory usage optimization

    unused_sol = {e: 0 for e in unused_denominations}
    for s in sol[-1][-1][1]:
        s.update(unused_sol)
    return sol[-1][-1]


def get_currency(c="EUR", d=None):
    """
    Method to create easily a currency with standard denominations, if none is provided.
    :param c: the currency name
    :param d: the list of denominations to be used
    :return: the new currency
    """
    if d is None:
        d = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500]
    cur = Currency(c)
    for i in d:
        cur.add_denomination(i)
    return cur


def main(r: float):
    c = get_currency()
    n_sol, list_sol = denominations_combinations(c, r, max_solutions=10)
    print(f"amount: {r : .2f}, {n_sol} solutions, printing only {len(list_sol)}:")
    for sol in list_sol:
        print(sol)


if __name__ == '__main__':
    args = init_parameter()
    main(args.r)
