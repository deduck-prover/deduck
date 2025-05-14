"""
Parser and grammar definitions for first-order logic.
"""

from lark import Lark, Transformer

from .utils import InternalError
from .syntax import (
    AST, Var, FVar, Const, Func, Atom, Not, And, Or, 
    Implies, Iff, ForAll, Exists, Sequent
)

grammar = r"""
start: sequent

sequent: premises TURNSTILE formula            -> sequent
  | TURNSTILE formula                          -> sequent_empty

premises: formula ("," formula)*
formulas: formula ("," formula)*
?formula: iff
iff: implies (IFF implies)*                    -> chain_iff
implies: or_expr (IMPLIES implies)?            -> implies
or_expr: and_expr (OR and_expr)*               -> chain_or
and_expr: not_expr (AND not_expr)*             -> chain_and
?not_expr: NOT not_expr                        -> not_
  | quantifier
?quantifier: ("∀" | "forall") NAME formula     -> forall
  | ("∃" | "exists") NAME formula              -> exists
  | atom
?atom: NAME "(" term_list ")"                  -> atom_with_args
  | NAME                                       -> atom_no_args
  | "(" formula ")"
  | term ("=" | "≈") term                      -> equality
term_list: term ("," term)*
?term: sum
?sum: sum "+" product                          -> plus
  | product
?product: product "*" factor                   -> times
  | factor
?factor: FVAR                                  -> fvar
  | "0"                                        -> zero
  | NAME "(" term_list ")"                     -> func
  | NAME                                       -> const_or_var
  | "(" sum "+" product ")"                    -> plus
  | "(" product ("*" | "·") factor ")"         -> times

%import common.CNAME -> NAME
%import common.WS
%ignore WS

IFF: "<->" | "↔"
IMPLIES: "->" | "→"
AND: "/\\" | "∧"
OR: "\\/" | "∨"
NOT: "~" | "¬"
TURNSTILE: "⊢" | "|-"
FVAR: "`" NAME
# NAME.-1: /[A-Za-z_][A-Za-z0-9_]*/
"""

class ASTBuilder(Transformer):
    def sequent(self, items):
        premises, _, conclusion = items
        return Sequent(premises, conclusion)
    def sequent_empty(self, items):
        _, conclusion = items
        return Sequent([], conclusion)
    def premises(self, items):
        return list(items)
    def formulas(self, items):
        return list(items)
    def chain_iff(self, items):
        left = items[0]
        for i in range(2, len(items), 2):
            right = items[i]
            left = Iff(left, right)
        return left
    def implies(self, items):
        if len(items) == 3:
            return Implies(items[0], items[2])
        return items[0]
    def chain_or(self, items):
        left = items[0]
        for i in range(2, len(items), 2):
            right = items[i]
            left = Or(left, right)
        return left
    def chain_and(self, items):
        left = items[0]
        for i in range(2, len(items), 2):
            right = items[i]
            left = And(left, right)
        return left
    def not_(self, items):
        return Not(items[1])
    def forall(self, items):
        varname = items[0].value
        return ForAll(varname, items[1])
    def exists(self, items):
        varname = items[0].value
        return Exists(varname, items[1])
    def atom_with_args(self, items):
        name = items[0].value
        return Atom(name, items[1])
    def atom_no_args(self, items):
        return Atom(items[0].value, [])
    def equality(self, items):
        left, right = items
        return Atom("≈", [left, right])
    def term_list(self, items):
        return list(items)
    def plus(self, items):
        left, right = items
        return Func("+", [left, right])
    def times(self, items):
        left, right = items
        return Func("·", [left, right])
    def fvar(self, items):
        return FVar(items[0].value[1:])
    def func(self, items):
        name = items[0].value
        args = items[1]
        return Func(name, args)
    def const_or_var(self, items):
        name = items[0].value
        return Const(name)
    def zero(self, items):
        return Const("0")

lark_parser_sequent = Lark(grammar, start="sequent", parser="lalr", propagate_positions=True)
lark_parser_formula = Lark(grammar, start="formula", parser="lalr", propagate_positions=True)
lark_parser_formulas = Lark(grammar, start="formulas", parser="lalr", propagate_positions=True)
lark_parser_term = Lark(grammar, start="term", parser="lalr", propagate_positions=True)

# Disambiguate Const nodes shadowed by quantifier-bound variables
def disambiguate_consts(node: AST, bound=None):
    """
    Transform AST by tracking variables bound by quantifiers and
    convert Const nodes with the same name as a bound variable to Var.
    """
    if bound is None:
        bound = set()
    # Leaf nodes
    if isinstance(node, Var):
        return Var(node.name)
    if isinstance(node, FVar):
        return FVar(node.name)
    if isinstance(node, Const):
        if node.name in bound:
            return Var(node.name)
        return Const(node.name)
    # Composite nodes
    if isinstance(node, Func):
        return Func(node.name, [disambiguate_consts(arg, bound) for arg in node.args])
    if isinstance(node, Atom):
        return Atom(node.name, [disambiguate_consts(arg, bound) for arg in node.args])
    if isinstance(node, Not):
        return Not(disambiguate_consts(node.formula, bound))
    if isinstance(node, And):
        return And(
            disambiguate_consts(node.left, bound),
            disambiguate_consts(node.right, bound)
        )
    if isinstance(node, Or):
        return Or(
            disambiguate_consts(node.left, bound),
            disambiguate_consts(node.right, bound)
        )
    if isinstance(node, Implies):
        return Implies(
            disambiguate_consts(node.left, bound),
            disambiguate_consts(node.right, bound)
        )
    if isinstance(node, Iff):
        return Iff(
            disambiguate_consts(node.left, bound),
            disambiguate_consts(node.right, bound)
        )
    if isinstance(node, ForAll):
        new_bound = bound | {node.var}
        return ForAll(node.var, disambiguate_consts(node.formula, new_bound))
    if isinstance(node, Exists):
        new_bound = bound | {node.var}
        return Exists(node.var, disambiguate_consts(node.formula, new_bound))
    if isinstance(node, Sequent):
        new_premises = [disambiguate_consts(p, bound) for p in node.premises]
        new_conclusion = disambiguate_consts(node.conclusion, bound)
        return Sequent(new_premises, new_conclusion)
    raise InternalError(f"Unsupported node type: {type(node)}")

class Parser:
    def __init__(self, text):
        self.text = text
    def parse_sequent(self):
        tree = lark_parser_sequent.parse(self.text)
        s = ASTBuilder().transform(tree)
        return disambiguate_consts(s)
    def parse_formula_only(self):
        tree = lark_parser_formula.parse(self.text, start='formula')
        f = ASTBuilder().transform(tree)
        return disambiguate_consts(f)
    def parse_formulas_only(self):
        tree = lark_parser_formulas.parse(self.text, start='formulas')
        fs = ASTBuilder().transform(tree)
        return [disambiguate_consts(f) for f in fs]
    def parse_term_only(self):
        tree = lark_parser_term.parse(self.text, start='term')
        return ASTBuilder().transform(tree)
