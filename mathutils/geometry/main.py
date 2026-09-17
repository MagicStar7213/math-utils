import re

from sympy import Equality, Expr, Line3D, Point3D, Symbol, Tuple, pretty

from .geometry import VPlane, angle, distance, process_geometry, rel_pos, sim, length
from .vector import Vector

def main():
    env = {"classes": [Vector, VPlane, Line3D, Point3D], "whitelist": [], "vars": {}}
    while True:
        raw = input(">> ")
        if raw == 'q':
            return
        if raw.replace(" ", "") == "":
            processed = ''
        elif re.match(r'relpos \w+,\w+(,\w+)?', raw):
            processed, env = rel_pos(raw, env)
        elif re.match(r'< ((\()?)(?(2)(\w+,\w+(,\w+)\))|\w+),((\()?)(?(6)(\w+,\w+(,\w+)\))|\w+)', raw):
            processed, env = angle(raw, env)
        elif re.match(r"d \w+,\w+", raw):
            processed, env = distance(raw, env)
        elif re.match(r"sim \w+,\w+", raw):
            processed, env = sim(raw, env)
        elif re.match(r'\|((\|)?)((\()?)(?(4)(\w+,\w+(,\w+)\))|\w+)(?(2)\|)\|', raw):
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
        print(pretty(processed))
