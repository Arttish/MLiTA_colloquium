import unittest

from parser import find_bracket_pair, binary_replacer, disjunction, conjunction, remove_overbrackets, preprocessor


class MainTestClass(unittest.TestCase):
    def test_bracket_pairs(self):
        msg = 'bad bracket pair method'
        self.assertEqual(-1, find_bracket_pair(0, '1234'), msg)
        self.assertEqual(-1, find_bracket_pair(0, '(1234'), msg)
        self.assertEqual(-1, find_bracket_pair(2, '12)34'), msg)

        self.assertEqual(5, find_bracket_pair(0, '(1234)'), msg)
        self.assertEqual(7, find_bracket_pair(0, '(1(2)34)'), msg)
        self.assertEqual(0, find_bracket_pair(7, '(1(2)34)'), msg)

        self.assertEqual(4, find_bracket_pair(2, '(1(2)34)'), msg)
        self.assertEqual(2, find_bracket_pair(4, '(1(2)34)'), msg)

        self.assertEqual(1, find_bracket_pair(0, '()(1(2)34)'), msg)
        self.assertEqual(0, find_bracket_pair(1, '()(1(2)34)'), msg)

    def test_disjunction_replacer(self):
        msg = 'something went wrong with disjunction replacer'

        self.assertEqual('(!a>b)', binary_replacer(1, 'a|b', disjunction), msg)
        self.assertEqual('(!a>!b)', binary_replacer(1, 'a|!b', disjunction), msg)
        self.assertEqual('(!(a)>b)', binary_replacer(3, '(a)|b', disjunction), msg)
        self.assertEqual('(!a>(b))', binary_replacer(1, 'a|(b)', disjunction), msg)

        self.assertEqual('(!(a*b)>(b))', binary_replacer(5, '(a*b)|(b)', disjunction), msg)

        self.assertEqual('(!(a*b)>(b))|c', binary_replacer(5, '(a*b)|(b)|c', disjunction), msg)
        self.assertEqual('(a*b)|(!(b)>c)', binary_replacer(9, '(a*b)|(b)|c', disjunction), msg)
        self.assertEqual('(a*b)|(!b>c)|(a*a)', binary_replacer(7, '(a*b)|b|c|(a*a)', disjunction), msg)

    def test_conjunction_replacer(self):
        msg = 'something went wrong with conjunction replacer'

        self.assertEqual('(!(a>!b))', binary_replacer(1, 'a*b', conjunction), msg)
        self.assertEqual('(!((a)>!b))', binary_replacer(3, '(a)*b', conjunction), msg)
        self.assertEqual('(!(a>!(b)))', binary_replacer(1, 'a*(b)', conjunction), msg)

        self.assertEqual('(!((a|b)>!(b)))', binary_replacer(5, '(a|b)*(b)', conjunction), msg)

        self.assertEqual('((!(a>!b)))|(b)|c', binary_replacer(2, '(a*b)|(b)|c', conjunction), msg)
        self.assertEqual('(a*b)|(!((b)>!c))', binary_replacer(9, '(a*b)|(b)*c', conjunction), msg)
        self.assertEqual('(a*b)|(!(b>!c))|(a*a)', binary_replacer(7, '(a*b)|b*c|(a*a)', conjunction), msg)

    def test_remove_overbrackets(self):
        self.assertEqual('a', remove_overbrackets('a'))
        self.assertEqual('a', remove_overbrackets('((a))'))
        self.assertEqual('(a+b)', remove_overbrackets('(a+((b)))'))
        self.assertEqual('(a+b)*(c+d)', remove_overbrackets('((a+b))*(c+d)'))
        self.assertEqual('((a+b)*(c+d))*c', remove_overbrackets('((a+b)*(c+d))*c'))

    @staticmethod
    def test_axioms():
        axiom_4 = 'A*B>A'
        axiom_5 = 'A*B>B'
        axiom_6 = 'A>(B>(A*B))'
        axiom_7 = 'A>(A|B)'
        axiom_8 = 'B>(A|B)'
        axiom_9 = '(A>C)>((B>C)>((A|B)>C))'
        axiom_a = '!A>(A>B)'
        axiom_b = 'A|!A'
        axioms = [axiom_4, axiom_5, axiom_6, axiom_7, axiom_8, axiom_9, axiom_a, axiom_b]

        for axiom in axioms:
            res = preprocessor(axiom)
            print(remove_overbrackets(res))


if __name__ == '__main__':
    unittest.main()
