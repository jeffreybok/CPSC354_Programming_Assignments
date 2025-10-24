#!/usr/bin/env python3
"""
Calculator implementation using Lark parser and recursive AST evaluation.
"""

import sys
import math
from lark import Lark, Transformer, v_args

# Load the grammar from grammar.lark
with open('grammar.lark', 'r') as f:
    grammar = f.read()

# Create parser instance
parser = Lark(grammar, parser='lalr', transformer=None)


class CalculatorTransformer(Transformer):
    """
    Transformer that converts parse tree nodes into calculator operations.
    Each method corresponds to a rule in the grammar and returns the computed result.
    """

    @v_args(inline=True)
    def number(self, token):
        """
        Convert NUMBER token to float.
        
        Args:
            token: The NUMBER token from the parser
            
        Returns:
            float: The numeric value
        """
        return float(token)

    @v_args(inline=True)
    def add(self, a, b):
        """
        Perform addition operation.
        
        Args:
            a: Left operand (float)
            b: Right operand (float)
            
        Returns:
            float: Result of a + b
        """
        return a + b

    @v_args(inline=True)
    def sub(self, a, b):
        """
        Perform subtraction operation.
        
        Args:
            a: Left operand (float)
            b: Right operand (float)
            
        Returns:
            float: Result of a - b
        """
        return a - b

    @v_args(inline=True)
    def mul(self, a, b):
        """
        Perform multiplication operation.
        
        Args:
            a: Left operand (float)
            b: Right operand (float)
            
        Returns:
            float: Result of a * b
        """
        return a * b

    @v_args(inline=True)
    def pow(self, base, exponent):
        """
        Perform exponentiation operation (base ^ exponent).
        Right-associative: 2^3^2 = 2^(3^2) = 512
        
        Args:
            base: Base value (float)
            exponent: Exponent value (float)
            
        Returns:
            float: Result of base ^ exponent
        """
        return base ** exponent

    @v_args(inline=True)
    def neg(self, value):
        """
        Perform unary negation operation.
        
        Args:
            value: The value to negate (float)
            
        Returns:
            float: Result of -value
        """
        return -value

    @v_args(inline=True)
    def log(self, value, base):
        """
        Perform logarithm operation: log(value) base base.
        
        Args:
            value: The value to take the logarithm of (float)
            base: The logarithm base (float)
            
        Returns:
            float: Result of log_base(value) = log(value) / log(base)
        """
        return math.log(value) / math.log(base)


def evaluate(expression):
    """
    Parse and evaluate a mathematical expression.
    
    This function:
    1. Takes a raw expression string as input
    2. Parses it using the Lark parser to create a parse tree
    3. Applies the CalculatorTransformer to recursively evaluate the tree
    4. Returns the final computed result
    
    Args:
        expression: String containing the mathematical expression
        
    Returns:
        float: The result of evaluating the expression
        
    Raises:
        lark.exceptions.UnexpectedInput: If the expression is syntactically invalid
        lark.exceptions.UnexpectedCharacters: If the expression contains invalid characters
        ZeroDivisionError: If division by zero occurs (including in logarithms)
    """
    # Parse the expression into a parse tree
    tree = parser.parse(expression)
    
    # Transform the tree using our CalculatorTransformer to get the final result
    transformer = CalculatorTransformer()
    result = transformer.transform(tree)
    
    return result


def main():
    """
    Main entry point for the calculator program.
    
    Reads the mathematical expression from command line arguments,
    evaluates it, and prints the result. The result is converted to int
    if it's a whole number, otherwise printed as a float.
    
    Usage: python calculator_cfg.py "expression"
    Example: python calculator_cfg.py "1+2*3"
    """
    if len(sys.argv) != 2:
        print("Usage: python calculator_cfg.py <expression>", file=sys.stderr)
        sys.exit(1)
    
    expression = sys.argv[1]
    
    try:
        result = evaluate(expression)
        
        # Convert to int if it's a whole number for cleaner output
        if isinstance(result, float) and result.is_integer():
            print(int(result))
        else:
            print(result)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
