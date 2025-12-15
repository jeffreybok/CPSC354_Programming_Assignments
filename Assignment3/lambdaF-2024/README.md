# Functional Programming Language Interpreter
Student Name: Jeffrey Bok
Student ID: 2428659
Student Email: bok@chapman.edu
Course Section: CPSC-354-01
Assignment: Programming Assignment 3: Functional Programming Language

## How to compile and run code:
    python3 interpreter.py "expression"
    python3 interpreter.py filename.lc
    python3 interpreter_test.py

## Sample Output:

### Milestone 1 (Arithmetic):
    python3 interpreter.py "(\x.x * x) 3"
    9.0

    python3 interpreter.py "1-2*3-4"
    -9.0

### Milestone 2 (Conditionals, Let, Letrec):
    python3 interpreter.py "if 0 == 0 then 5 else 6"
    5.0

    python3 interpreter.py "let f = \x.x+1 in f 10"
    11.0

    python3 interpreter.py "letrec f = \n. if n==0 then 1 else n*f(n-1) in f 5"
    120.0

### Milestone 3 (Sequencing, Lists):
    python3 interpreter.py "1:2:3:#"
    (1.0 : (2.0 : (3.0 : #)))

    python3 interpreter.py "hd 1:2:3:#"
    1.0

    python3 interpreter.py "tl 1:2:3:#"
    (2.0 : (3.0 : #))

    python3 interpreter.py test.lc
    120.0 ;; 55.0 ;; (1.0 : (3.0 : (3.0 : (4.0 : (5.0 : #)))))