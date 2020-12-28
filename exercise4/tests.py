import sys
sys.path.append('../../final-project')

from tqdm import trange
from statistics import mean
from time import perf_counter
from pickle import dump
import os

from exercise4.exchange_tour import two_opt, three_opt, simulated_annealing
from exercise4.main import create_currencies, create_graph_from_currencies, OVER_COST


N = 1000


def sort_dict(x):
    return dict(sorted(x.items(), key=lambda item: item[1]))


def call_and_time(func, *args):
    t0 = perf_counter()
    tour_cost, _ = func(*args)
    t1 = perf_counter()
    return tour_cost, t1 - t0


algorithms = ("2-OPT", "3-OPT", "SA")
funcs = {
    "2-OPT": two_opt,
    "3-OPT": three_opt,
    "SA": simulated_annealing
}
results = {algorithm: [] for algorithm in algorithms}
times = {algorithm: [] for algorithm in algorithms}
failures = {algorithm: 0 for algorithm in algorithms}
for _ in trange(N):
    currencies = create_currencies(100)
    graph = create_graph_from_currencies(currencies)[1]
    for algorithm in algorithms:
        if algorithm == "SA":
            cost, time = call_and_time(funcs[algorithm], graph)
        else:
            cost, time = call_and_time(funcs[algorithm], graph, list(range(len(graph))))
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

filename = f"results_N-{N}_nt-25_000.dat"
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'resources', filename), 'wb') as f:
    dump(results, f)

filename = f"times_N-{N}_nt-25_000.dat"
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'resources', filename), 'wb') as f:
    dump(times, f)

filename = f"failures_N-{N}_nt-25_000.dat"
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'resources', filename), 'wb') as f:
    dump(failures, f)
