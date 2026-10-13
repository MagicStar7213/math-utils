import warnings
import regex as re
from sympy import MutableDenseMatrix, NonSquareMatrixError, factor, nsimplify, parse_expr, srepr
from sympy.parsing.sympy_parser import T


class Matrix(MutableDenseMatrix):
    pass

MATRIX_PATTERN = r"(\d+(x\d+)?)(\((([^()]|(?3))+)\))"
ZEROS_PATTERN = r"O(\d+(x\d+)?)"
EYE_PATTERN = r"I(\d+(x\d+)?)"
OPERATION_PATTERN = rf"((\()|)({MATRIX_PATTERN}|[^()]+)(?(2)\)|)"
ADJ_PATTERN = rf"adj {OPERATION_PATTERN}"
DET_PATTERN = rf"((\|)|(det ))((\()|)({MATRIX_PATTERN}|[^()]+)(?(5)\)|)(?(2)\|)"

def get_matrix(raw: str) -> Matrix | None:
    raw_matrix = re.search(MATRIX_PATTERN, re.sub(r"\s{2,}", " ", raw))
    if raw_matrix:
        try:
            dimensions = tuple(map(int,raw_matrix.group(1).split('x')))
            if not 0 < len(dimensions) < 3:
                raise ValueError('Matrix dimensions introduced are not valid')
        except ValueError as e:
            print(f'Value error: {e}')
            return None
        else:
            if len(dimensions) == 1:
                dimensions += dimensions
            elts = [parse_expr(x, transformations=T[1:5]+T[6]+T[8]+T[7]+T[9:]) for x in raw_matrix.group(4).split(" ")]
            if len(elts) != dimensions[0]*dimensions[1]:
                print("Value error: Dimension mismatch. Check if you put the right dimensions or elements.")
                return None
            return Matrix(*dimensions,elts)

def parse_matrices(raw: str, env: dict) -> str:
    parsed = raw
    for adj in re.finditer(ADJ_PATTERN, raw):
        raw_matrix = adj.group(0).replace("adj ", "")
        pre_matrix = parse_matrices(raw_matrix, env)
        matrix = parse_expr(pre_matrix)
        if matrix:
            try:
                adjugate = matrix.adjugate()
            except NonSquareMatrixError:
                print("ERROR: Given matrix not square, thus ∄ adj A.")
            else:
                parsed = parsed.replace(adj.group(0), srepr(adjugate).replace('MutableDenseMatrix', 'Matrix'))
    for det in re.finditer(DET_PATTERN, raw):
        raw_matrix = det.group(0).removeprefix('|').removesuffix('|').replace("det ", "")
        pre_matrix = parse_matrices(raw_matrix, env)
        matrix = parse_expr(pre_matrix)
        if matrix:
            try:
                determinant = matrix.det(iszerofunc=matrix_is_zero)
            except NonSquareMatrixError:
                print("ERROR: Given matrix not square, thus ∄ det A.")
            else:
                parsed = parsed.replace(det.group(0), str(factor(nsimplify(determinant))))
    for var in reversed(sorted(env['vars'].keys(), key=len)):
        for find in re.finditer(var,raw):
            parsed = parsed.replace(find.group(0), srepr(env["vars"][var]))
    for match in re.finditer(MATRIX_PATTERN, raw):
        matrix = get_matrix(match.group(0))
        if matrix:
            parsed = parsed.replace(match.group(0), srepr(matrix))
    for zero in re.finditer(ZEROS_PATTERN, raw):
        try:
            dimensions = tuple(map(int,zero.group(1).split('x')))
            if not 0 < len(dimensions) < 3:
                raise ValueError('Matrix dimensions introduced are not valid')
        except ValueError as e:
            print(f'Value error: {e}')
        else:
            parsed = parsed.replace(zero.group(0), srepr(Matrix.zeros(dimensions[0], dimensions[1] if len(dimensions) == 2 else dimensions[0])))
    for eye in re.finditer(EYE_PATTERN, raw):
        try:
            dimensions = tuple(map(int,eye.group(1).split('x')))
            if not 0 < len(dimensions) < 3:
                raise ValueError('Matrix dimensions introduced are not valid')
        except ValueError as e:
            print(f'Value error: {e}')
        else:
            parsed = parsed.replace(eye.group(0), srepr(Matrix.eye(dimensions[0])))
    return parsed

def matrix_is_zero(x):
    result = x.is_zero
    if result is None:
        warnings.warn(f"Zero testing of {x} evaluated into None")
    return result

def decompose_matrix(matrix_list: list[Matrix]) -> list[Matrix]:
    return_list: list[Matrix] = []
    for A in matrix_list:
        shape = A.shape
        minors_list: list[Matrix] = []
        for row in range(shape[0]):
            for col in range(shape[1]):
                rowlist = list(range(shape[0]))
                collist = list(range(shape[1]))
                if shape[0] > shape[1]:
                    rowlist.remove(row)
                elif shape[1] > shape[0]:
                    collist.remove(col)
                else:
                    rowlist.remove(row)
                    collist.remove(col)
                minor = A.extract(rowlist, collist)
                if minor not in minors_list:
                    minors_list.append(minor)
        return_list.extend(minors_list)
    return return_list