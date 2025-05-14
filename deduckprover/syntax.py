"""
AST (Abstract Syntax Tree) node definitions and core operations for first-order logic formulas.
"""

from .utils import InternalError

class AST:
    def __str__(self):
        return pretty(self, paren=False)
    def ascii(self):
        return '\n'.join(_ascii_tree(self, '', True))
    def __eq__(self, other):
        """
        Alpha-equivalence: equality up to renaming of bound variables.
        """
        return _alpha_eq(self, other, {}, {})
    def __hash__(self):
        """
        Hash based on alpha-equivalence canonical structure.
        """
        def canon(node, env, counter):
            # leaf nodes
            if isinstance(node, Var):
                if node.name in env:
                    return ('Bound', env[node.name]), counter
                else:
                    return ('Var', node.name), counter
            if isinstance(node, FVar):
                return ('FVar', node.name), counter
            if isinstance(node, Const):
                return ('Const', node.name), counter
            # composite nodes
            if isinstance(node, Func):
                items, cnt = [], counter
                for arg in node.args:
                    rep, cnt = canon(arg, env, cnt)
                    items.append(rep)
                return ('Func', node.name, tuple(items)), cnt
            if isinstance(node, Atom):
                items, cnt = [], counter
                for arg in node.args:
                    rep, cnt = canon(arg, env, cnt)
                    items.append(rep)
                return ('Atom', node.name, tuple(items)), cnt
            if isinstance(node, Not):
                rep, cnt = canon(node.formula, env, counter)
                return ('Not', rep), cnt
            if isinstance(node, And):
                rep_l, cnt1 = canon(node.left, env, counter)
                rep_r, cnt2 = canon(node.right, env, cnt1)
                return ('And', rep_l, rep_r), cnt2
            if isinstance(node, Or):
                rep_l, cnt1 = canon(node.left, env, counter)
                rep_r, cnt2 = canon(node.right, env, cnt1)
                return ('Or', rep_l, rep_r), cnt2
            if isinstance(node, Implies):
                rep_l, cnt1 = canon(node.left, env, counter)
                rep_r, cnt2 = canon(node.right, env, cnt1)
                return ('Implies', rep_l, rep_r), cnt2
            if isinstance(node, Iff):
                rep_l, cnt1 = canon(node.left, env, counter)
                rep_r, cnt2 = canon(node.right, env, cnt1)
                return ('Iff', rep_l, rep_r), cnt2
            if isinstance(node, ForAll):
                id = counter
                new_env = env.copy()
                new_env[node.var] = id
                rep, cnt2 = canon(node.formula, new_env, counter+1)
                return ('ForAll', id, rep), cnt2
            if isinstance(node, Exists):
                id = counter
                new_env = env.copy()
                new_env[node.var] = id
                rep, cnt2 = canon(node.formula, new_env, counter+1)
                return ('Exists', id, rep), cnt2
            if isinstance(node, Sequent):
                premises = []
                for p in node.premises:
                    rep, _ = canon(p, {}, 0)
                    premises.append(rep)
                rep, _ = canon(node.conclusion, {}, 0)
                return ('Sequent', tuple(premises), rep), 0
            raise InternalError(f"Unsupported node type: {type(node)}")

        rep, _ = canon(self, {}, 0)
        return hash(rep)

class Var(AST):
    def __init__(self, name): self.name = name
    def __repr__(self): return f"Var({self.name})"

class FVar(AST):
    def __init__(self, name): self.name = name
    def __repr__(self): return f"FVar({self.name})"

class Const(AST):
    def __init__(self, name): self.name = name
    def __repr__(self): return f"Const({self.name})"

class Func(AST):
    def __init__(self, name, args): self.name = name; self.args = args
    def __repr__(self): return f"Func({self.name}, {self.args})"

class Atom(AST):
    def __init__(self, name, args): self.name = name; self.args = args
    def __repr__(self): return f"Atom({self.name}, {self.args})"

class Not(AST):
    def __init__(self, formula): self.formula = formula
    def __repr__(self): return f"Not({self.formula})"

class And(AST):
    def __init__(self, left, right): self.left = left; self.right = right
    def __repr__(self): return f"And({self.left}, {self.right})"

class Or(AST):
    def __init__(self, left, right): self.left = left; self.right = right
    def __repr__(self): return f"Or({self.left}, {self.right})"

class Implies(AST):
    def __init__(self, left, right): self.left = left; self.right = right
    def __repr__(self): return f"Implies({self.left}, {self.right})"

class Iff(AST):
    def __init__(self, left, right): self.left = left; self.right = right
    def __repr__(self): return f"Iff({self.left}, {self.right})"

class ForAll(AST):
    def __init__(self, var, formula): self.var = var; self.formula = formula
    def __repr__(self): return f"ForAll({self.var}, {self.formula})"

class Exists(AST):
    def __init__(self, var, formula): self.var = var; self.formula = formula
    def __repr__(self): return f"Exists({self.var}, {self.formula})"

class Sequent(AST):
    def __init__(self, premises, conclusion):
        self.premises = frozenset(premises)
        self.conclusion = conclusion
    def __repr__(self):
        return f"Sequent({self.premises}, {self.conclusion})"

def subst_var(node, subst):
    """
    Substitute bound variables (Var) in an AST according to subst mapping.
    subst: dict mapping bound variable names (str) to AST nodes.
    Returns a new AST with substitutions applied.
    """
    # Bound variable substitution
    if isinstance(node, Var):
        if node.name in subst:
            return subst[node.name]
        else:
            return Var(node.name)
    # Free variables and constants remain unchanged
    if isinstance(node, FVar):
        return node
    if isinstance(node, Const):
        return node
    # Recursive cases for composite nodes
    if isinstance(node, Func):
        return Func(node.name, [subst_var(arg, subst) for arg in node.args])
    if isinstance(node, Atom):
        return Atom(node.name, [subst_var(arg, subst) for arg in node.args])
    if isinstance(node, Not):
        return Not(subst_var(node.formula, subst))
    if isinstance(node, And):
        return And(subst_var(node.left, subst), subst_var(node.right, subst))
    if isinstance(node, Or):
        return Or(subst_var(node.left, subst), subst_var(node.right, subst))
    if isinstance(node, Implies):
        return Implies(subst_var(node.left, subst), subst_var(node.right, subst))
    if isinstance(node, Iff):
        return Iff(subst_var(node.left, subst), subst_var(node.right, subst))
    if isinstance(node, ForAll):
        # Capture avoidance
        new_subst = {k: v for k, v in subst.items() if k != node.var}
        return ForAll(node.var, subst_var(node.formula, new_subst))
    if isinstance(node, Exists):
        # Capture avoidance
        new_subst = {k: v for k, v in subst.items() if k != node.var}
        return Exists(node.var, subst_var(node.formula, new_subst))
    if isinstance(node, Sequent):
        new_premises = [subst_var(p, subst) for p in node.premises]
        new_conclusion = subst_var(node.conclusion, subst)
        return Sequent(new_premises, new_conclusion)
    raise InternalError(f"Unsupported node type: {type(node)}")

def subst_fvar(node, subst):
    """
    Substitute free variables (FVar) in an AST according to subst mapping.
    subst: dict mapping free variable names (str) to AST nodes.
    Returns a new AST with substitutions applied.
    """
    # Free variable substitution
    if isinstance(node, FVar):
        if node.name in subst:
            return subst[node.name]
        else:
            return FVar(node.name)
    # Bound variables and constants remain unchanged
    if isinstance(node, Var):
        return Var(node.name)
    if isinstance(node, Const):
        return Const(node.name)
    # Recursive cases for composite nodes
    if isinstance(node, Func):
        return Func(node.name, [subst_fvar(arg, subst) for arg in node.args])
    if isinstance(node, Atom):
        return Atom(node.name, [subst_fvar(arg, subst) for arg in node.args])
    if isinstance(node, Not):
        return Not(subst_fvar(node.formula, subst))
    if isinstance(node, And):
        return And(subst_fvar(node.left, subst), subst_fvar(node.right, subst))
    if isinstance(node, Or):
        return Or(subst_fvar(node.left, subst), subst_fvar(node.right, subst))
    if isinstance(node, Implies):
        return Implies(subst_fvar(node.left, subst), subst_fvar(node.right, subst))
    if isinstance(node, Iff):
        return Iff(subst_fvar(node.left, subst), subst_fvar(node.right, subst))
    # Quantifiers
    if isinstance(node, ForAll):
        return ForAll(node.var, subst_fvar(node.formula, subst))
    if isinstance(node, Exists):
        return Exists(node.var, subst_fvar(node.formula, subst))
    # Sequent: substitute in each premise and the conclusion
    if isinstance(node, Sequent):
        return Sequent(
            [subst_fvar(p, subst) for p in node.premises],
            subst_fvar(node.conclusion, subst)
        )
    raise InternalError(f"Unsupported node type: {type(node)}")

# pretty-printing for AST nodes
# Optional argument 'paren' is a boolean that controls whether to parenthesize the output
def pretty(node: AST, paren: bool = True):
    # basic nodes
    if isinstance(node, (Var, Const)):
        return node.name
    if isinstance(node, FVar):
        return '`' + node.name
    if isinstance(node, Func):
        args = ', '.join(pretty(arg) for arg in node.args)
        if node.name == "+":
            return f"({pretty(node.args[0])} + {pretty(node.args[1])})"
        elif node.name == "·":
            return f"({pretty(node.args[0])} · {pretty(node.args[1])})"
        else:
            return f"{node.name}({args})"
    if isinstance(node, Atom):
        if node.args:
            if node.name == "≈":
                s = f"{pretty(node.args[0])} ≈ {pretty(node.args[1])}"
                return f"({s})" if paren else s
            else: 
                args = ', '.join(pretty(arg) for arg in node.args)
                return f"{node.name}({args})"
        else:
            return node.name
    # logical connectives
    if isinstance(node, Not):
        s = f"¬{pretty(node.formula)}"
        return f"({s})" if paren else s
    if isinstance(node, And):
        s = f"{pretty(node.left)} ∧ {pretty(node.right)}"
        return f"({s})" if paren else s
    if isinstance(node, Or):
        s = f"{pretty(node.left)} ∨ {pretty(node.right)}"
        return f"({s})" if paren else s
    if isinstance(node, Implies):
        s = f"{pretty(node.left)} → {pretty(node.right)}"
        return f"({s})" if paren else s
    if isinstance(node, Iff):
        s = f"{pretty(node.left)} ↔ {pretty(node.right)}"
        return f"({s})" if paren else s
    # quantifiers
    if isinstance(node, ForAll):
        return f"∀{node.var} {pretty(node.formula)}"
    if isinstance(node, Exists):
        return f"∃{node.var} {pretty(node.formula)}"
    # sequents
    if isinstance(node, Sequent):
        premises = pretty_formulas(node.premises)
        return f"{premises} ⊢ {pretty(node.conclusion, paren=False)}"
    raise InternalError(f"Unsupported node type: {type(node)}")

# Pretty-printing a list/set of formulas
def pretty_formulas(formulas):
    if formulas:
        return ', '.join(pretty(f, paren=False) for f in formulas)
    else:
        return ''

# Alpha-equivalence helper
def _alpha_eq(node1, node2, env, inv_env):
    # Check that types match
    if type(node1) is not type(node2):
        return False
    # Bound variable (alpha-renaming)
    if isinstance(node1, Var):
        name1, name2 = node1.name, node2.name
        if name1 in env:
            return env[name1] == name2
        if name2 in inv_env:
            return False
        env[name1] = name2
        inv_env[name2] = name1
        return True
    # Free variable
    if isinstance(node1, FVar):
        return isinstance(node2, FVar) and node1.name == node2.name
    # Constant
    if isinstance(node1, Const):
        return node1.name == node2.name
    # Function application
    if isinstance(node1, Func):
        if node1.name != node2.name or len(node1.args) != len(node2.args):
            return False
        return all(_alpha_eq(a1, a2, env, inv_env) for a1, a2 in zip(node1.args, node2.args))
    # Atomic formula
    if isinstance(node1, Atom):
        if node1.name != node2.name or len(node1.args) != len(node2.args):
            return False
        return all(_alpha_eq(a1, a2, env, inv_env) for a1, a2 in zip(node1.args, node2.args))
    # Negation
    if isinstance(node1, Not):
        return _alpha_eq(node1.formula, node2.formula, env, inv_env)
    # Binary connectives
    if isinstance(node1, And):
        return _alpha_eq(node1.left, node2.left, env, inv_env) and _alpha_eq(node1.right, node2.right, env, inv_env)
    if isinstance(node1, Or):
        return _alpha_eq(node1.left, node2.left, env, inv_env) and _alpha_eq(node1.right, node2.right, env, inv_env)
    if isinstance(node1, Implies):
        return _alpha_eq(node1.left, node2.left, env, inv_env) and _alpha_eq(node1.right, node2.right, env, inv_env)
    if isinstance(node1, Iff):
        return _alpha_eq(node1.left, node2.left, env, inv_env) and _alpha_eq(node1.right, node2.right, env, inv_env)
    # Quantifiers
    if isinstance(node1, ForAll):
        var1, var2 = node1.var, node2.var
        new_env, new_inv = env.copy(), inv_env.copy()
        if var1 in new_env:
            if new_env[var1] != var2:
                return False
        else:
            if var2 in new_inv:
                return False
            new_env[var1] = var2
            new_inv[var2] = var1
        return _alpha_eq(node1.formula, node2.formula, new_env, new_inv)
    if isinstance(node1, Exists):
        var1, var2 = node1.var, node2.var
        new_env, new_inv = env.copy(), inv_env.copy()
        if var1 in new_env:
            if new_env[var1] != var2:
                return False
        else:
            if var2 in new_inv:
                return False
            new_env[var1] = var2
            new_inv[var2] = var1
        return _alpha_eq(node1.formula, node2.formula, new_env, new_inv)
    # Sequent
    if isinstance(node1, Sequent):
        if node1.conclusion == node2.conclusion:
            # Notice that the comparisons here use alpha-equality under
            # the empty env
            return node1.premises == node2.premises
        else:
            return False
    raise InternalError(f"Unsupported node type: {type(node1)}")

def is_free_in(node, name):
    """
    Return True if the FVAR named 'name' occurs free in the AST node.
    """
    if isinstance(node, FVar):
        return node.name == name
    if isinstance(node, (Var, Const)):
        return False
    if isinstance(node, Func):
        return any(is_free_in(arg, name) for arg in node.args)
    if isinstance(node, Atom):
        return any(is_free_in(arg, name) for arg in node.args)
    if isinstance(node, Not):
        return is_free_in(node.formula, name)
    if isinstance(node, (And, Or, Implies, Iff)):
        return is_free_in(node.left, name) or is_free_in(node.right, name)
    if isinstance(node, (ForAll, Exists)):
        return is_free_in(node.formula, name)
    if isinstance(node, Sequent):
        return any(is_free_in(p, name) for p in node.premises) \
               or is_free_in(node.conclusion, name)
    raise InternalError(f"Unsupported node type: {type(node)}")

def is_bound_in(node, name):
    """
    Return True if the VAR named 'name' occurs in the AST node as either a quantifier-bound variable or a constant
    """
    if isinstance(node, (ForAll, Exists)):
        if node.var == name:
            return True
        else:
            return is_bound_in(node.formula, name)
    if isinstance(node, Const):
        if node.name == name:
            return True
        else:
            return False
    if isinstance(node, Var):
        assert node.name != name
        return False
    if isinstance(node, FVar):
        return False
    if isinstance(node, Func):
        return any(is_bound_in(arg, name) for arg in node.args)
    if isinstance(node, Atom):
        return any(is_bound_in(arg, name) for arg in node.args)
    if isinstance(node, Not):
        return is_bound_in(node.formula, name)
    if isinstance(node, (And, Or, Implies, Iff)):
        return is_bound_in(node.left, name) or is_bound_in(node.right, name)
    if isinstance(node, Sequent):
        return any(is_bound_in(p, name) for p in node.premises) \
               or is_bound_in(node.conclusion, name)
    raise InternalError(f"Unsupported node type: {type(node)}")

# Arity consistency checker for Func and Atom nodes
def check_arity_consistency(ast):
    """
    Recursively checks for inconsistent arities of Func and Atom nodes.
    Raises ValueError if inconsistent arities are found.  
    TODO: This function is not used anywhere yet.
    """
    seen_func_arities = {}
    seen_atom_arities = {}

    def visit(node):
        if isinstance(node, Func):
            arity = len(node.args)
            if node.name in seen_func_arities:
                if seen_func_arities[node.name] != arity:
                    raise ValueError(f"Inconsistent arity for function {node.name}: "
                                     f"{seen_func_arities[node.name]} vs {arity}")
            else:
                seen_func_arities[node.name] = arity
            for arg in node.args:
                visit(arg)
        elif isinstance(node, Atom):
            arity = len(node.args)
            if node.name in seen_atom_arities:
                if seen_atom_arities[node.name] != arity:
                    raise ValueError(f"Inconsistent arity for atom {node.name}: "
                                     f"{seen_atom_arities[node.name]} vs {arity}")
            else:
                seen_atom_arities[node.name] = arity
            for arg in node.args:
                visit(arg)
        else:
            for child in _get_children(node):
                visit(child)

    visit(ast)

def _get_children(node):
    children = []
    for val in node.__dict__.values():
        if isinstance(val, AST):
            children.append(val)
        elif isinstance(val, (set, list)):
            children.extend(e for e in val if isinstance(e, AST))
    return children

def _ascii_tree(node, prefix, is_last):
    # ASCII-art tree printer
    connector = '└── ' if is_last else '├── '
    # lines = [prefix + connector + node.__class__.__name__]
    lines = [prefix + connector + node.__class__.__name__ + "  " + pretty(node)]
    children = _get_children(node)
    for idx, child in enumerate(children):
        last = idx == len(children) - 1
        new_prefix = prefix + ('    ' if is_last else '│   ')
        lines.extend(_ascii_tree(child, new_prefix, last))
    return lines

