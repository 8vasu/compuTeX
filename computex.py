#!/usr/bin/python3

# compuTeX - Convert LaTeX -> SymPy -> evaluate -> LaTeX.
# Copyright (C) 2023 Soumendra Ganguly

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import argparse
from sympy import Matrix
from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import parse_expr
from sympy.printing.latex import latex
from sympy.simplify.simplify import simplify
from random import choice
from string import ascii_lowercase
from sympy import UnevaluatedExpr
from re import split as re_split
import itertools

MATRIX_DELIM = {"\\left(\\begin{matrix}": "\\end{matrix}\\right)",
                "\\left[\\begin{matrix}": "\\end{matrix}\\right]",
                "\\begin{pmatrix}": "\\end{pmatrix}",
                "\\begin{bmatrix}": "\\end{bmatrix}"
                }

def gen_var_name():
    """Generate a random variable name."""
    return "".join(choice(ascii_lowercase) for i in range(0,10))

def parse_matrix(matrix_str):
    """Construct a SymPy Matrix from a LaTeX matrix string."""
    matrix_str = matrix_str.replace("\n", "")
    mat = []
    for row_str in matrix_str.split("\\\\"):
        row = row_str.split("&")
        if row != [""]:
            parsed_row = [parse_latex(x) for x in row]
            mat.append(parsed_row)
    return UnevaluatedExpr(Matrix(mat))

def uniformize_matrix_delimiters(latex_str, uniform_begin, uniform_end):
    """Replace all matrix begin, end delimiters with specific ones."""
    for begin_delim in MATRIX_DELIM:
        end_delim = MATRIX_DELIM[begin_delim]
        latex_str = latex_str.replace(begin_delim, uniform_begin)
        latex_str = latex_str.replace(end_delim, uniform_end)
    return latex_str

def fix_substring_order(input_str, correct_order_list):
    """Fix the order of substrings in input_str to
    match correct_order_list."""
    l = re_split("|".join(correct_order_list), input_str)
    z = itertools.zip_longest(l, correct_order_list)
    return "".join([x for x in itertools.chain.from_iterable(z) if x])

def parse_latex_extended(latex_str):
    """Add matrix parsing to SymPy's parse_latex."""
    original_latex_str = latex_str

    # uniform_begin = "<<<<<<<<<<"
    # uniform_end = ">>>>>>>>>>"

    uniform_begin = "\\begin{pmatrix}"
    uniform_end = "\\end{pmatrix}"
    latex_str = uniformize_matrix_delimiters(latex_str,
                                             uniform_begin,
                                             uniform_end)

    matrices = {}
    used_var_names = []
    while True:
        b = latex_str.find(uniform_begin)
        e = latex_str.find(uniform_end)
        if b == -1 and e == -1:
            # all matrices have been parsed

            # Unfortunately, parse_latex does not know that the new
            # variables are matrices and changes their multiplication
            # order. It is also strange that this reordering is not
            # the same every time, which might have something to do
            # with sorting variables by name in alphabetical order and
            # the fact that our variable names are random strings.
            # We will have to fix the order here.
            sympy_expr = parse_latex(latex_str)
            sympy_str = str(sympy_expr)
            sympy_str = fix_substring_order(sympy_str, used_var_names)

            # Unfortunately, parse_expr also has the same above mentioned
            # flaw as parse_latex, so we will not perform the following now:
            # parse_expr(sympy_str).subs(matrices)
            #
            # Instead, we will replace the varibles with the corresponding
            # matrices in sympy_str and then call parse_expr.
            for var_name in matrices:
                sympy_str = sympy_str.replace(var_name,
                                              str(matrices[var_name]))
            return parse_expr(sympy_str)

        if (b != -1 and e == -1) or (b == -1 and e != -1):
            print("Mismatched matrix delimiters.", file=sys.stderr)
            sys.exit(1)

        b2 = b + len(uniform_begin)
        e2 = e + len(uniform_end)

        before_matrix = latex_str[:b]
        matrix_content = latex_str[b2:e]
        after_matrix = latex_str[e2:]

        new_matrix_name = gen_var_name()
        while ((new_matrix_name in used_var_names)
               or (new_matrix_name in original_latex_str)):
            new_matrix_name = gen_var_name()
        used_var_names.append(new_matrix_name)

        matrices[new_matrix_name] = parse_matrix(matrix_content)
        latex_str = f"{before_matrix}\{new_matrix_name}{after_matrix}"

PROGRAM_DESCRIPTION = "Convert LaTeX -> SymPy -> evaluate -> LaTeX."

parser = argparse.ArgumentParser(description=PROGRAM_DESCRIPTION)
parser.add_argument("-e", "--equation-form",
                    help="""Print "input = output" instead of
just "output".""",
                    action='store_const',
                    const=True, default=False)
parser.add_argument("-b", "--bmatrix",
                    help="""Output matrices are [] enclosed
instead of the default ().""",
                    action='store_const',
                    const=True, default=False)
group = parser.add_mutually_exclusive_group()
group.add_argument("-E", "--expand",
                    help="""Try to expand output.""",
                    action='store_const',
                    const=True, default=False)
group.add_argument("-f", "--factorize",
                    help="""Try to factorize output.""",
                    action='store_const',
                    const=True, default=False)
parser.add_argument("-s", "--simplify",
                    help="""Try to simplify output. The simplification
will be done after expansion or factorization.""",
                    action='store_const',
                    const=True, default=False)
parser.add_argument("latex_expr",
                    help="LaTeX math expression.",
                    nargs="?", default=None)
args = parser.parse_args()

if args.latex_expr == None:
    latex_expr = sys.stdin.read()
else:
    latex_expr = args.latex_expr

sympy_expr = parse_latex_extended(latex_expr)
evaluated_sympy_expr = sympy_expr.doit()

if args.expand:
    evaluated_sympy_expr = evaluated_sympy_expr.expand()
if args.factorize:
    evaluated_sympy_expr = evaluated_sympy_expr.factor()
if args.simplify:
    evaluated_sympy_expr = simplify(evaluated_sympy_expr)

evaluated_latex_expr = latex(evaluated_sympy_expr)

output_matrix_begin = "\\begin{pmatrix}"
output_matrix_end = "\\end{pmatrix}"
if args.bmatrix:
    output_matrix_begin = "\\begin{bmatrix}"
    output_matrix_end = "\\end{bmatrix}"

evaluated_latex_expr = uniformize_matrix_delimiters(evaluated_latex_expr,
                                                     output_matrix_begin,
                                                     output_matrix_end)
if args.equation_form:
    print(f"{latex_expr} = {evaluated_latex_expr}", end="")
else:
    print(f"{evaluated_latex_expr}", end="")
