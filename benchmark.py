#!/usr/bin/env python3
import argparse
import lp_solver as lp


def parseArg():
    """
    CMD argument parsing
    :return: the parser
    """
    parser = argparse.ArgumentParser(description='Simplex Benchmarking')
    parser.add_argument('file', metavar='fpath', type=str)
    return parser


if __name__ == "__main__":
    args = parseArg().parse_args()
    parser = lp.formula_parser()
    transformer = lp.FormulaTransformer()
    with open(args.file, 'r') as f:
        case = []
        for line in f:
            line = line.strip()
            if len(line) == 0 or line[0] == '%':
                continue
            case.append(line)
            if len(case) == 2:
                formula, expected = case
                print(formula)
                res = lp.run(formula)
                print(res)
                if 'UNSAT' in expected and 'UNSAT' in res or \
                    'UNSAT' not in expected and 'UNSAT' not in res:
                    print("Passed")
                else:
                    print("Failed. Expected:", expected)
                case = []
                print('='*80)

