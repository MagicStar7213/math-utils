import regex as re

from sympy import Add, Integer, Mul, Rational, Symbol, parse_expr, pprint, pretty, solve
from sympy.parsing.sympy_parser import T

from mathutils.parser import safe_eval
from .codec import Main
from .determinants import del_proportional_lines, del_zero_lines
from .rank import print_rank, rank
from .utils import Matrix, parse_matrices


def matrices():
    env = {"classes": [Matrix, Symbol, Mul, Add, Rational, Integer], "vars": {}, "whitelist": [], 'attrs': ['L', 'U']}
    raw = input(">> ").strip()
    rg_match = re.match(r"(rg|rang) ", raw)
    while raw != 'q':
        if raw == "":
            pass
        elif raw == "codec":
            Main().app()
        elif rg_match:
            A = parse_matrices(raw.removeprefix(rg_match.group(0)), env)
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
                if result is not None:
                    pprint(result)
        raw = input(">> ").strip()
