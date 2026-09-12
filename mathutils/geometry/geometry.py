import re
from sympy import N, Mul, Symbol, acos, asin, atan, parse_expr, Equality, Expr, Point3D, pi, pretty, solve, Plane, Line3D
from sympy.abc import x, y ,z
from sympy.parsing.sympy_parser import T
from .operations import relpos, sym_point
from .vector import Vector
from mathutils.parser import construct_string, safe_eval


class VPlane(Plane):
    def __new__(cls, p1, normal_vector: Vector):
        return super().__new__(cls, p1, normal_vector=normal_vector.components)

def rel_pos(raw: str, env: dict):
    split = raw.removeprefix('relpos ').split(',')
    relp: list[Point3D | Line3D | VPlane] = []
    for geomid in split:
        processed, env = process_geometry(geomid, env)
        if processed:
            relp.append(processed)
    print(relpos(*relp))
    return env

def angle(raw: str, env: dict):
    split = raw.removeprefix("< ").split(",")
    ang: list[Line3D | VPlane] = []
    for geomid in split:
        processed, env = process_geometry(geomid, env)
        if processed and not isinstance(processed, Point3D): 
            ang.append(processed)
    try:
        result_angle = ang[0].angle_between(ang[1])
    except AttributeError:
        result_angle = ang[1].angle_between(ang[0])
    print(str(N(result_angle) if isinstance(result_angle, (asin,acos,atan)) else N(2*pi+result_angle) if isinstance(result_angle, Mul) else pretty(result_angle))+" rad")
    return env

def distance(raw: str, env: dict):
    split = raw.removeprefix("d ").split(",")
    dist: list[Line3D | VPlane | Point3D] = []
    for geomid in split:
        processed, env = process_geometry(geomid, env)
        if processed:
            dist.append(processed)
    result_distance = dist[0].distance(dist[1])
    num_distance = int(N(result_distance)) if float(N(result_distance)).is_integer() else float(N(result_distance))
    print(f'{pretty(result_distance)}{f" ({num_distance})" if pretty(num_distance) != pretty(result_distance) else ""}')
    return env

def sim(raw: str, env: dict):
    split = raw.removeprefix("sim ").split(",")
    simg: list[Line3D | VPlane | Point3D] = []
    for geomid in split:
        processed, env = process_geometry(geomid, env)
        if processed:
            simg.append(processed)
    if len(simg) == 2 and any(isinstance(i,Point3D) for i in simg):
        p = next(i for i in simg if isinstance(i, Point3D))
        r = next(i for i in simg if isinstance(i, (Line3D, VPlane)))
        print(sym_point(p, r))
    return env

def str_to_list(raw: str) -> list[str | list] | tuple[str, list[Expr]]:
    stack: list[list[str | list]] = [[]]
    current: list[str | list] = stack[-1]
    for char in raw:
        if char == "(":
            new_list = []
            current.append(new_list)
            stack.append(new_list)
            current = new_list

        elif char == ")":
            stack.pop()
            current = stack[-1]
        else:
            if char.isdigit() and current and current[-1] == "-":
                current[-1] = f"-{char}"
            elif char == ",":
                pass
            else:
                current.append(char)
                if char == ":":
                    var = current.copy()
                    current.clear()
                    current.extend(["".join(list(map(str, var[:-1]))), "="])
                    current.append(raw[raw.index(char) + 1 :].split(","))
                    break
    return stack[0]

def get_plane(eq: Equality) -> VPlane:
    def_point:dict[Symbol,(int | Expr)] = {x:0,y:0,z:0}
    coeffs: list[tuple[Symbol, Expr]] = [(i, eq.lhs.coeff(i)) for i in [x, y, z] if eq.lhs.coeff(i) != 0] # type: ignore
    if len(coeffs) == 1:
        var = coeffs[0][0]
        point = def_point.copy()
        point.update({var: solve(eq.subs(*[(i, 0) for i in [x, y, z] if i != var]))[0]})
        p1 = Point3D(*[v for (_,v) in point.items()])
    elif len(coeffs) == 2:
        variables = [i[0] for i in coeffs]
        point = def_point.copy()
        point.update({variables[1]: solve(eq.subs([(i, 0) for i in [x, y, z] if i != variables[1]]), variables[1])[0]})
        p1 = Point3D(*[v for (_, v) in point.items()])
    else:
        p1 = Point3D(0,0, solve(eq.subs([(x,0),(y,0)]),z)[0])
    
    return VPlane(p1, normal_vector=Vector(eq.lhs.coeff(x), eq.lhs.coeff(y), eq.lhs.coeff(z))) # type: ignore

def parse_equations(raw: list[str | list] | tuple[str, list[Expr]], env: dict):
    parsed: list[str | list | Point3D | Line3D | VPlane] = []
    parsed += list(raw).copy()
    if isinstance(raw, tuple):
        parsed.insert(-1, '=')
        parsed[-1] = Point3D(*raw[1])
    else:
        if construct_string(raw) in env['vars']:
            return construct_string(raw)
        else:
            transformations = T[1:5]+T[6]+T[8]+T[7]+T[9:]
            raw_equations: list[Equality] = [parse_expr(eq, transformations=transformations) for eq in raw[-1]]
            equations: list[Equality] = [Equality(eq.lhs - eq.rhs,0) for eq in raw_equations] # type: ignore
            if len(equations) == 1:
                eq = equations[0]
                parsed[-1] = get_plane(eq)
            elif len(equations) == 2:
                line = get_plane(equations[0]).intersection(get_plane(equations[1]))
                parsed[-1] = '' if not line else line[0] # type: ignore
            else:
                raise ValueError('Objects defined by more than 2 equations are not supported')
    return list(map(str, parsed))

def process_geometry(raw: str, env: dict) -> tuple[Point3D | Line3D | VPlane | None, dict]:
    try:
        if ":" in raw and "=" in raw:
            lst = str_to_list(raw)
            equations = parse_equations(lst, env)
            code = equations if isinstance(equations,str) else construct_string(equations) # type: ignore
        else:
            code = raw
            if re.match(r"([A-Z]+\(-?\d(\.\d+)?,-?\d(\.\d+)?(,-?\d(\.\d+)?)?\))", raw):
                separated = raw.split("(")
                separated[-1] = separated[-1].removesuffix(")")
                point = (separated[0], tuple(map(parse_expr, separated[-1].split(","))))
                code = f"{point[0]}=Point3D{point[1]}"
        parsed, env = safe_eval(code, env)
    except SyntaxError as e:
        print(f'Syntax error: {e}')
        return None, env
    except TypeError as e:
        print(f'Type error: {e}')
        return None, env
    except ValueError as e:
        print(f'Value error: {e}')
        return None, env
    except NameError as e:
        print(f'Name error: {e}')
        return None, env
    else:
        return parsed, env