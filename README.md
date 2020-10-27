Rational Linear Inequality Checker
===  
Authors: Lizhou Cai, Junrui Liu  

## Prerequisites
* python v >= 3.7.4
* lark

    pip3 install lark-parser


## Usage

Run

    python3 lp_solver.py

And the program will read in a line from standard input.
The program will print out either 
* `UNSAT` if the input formula is unsatisfiable, or
* a satisfying assignment of variables in the input formula.


---
## Benchmarking
Benchmark file format:
- Interleave a line of formula with a line that is `SAT` or `UNSAT`, e.g.
    ```
    AND(...)
    UNSAT
    
    AND(...)
    SAT
    ```
    and so on.

    
- To comment out a line, prefix it with `%`.
- Empty lines are ignored.

To run a benchmark, simply run

    python3 benchmark.py BENCHMARK_FILE

It will run the `lp_solver.run()` for each formula in `BENCHMARK_FILE`.