import sys
sys.path.append('../../final-project')

from tqdm import trange
from statistics import mean
from time import perf_counter
from pickle import dump
import os

from exercise4.tsp import twoOPT, threeOPT, TSP_SA
from exercise4.main import create_currencies, create_graph_from_currencies, OVER_COST


N = 1000


def sort_dict(x):
    return dict(sorted(x.items(), key=lambda item: item[1]))


def call_and_time(name, func, *args):
    t0 = perf_counter()
    _, tour_cost = func(*args)
    t1 = perf_counter()
    return tour_cost, t1 - t0


algorithms = ("2-OPT", "3-OPT", "SA")
funcs = {
    "2-OPT": twoOPT,
    "3-OPT": threeOPT,
    "SA": TSP_SA
}
results = {algorithm: [] for algorithm in algorithms}
times = {algorithm: [] for algorithm in algorithms}
failures = {algorithm: 0 for algorithm in algorithms}
for _ in trange(N):
    currencies = create_currencies(100)
    graph = create_graph_from_currencies(currencies)[1]
    for algorithm in algorithms:
        if algorithm == "SA":
            cost, time = call_and_time(algorithm, funcs[algorithm], graph)
        else:
            cost, time = call_and_time(algorithm, funcs[algorithm], graph, list(range(len(graph))))
        if cost > OVER_COST:
            failures[algorithm] += 1
        else:
            results[algorithm].append(cost)
            times[algorithm].append(time)

print("*** RESULTS ***")
for key, value in results.items():
    results[key] = mean(value)
results = sort_dict(results)
for algorithm, result in results.items():
    print(f"{algorithm}: {result}")

print("*** TIMES ***")
for key, value in times.items():
    times[key] = mean(value)
times = sort_dict(times)
for algorithm, time in times.items():
    print(f"{algorithm}: {time}")

print("*** FAILURES ***")
failures = sort_dict(failures)
for algorithm, failure in failures.items():
    print(f"{algorithm}: {failure}")

filename = f"results_{N}.dat"
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'resources', filename), 'wb') as f:
    dump(results, f)

filename = f"times_{N}.dat"
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'resources', filename), 'wb') as f:
    dump(times, f)

filename = f"failures_{N}.dat"
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'resources', filename), 'wb') as f:
    dump(failures, f)
