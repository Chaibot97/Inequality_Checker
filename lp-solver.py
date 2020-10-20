from lark import Lark

def formula_parser():
	grammar = """
	formula : "AND" "(" atom ("," atom)* ")"
	atom : term operator term
	operator : OP
	term : term arith term 
		| term arith term 
		| c arith VAR
		| c 
		| VAR
	arith : ARITH
	?c : SIGNED_NUMBER


	ARITH : "+" | "-"| "*"
	OP :  ">=" | "<=" | "<" | ">"
	VAR : /[a-zA-Z][a-zA-Z0-9]*/

	%import common.SIGNED_NUMBER
	%import common.WS
	%ignore WS
	"""

	return Lark(grammar,start = "formula")

if __name__ == "__main__":
	parser = formula_parser()
	formula = "AND(x >= 1, 2 * x3 <= 1)"
	print(parser.parse(formula).pretty())