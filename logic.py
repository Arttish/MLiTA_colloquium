from copy import copy
from time import perf_counter


def remove_duplicates(lst: list):
    return list(set(lst))


class Variable:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name

    def substitute(self, var, expr):
        if var == self:
            return expr
        return self

    def to_implication(self):
        return Implication(Negation(self), zero)

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self)


zero = Variable(0)


class Expression:
    def __init__(self, left, right):
        if isinstance(left, str):
            left = Variable(left)
        if isinstance(right, str):
            right = Variable(right)
        self.left = left
        self.right = right
        self.symbol = '#'

    def substitute(self, var, expr, inplace=True):
        if inplace:
            if self.left is not None:
                self.left = self.left.substitute(var, expr)
            if self.right is not None:
                self.right = self.right.substitute(var, expr)
            return self

        res = copy(self)
        return res.substitute(var, expr)

    def __eq__(self, other):
        return (isinstance(other, Expression)
                and self.left == other.left
                and self.right == other.right
                and self.symbol == other.symbol)

    def __str__(self):
        return f"({str(self.left)}{self.symbol}{str(self.right)})"

    def __hash__(self):
        return hash(self.__str__())

    def __repr__(self):
        return str(self)


class Implication(Expression):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.symbol = '>'


class Conjunction(Expression):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.symbol = '*'

    def to_implication(self):
        return Negation(Implication(self.left, Negation(self.right)))


class Negation(Expression):
    def __init__(self, left):
        super().__init__(left, None)

    def __str__(self):
        return f'!({str(self.left)})'

    def to_implication(self):
        return Implication(self.left, zero)


class Disjunction(Expression):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.symbol = '+'

    def to_implication(self):
        return Implication(Negation(self.left), self.right)


def kill_double_negation(expression):
    if isinstance(expression, Variable):
        return expression
    if isinstance(expression, Negation) and isinstance(expression.left, Negation):
        expression = expression.left.left
        expression = kill_double_negation(expression)
        return expression
    if expression.left is not None and isinstance(expression.left, Expression):
        expression.left = kill_double_negation(expression.left)
    if expression.right is not None and isinstance(expression.right, Expression):
        expression.right = kill_double_negation(expression.right)
    return expression


def deduce(expression):
    res = []
    if isinstance(expression, Conjunction) or isinstance(expression, Disjunction):
        expression = expression.to_implication()
    if isinstance(expression, Negation) and isinstance(expression.left, Implication):
        expression = expression.to_implication()
    while isinstance(expression, Implication):
        res.append(expression.left)
        expression = expression.right
        if isinstance(expression, Conjunction) or isinstance(expression, Disjunction):
            expression = expression.to_implication()
        if isinstance(expression, Negation) and isinstance(expression.left, Implication):
            expression = expression.to_implication()

    i = 0
    while i < len(res):
        if isinstance(res[i], Disjunction):
            res[i] = res[i].to_implication()
        if isinstance(res[i], Conjunction):
            res[i] = res[i].to_implication()
        if isinstance(res[i], Negation) and isinstance(res[i].left, Implication):
            if expression != zero:
                expression = expression.to_implication()
                res.append(expression.left)
            expression = res[i].left.right
            res[i] = res[i].left.left

            continue
        i += 1

    return remove_duplicates(res), expression


def modus_ponens(expressions: list, requirement):
    expressions.append(Negation(requirement))
    i = 0

    while i < len(expressions):
        j = i + 1
        while j < len(expressions):
            if (isinstance(expressions[j], Implication)
                    and expressions[i] == expressions[j].left
                    and expressions[j].right not in expressions):
                expressions.append(expressions[j].right)
            if (isinstance(expressions[i], Implication)
                    and expressions[j] == expressions[i].left
                    and expressions[i].right not in expressions):
                expressions.append(expressions[i].right)
            j += 1
        i += 1
        # expressions = remove_duplicates(expressions)
    expressions.remove(Negation(requirement))
    return remove_duplicates(expressions)


def modus_tollens(expressions: list, requirement):
    expressions.append(Negation(requirement))
    i = 0
    while i < len(expressions):
        j = i + 1
        while j < len(expressions):
            if (isinstance(expressions[j], Implication)
                    and kill_double_negation(Negation(expressions[i])) == expressions[j].right
                    and kill_double_negation(Negation(expressions[j].left)) not in expressions):
                expressions.append(kill_double_negation(Negation(expressions[j].left)))
            if (isinstance(expressions[i], Implication)
                    and kill_double_negation(Negation(expressions[j])) == expressions[i].right
                    and kill_double_negation(Negation(expressions[i].left)) not in expressions):
                expressions.append(kill_double_negation(Negation(expressions[i].left)))
            j += 1
        i += 1
    expressions.remove(Negation(requirement))
    return remove_duplicates(expressions)


def axiom1(expressions: list, requirement):
    A = Variable('replace')
    B = requirement
    not_B = kill_double_negation(Negation(requirement))
    ax1 = Implication(B, A)
    ax2 = Implication(not_B, A)
    for i in range(len(expressions)):
        expressions.append(ax1.substitute(A, expressions[i], False))
        expressions.append(ax2.substitute(A, expressions[i], False))
    return remove_duplicates(expressions)


def axiom3(expressions: list):
    for i in range(len(expressions)):
        if not isinstance(expressions[i], Implication):
            continue
        for j in range(i + 1, len(expressions)):
            if (
                    not isinstance(expressions[j], Implication)
                    or expressions[j].left != expressions[i].left
                    or not (
                    isinstance(expressions[i].right, Negation)
                    and expressions[j].right == expressions[i].right.left
                    or isinstance(expressions[j].right, Negation)
                    and expressions[i].right == expressions[j].right.left
            )
            ):
                continue
            expressions.append(kill_double_negation(Negation(expressions[j].left)))
    return remove_duplicates(expressions)


def axiom10(expressions: list, requirement):
    for i in range(len(expressions)):
        for j in range(i + 1, len(expressions)):
            if expressions[i] == kill_double_negation(Negation(expressions[j])):
                expressions.append(requirement)
                return remove_duplicates(expressions)
    return expressions


def preproof():
    # A10: !A -> (A -> B) ~~~ !A, A |- B
    A = Variable('A')
    B = Variable('B')
    expr = Implication(Negation(A), Implication(A, B))
    print(expr)
    expressions, req = deduce(expr)
    axiom1(expressions, req)
    print(expressions)
    axiom3(expressions)
    print(expressions)

    if req in expressions:
        print("Axiom 10 is proved")

    # modus tollens
    expressions = [Implication(A, B), Negation(B)]
    req = Negation(A)

    print(*expressions, '|-', req)

    axiom1(expressions, req)
    print(expressions)
    axiom3(expressions)
    print(expressions)

    if req in expressions:
        print("Modus tollens is proved")



def proof(expression):
    expressions, exp = deduce(expression)
    time_limit = 2
    start = perf_counter()
    while time_limit > 0:
        axiom1(expressions, exp)
        print(expressions)
        axiom3(expressions)
        print(expressions)
        modus_ponens(expressions, exp)
        print(expressions)
        modus_tollens(expressions, exp)
        print(expressions)
        axiom10(expressions, exp)
        print(expressions)
        if exp in expressions:
            print("Expression is proved")
            return True
        time_limit -= perf_counter() - start
    print("Expression is not proved")
    return False


if __name__ == "__main__":
    A = Variable("A")
    B = Variable("B")
    C = Variable('C')
    e = [Implication(A, C), Implication(B, C), Negation(C)]
    modus_tollens(e, zero)
    print(e)
