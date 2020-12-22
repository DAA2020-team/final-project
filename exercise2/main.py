import sys
sys.path.append('../final-project')

from typing import Tuple
from data_structures.currency import Currency
import decimal


def get_decimal_places(f):
    """
    Method used to get the number of the meaningful decimal places of the parameter.
    :param f: the float value
    :return: the number of the meaningful decimal places of the parameter
    """
    return -decimal.Decimal(str(f)).as_tuple().exponent


def add_den_usage(den, sol, max_solutions):
    new_sol = []
    for i, d in enumerate(sol):
        new_dict = dict(d)
        new_dict[den] = new_dict[den] + 1
        new_sol.append(new_dict)
        if i >= max_solutions:
            new_sol.pop(0)
    return new_sol


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
    temp_den = []
    unused_den = []
    for den in cur.iter_denominations():
        if den <= amount:
            den_decimal_places = max(den_decimal_places, get_decimal_places(round(den, 2)))  # max is needed
            temp_den.append(round(den, 2))
        else:
            unused_den.append(den)

    if amount_decimal_places > den_decimal_places:
        # if the smallest denomination has less decimal places than the amount, then a solution does not exist
        return 0, []

    # the amount and the denominations are multiplied by the minimum possible value
    # e.g. if amount = 2.20 and den = [0.10, 0.20, 0.50] then everything is multiplied by 10^1
    amount = int(round(amount, 2) * (10 ** den_decimal_places))
    scaled_den = [int(e * (10 ** den_decimal_places)) for e in temp_den]
    den_dict = {k: v for k, v in zip(scaled_den, temp_den)}

    # dynamic programmic solution
    base_sol = {e: 0 for e in temp_den}
    sol = [[(0, [])] * (amount + 1) for _ in range(len(scaled_den))]
    for i in range(len(scaled_den)):
        for j in range(amount + 1):
            if j == 0:
                sol[i][j] = (1, [base_sol])  # base solution, take zero denominations
                continue
            if i == 0:
                if j % scaled_den[i] == 0:
                    d_sol = dict(base_sol)
                    d_sol[den_dict[scaled_den[i]]] = j // scaled_den[i]
                    sol[i][j] = (1, [d_sol])
                else:
                    sol[i][j] = (0, [])
                continue
            if j >= scaled_den[i]:
                n_sol = sol[i - 1][j][0] + sol[i][j - scaled_den[i]][0]
                d_sol = []
                d_sol += sol[i - 1][j][1][:]
                d_sol += add_den_usage(den_dict[scaled_den[i]], sol[i][j - scaled_den[i]][1], max_solutions=max_solutions)
                sol[i][j] = (n_sol, d_sol[-max_solutions:])
            else:
                sol[i][j] = (sol[i - 1][j][0], sol[i - 1][j][1][:])
            sol[i-1][j] = (sol[i-1][j][0], [])  # Memory usage optimization :)

    unused_sol = {e: 0 for e in unused_den}
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


def main():
    c = get_currency()
    r = 1.42
    n_sol, list_sol = denominations_combinations(c, r, max_solutions=1000)
    print(f"amount: {r : .2f}, {n_sol} solutions, printing only {len(list_sol)}:")
    for sol in list_sol:
        print(sol)


if __name__ == '__main__':
    main()
