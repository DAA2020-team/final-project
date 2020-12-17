from data_structures.currency import Currency
import decimal


def get_decimal_places(f):
    """
    Method used to get the number of the meaningful decimal places of the parameter.
    :param f: the float value
    :return: the number of the meaningful decimal places of the parameter
    """
    return -decimal.Decimal(str(f)).as_tuple().exponent


def denominations_combinations(cur: Currency, amount: float):
    """
    This function returns the number of different ways that value given as parameter can be achieved
    by using all the possible comibinations of the denominations of the given currency.
    :param cur: currency to use
    :param amount: the total amount to be achieved
    :return: the number of all the possible cominations of denominations that match the amount
    """
    amount = round(amount, 2)
    amount_decimal_places = get_decimal_places(amount)

    den_decimal_places = 0
    temp_den = []
    for den in cur.iter_denominations():
        if den <= amount:
            den_decimal_places = max(den_decimal_places, get_decimal_places(round(den, 2)))
            temp_den.append(round(den, 2))

    if amount_decimal_places > den_decimal_places:
        # if the smallest denomination has less decimal places than the amount, then a solution does not exist
        return 0

    # the amount and the denominations are multiplied by the minimum possible value
    # e.g. if amount = 2.20 and den = [0.10, 0.20, 0.50] then everything is multiplied by 10^1
    amount = int(round(amount, 2) * (10 ** den_decimal_places))
    temp_den = [int(e * (10 ** den_decimal_places)) for e in temp_den]

    # dynamic programmic solution
    sol = [[0] * (amount + 1) for _ in range(len(temp_den))]
    for i in range(len(temp_den)):
        for j in range(amount + 1):
            if j == 0:
                sol[i][j] = 1
                continue
            if i == 0:
                sol[i][j] = 1 if j % temp_den[i] == 0 else 0
                continue
            if j >= temp_den[i]:
                sol[i][j] = sol[i - 1][j] + sol[i][j - temp_den[i]]
            else:
                sol[i][j] = sol[i - 1][j]
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
    print(denominations_combinations(c, 0.10))


if __name__ == '__main__':
    main()
