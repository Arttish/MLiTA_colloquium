from parser import preprocessor, remove_overbrackets, from_string_to_expression
from logic import proof
from time import perf_counter


def get_time(res):
    start = perf_counter()
    proof(res)
    time = perf_counter() - start
    return time


if __name__ == '__main__':
    axioms = {
        'axiom_4': 'A*B>A',
        'axiom_5': 'A*B>B',
        'axiom_6': 'A>(B>(A*B))',
        'axiom_7': 'A>(A|B)',
        'axiom_8': 'B>(A|B)',
        'axiom_9': '(A>C)>((B>C)>((A|B)>C))',
        'axiom_10': '!A>(A>B)',
        'axiom_11': 'A|!A',
        'team 8': "(A>A)>((A>B)>(A>B))",
        'team 14': '((!(A>(B>c))>!((A>B)>(A>c)))>((!(A>(B>A))>((A>B)>(A>B)))))',
        'team 15': '(((A>(B>(A>(B>A))))>(B>c))>((A>(B>(B>(B>B))))>(A>(B>(c>(B>(c>c)))))))>((B>B)>(((A>(B>(A>('
                   'B>A))))>(B>c))>((A>(B>(B>(B>B))))>(A>(B>(c>(B>(c>c))))))))',
        'team 18': '(A>B)>((B>C)>(A>B))'
    }

    for name, expr in axioms.items():
        res = preprocessor(expr)
        res = remove_overbrackets(res)
        res = (from_string_to_expression(res))
        print(res)
        print(get_time(res))
