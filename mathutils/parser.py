import ast
import math
import operator


def are_elements_numbers(lst: list[str]) -> bool:
    for x in lst:
        try:
            float(x)
        except ValueError:
            return False
    return True

def construct_string(lst: list[str | list]) -> str:
    return ''.join([construct_string(x) if isinstance(x, list) else x for x in lst])


OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.BitXor: operator.xor,
    ast.USub: operator.neg
}
ALLOWED_FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "max": max,
    "min": min,
}

class SafeEval(ast.NodeTransformer):
    def __init__(self, env: dict):
        self.env = env

    def visit_Module(self, node):
        node.body = [self.visit(stmt) for stmt in node.body]
        return node

    def visit_Expr(self, node):
        node.value = self.visit(node.value)
        return node

    def visit_Assign(self, node):
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            raise ValueError("Invalid assignment")
        name = node.targets[0].id
        node.value = self.visit(node.value)
        self.env["vars"][name] = safe_eval(ast.unparse(node.value), self.env)[0]
        return node

    def visit_Num(self, node):
        return node

    def visit_Name(self, node):
        classes = [cls.__name__ for cls in self.env['classes']]
        if node.id not in self.env['whitelist'] and node.id not in self.env['vars'] and node.id not in classes:
            raise NameError(f"Undefined variable '{node.id}'")
        return node

    def visit_Attribute(self, node):
        if type(node.value) is not ast.Name:
            raise ValueError('Attribute should be called from a Name')
        if node.value.id not in self.env['vars']:
            raise ValueError(f'Class {node.value.id} cannot be called')
        if 'attrs' in self.env.keys() and node.attr in self.env['attrs']:
            return node
        else:
            raise ValueError(f'Attribute {node.attr} cannot be called')

    def visit_UnaryOp(self, node):
        if type(node.op) in [ast.Not, ast.Invert, ast.UAdd]:
            raise ValueError(f'Operator {type(node.op).__name__} is not allowed')
        node.operand = self.visit(node.operand)
        return node

    def visit_BinOp(self, node):
        if type(node.op) not in OPS.keys():
            raise ValueError("Operation not allowed")
        node.left = self.visit(node.left)
        if isinstance(node.op, ast.Pow) and isinstance(node.right, ast.Name) and node.right.id.lower() == "t":
            node = ast.Attribute(value=node.left, attr=node.right.id.upper(), ctx=ast.Load())
        else:
            node.right = self.visit(node.right)
        return node

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            method = node.func.attr
            if method not in self.env['whitelist']:
                raise ValueError(f"Method {method} not allowed")
            if method in self.env['whitelist'] and type(self.visit(node.func.value)) in self.env['classes']:
                node.args = [self.visit(arg) for arg in node.args]
                return node
            else:
                raise ValueError(f'{method} cannot be called from {type(self.visit(node.func.value)).__name__}')

        elif isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name not in ALLOWED_FUNCTIONS and not any(func_name == cls.__name__ for cls in self.env['classes']):
                raise ValueError(f"Function '{func_name}' is not allowed")

            node.args = [self.visit(arg) for arg in node.args]
            if func_name not in ALLOWED_FUNCTIONS:
                node.func=self.visit(node.func)
            return node
        else:
            raise ValueError('Call not allowed.')

    def visit_Tuple(self, node):
        for e in list(node.elts):
            self.visit(e) 
        return ast.Call(
            func=ast.Name(id='Vector', ctx=ast.Load()),
            args=node.elts,
            keywords=[]
        )
    
    def visit_List(self, node):
        node.elts = [self.visit(e) for e in node.elts]
        if isinstance(node.ctx, ast.Store):
            raise ValueError("Storing variables as lists is not allowed")
        return node
    
    def visit_Constant(self, node: ast.Constant):
        if not isinstance(node.value, (str,bytes,int,float,complex,bool)) and node.value and node.value is not Ellipsis:
            raise ValueError("Constant not allowed")
        return node

    def visit_Expression(self, node):
        node.body = self.visit(node.body)
        return node

    def generic_visit(self, node):
        raise ValueError(f"Disallowed syntax: {type(node).__name__}")

def safe_eval(code: str, env=None):
    if env is None:
        env = {}
    tree = ast.parse(code)
    evaluator = SafeEval(env)
    new_code = ast.unparse(evaluator.visit(tree))
    try:
        ast.parse(new_code, mode='eval')
    except SyntaxError:
        exec(new_code, evaluator.env['vars'] | dict((k,v) for k,v in zip([cls.__name__ for cls in env['classes']], env['classes'])) | ALLOWED_FUNCTIONS)
        return None, evaluator.env
    else:
        return eval(new_code, evaluator.env['vars'] | dict((k,v) for k,v in zip([cls.__name__ for cls in env['classes']], env['classes'])) | ALLOWED_FUNCTIONS), evaluator.env
