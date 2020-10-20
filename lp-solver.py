from lark import Lark, Transformer
from fractions import Fraction


def formula_parser():
    grammar = """
        formula : "AND" "(" atom ("," atom)* ")" -> formula
        atom : term OP term   -> atom
        term : term "+" term        -> plus
            | term "-" term         -> minus
            | RATIONAL "*" VAR      -> times
            | RATIONAL              -> number
            | VAR                   -> var

        RATIONAL : SIGNED_NUMBER ["/" NUMBER]
        OP :  ">=" | "<=" | "<" | ">"
        VAR : /[a-zA-Z][a-zA-Z0-9]*/

        %import common.SIGNED_NUMBER
        %import common.NUMBER
        %import common.WS
        %ignore WS
        """

    return Lark(grammar, start="formula")


class FormulaTransformer(Transformer):
    def number(self, n):
        (n,) = n
        return Term(n, 1)

    def var(self, x):
        (x,) = x
        return Term(1, x)

    def times(self, args):
        return Term(args[0], args[1])

    def minus(self, args):
        return args[0] + args[1]

    def plus(self, args):
        return args[0] - args[1]

    def atom(self, args):
        return Atom(args[0], args[2], args[1])

    def formula(self, args):
        return Formula(args)


class Opti:
    def __init__(self, formula):
        self.target = Term(-1, 'x0')
        self.formula = formula
        self.vars = list(formula.get_vars())
        self.values = self.vars
        self.value = 'v'

    def __str__(self):
        return 'OPT({}, {}, {}, {})'.format(self.target, self.formula, tuple(self.vars), self.value)


class Formula:
    def __init__(self, atoms):
        self.atoms = [a for a in atoms]

    def get_vars(self):
        result = set()
        for a in self.atoms:
            result = result.union(a.get_vars())
        return result

    def __str__(self):
        string = 'AND('
        for a in self.atoms:
            string += '{},'.format(a)
        string = string[:-1] + ')'
        return string


class Atom:
    def __init__(self, tl, tr, op):
        self.tl = tl
        self.tr = tr
        self.op = op

    def get_vars(self):
        result = set()
        result = result.union(self.tl.get_vars())
        result = result.union(self.tr.get_vars())
        return result

    def __str__(self):
        return '{} {} {}'.format(str(self.tl), self.op, str(self.tr))


class Term:
    def __init__(self, coeff, var):
        coeff = Fraction(coeff)
        var = str(var)
        self.vars = {}
        self.c = 0
        if var == '1':
            self.c = coeff
        else:
            self.vars[var] = coeff

    def get_vars(self):
        return set(self.vars.keys())

    def __add__(self, o):
        for v in o.vars:
            if v in self.vars:
                self.vars[v] += o.vars[v]
            else:
                self.vars[v] = o.vars[v]

    def __sub__(self, o):
        for v in o.vars:
            if v in self.vars:
                self.vars[v] -= o.vars[v]
            else:
                self.vars[v] = -o.vars[v]

    def __str__(self):
        string = ""
        if self.c != 0:
            string += str(self.c) + ' + '
        for v in sorted(self.vars):
            coeff = self.vars[v]
            if coeff == 1:
                string += '{} + '.format(v)
            elif coeff == -1:
                string += '-{} + '.format(v)
            else:
                string += '{} * {} + '.format(str(coeff), v)
        return string[:-3]


if __name__ == "__main__":
    inp = "AND(x >= 1, -2/3 * x <= 1)"
    # inp = input()

    parser = formula_parser()
    par_tree = parser.parse(inp)
    formula = FormulaTransformer().transform(par_tree)
    print(Opti(formula))
