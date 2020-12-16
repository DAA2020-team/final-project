from data_structures.currency import Currency


def denominations_combinations(cur: Currency, r: float):
    amount = int(round(r, 2) * 100)
    temp_den = []
    for den in cur.iter_denominations():
        temp_den.append(int(round(den, 2) * 100))

    sol = [[0]*(amount+1) for _ in range(len(temp_den))]
    for i in range(len(temp_den)):
        for j in range(amount + 1):
            if j == 0:
                sol[i][j] = 1
                continue
            if i == 0:
                sol[i][j] = 1 if j % temp_den[i] == 0 else 0
                continue
            if j >= temp_den[i]:
                sol[i][j] = sol[i-1][j] + sol[i][j - temp_den[i]]
            else:
                sol[i][j] = sol[i-1][j]
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
    print(denominations_combinations(c, 10))


if __name__ == '__main__':
    main()
