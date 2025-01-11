from logic import Variable, Implication, Negation


def conjunction(s1: str, s2: str) -> str:
    return f'!({s1}>!{s2})'


# convert disjunction to negotiation and implication
def disjunction(s1: str, s2: str) -> str:
    return f'!{s1}>{s2}'


# find index of current bracket's pair
# return -1 if not found
def find_bracket_pair(index: int, expression: str) -> int:
    bracket = expression[index]
    if bracket == '(':
        step = 1
        contra = ')'
    elif bracket == ')':
        step = -1
        contra = '('
    else:
        return -1

    counter = 1
    index += step
    while 0 <= index < len(expression):
        if expression[index] == contra:
            counter -= 1
        elif expression[index] == bracket:
            counter += 1
        if not counter:
            return index
        index += step
    return -1


# relace selected operation and its operands to another form
def binary_replacer(index: int, expr: str, matcher) -> str:
    # find bounds for left operand
    left_end = index - 1
    left_start = find_bracket_pair(left_end, expr) if expr[left_end] == ')' else left_end
    if not left_end and expr[left_end - 1] == '!':
        left_start -= 1

    # find bounds for right operand
    right_start = index + 1
    shift = int(expr[right_start] == '!')
    right_end = find_bracket_pair(right_start + shift, expr) if expr[right_start] == '(' else right_start + shift

    # build result expression
    s1 = expr[left_start:left_end + 1]
    s2 = expr[right_start:right_end + 1]
    res = matcher(s1, s2)
    expr = f'{expr[:left_start]}({res}){expr[right_end + 1:]}'

    # logging
    # print(s1, '-' * 5, s2, '\t' * 4, expr)
    return expr


# replace conjunction and disjunction with negation and implication
def preprocessor(expr: str) -> str:
    # replace all conjunctions
    while expr.find('*') != -1:
        index = expr.find('*')
        expr = binary_replacer(index, expr, conjunction)

    # replace all disjunctions
    while expr.find('|') != -1:
        index = expr.find('|')
        expr = binary_replacer(index, expr, disjunction)

    return expr


# remove brackets if whey wrap something twice or wrap a single variable
def remove_overbrackets(expr: str) -> str:
    ignore_set = set()
    non_variable = {'(', ')', '*', '|', '>', '!'}

    # remove duplicated brackets
    for i in range(len(expr)):
        if expr[i] != '(': continue
        left = i
        right = find_bracket_pair(left, expr)
        if right == -1: raise

        if expr[left + 1] == '(' and right - 1 == find_bracket_pair(left + 1, expr):
            ignore_set.add(left + 1)
            ignore_set.add(right - 1)

    # build string without duplicated brackets
    expr = [c for i, c in enumerate(expr) if i not in ignore_set]
    ignore_set.clear()

    # build string without duplicated brackets
    expr = [c for i, c in enumerate(expr) if i not in ignore_set]
    ignore_set.clear()

    # remove wrapping of single variable
    for i in range(len(expr)):
        if i == 0 or i + 1 == len(expr) or expr[i] in non_variable: continue
        if expr[i - 1] == '(' and expr[i + 1] == ')':
            ignore_set.add(i - 1)
            ignore_set.add(i + 1)

    # build result string
    result_string = [c for i, c in enumerate(expr) if i not in ignore_set]
    return ''.join(result_string)


# find position of next priority implication
def find_main_implication(expr: str) -> int:
    i = 0
    while i < len(expr):
        if expr[i] == '>':
            return i
        if expr[i] == '(':
            i = find_bracket_pair(i, expr)
        i += 1
    return -1


# obtain class hierarchy from string representation
def from_string_to_expression(expr: str):
    # unwrap external brackets
    while len(expr) > 1 and expr[0] == '(' and find_bracket_pair(0, expr) == len(expr) - 1:
        expr = expr[1:-1]

    # wrap expression to negation class
    if len(expr) and expr[0] == '!' and expr[1] == '(' and find_bracket_pair(1, expr) == len(expr) - 1:
        expr = expr[2:-1]
        neg_expr = from_string_to_expression(expr)
        return Negation(neg_expr)

    implication_position = find_main_implication(expr)
    if implication_position == -1:
        if len(expr) == 1: return Variable(expr)
        if len(expr) == 2 and expr[0] == '!': return Negation(expr[1])
        raise 'Uncorrected expression'

    left = expr[:implication_position]
    left = from_string_to_expression(left)

    right = expr[implication_position + 1:]
    right = from_string_to_expression(right)

    expression = Implication(left, right)
    return expression


def main():
    axioms = {
        'axiom_4': 'A*B>A',
        'axiom_5': 'A*B>B',
        'axiom_6': 'A>(B>(A*B))',
        'axiom_7': 'A>(A|B)',
        'axiom_8': 'B>(A|B)'
    }

    for name, expr in axioms.items():
        print(f'{name}: {expr}')
        res = preprocessor(expr)
        print(f'converted: {res}')
        res = remove_overbrackets(res)
        print(f'removed too much brackets {res}')
        res = (from_string_to_expression(res))
        print(f'in class representation {res}')
        print('-' * 10)


if __name__ == '__main__':
    main()
