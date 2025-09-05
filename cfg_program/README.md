# How to run

There are 3 provided scripts, which all use `bril2json`:

    - ./cfg
    - ./run
    - ./print

## CFG Script

Takes in a `.bril` file as a parameter and calls
the `./run` script, piping the digraph output from the `mcfg.py`
script and creating the graph using graphviz.

## Run Script

Takes in a `.bril` file as a parameter and outputs the
digraph.

## Print Script

Takes in a `.bril` file as a parameter and outputs a formatted
JSON string of the `bril` program

## Test Directory

Contains all of the `bril/tests/interp/core/` tests
