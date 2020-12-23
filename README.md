# Final-project

Final project for Design and Analysis of Algorithms 2020/2021 - Group 12

GitHub Repository: https://github.com/DAA2020-team/final-project

Midterm project GitHub Repository: https://github.com/DAA2020-team/midterm-project

## Team Members
* [Giovanni Ammendola](https://github.com/giorge1)
* [Riccardo Imparato](https://github.com/r4004)
* [Stefano La Corte](https://github.com/phesmatos)
* [Vincenzo Petrone](https://github.com/v8p1197)

## Usage
### Requirements
#### Python
The lower python version which these files have been tested is 3.6.9. Compatibility should not be a problem, assuming that a not too old version is used.

#### Dependencies
In order to run these files, it is necessary to install some dependencies, listed in the [requirements](https://github.com/DAA2020-team/final-project/blob/exercise4/requirements.txt) file. They can be easily installed running the command

```shell
pip install -r requirements.txt
```

The main dependecies are:

* [iso4217](https://pypi.org/project/iso4217/) ([github repository](https://github.com/dahlia/iso4217)) module for python
    * This module is used in order to get real ISO4217 codes and to check that the codes added are valid
* [networkx](https://networkx.org/) ([github repository](https://github.com/networkx/networkx)) module
    * This module is used to draw a graph with vertices, edges and weight labels
    * Obviously, it is ***not*** applied to use typical graph-theory algorithms
* [matplotlib](https://matplotlib.org/) ([github repository](https://github.com/matplotlib/matplotlib)) module
    * This module is used to show the graph in an interactive figure

### Exercise 1

1. Change directory to the root folder.
2. Run `python exercise1/main.py`
    * This will test the greedy algorithm on a randomly generated (2,8)-Tree, searching for a (1,'AAA','ZZZ')-cover. 
3. You can test the algorithm with different `k`, `c1` and `c2` parameters with the command `python exercise1/main.py -k K -c1 C1 -c2 C2`
    * For example, `python exercise1/main.py -k 3 -c1 EUR -c2 GBP` will find a (3,'EUR','GBP')-cover.
    * Run `python exercise1/main.py --help` to show usage suggestions
    
The implementation of the `compute_cover()` function is in the file [exercise1/main.py](https://github.com/DAA2020-team/final-project/blob/master/exercise1/main.py).

### Exercise 2

1. Change directory to the root folder.
2. Run `python exercise2/main.py`
   * This will test the function using the EUR denomination with an amount of 1.0
3. You can test the algorithm with different `r` and `d` parameters with the command `python exercise2/main.py -r R -d D [D ...]`, where:
    * `R` is the amount to change
    * `D` is the sequence of values to use as denominations  
    * For example, `python exercise2/main.py -r 0.6 -d 0.1 0.2 0.5` will print all the five different possible ways that can be used for changing 0.6 with denominations [0.1, 0.2, 0.5]
        * i.e.: 0.5+0.1, 3\*0.2, 2\*0.2+2\*0.1, 0.2+4\*0.1, 6\*0.1
        * A value smaller than 5.0 is advisable for `R`
    * Run `python exercise2/main.py --help` to show usage suggestions

The implementation of the `denominations_combinations()` function is in the file [exercise2/main.py](https://github.com/DAA2020-team/final-project/blob/master/exercise2/main.py).

### Exercise 3

1. Change directory to the root folder.
2. Run `python exercise3/main.py`
    * This will test the function creating a strongly connected dense graph of 5 currencies, searching for an arbitrage opportunity for a random currency
3. You can test the algorithm with different `n` and `s` parameters with the command `python exercise2/main.py -n N -s S -v [V]`, where:
    * `N` is the number of currencies to insert in the graph
    * `S` is the code of the currency to search an arbitrage opportunity for
    * `-v` will draw the graph if set to `True`
        * If not specified, this flag is `False` and no graph will be shown
    * For example, `python exercise3/main.py -n 8 -s EUR -v` will search an arbitrage opportunity for EUR in a graph of 8 currencies, visualizing the graph 
        * A value smaller or equal to 5 is advisable for `N` if you want to see the graph
    * Run `python exercise3/main.py --help` to show usage suggestions

The implementation of the `find_arbitrage_opportunity()` function is in the file [exercise3/main.py](https://github.com/DAA2020-team/final-project/blob/master/exercise3/main.py).

### Exercise 4

1. Change directory to the root folder.
2. Run `python exercise4/main.py`
   
## Other resources

In the `resources` folder there is the [primes.bin](https://github.com/DAA2020-team/final-project/blob/master/resources/primes.bin) file, which contains prime numbers used by the [DoubleHashingHashMap](https://github.com/DAA2020-team/final-project/blob/master/data_structures/double_hashing_hash_map.py).

In the [utils.py](https://github.com/DAA2020-team/final-project/blob/master/utils.py) module there are some support functions used by different modules.
