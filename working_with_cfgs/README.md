# Working with CFGs

## How to run

There are 3 provided scripts, which all use `bril2json`:

    - ./cfg
    - ./run_mycfg
    - ./print

## CFG Script

Takes in a `.bril` file as a parameter and calls
the `./run_mycfg` script, piping the digraph output from the `mcfg.py`
script and creating the graph using graphviz and generated within the
`./pdf` directory. A `-i` flag can be passed to output as a png instead
of a pdf.

## Run Script

Takes in a `.bril` file as a parameter and outputs the
digraph to stdout.

Takes in `-h`, `--help` or `-d`, `--debug` or `-r`, `--reduceable` flags for help
using the scripts, verbose output for debugging, or determining of a given bril file
is reduceable, respectively.

## Print Script

Takes in a `.bril` file as a parameter and outputs a formatted
JSON string of the `bril` program to stdout

## Test Directory

Contains all of the `bril/tests/interp/core/` tests
