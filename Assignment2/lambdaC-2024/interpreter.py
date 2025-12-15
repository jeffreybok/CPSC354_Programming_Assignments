Normalizing Lambda Calculus Interpreter
Student Name: Jeffrey Bok
Student ID: 2428659
Student Email: bok@chapman.edu
Course Section: CPSC-354
Assignment: Programming Assignment 2: Normalizing Interpreter

## How to compile and run code:
    python3 interpreter.py "(\x.x) a"
    python3 interpreter.py "expression"
    python3 interpreter.py filename.lc

## Sample Output:
    python3 interpreter.py "(\x.x) a"
    a

    python3 interpreter.py "(\x.y) ((\x.x x) (\x.x x))"
    y

    python3 interpreter.py "(\f.\x.f(f(x))) (\f.\x.(f(f(f x))))"
    (\Var1.(\Var2.(Var1 (Var1 (Var1 (Var1 (Var1 (Var1 (Var1 (Var1 (Var1 Var2)))))))))))