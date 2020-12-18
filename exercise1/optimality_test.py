from exercise1.main import build_tree, compute_cover, get_number_of_useful_items
import itertools
from statistics import mean
from random import randint, choice, shuffle
from time import perf_counter


def show_results():
    print(f'{i + 1 : _} / {N : _}, approximation: {mean(approximation)}, '
          f'mean_solution: {mean(optimal_cover_sizes) : .2f}, '
          f'time_comparison: {mean(performance_time_ratioes) : .8f}, '
          f'none_counter: {none_counter}')


def compute_optimal_cover(tree_, k_, c1_, c2_):
    # Step 1: Find nodes useful for the (k, c1, c2)-cover
    nodes = tree_.find_nodes_in_range(c1_, c2_)

    # Step 2: Count number of items in range [c1, c2]
    n_ = get_number_of_useful_items(nodes, c1, c2)

    # Step 3: Compare with k
    if not n_ >= k_:
        return None

    optimal_cover_size_ = len(nodes)
    for j in range(1, len(nodes)):
        for remaining_nodes in itertools.combinations(nodes, j):
            remaining_nodes = set(remaining_nodes)
            useful_items = get_number_of_useful_items(remaining_nodes, c1_, c2_)
            if useful_items >= k_:
                optimal_cover_size_ = min(optimal_cover_size_, len(remaining_nodes))
                return optimal_cover_size_
    return optimal_cover_size_


N = 10_000

approximation = []
none_counter = 0
optimal_cover_sizes = []
performance_time_ratioes = []
for i in range(N):
    n = randint(80, 166)
    tree = build_tree(n)

    k = randint(1, 50)
    keys = list(tree.keys())
    shuffle(keys)
    c = keys[0], keys[1]
    c1 = min(c)
    c2 = max(c)

    t0 = perf_counter()
    greedy_cover = compute_cover(tree, k, c1, c2)
    t1 = perf_counter()
    greedy_time = t1 - t0
    if greedy_cover is not None:
        greedy_cover_size = len(greedy_cover)

    t0 = perf_counter()
    optimal_solution = compute_optimal_cover(tree, k, c1, c2)
    t1 = perf_counter()
    optimal_time = t1 - t0
    if optimal_solution is not None:
        optimal_cover_sizes.append(optimal_solution)

    if greedy_cover is None or optimal_solution is None:
        assert greedy_cover is optimal_solution
        none_counter += 1
    else:
        approximation.append(optimal_solution / greedy_cover_size)
        performance_time_ratioes.append(greedy_time / optimal_time)
        if optimal_solution < greedy_cover_size:
            print("HEY")

    if (i + 1) % 10 == 0 and len(approximation) > 0:
        show_results()

print(mean(approximation))
