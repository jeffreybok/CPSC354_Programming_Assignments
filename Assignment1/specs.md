# Calculator Implementation Specifications

## Overview

This document describes the implementation of a mathematical expression calculator using Lark parser generator. The calculator parses mathematical expressions according to an unambiguous context-free grammar and evaluates them using recursive AST traversal.

## Context-Free Grammar

### Original Grammar (Ambiguous)

```
exp -> exp '+' exp
exp -> exp '*' exp
exp -> exp '^' exp
exp -> exp '-' exp
exp -> '-' exp 
exp -> 'log' exp 'base' exp
exp -> '(' exp ')'
exp -> number
```

The original grammar is **ambiguous** because it doesn't specify operator precedence or associativity. For example, `1+2*3` could be parsed as either `(1+2)*3 = 9` or `1+(2*3) = 7`, depending on the parse tree generated.

### Modified Grammar (Unambiguous)

```
?start: exp

?exp: add_exp

?add_exp: mul_exp
        | add_exp "+" mul_exp -> add
        | add_exp "-" mul_exp -> sub

?mul_exp: unary_exp
        | mul_exp "*" unary_exp -> mul

?unary_exp: pow_exp
          | "-" unary_exp -> neg

?pow_exp: atom
        | atom "^" pow_exp -> pow

?atom: NUMBER -> number
     | "(" exp ")"
     | "log" pow_exp "base" pow_exp -> log
```

### Grammar Modifications Explained

The key modification is the introduction of **precedence levels** as separate grammar rules, from lowest to highest precedence:

1. **add_exp** (lowest precedence): Handles `+` and `-` operations
2. **mul_exp**: Handles `*` operations
3. **unary_exp**: Handles unary `-` (unary negation)
4. **pow_exp**: Handles `^` (exponentiation)
5. **atom** (highest): Handles numbers, parentheses, and logarithms

This hierarchical structure ensures that higher-precedence operations are parsed deeper in the tree, making them bind tighter.

The `?` prefix tells Lark to inline rules, eliminating unnecessary tree nodes and making evaluation cleaner.

## Order of Operations (Operator Precedence and Associativity)

### Precedence (Highest to Lowest)

1. **Atom** (parentheses, numbers, logarithms): e.g., `(3+2)`, `8`, `log 8 base 2`
2. **Exponentiation** (`^`): e.g., `2^3`
3. **Multiplication** (`*`): e.g., `2*3`
4. **Unary negation** (`-`): e.g., `-3`
5. **Addition and subtraction** (`+`, `-`): e.g., `1+2`, `1-2` (lowest precedence)

### Associativity

- **Right-associative operators**: `^` (exponentiation)
  - `2^3^2` = `2^(3^2)` = `2^9` = `512`
  - This is achieved by making `pow_exp` a recursive rule that recurses on the right side: `pow_exp: atom | atom "^" pow_exp`

- **Left-associative operators**: `+`, `-`, `*`
  - `10-5-2` = `(10-5)-2` = `3`
  - `1+2+3` = `(1+2)+3` = `6`
  - This is achieved by making `add_exp` and `mul_exp` recurse on the left side

### Special Cases

**Unary negation with exponentiation**:
- `-3^2` = `-(3^2)` = `-9` (not `(-3)^2 = 9`)
- This is achieved by placing `unary_exp` BEFORE `pow_exp` in the precedence hierarchy
- The grammar structure ensures that `pow_exp` (exponentiation) is evaluated before unary negation

**Double negation**:
- `--1` = `-(-1)` = `1`
- The rule `unary_exp: "-" unary_exp` allows multiple negations to chain

**Logarithm precedence**:
- `log 8 base 2 + 1` = `(log 8 base 2) + 1` = `3 + 1` = `4`
- Logarithm operands use `pow_exp` level, which is higher than addition
- This ensures the `+` applies to the result of the logarithm, not to the base

**Parentheses**:
- Parentheses have the highest precedence and override normal precedence rules
- `(1+2)*3` = `3*3` = `9`

## Implementation Details

### Class: CalculatorTransformer

**Purpose**: Transforms the parse tree into computed results by implementing recursive evaluation.

**Methods**:

- **number(token)**: Converts a NUMBER token to a float value
  - Input: Token from parser
  - Output: float
  - Purpose: Base case for numbers in the AST

- **add(a, b)**: Performs addition (a + b)
  - Input: Two float operands
  - Output: float (sum)
  - Purpose: Implements + operator

- **sub(a, b)**: Performs subtraction (a - b)
  - Input: Two float operands
  - Output: float (difference)
  - Purpose: Implements - operator

- **mul(a, b)**: Performs multiplication (a * b)
  - Input: Two float operands
  - Output: float (product)
  - Purpose: Implements * operator

- **pow(base, exponent)**: Performs exponentiation (base ^ exponent)
  - Input: Two float operands (base and exponent)
  - Output: float (base raised to exponent)
  - Purpose: Implements ^ operator (right-associative)

- **neg(value)**: Performs unary negation (-value)
  - Input: One float operand
  - Output: float (negated value)
  - Purpose: Implements unary - operator

- **log(value, base)**: Performs logarithm computation
  - Input: Two float operands (value and logarithm base)
  - Output: float (log_base(value) = ln(value) / ln(base))
  - Purpose: Implements logarithm operation using change of base formula

### Function: evaluate(expression)

**Purpose**: Main evaluation pipeline that orchestrates parsing and transformation.

**Steps**:
1. Parse the expression string using Lark parser to create a parse tree
2. Create a CalculatorTransformer instance
3. Apply the transformer to the parse tree (recursive evaluation)
4. Return the final computed result

**Error Handling**: Propagates parsing errors and computation errors (e.g., division by zero) to caller

### Function: main()

**Purpose**: Command-line interface and entry point.

**Steps**:
1. Validate that exactly one command-line argument (the expression) is provided
2. Call evaluate() on the expression
3. Format the result:
   - If result is a whole number, print as integer
   - Otherwise, print as float
4. Handle errors gracefully with error messages

**Usage**: `python calculator_cfg.py "expression"`

## Program Flow

1. **Parser Initialization**: `grammar.lark` is loaded and used to create a Lark parser
2. **Input Reception**: Expression string is received via command-line argument
3. **Parsing Phase**: The parser converts the expression into a parse tree, respecting the grammar rules
4. **Evaluation Phase**: CalculatorTransformer recursively traverses the parse tree:
   - For each node in the tree, the corresponding method is called
   - Terminal nodes (numbers) are converted to floats
   - Intermediate nodes (operations) call child evaluation methods and apply the operation
   - The recursion naturally respects operator precedence and associativity due to tree structure
5. **Output**: The final numeric result is printed to stdout

## Example Evaluations

**Example 1**: `1+2*3`
- Parse tree respects precedence: `+` is higher-level than `*`, so `2*3` is evaluated first
- Evaluation: `1 + (2*3)` = `1 + 6` = `7`

**Example 2**: `2^3^2`
- Parse tree is right-associative: `2^(3^2)` 
- Evaluation: `2^9` = `512`

**Example 3**: `-3^2`
- Parse tree: exponentiation is evaluated first, then unary negation
- Evaluation: `-(3^2)` = `-(9)` = `-9`

**Example 4**: `log 8 base 2 + 1`
- Parse tree: logarithm is evaluated as one subtree, then addition is applied
- Evaluation: `(log_2(8)) + 1` = `3 + 1` = `4`

## Testing

All provided test cases pass with this implementation:
- `1+2*3` → 7
- `2-(4+2)` → -4
- `(3+2)*2` → 10
- `--1` → 1
- `2^3^2` → 512
- `2^3+1` → 9
- `2^3*2` → 16
- `log 8 base 2` → 3
- `log 8 base 2 + 1` → 4
- `-3^2` → -9

## Key Design Decisions

1. **Hierarchical Grammar Rules**: Using separate rules for each precedence level makes the grammar unambiguous and naturally enforces precedence

2. **Operator Associativity**:
   - Right-recursive power rule: `pow_exp: atom | atom "^" pow_exp` makes exponentiation right-associative
   - Left-recursive addition/multiplication rules make `+`, `-`, and `*` left-associative

3. **Unary Negation Precedence**: Placing `unary_exp` between `mul_exp` and `pow_exp` in the hierarchy ensures unary negation has lower precedence than exponentiation but higher than multiplication

4. **Logarithm Implementation**: Logarithm operands use `pow_exp` level so that `log 8 base 2 + 1` parses as `(log 8 base 2) + 1`, not `log 8 base (2 + 1)`

5. **Transformer Pattern**: Using Lark's Transformer class provides clean separation between parsing and evaluation logic

6. **Inline Rules**: The `?` prefix reduces parse tree complexity and makes evaluation simpler

7. **Float Arithmetic**: Using Python's built-in float arithmetic simplifies implementation

8. **Change of Base for Logarithms**: `log_b(x) = ln(x) / ln(b)` allows computing arbitrary-base logarithms using natural logarithm

