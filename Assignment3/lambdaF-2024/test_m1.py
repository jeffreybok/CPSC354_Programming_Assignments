#!/usr/bin/env python3
"""Simple test runner for M1, M2, and M3 tests"""

from interpreter import interpret

def run_tests():
    tests = [
        # M1 tests
        (r"\x.(\y.y)x", r"(\x.((\y.y) x))"),
        (r"(\x.a x) ((\x.x)b)", r"(a ((\x.x) b))"),
        (r"(\x.x) (1--2)", "3.0"),
        (r"(\x.x) (1---2)", "-1.0"),
        (r"(\x.x + 1) 5", "6.0"),
        (r"(\x.x * x) 3", "9.0"),
        (r"(\x.\y.x + y) 3 4", "7.0"),
        (r"1-2*3-4", "-9.0"),
        (r"(\x.x * x) 2 * 3", "12.0"),
        (r"(\x.x * x) (-2) * (-3)", "-12.0"),
        (r"((\x.x * x) (-2)) * (-3)", "-12.0"),
        (r"(\x.x) (---2)", "-2.0"),
        # M2 tests
        (r"if 0 then 2 else 1", "1.0"),
        (r"if 1 then 2 else 2", "2.0"),
        (r"if 0 then 2 else if 1 then 3 else 4", "3.0"),
        (r"if 0 then 2 else if 0 then 3 else 4", "4.0"),
        (r"if 0 == 0 then 5 else 6", "5.0"),
        (r"if 0 <= 1 then 6 else 7", "6.0"),
        (r"if 1 <= 0 then 6 else 7", "7.0"),
        (r"let x = 1 in if x == 1 then 8 else 9", "8.0"),
        (r"let x = 0 in if x == 1 then 8 else 9", "9.0"),
        (r"let f = \x.x in f 10", "10.0"),
        (r"let f = \x.x+1 in f 10", "11.0"),
        (r"let f = \x.x*6 in let g = \x.x+1 in f (g 1)", "12.0"),
        (r"let f = \x.x*6 in let g = \x.x+1 in g (f 2)", "13.0"),
        (r"let f = \x.x*6 in let f = \x.x+1 in f (f 2) + 10", "14.0"),
        (r"letrec f = \n. if n==0 then 1 else n*f(n-1) in f 4", "24.0"),
        (r"letrec f = \n. if n==0 then 0 else 1 + 2*(n-1) + f(n-1) in f 6", "36.0"),
        # M3 tests
        (r"1", "1.0"),
        (r"(if 1 == 1 then \x.x+1 else \x.x+2) 5 + 10", "16.0"),
        (r"if 1 == 1 then 1 else 2 + 1", "1.0"),
        (r"1 ;; 2", "1.0 ;; 2.0"),
        (r"1 ;; 2 ;; 3", "1.0 ;; 2.0 ;; 3.0"),
        (r"1+1 ;; (\x.x)a ;; (\x.x+x)2", "2.0 ;; a ;; 4.0"),
        (r"1:2 ;; 1:2:#", "(1.0 : 2.0) ;; (1.0 : (2.0 : #))"),
        (r"(1)", "1.0"),
        (r"#", "#"),
        (r"1:2:3:#", "(1.0 : (2.0 : (3.0 : #)))"),
        (r"(\x.x) #", "#"),
        (r"(\x.\y.x) 1:# a", "(1.0 : #)"),
        (r"(\x.\y.y) a 1:#", "(1.0 : #)"),
        (r"let f = \x.x+1 in (f 1) : (f 2) : (f 3) : #", "(2.0 : (3.0 : (4.0 : #)))"),
        (r"1:2 == 1:2", "1.0"),
        (r"1:2 == 1:3", "0.0"),
        (r"1:2:# == 1:2:#", "1.0"),
        (r"(1-2) : (2+2) : # == (-1):4:#", "1.0"),
        (r"hd a", "(hd a)"),
        (r"hd (1:2:#)", "1.0"),
        (r"hd 1:2:#", "1.0"),
        (r"tl a", "(tl a)"),
        (r"tl (1:2:#)", "(2.0 : #)"),
        (r"tl 1:2:#", "(2.0 : #)"),
        (r"letrec map = \f. \xs. if xs==# then # else (f (hd xs)) : (map f (tl xs)) in (map (\x.x+1) (1:2:3:#))", "(2.0 : (3.0 : (4.0 : #)))"),
    ]
    
    passed = 0
    failed = 0
    
    for input_expr, expected in tests:
        try:
            result = interpret(input_expr)
            if result == expected:
                print(f"✓ PASS: {input_expr} --> {result}")
                passed += 1
            else:
                print(f"✗ FAIL: {input_expr}")
                print(f"    Expected: {expected}")
                print(f"    Got:      {result}")
                failed += 1
        except Exception as e:
            print(f"✗ ERROR: {input_expr}")
            print(f"    Exception: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    import sys
    sys.exit(0 if run_tests() else 1)