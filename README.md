linear inequality checker
===  
Authors: Lizhou Cai, Junrui Liu  

## Prerequisites
* python v>=3.7.4
* lark

      pip install lark-parser


## Usage

Run

    python3 lp_solver.py

And the program will read in a line from standard input.\
The program will print out either 
* `UNSAT` if the input formula is unsatisfiable
* __value for all the variables in the formula__ if the input formula is unsatisfiable


---
## Benchmarking
To construct a benchmark:
1. put all the formulae in one file, one for each line.
2. add a `%` at the initial of a line to comment out that line.

To run a benchmark, simply run

    python3 benchmark.py BENCHMARK_FILE

It will run the `lp_solver` for each line of formula.