# CS111 autograder and test cases

Autograding scripts for Wellesley's [CS111](http://cs111.wellesley.edu) (Introductory CS) course. The program evaluates student Python code on a suite of test cases, and generates HTML outputs with error hints, as well as plaintext logs. It supports grading for a variety of functions, including those with print statements and some support for graphics.

Currently in active development. The codebase is adapted from the [Berkeley AI autograder](http://ai.berkeley.edu/).  

## How to use

1. Clone this repository
1. Edit `projectParams.py` to point to the directory with the student code (which may be the current directory), and the list of program file names.
1. Create a file like `casefile_creator.txt` which is a |-separated file of test cases and expected outputs. Run `testCaseReader.py` to parse the test cases from this file. 
1. Finally, run `autograder.py` with no arguments.
