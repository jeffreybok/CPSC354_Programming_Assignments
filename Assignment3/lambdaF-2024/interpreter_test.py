from interpreter import interpret, substitute, evaluate, LambdaCalculusTransformer, parser, linearize
from lark import Lark, Transformer
from colorama import Fore, Style

# for testing the grammar, the parser and the conversion to ASTs
def print_trees(source_code):
    print("Source code:", source_code); print()
    cst = parser.parse(source_code)
    #print("CST:", cst); print()
    ast = LambdaCalculusTransformer().transform(cst)
    print("AST:", ast); print()
    print("===\n")

# convert concrete syntax to AST
def ast(source_code):
    return LambdaCalculusTransformer().transform(parser.parse(source_code))

def print_ast(source_code):
    print()
    print("AST:", ast(source_code))
    print()

def test_parse():
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    
    assert ast(r"x") == ('var', 'x')
    print(f"AST {MAGENTA}x{RESET} == ('var', 'x')")
    
    assert ast(r"(((x)) ((y)))") == ('app', ('var', 'x'), ('var', 'y'))
    print(f"AST {MAGENTA}(((x)) ((y))){RESET} == ('app', ('var', 'x'), ('var', 'y'))")
    
    assert ast(r"x y") == ('app', ('var', 'x'), ('var', 'y'))
    print(f"AST {MAGENTA}x y{RESET} == ('app', ('var', 'x'), ('var', 'y'))")
    
    assert ast(r"x y z") == ('app', ('app', ('var', 'x'), ('var', 'y')), ('var', 'z'))
    print(f"AST {MAGENTA}x y z{RESET} == ('app', ('app', ('var', 'x'), ('var', 'y')), ('var', 'z'))")
    
    assert ast(r"\x.y") == ('lam', 'x', ('var', 'y'))
    print(f"AST {MAGENTA}\\x.y{RESET} == ('lam', 'x', ('var', 'y'))")
    
    assert ast(r"\x.x y") == ('lam', 'x', ('app', ('var', 'x'), ('var', 'y')))
    print(f"AST {MAGENTA}\\x.x y{RESET} == ('lam', 'x', ('app', ('var', 'x'), ('var', 'y')))")
    
    assert ast(r"\x.x y z") == ('lam', 'x', ('app', ('app', ('var', 'x'), ('var', 'y')), ('var', 'z')))
    print(f"AST {MAGENTA}\\x.x y z{RESET} == ('lam', 'x', ('app', ('app', ('var', 'x'), ('var', 'y')), ('var', 'z')))")
    
    assert ast(r"\x. \y. \z. x y z") == ('lam', 'x', ('lam', 'y', ('lam', 'z', ('app', ('app', ('var', 'x'), ('var', 'y')), ('var', 'z')))))
    print(f"AST {MAGENTA}\\x. \\y. \\z. x y z{RESET} == ('lam', 'x', ('lam', 'y', ('lam', 'z', ('app', ('app', ('var', 'x'), ('var', 'y')), ('var', 'z')))))")
    
    assert ast(r"\x. x a") == ('lam', 'x', ('app', ('var', 'x'), ('var', 'a')))
    print(f"AST {MAGENTA}\\x. x a{RESET} == ('lam', 'x', ('app', ('var', 'x'), ('var', 'a')))")
    
    assert ast(r"\x. x (\y. y)") == ('lam', 'x', ('app', ('var', 'x'), ('lam', 'y', ('var', 'y'))))
    print(f"AST {MAGENTA}\\x. x (\\y. y){RESET} == ('lam', 'x', ('app', ('var', 'x'), ('lam', 'y', ('var', 'y'))))")
    
    assert ast(r"\x. x (\y. y (\z. z z2))") == ('lam', 'x', ('app', ('var', 'x'), ('lam', 'y', ('app', ('var', 'y'), ('lam', 'z', ('app', ('var', 'z'), ('var', 'z2')))))))
    print(f"AST {MAGENTA}\\x. x (\\y. y (\\z. z z2)){RESET} == ('lam', 'x', ('app', ('var', 'x'), ('lam', 'y', ('app', ('var', 'y'), ('lam', 'z', ('app', ('var', 'z'), ('var', 'z2')))))))")
    
    assert ast(r"\x. y z (\a. b (\c. d e f))") == ('lam', 'x', ('app', ('app', ('var', 'y'), ('var', 'z')), ('lam', 'a', ('app', ('var', 'b'), ('lam', 'c', ('app', ('app', ('var', 'd'), ('var', 'e')), ('var', 'f')))))))
    print(f"AST {MAGENTA}\\x. y z (\\a. b (\\c. d e f)){RESET} == ('lam', 'x', ('app', ('app', ('var', 'y'), ('var', 'z')), ('lam', 'a', ('app', ('var', 'b'), ('lam', 'c', ('app', ('app', ('var', 'd'), ('var', 'e')), ('var', 'f')))))))")
    
    print("\nParser: All tests passed!\n")

def test_substitute():
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    
    # x [y/x] = y
    assert substitute(('var', 'x'), 'x', ('var', 'y')) == ('var', 'y')
    print(f"SUBST {MAGENTA}x [y/x]{RESET} == ('var', 'y')")
    
    # \x.x [y/x] = (\x.x)
    assert substitute(('lam', 'x', ('var', 'x')), 'x', ('var', 'y')) == ('lam', 'x', ('var', 'x'))
    print(f"SUBST {MAGENTA}\\x.x [y/x]{RESET} == ('lam', 'x', ('var', 'x'))")
    
    # (x x) [y/x] = y y
    assert substitute(('app', ('var', 'x'), ('var', 'x')), 'x', ('var', 'y')) == ('app', ('var', 'y'), ('var', 'y'))
    print(f"SUBST {MAGENTA}(x x) [y/x]{RESET} == ('app', ('var', 'y'), ('var', 'y'))")
    
    # (\y. x ) [y/x] = (\Var1. y)
    assert substitute(('lam', 'y', ('var', 'x')), 'x', ('var', 'y')) == ('lam', 'Var1', ('var', 'y'))
    print(f"SUBST {MAGENTA}\\y. x [y/x]{RESET} == ('lam', 'Var1', ('var', 'y'))")

    print("\nsubstitute(): All tests passed!\n")

def test_evaluate():
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    
    # EVAL x == x
    assert linearize(evaluate(ast(r"x"))) == "x"
    print(f"EVAL {MAGENTA}x{RESET} == x")
    
    # EVAL x y == (x y)
    assert linearize(evaluate(ast(r"x y"))) == "(x y)"
    print(f"EVAL {MAGENTA}x y{RESET} == (x y)")
    
    # EVAL x y z == ((x y) z)
    assert linearize(evaluate(ast(r"x y z"))) == "((x y) z)"
    print(f"EVAL {MAGENTA}x y z{RESET} == ((x y) z)")
    
    # EVAL x (y z) == (x (y z))
    assert linearize(evaluate(ast(r"x (y z)"))) == "(x (y z))"
    print(f"EVAL {MAGENTA}x (y z){RESET} == (x (y z))")
    
    # EVAL \x.y == \x.y
    assert linearize(evaluate(ast(r"\x.y"))) == r"(\x.y)"
    print(f"EVAL {MAGENTA}\\x.y{RESET} == \\x.y")
    
    # EVAL (\x.x) y == y
    assert linearize(evaluate(ast(r"(\x.x) y"))) == "y"
    print(f"EVAL {MAGENTA}(\\x.x) y{RESET} == y")

    print("\nevaluate(): All tests passed!\n")

def test_interpret():
    print(f"Testing x --> {interpret('x')}")
    print(f"Testing x y --> {interpret('x y')}")
    input=r"\x.x"; output = interpret(input); print(f"Testing {input} --> {output}")
    input=r"(\x.x) y"; output = interpret(input); print(f"Testing {input} --> {output}")
    input=r"(\x.\y.x y) y"; output = interpret(input); print(f"Testing {input} --> {output}")

    print("\ninterpret(): All tests passed!\n")

# ============================================================================
# NEW TESTS FOR MILESTONE 1, 2, AND 3 (highlighted in BLUE)
# ============================================================================

def test_milestone1():
    """Tests for Milestone 1: Lambda calculus + arithmetic"""
    BLUE = '\033[94m'
    RESET = '\033[0m'
    
    tests = [
        # Lazy evaluation tests
        (r"\x.(\y.y)x", r"(\x.((\y.y) x))"),
        (r"(\x.a x) ((\x.x)b)", r"(a ((\x.x) b))"),
        # Arithmetic tests
        (r"(\x.x) (1--2)", "3.0"),
        (r"(\x.x) (1---2)", "-1.0"),
        (r"(\x.x + 1) 5", "6.0"),
        (r"(\x.x * x) 3", "9.0"),
        (r"(\x.\y.x + y) 3 4", "7.0"),
        # Order of operations
        (r"1-2*3-4", "-9.0"),
        (r"(\x.x * x) 2 * 3", "12.0"),
        (r"(\x.x * x) (-2) * (-3)", "-12.0"),
        (r"((\x.x * x) (-2)) * (-3)", "-12.0"),
        (r"(\x.x) (---2)", "-2.0"),
    ]
    
    passed = 0
    for input_expr, expected in tests:
        result = interpret(input_expr)
        status = "✓" if result == expected else "✗"
        color = BLUE if result == expected else Fore.RED
        print(f"{color}{status} {input_expr} --> {result}{RESET}")
        if result == expected:
            passed += 1
        else:
            print(f"    Expected: {expected}")
    
    print(f"\n{BLUE}Milestone 1: {passed}/{len(tests)} tests passed{RESET}\n")

def test_milestone2():
    """Tests for Milestone 2: Conditionals, let, letrec, fix"""
    BLUE = '\033[94m'
    RESET = '\033[0m'
    
    tests = [
        # Conditionals
        (r"if 0 then 2 else 1", "1.0"),
        (r"if 1 then 2 else 2", "2.0"),
        (r"if 0 then 2 else if 1 then 3 else 4", "3.0"),
        (r"if 0 then 2 else if 0 then 3 else 4", "4.0"),
        # Comparison operators
        (r"if 0 == 0 then 5 else 6", "5.0"),
        (r"if 0 <= 1 then 6 else 7", "6.0"),
        (r"if 1 <= 0 then 6 else 7", "7.0"),
        # Let bindings
        (r"let x = 1 in if x == 1 then 8 else 9", "8.0"),
        (r"let x = 0 in if x == 1 then 8 else 9", "9.0"),
        (r"let f = \x.x in f 10", "10.0"),
        (r"let f = \x.x+1 in f 10", "11.0"),
        # Nested let
        (r"let f = \x.x*6 in let g = \x.x+1 in f (g 1)", "12.0"),
        (r"let f = \x.x*6 in let g = \x.x+1 in g (f 2)", "13.0"),
        # Shadowing
        (r"let f = \x.x*6 in let f = \x.x+1 in f (f 2) + 10", "14.0"),
        # Letrec (recursion)
        (r"letrec f = \n. if n==0 then 1 else n*f(n-1) in f 4", "24.0"),
        (r"letrec f = \n. if n==0 then 0 else 1 + 2*(n-1) + f(n-1) in f 6", "36.0"),
    ]
    
    passed = 0
    for input_expr, expected in tests:
        result = interpret(input_expr)
        status = "✓" if result == expected else "✗"
        color = BLUE if result == expected else Fore.RED
        print(f"{color}{status} {input_expr} --> {result}{RESET}")
        if result == expected:
            passed += 1
        else:
            print(f"    Expected: {expected}")
    
    print(f"\n{BLUE}Milestone 2: {passed}/{len(tests)} tests passed{RESET}\n")

def test_milestone3():
    """Tests for Milestone 3: Sequencing and Lists"""
    BLUE = '\033[94m'
    RESET = '\033[0m'
    
    tests = [
        # Basic tests
        (r"1", "1.0"),
        (r"(if 1 == 1 then \x.x+1 else \x.x+2) 5 + 10", "16.0"),
        (r"if 1 == 1 then 1 else 2 + 1", "1.0"),
        # Sequencing
        (r"1 ;; 2", "1.0 ;; 2.0"),
        (r"1 ;; 2 ;; 3", "1.0 ;; 2.0 ;; 3.0"),
        (r"1+1 ;; (\x.x)a ;; (\x.x+x)2", "2.0 ;; a ;; 4.0"),
        (r"1:2 ;; 1:2:#", "(1.0 : 2.0) ;; (1.0 : (2.0 : #))"),
        # Lists - basic
        (r"(1)", "1.0"),
        (r"#", "#"),
        (r"1:2:3:#", "(1.0 : (2.0 : (3.0 : #)))"),
        (r"(\x.x) #", "#"),
        # Lists - with application
        (r"(\x.\y.x) 1:# a", "(1.0 : #)"),
        (r"(\x.\y.y) a 1:#", "(1.0 : #)"),
        (r"let f = \x.x+1 in (f 1) : (f 2) : (f 3) : #", "(2.0 : (3.0 : (4.0 : #)))"),
        # List equality
        (r"1:2 == 1:2", "1.0"),
        (r"1:2 == 1:3", "0.0"),
        (r"1:2:# == 1:2:#", "1.0"),
        (r"(1-2) : (2+2) : # == (-1):4:#", "1.0"),
        # Head
        (r"hd a", "(hd a)"),
        (r"hd (1:2:#)", "1.0"),
        (r"hd 1:2:#", "1.0"),
        # Tail
        (r"tl a", "(tl a)"),
        (r"tl (1:2:#)", "(2.0 : #)"),
        (r"tl 1:2:#", "(2.0 : #)"),
        # Map function
        (r"letrec map = \f. \xs. if xs==# then # else (f (hd xs)) : (map f (tl xs)) in (map (\x.x+1) (1:2:3:#))", "(2.0 : (3.0 : (4.0 : #)))"),
    ]
    
    passed = 0
    for input_expr, expected in tests:
        result = interpret(input_expr)
        status = "✓" if result == expected else "✗"
        color = BLUE if result == expected else Fore.RED
        print(f"{color}{status} {input_expr} --> {result}{RESET}")
        if result == expected:
            passed += 1
        else:
            print(f"    Expected: {expected}")
    
    print(f"\n{BLUE}Milestone 3: {passed}/{len(tests)} tests passed{RESET}\n")

if __name__ == "__main__":
    print(Fore.GREEN + "\nTEST PARSING\n" + Style.RESET_ALL); test_parse()
    print(Fore.GREEN + "\nTEST SUBSTITUTION\n" + Style.RESET_ALL); test_substitute()
    print(Fore.GREEN + "\nTEST EVALUATION\n" + Style.RESET_ALL); test_evaluate()
    print(Fore.GREEN + "\nTEST INTERPRETATION\n" + Style.RESET_ALL); test_interpret()
    
    # New tests for Milestones 1, 2, 3 (highlighted in BLUE)
    print(Fore.BLUE + "\n" + "="*60 + Style.RESET_ALL)
    print(Fore.BLUE + "NEW TESTS FOR MILESTONES 1, 2, 3" + Style.RESET_ALL)
    print(Fore.BLUE + "="*60 + "\n" + Style.RESET_ALL)
    
    print(Fore.BLUE + "\nTEST MILESTONE 1 (Arithmetic)\n" + Style.RESET_ALL); test_milestone1()
    print(Fore.BLUE + "\nTEST MILESTONE 2 (Conditionals, Let, Letrec)\n" + Style.RESET_ALL); test_milestone2()
    print(Fore.BLUE + "\nTEST MILESTONE 3 (Sequencing, Lists)\n" + Style.RESET_ALL); test_milestone3()