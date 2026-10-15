import regex as re
from sympy import Equality, Expr, Line3D, Point3D, Symbol, Tuple, pretty
from .geometry import VPlane, process_geometry, length
from .vector import Vector

def main():
    env = {"classes": [Vector, VPlane, Line3D, Point3D], "whitelist": [], "vars": {}}
    raw = input(">> ").strip()
    while raw != 'q':
        if raw.replace(" ", "") == "":
            processed = ''
        elif re.match(r'relpos \w+,\w+(,\w+)?', raw):
            valid_raw = raw.replace('relpos ', 'relpos(') + ')'
            processed, env = process_geometry(valid_raw, env)
        elif re.match(r'< (\([^()]+\)|\w+),((\([^()]+\))|\w+)', raw):
            valid_raw = raw.replace('< ', '<(') + ')'
            processed, env = process_geometry(valid_raw, env)
        elif re.match(r"d \w+,\w+", raw):
            valid_raw = raw.replace('d ', 'd(') + ')'
            processed, env = process_geometry(valid_raw, env)
        elif re.match(r"sim \w+,\w+", raw):
            valid_raw = raw.replace('sim ', 'sim(') + ')'
            processed, env = process_geometry(valid_raw, env)
        elif re.match(r'\|((\|)?)\S+(?(2)\|)\|', raw):
            processed, env = length(raw, env)
        else:
            processed, env = process_geometry(raw, env)
            if processed is not None:
                if processed in list(env['vars'].values()):
                    ind = list(env["vars"].values()).index(processed)
                    sym = pretty(Symbol(list(env['vars'].keys())[ind]))
                    if isinstance(processed, (Line3D, VPlane)):
                        eq = processed.equation()
                        if isinstance(eq, Expr):
                            eq = Equality(eq,0)
                        elif isinstance(eq, Tuple):
                            eq = tuple(Equality(i,0) for i in eq)
                        print(f'{sym} ≡ {pretty(eq).replace("(","{").replace(")","}")}')
                        continue
                    elif isinstance(processed, Point3D):
                        print(f'{sym}{processed.coordinates}')
                        continue
            else:
                processed = ''
        print(pretty(processed))
        raw = input(">> ").strip()
