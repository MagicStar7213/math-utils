import regex as re

from sympy import Add, Integer, Mul, Rational, Symbol, parse_expr, pprint, pretty, solve
from sympy.parsing.sympy_parser import T

from mathutils.parser import safe_eval
from .codec import Main
from .determinants import del_proportional_lines, del_zero_lines
from .rank import print_rank, rank
from .utils import OPERATION_PATTERN, Matrix, parse_matrices


def matrices():
    env = {"classes": [Matrix, Symbol, Mul, Add, Rational, Integer], "vars": {}, "whitelist": []}
    raw = input(">> ").strip()
    while raw != 'q':
        if raw == "":
            pass
        elif raw == "codec":
            Main().app()
        elif re.match(rf"(rg|rango|rank) {OPERATION_PATTERN}", raw):
            A = parse_matrices(raw.replace('rg','').replace('rango','').replace('rank',''), env)
            if A:
                A = del_proportional_lines(del_zero_lines(parse_expr(A)))
                try:
                    ranks = rank(A)
                    print_rank(ranks)
                except ValueError:
                    print("ERROR: Mismatched dimensions.")
        elif re.match(r"solve \S+", raw):
            clean = raw.removeprefix('solve ')
            systems = [parse_expr(x, transformations=T[1:5]+T[6]+T[8]+T[7]+T[9:]) for x in clean.split(',')]
            processed = pretty(solve(systems))
            result = processed.strip('{').strip('}').replace(', ', '\n')
            print(f'Soluciones:\n{result}')
        else:
            parsed = parse_matrices(raw, env).replace("^","**")
            try:
                result, env = safe_eval(parsed, env)
            except (ValueError, NameError, TypeError, SyntaxError) as e:
                print(f"ERROR: {e}")
            else:
                if result:
                    print()
                    pprint(result)
        raw = input(">> ").strip()
