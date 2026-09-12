import re

from sympy import Equality, Expr, Line3D, Point3D, Symbol, Tuple, pretty

from .geometry import VPlane, angle, distance, process_geometry, rel_pos, sim
from .vector import Vector

def main():
    env = {"classes": [Vector, VPlane, Line3D, Point3D], "whitelist": [], "vars": {}}
    print("""
     ____                                _                
    / ___|   ___   ___   _ __ ___    ___ | |_  _ __  _   _ 
    | |  _  / _ \\ / _ \\ | '_ ` _ \\  / _ \\| __|| '__|| | | |
    | |_| ||  __/| (_) || | | | | ||  __/| |_ | |   | |_| |
     \\____| \\___| \\___/ |_| |_| |_| \\___| \\__||_|    \\__, |
                                                     |___/ 
    """)
    while True:
        raw = input(">> ")
        if raw == 'q':
            return
        if raw.replace(" ", "") == "":
            pass
        elif re.match(r'relpos \w+,\w+(,\w+)?', raw):
            env = rel_pos(raw, env)
        elif re.match(r'< ((\()?)(?(2)(\w+,\w+(,\w+)\))|\w+),((\()?)(?(6)(\w+,\w+(,\w+)\))|\w+)', raw):
            env = angle(raw, env)
        elif re.match(r"d \w+,\w+", raw):
            env = distance(raw, env)
        elif re.match(r"sim \w+,\w+", raw):
            env = sim(raw, env)
        else:
            processed, env = process_geometry(raw, env)
            if processed:
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
                    elif isinstance(processed, Point3D):
                        print(f'{sym}{processed.coordinates}')
                    else:
                        print(pretty(processed))
                else:
                    print(pretty(processed))
