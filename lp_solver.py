from lark import Lark, Transformer
from fractions import Fraction

# parser
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


# transformer for parser (to Object)
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
        return args[0] - args[1]

    def plus(self, args):
        return args[0] + args[1]

    def atom(self, args):
        return Atom(args[0], args[2], args[1])

    def formula(self, args):
        return Formula(args)


# define a LP problem
class Opti:
    def __init__(self, formula, obj_fun):
        self.obj_fun = obj_fun
        self.formula = formula
        self.vars = {}
        for x in sorted(formula.get_vars()):
            self.vars[x] = x
        self.value = 'v'

    def __str__(self):
        vertices = ', '.join([str(self.vars[k]) for k in sorted(self.vars.keys())])
        return 'OPT({}, {}, ({}), {})'.format(self.obj_fun, self.formula, vertices, self.value)

    def evaluate(self):
        atoms = self.formula.atoms
        for a in atoms:
            nb = a.non_basic()
            b = list(a.basic())[0]
            for x in nb:
                self.vars[x] = 0
            self.vars[b] = a.evaluate(self.vars)
        self.value = self.obj_fun.evaluate(self.vars)

    def simplex(self):
        self.simplex_auxiliary()
        if self.value == 0:
            for x in self.formula.targets:
                x_f, x_ff = x + '_f', x + '_ff'
                new_term = Term(1, x_f) - Term(1, x_ff)
                print('{}={}'.format(x, new_term.evaluate(self.vars)))
        else:
            print('UNSAT')

    def simplex_auxiliary(self):
        # auxiliary step
        x = 'x0'
        atoms = self.formula.atoms
        min_index = -1
        min_constrain = float('inf')
        for i, a in enumerate(atoms):
            cons = a.constrain(x)
            if cons < min_constrain:
                min_index = i
                min_constrain = cons

        # basic solution feasible
        if min_constrain > 0:
            self.evaluate()
            print(self)
            return

        tmp = atoms[min_index].represent(x)
        for i, _ in enumerate(atoms):
            if i != min_index:
                atoms[i].substitute(x, tmp)
        self.obj_fun.substitute(x, tmp)

        self.simplex_recursive()

    def simplex_recursive(self):
        self.evaluate()
        print(self)
        pos_terms = self.obj_fun.get_positive_terms()
        if len(pos_terms) == 0:
            return

        atoms = self.formula.atoms
        for x in pos_terms:
            min_index = -1
            min_constrain = float('inf')
            for i, a in enumerate(atoms):
                cons = -a.constrain(x)
                if 0 < cons < min_constrain:
                    min_index = i
                    min_constrain = cons

            if min_index != -1:
                tmp = atoms[min_index].represent(x)
                for i in range(len(atoms)):
                    if i != min_index:
                     atoms[i].substitute(x, tmp)
                self.obj_fun.substitute(x, tmp)

                self.simplex_recursive()


class Formula:
    def __init__(self, atoms):
        self.atoms = []
        targets = set()
        for i, a in enumerate(atoms):
            a.clear_negation()
            a.to_slack(i+1)
            self.atoms.append(a)
            targets = targets.union(a.targets)

        # list of original vars in the input
        self.targets = {}
        for t in targets:
            self.targets[t] = Term(1, t)

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
        self.targets = self.get_vars()

    def non_basic(self):
        return self.tr.get_vars()

    def basic(self):
        return self.tl.get_vars()

    def evaluate(self, vars):
        return self.tr.evaluate(vars)

    def represent(self, var):
        old_coeff = self.tr.remove(var)
        self.tr -= self.tl
        self.tr.mul(-old_coeff)
        self.tl = Term(1, var)
        return self.tr

    def substitute(self, old, new):
        self.tr.substitute(old, new)

    def constrain(self, var):
        return self.tr.constrain(var)

    def get_vars(self):
        result = set()
        result = result.union(self.tl.get_vars())
        result = result.union(self.tr.get_vars())
        return result

    def clear_negation(self):
        for x in sorted(self.targets):
            x_f, x_ff = x+'_f', x+'_ff'
            new_term = Term(1, x_f) - Term(1, x_ff)
            self.tl.substitute(x, new_term)
            self.tr.substitute(x, new_term)

    def to_slack(self, index):
        # index of the slack var
        if self.op == '=':
            return
        slack = Term(1, 's' + str(index))
        if self.op == '<=':
            self.tr = self.tr - self.tl
            self.tl = slack
        elif self.op == '>=':
            self.tr = self.tl - self.tr
            self.tl = slack

        # TODO: add cases for < and  >
        self.tr += Term(1, 'x0')
        self.op = '='

    def __str__(self):
        return '{} {} {}'.format(str(self.tl), self.op, str(self.tr))


class Term:
    def __init__(self, coeff=0, var='1'):
        coeff = Fraction(coeff)
        var = str(var)
        self.vars = {}
        self.c = 0
        if var == '1':
            self.c = coeff
        else:
            self.vars[var] = coeff

    def constrain(self, var):
        if var not in self.vars:
            return float('inf')
        return self.c / self.vars[var]

    def remove(self, var):
        # remove a term and return its coefficient
        coeff = self.vars[var]
        self.vars.pop(var)
        return coeff

    def get_positive_terms(self):
        return [v for v in self.vars if self.vars[v] > 0]

    def get_vars(self):
        return set(self.vars.keys())

    def evaluate(self, vars):
        # vars and corresponding values
        sum = self.c
        for x in self.vars:
            sum += self.vars[x] * vars[x]
        return sum

    def substitute(self, old, new):
        """
        :param old: old var string
        :param new: new term
        """
        if old not in self.vars:
            return
        old_coeff = self.vars[old]
        self.vars.pop(old)
        tmp = self + new.mul(old_coeff)
        self.vars = tmp.vars
        self.c = tmp.c

    def mul(self, c):
        # modifier
        self.c *= c
        for v in self.vars:
            self.vars[v] *= c
        return self

    def __add__(self, o):
        tmp = Term()
        tmp.vars = self.vars.copy()
        tmp.c = self.c + o.c
        for v in o.vars:
            if v in tmp.vars:
                tmp.vars[v] += o.vars[v]
            else:
                tmp.vars[v] = o.vars[v]
        return tmp

    def __sub__(self, o):
        tmp = Term()
        tmp.vars = self.vars.copy()
        tmp.c = self.c - o.c
        for v in o.vars:
            if v in tmp.vars:
                tmp.vars[v] -= o.vars[v]
            else:
                tmp.vars[v] = -o.vars[v]
        return tmp

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
            elif coeff != 0:
                string += '{} * {} + '.format(str(coeff), v)
        return string[:-3]


if __name__ == "__main__":
    inp = "AND(x >= 1, -2/3 * x <= 1)"
    inp = "AND(x <= 2)"
    # inp = input()

    parser = formula_parser()
    par_tree = parser.parse(inp)
    formula = FormulaTransformer().transform(par_tree)
    lp = Opti(formula, Term(-1, 'x0'))
    print(lp)
    lp.simplex()
