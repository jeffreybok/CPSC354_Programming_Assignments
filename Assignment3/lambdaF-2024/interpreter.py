import sys
from lark import Lark, Transformer, Tree
import lark
import os

#print(f"Python version: {sys.version}")
#print(f"Lark version: {lark.__version__}")

#  run/execute/interpret source code
def interpret(source_code):
    cst = parser.parse(source_code)
    ast = LambdaCalculusTransformer().transform(cst)
    result_ast = evaluate(ast)
    result = linearize(result_ast)
    return result

# convert concrete syntax to CST
parser = Lark(open("grammar.lark").read(), parser='lalr')

# convert CST to AST
class LambdaCalculusTransformer(Transformer):
    def lam(self, args):
        name, body = args
        return ('lam', str(name), body)

    def app(self, args):
        return ('app', *args)

    def var(self, args):
        token, = args
        return ('var', str(token))

    def num(self, args):
        token, = args
        return ('num', float(token))

    def plus(self, args):
        left, right = args
        return ('plus', left, right)

    def minus(self, args):
        left, right = args
        return ('minus', left, right)

    def times(self, args):
        left, right = args
        return ('times', left, right)

    def neg(self, args):
        operand, = args
        return ('neg', operand)

    def if_exp(self, args):
        cond, then_branch, else_branch = args
        return ('if', cond, then_branch, else_branch)

    def leq(self, args):
        left, right = args
        return ('leq', left, right)

    def eq(self, args):
        left, right = args
        return ('eq', left, right)

    def let_exp(self, args):
        name, value, body = args
        return ('let', str(name), value, body)

    def letrec_exp(self, args):
        name, value, body = args
        return ('letrec', str(name), value, body)

    def fix_exp(self, args):
        expr, = args
        return ('fix', expr)

    def seq(self, args):
        left, right = args
        return ('seq', left, right)

    def cons(self, args):
        head, tail = args
        return ('cons', head, tail)

    def empty_list(self, args):
        return ('nil',)

    def hd(self, args):
        expr, = args
        return ('hd', expr)

    def tl(self, args):
        expr, = args
        return ('tl', expr)

    def NAME(self, token):
        return str(token)

# reduce AST to normal form
def evaluate(tree):
    if tree[0] == 'app':
        e1 = evaluate(tree[1])
        if e1[0] == 'lam':
            body = e1[2]
            name = e1[1]
            arg = tree[2]
            rhs = substitute(body, name, arg)
            result = evaluate(rhs)
        else:
            result = ('app', e1, tree[2])
    elif tree[0] == 'plus':
        left = evaluate(tree[1])
        right = evaluate(tree[2])
        if left[0] == 'num' and right[0] == 'num':
            result = ('num', left[1] + right[1])
        else:
            result = ('plus', left, right)
    elif tree[0] == 'minus':
        left = evaluate(tree[1])
        right = evaluate(tree[2])
        if left[0] == 'num' and right[0] == 'num':
            result = ('num', left[1] - right[1])
        else:
            result = ('minus', left, right)
    elif tree[0] == 'times':
        left = evaluate(tree[1])
        right = evaluate(tree[2])
        if left[0] == 'num' and right[0] == 'num':
            result = ('num', left[1] * right[1])
        else:
            result = ('times', left, right)
    elif tree[0] == 'neg':
        operand = evaluate(tree[1])
        if operand[0] == 'num':
            result = ('num', -operand[1])
        else:
            result = ('neg', operand)
    elif tree[0] == 'leq':
        left = evaluate(tree[1])
        right = evaluate(tree[2])
        if left[0] == 'num' and right[0] == 'num':
            result = ('num', 1.0 if left[1] <= right[1] else 0.0)
        else:
            result = ('leq', left, right)
    elif tree[0] == 'eq':
        left = evaluate(tree[1])
        right = evaluate(tree[2])
        result = ('num', 1.0 if ast_equal(left, right) else 0.0)
    elif tree[0] == 'if':
        cond = evaluate(tree[1])
        if cond[0] == 'num':
            if cond[1] != 0:  # true (non-zero)
                result = evaluate(tree[2])
            else:  # false (zero)
                result = evaluate(tree[3])
        else:
            result = ('if', cond, tree[2], tree[3])
    elif tree[0] == 'let':
        # let x = e1 in e2 --> (\x.e2) e1
        name = tree[1]
        value = tree[2]
        body = tree[3]
        result = evaluate(('app', ('lam', name, body), value))
    elif tree[0] == 'letrec':
        # letrec f = e1 in e2 --> let f = (fix (\f. e1)) in e2
        name = tree[1]
        value = tree[2]
        body = tree[3]
        fixed = ('fix', ('lam', name, value))
        result = evaluate(('let', name, fixed, body))
    elif tree[0] == 'fix':
        # fix F --> F (fix F)
        f = evaluate(tree[1])
        result = evaluate(('app', f, ('fix', f)))
    elif tree[0] == 'seq':
        # Evaluate both sides and keep as sequence
        left = evaluate(tree[1])
        right = evaluate(tree[2])
        result = ('seq', left, right)
    elif tree[0] == 'cons':
        # Evaluate both head and tail
        head = evaluate(tree[1])
        tail = evaluate(tree[2])
        result = ('cons', head, tail)
    elif tree[0] == 'nil':
        result = tree
    elif tree[0] == 'hd':
        # hd (a:b) --> a
        expr = evaluate(tree[1])
        if expr[0] == 'cons':
            result = expr[1]
        else:
            result = ('hd', expr)
    elif tree[0] == 'tl':
        # tl (a:b) --> b
        expr = evaluate(tree[1])
        if expr[0] == 'cons':
            result = expr[2]
        else:
            result = ('tl', expr)
    else:
        result = tree
    return result

# Helper function to compare ASTs for equality (used by ==)
def ast_equal(left, right):
    if left[0] != right[0]:
        return False
    if left[0] == 'num':
        return left[1] == right[1]
    elif left[0] == 'nil':
        return True
    elif left[0] == 'cons':
        return ast_equal(left[1], right[1]) and ast_equal(left[2], right[2])
    else:
        return left == right

# generate a fresh name 
# needed eg for \y.x [y/x] --> \z.y where z is a fresh name)
class NameGenerator:
    def __init__(self):
        self.counter = 0

    def generate(self):
        self.counter += 1
        # user defined names start with lower case (see the grammar), thus 'Var' is fresh
        return 'Var' + str(self.counter)

name_generator = NameGenerator()

# for beta reduction (capture-avoiding substitution)
# 'replacement' for 'name' in 'tree'
def substitute(tree, name, replacement):
    # tree [replacement/name] = tree with all instances of 'name' replaced by 'replacement'
    if tree[0] == 'var':
        if tree[1] == name:
            return replacement # n [r/n] --> r
        else:
            return tree # x [r/n] --> x
    elif tree[0] == 'lam':
        if tree[1] == name:
            return tree # \n.e [r/n] --> \n.e
        else:
            fresh_name = name_generator.generate()
            return ('lam', fresh_name, substitute(substitute(tree[2], tree[1], ('var', fresh_name)), name, replacement))
            # \x.e [r/n] --> (\fresh.(e[fresh/x])) [r/n]
    elif tree[0] == 'app':
        return ('app', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    elif tree[0] == 'num':
        return tree
    elif tree[0] == 'plus':
        return ('plus', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    elif tree[0] == 'minus':
        return ('minus', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    elif tree[0] == 'times':
        return ('times', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    elif tree[0] == 'neg':
        return ('neg', substitute(tree[1], name, replacement))
    elif tree[0] == 'leq':
        return ('leq', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    elif tree[0] == 'eq':
        return ('eq', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    elif tree[0] == 'if':
        return ('if', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement), substitute(tree[3], name, replacement))
    elif tree[0] == 'let':
        # let x = e1 in e2
        if tree[1] == name:
            # x is shadowed in e2, only substitute in e1
            return ('let', tree[1], substitute(tree[2], name, replacement), tree[3])
        else:
            fresh_name = name_generator.generate()
            new_body = substitute(substitute(tree[3], tree[1], ('var', fresh_name)), name, replacement)
            return ('let', fresh_name, substitute(tree[2], name, replacement), new_body)
    elif tree[0] == 'letrec':
        # letrec f = e1 in e2 (f is bound in both e1 and e2)
        if tree[1] == name:
            return tree  # name is shadowed
        else:
            fresh_name = name_generator.generate()
            new_value = substitute(substitute(tree[2], tree[1], ('var', fresh_name)), name, replacement)
            new_body = substitute(substitute(tree[3], tree[1], ('var', fresh_name)), name, replacement)
            return ('letrec', fresh_name, new_value, new_body)
    elif tree[0] == 'fix':
        return ('fix', substitute(tree[1], name, replacement))
    elif tree[0] == 'seq':
        return ('seq', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    elif tree[0] == 'cons':
        return ('cons', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    elif tree[0] == 'nil':
        return tree
    elif tree[0] == 'hd':
        return ('hd', substitute(tree[1], name, replacement))
    elif tree[0] == 'tl':
        return ('tl', substitute(tree[1], name, replacement))
    else:
        raise Exception('Unknown tree', tree)

def linearize(ast):
    if ast[0] == 'var':
        return ast[1]
    elif ast[0] == 'lam':
        return "(" + "\\" + ast[1] + "." + linearize(ast[2]) + ")"
    elif ast[0] == 'app':
        return "(" + linearize(ast[1]) + " " + linearize(ast[2]) + ")"
    elif ast[0] == 'num':
        # Format number: show as integer if whole number, otherwise as float
        val = ast[1]
        if val == int(val):
            return str(int(val)) + ".0"
        else:
            return str(val)
    elif ast[0] == 'plus':
        return "(" + linearize(ast[1]) + " + " + linearize(ast[2]) + ")"
    elif ast[0] == 'minus':
        return "(" + linearize(ast[1]) + " - " + linearize(ast[2]) + ")"
    elif ast[0] == 'times':
        return "(" + linearize(ast[1]) + " * " + linearize(ast[2]) + ")"
    elif ast[0] == 'neg':
        return "(-" + linearize(ast[1]) + ")"
    elif ast[0] == 'leq':
        return "(" + linearize(ast[1]) + " <= " + linearize(ast[2]) + ")"
    elif ast[0] == 'eq':
        return "(" + linearize(ast[1]) + " == " + linearize(ast[2]) + ")"
    elif ast[0] == 'if':
        return "(if " + linearize(ast[1]) + " then " + linearize(ast[2]) + " else " + linearize(ast[3]) + ")"
    elif ast[0] == 'let':
        return "(let " + ast[1] + " = " + linearize(ast[2]) + " in " + linearize(ast[3]) + ")"
    elif ast[0] == 'letrec':
        return "(letrec " + ast[1] + " = " + linearize(ast[2]) + " in " + linearize(ast[3]) + ")"
    elif ast[0] == 'fix':
        return "(fix " + linearize(ast[1]) + ")"
    elif ast[0] == 'seq':
        return linearize(ast[1]) + " ;; " + linearize(ast[2])
    elif ast[0] == 'cons':
        return "(" + linearize(ast[1]) + " : " + linearize(ast[2]) + ")"
    elif ast[0] == 'nil':
        return "#"
    elif ast[0] == 'hd':
        return "(hd " + linearize(ast[1]) + ")"
    elif ast[0] == 'tl':
        return "(tl " + linearize(ast[1]) + ")"
    else:
        return str(ast)

def main():
    import sys
    if len(sys.argv) != 2:
        #print("Usage: python interpreter.py <filename or expression>", file=sys.stderr)
        sys.exit(1)

    input_arg = sys.argv[1]

    if os.path.isfile(input_arg):
        # If the input is a valid file path, read from the file
        with open(input_arg, 'r') as file:
            expression = file.read()
    else:
        # Otherwise, treat the input as a direct expression
        expression = input_arg

    result = interpret(expression)
    print(f"\033[95m{result}\033[0m")

if __name__ == "__main__":
    main()