import argparse
import lp_solver as lp


def parseArg():
    """
    CMD argument parsing
    :return: the parser
    """
    parser = argparse.ArgumentParser(description='Blotto solver.')
    parser.add_argument('file', metavar='fpath', type=str)
    return parser


if __name__ == "__main__":
    args = parseArg().parse_args()
    parser = lp.formula_parser()
    transformer = lp.FormulaTransformer()
    with open(args.file, 'r') as f:
        for line in f:
            line = line.strip()
            if len(line) == 0 or line[0] == '%':
                continue
            par_tree = parser.parse(line)
            print(line)
            print('----')
            formula = transformer.transform(par_tree)
            lp_prob = lp.Opti(formula)
            lp_prob.simplex()
            print('='*80)

