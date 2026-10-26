import regex as re


def get_op_scope(raw: str, start_index: int, enclosing_chars: str = '()') -> tuple[int, int]:
    if len(enclosing_chars) == 1:
        open_char = enclosing_chars
        close_char = enclosing_chars
    elif len(enclosing_chars) == 2:
        open_char = enclosing_chars[0]
        close_char = enclosing_chars[1]
    elif enclosing_chars == '':
        open_char = '('
        close_char = ')'
    else:
        raise ValueError('DEBUG: Enclosing characters string must be at most 2 characters long')
    parentheses_count = 0
    for index in range(start_index,len(raw)):
        if raw[index] == open_char:
            parentheses_count += 1
        elif raw[index] == close_char:
            parentheses_count -= 1
        if parentheses_count < 0:
            raise SyntaxError('There are opening brackets missing')
        if parentheses_count == 0:
            return (start_index, index+1)
    raise SyntaxError('Ending brackets missing')

def parse_special_op(pattern: str, raw: str, enclosing_chars = '()'):
    subs: list[tuple[str, str]] = []
    for call in re.finditer(pattern, raw):
        start_index, end_index = get_op_scope(raw, call.end(), enclosing_chars)
        raw_func = raw[start_index:end_index]
        subs.append((call.group(0)+raw_func, raw_func.removeprefix('(').removesuffix(')')))
    return subs
