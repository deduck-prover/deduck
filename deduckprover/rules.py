import re
from .syntax import *
from .parser import Parser
from .verifier import rule

@rule('exact', usage="""
Usage: exact [index]
    [index] — 1-based index of an existing hypothesis (optional; defaults to last hypothesis)
Effect: Discharges the goal if its conclusion exactly matches the selected hypothesis.
""")
def r_exact(state, *params):
    """Discharge goal if conclusion is exactly one of the hypotheses."""
    if len(params) > 1:
        raise ValueError(r_exact.usage)
    if len(params) == 0:
        s = state.last_hyp()
    else:
        index = state.process_index_param(params[0])
        s = state.hyp(index)
    if s == state.goal:
        state.discharge()
    else:
        raise ValueError("Exact rule failed: not an exact match.")

@rule('rm', usage="""
Usage: rm <index>
    <index> — 1-based index of an existing hypothesis
Effect: Removes the selected hypothesis from the current goal.
""")
def r_remove(state, *params):
    """Remove a hypothesis from the current goal."""
    if len(params) != 1:
        raise ValueError(r_remove.usage)
    index = state.process_index_param(params[0])
    state.remove_hyp(index)

@rule(['Ref', 'ref'], usage="""
Axiom Ref:
    A ⊢ A
Usage: Ref <formula>
    <formula> — a formula: A
Effect: Adds A ⊢ A as a new hypothesis.
""")
def r_ref(state, *params):
    if len(params) != 1:
        raise ValueError(r_ref.usage)
    formula = Parser(params[0]).parse_formula_only()
    new_hyp = Sequent([formula], formula)
    state.add_hyp(new_hyp)

@rule('+', usage="""
Axiom +:
    If Σ ⊢ A, then Σ, Σ' ⊢ A
Usage: + <index> <formulas>
    <index> — 1-based index of an existing hypothesis: Σ ⊢ A
    <formulas> — comma-separated list of formulas: Σ'
Effect: Adds Σ, Σ' ⊢ A as a new hypothesis.
""")
def r_add(state, *params):
    if len(params) != 2:
        raise ValueError(r_add.usage)
    index = state.process_index_param(params[0])
    formulas = Parser(params[1]).parse_formulas_only()
    selected = state.hyp(index)
    new_hyp = Sequent(list(selected.premises) + formulas, selected.conclusion)
    state.add_hyp(new_hyp)

@rule(['not-', '¬-'], usage="""
Axiom ¬-:
    If Σ, ¬A ⊢ B and Σ, ¬A ⊢ ¬B, then Σ ⊢ A
Usage: ¬- <index1> <index2> <formula>
    <index1> — 1-based index of an existing hypothesis: Σ, ¬A ⊢ B
    <index2> — 1-based index of an existing hypothesis: Σ, ¬A ⊢ ¬B
    <formula> — a formula: A
Effect: Adds Σ ⊢ A as a new hypothesis.
""")
def r_not_elim(state, *params):
    if len(params) != 3:
        raise ValueError(r_not_elim.usage)
    index1 = state.process_index_param(params[0])
    index2 = state.process_index_param(params[1])
    formula = Parser(params[2]).parse_formula_only()
    s1 = state.hyp(index1)
    s2 = state.hyp(index2)
    # Check both hypotheses have ¬A in their premises
    not_formula = Not(formula)
    if not_formula not in s1.premises:
        raise ValueError(f"Cannot find ¬{formula} in {s1}")
    if not_formula not in s2.premises:
        raise ValueError(f"Cannot find ¬{formula} in {s2}")
    # Check both hypotheses have the same set of premises
    if s1.premises != s2.premises:
        raise ValueError(f"Premises of {s1} and {s2} do not match.")
    # Check that s1 concludes B, s2 concludes ¬B
    b = s1.conclusion
    if not (isinstance(s2.conclusion, Not) and s2.conclusion.formula == b):
        raise ValueError("Second hypothesis must conclude ¬B, where B is conclusion of first hypothesis.")
    # Add Σ ⊢ A as hypothesis
    new_hyp = Sequent(list(s1.premises - {not_formula}), formula)
    state.add_hyp(new_hyp)

@rule(['imp-', '→-'], usage="""
Axiom →-:
    If Σ ⊢ A → B and Σ ⊢ A, then Σ ⊢ B
Usage: →- <index1> <index2>
    <index1> — 1-based index of an existing hypothesis: Σ ⊢ A → B
    <index2> — 1-based index of an existing hypothesis: Σ ⊢ A
Effect: Adds Σ ⊢ B as a new hypothesis.
""")
def r_implies_elim(state, *params):
    if len(params) != 2:
        raise ValueError(r_implies_elim.usage)
    index1 = state.process_index_param(params[0])
    index2 = state.process_index_param(params[1])
    s1 = state.hyp(index1)
    s2 = state.hyp(index2)
    if s1.premises != s2.premises:
        raise ValueError("hypotheses must share the same set of premises.")
    if not isinstance(s1.conclusion, Implies):
        raise ValueError("First hypothesis must conclude A → B.")
    if s1.conclusion.left != s2.conclusion:
        raise ValueError("Second hypothesis must conclude A, the antecedent of the implication.")
    # Add Σ ⊢ B as hypothesis
    new_hyp = Sequent(list(s1.premises), s1.conclusion.right)
    state.add_hyp(new_hyp)

@rule(['imp+', '→+'], usage="""
Axiom →+:
    If Σ, A ⊢ B, then Σ ⊢ A → B
Usage: →+ <index> <formula>
    <index> — 1-based index of an existing hypothesis: Σ, A ⊢ B
    <formula> — a formula: A
Effect: Adds Σ ⊢ A → B as a new hypothesis.
""")
def r_implies_intro(state, *params):
    if len(params) != 2:
        raise ValueError(r_implies_intro.usage)
    index = state.process_index_param(params[0])
    formula = Parser(params[1]).parse_formula_only()
    s1 = state.hyp(index)
    if formula not in s1.premises:
        raise ValueError(f"The formula {formula} must appear in the premises of the hypothesis.")    
    new_premises = s1.premises - {formula}
    new_conclusion = Implies(formula, s1.conclusion)
    new_hyp = Sequent(list(new_premises), new_conclusion)
    state.add_hyp(new_hyp)

@rule(['and-', '∧-'], usage="""
Axiom ∧-:
    If Σ ⊢ A ∧ B, then Σ ⊢ A and Σ ⊢ B
Usage: ∧- <index>
    <index> — 1-based index of an existing hypothesis: Σ ⊢ A ∧ B
Effect: Adds Σ ⊢ A and Σ ⊢ B as new hypotheses.
""")
def r_and_elim(state, *params):
    if len(params) != 1:
        raise ValueError(r_and_elim.usage)
    index = state.process_index_param(params[0])
    selected = state.hyp(index)
    if not isinstance(selected.conclusion, And):
        raise ValueError(f"Selected hypothesis does not conclude a conjunction: {selected}")
    # Extract conjuncts
    conj = selected.conclusion
    left, right = conj.left, conj.right
    # Create two new sequents
    new_left = Sequent(list(selected.premises), left)
    new_right = Sequent(list(selected.premises), right)
    # Add them as new hypotheses
    state.add_hyp(new_left)
    state.add_hyp(new_right)

@rule(['and+', '∧+'], usage="""
Axiom ∧+:
    If Σ ⊢ A and Σ ⊢ B, then Σ ⊢ A ∧ B
Usage: ∧+ <index1> <index2>
    <index1> — 1-based index of an existing hypothesis: Σ ⊢ A
    <index2> — 1-based index of an existing hypothesis: Σ ⊢ B
Effect: Adds Σ ⊢ A ∧ B as a new hypothesis.
""")
def r_and_intro(state, *params):
    if len(params) != 2:
        raise ValueError(r_and_intro.usage)
    index1 = state.process_index_param(params[0])
    index2 = state.process_index_param(params[1])
    s1 = state.hyp(index1)
    s2 = state.hyp(index2)
    if s1.premises != s2.premises:
        raise ValueError("Hypotheses must share the same premises.")
    new_hyp = Sequent(list(s1.premises), And(s1.conclusion, s2.conclusion))
    state.add_hyp(new_hyp)

@rule(['or-', '∨-'], usage="""
Axiom ∨-:
    If Σ, A ⊢ C and Σ, B ⊢ C, then Σ, A ∨ B ⊢ C
Usage: ∨- <index1> <index2> <formula1> <formula2>
    <index1> — 1-based index of an existing hypothesis: Σ, A ⊢ C
    <index2> — 1-based index of an existing hypothesis: Σ, B ⊢ C
    <formula1> — a formula: A
    <formula2> — a formula: B
Effect: Adds Σ, A ∨ B ⊢ C as a new hypothesis.
""")
def r_or_elim(state, *params):
    if len(params) != 4:
        raise ValueError(r_or_elim.usage)
    # Parse indices
    index1 = state.process_index_param(params[0])
    index2 = state.process_index_param(params[1])
    # Parse the disjunct formulas A and B
    formula1 = Parser(params[2]).parse_formula_only()
    formula2 = Parser(params[3]).parse_formula_only()
    s1 = state.hyp(index1)
    s2 = state.hyp(index2)
    # Check that each hypothesis has the correct disjunct in its premises
    if formula1 not in s1.premises:
        raise ValueError(f"Formula {formula1} not in premises of hypothesis {s1}")
    if formula2 not in s2.premises:
        raise ValueError(f"Formula {formula2} not in premises of hypothesis {s2}")
    # Ensure the remaining premises match
    sigma1 = s1.premises - {formula1}
    sigma2 = s2.premises - {formula2}
    if sigma1 != sigma2:
        raise ValueError("Premises other than the disjunct do not match between hypotheses.")
    # Ensure conclusions match
    if s1.conclusion != s2.conclusion:
        raise ValueError("Conclusions of both hypotheses must match.")
    # Build disjunction and new sequent
    new_disj = Or(formula1, formula2)
    new_hyp = Sequent(list(sigma1) + [new_disj], s1.conclusion)
    # Add the derived sequent as a hypothesis
    state.add_hyp(new_hyp)

@rule(['or+', '∨+'], usage="""
Axiom ∨+:
    If Σ ⊢ A, then Σ ⊢ A ∨ B and Σ ⊢ B ∨ A.
Usage: ∨+ <index> <formula>
    <index> — 1-based index of an existing hypothesis: Σ ⊢ A
    <formula> — a formula: B
Effect: Adds Σ ⊢ A ∨ B and Σ ⊢ B ∨ A as new hypotheses.
""")
def r_or_intro(state, *params):
    if len(params) != 2:
        raise ValueError(r_or_intro.usage)
    index = state.process_index_param(params[0])
    formula = Parser(params[1]).parse_formula_only()
    selected = state.hyp(index)
    # Build disjunctions
    new_conj1 = Or(selected.conclusion, formula)
    new_conj2 = Or(formula, selected.conclusion)
    # Create new sequents with same premises and disjunction conclusions
    new_hyp1 = Sequent(list(selected.premises), new_conj1)
    new_hyp2 = Sequent(list(selected.premises), new_conj2)
    # Add as hypotheses
    state.add_hyp(new_hyp1)
    state.add_hyp(new_hyp2)

@rule(['iff-l', '↔-l'], usage="""
Axiom ↔-l:
    If Σ ⊢ A ↔ B and Σ ⊢ A, then Σ ⊢ B.
Usage: ↔-l <index1> <index2>
    <index1> — 1-based index of an existing hypothesis: Σ ⊢ A ↔ B
    <index2> — 1-based index of an existing hypothesis: Σ ⊢ A
Effect: Adds Σ ⊢ B as a new hypothesis.
""")
def r_iff_elim_l(state, *params):
    if len(params) != 2:
        raise ValueError(r_iff_elim_l.usage)
    index1 = state.process_index_param(params[0])
    index2 = state.process_index_param(params[1])
    s1 = state.hyp(index1)
    s2 = state.hyp(index2)
    if s1.premises != s2.premises:
        raise ValueError("Hypotheses must share the same premises.")
    if not isinstance(s1.conclusion, Iff):
        raise ValueError("First hypothesis must conclude a biconditional.")
    if s1.conclusion.left != s2.conclusion:
        raise ValueError("Second hypothesis must conclude A, the left side of the biconditional.")
    # Add Σ ⊢ B as hypothesis
    new_hyp = Sequent(list(s1.premises), s1.conclusion.right)
    state.add_hyp(new_hyp)

@rule(['iff-r', '↔-r'], usage="""
Axiom ↔-r:
    If Σ ⊢ A ↔ B and Σ ⊢ B, then Σ ⊢ A.
Usage: ↔-r <index1> <index2>
    <index1> — 1-based index of an existing hypothesis: Σ ⊢ A ↔ B
    <index2> — 1-based index of an existing hypothesis: Σ ⊢ B
Effect: Adds Σ ⊢ A as a new hypothesis.
""")
def r_iff_elim_r(state, *params):
    if len(params) != 2:
        raise ValueError(r_iff_elim_r.usage)
    index1 = state.process_index_param(params[0])
    index2 = state.process_index_param(params[1])
    s1 = state.hyp(index1)
    s2 = state.hyp(index2)
    if s1.premises != s2.premises:
        raise ValueError("Hypotheses must share the same premises.")
    if not isinstance(s1.conclusion, Iff):
        raise ValueError("First hypothesis must conclude a biconditional.")
    if s1.conclusion.right != s2.conclusion:
        raise ValueError("Second hypothesis must conclude B, the right side of the biconditional.")
    # Add Σ ⊢ A as hypothesis
    new_sequent = Sequent(list(s1.premises), s1.conclusion.left)
    state.add_hyp(new_sequent)

@rule(['iff+', '↔+'], usage="""
Axiom ↔+:
    If Σ, A ⊢ B and Σ, B ⊢ A, then Σ ⊢ A ↔ B.
Usage: ↔+ <index1> <index2>
    <index1> — 1-based index of an existing hypothesis: Σ, A ⊢ B
    <index2> — 1-based index of an existing hypothesis: Σ, B ⊢ A
Effect: Adds Σ ⊢ A ↔ B as a new hypothesis.
""")
def r_iff_intro(state, *params):
    if len(params) != 2:
        raise ValueError(r_iff_intro.usage)
    index1 = state.process_index_param(params[0])
    index2 = state.process_index_param(params[1])
    s1 = state.hyp(index1)
    s2 = state.hyp(index2)
    # Check that each hypothesis has the other's conclusion as a premise
    if s2.conclusion not in s1.premises:
        raise ValueError(f"Formula {s2.conclusion} not in premises of hypothesis {s1}")
    if s1.conclusion not in s2.premises:
        raise ValueError(f"Formula {s1.conclusion} not in premises of hypothesis {s2}")
    # Compute common premises Σ
    sigma1 = set(s1.premises) - {s2.conclusion}
    sigma2 = set(s2.premises) - {s1.conclusion}
    if sigma1 != sigma2:
        raise ValueError("Premises other than the introduced formulas do not match.")
    # Build biconditional A ↔ B with A = s2.conclusion, B = s1.conclusion
    new_conj = Iff(s2.conclusion, s1.conclusion)
    # Create new sequent Σ ⊢ A ↔ B
    new_sequent = Sequent(list(sigma1), new_conj)
    # Add as new hypothesis
    state.add_hyp(new_sequent)

@rule(['forall-', '∀-'], usage="""
Axiom ∀-:
    If Σ ⊢ ∀x A(x), then Σ ⊢ A(t).
Usage: ∀- <index> <term>
    <index> — 1-based index of an existing hypothesis: Σ ⊢ ∀x A
    <term> — a term: t
Effect: Adds Σ ⊢ A(t) as a new hypothesis.
""")
def r_forall_elim(state, *params):
    if len(params) != 2:
        raise ValueError(r_forall_elim.usage)
    index = state.process_index_param(params[0])
    term = Parser(params[1]).parse_term_only()
    s = state.hyp(index)
    if not isinstance(s.conclusion, ForAll):
        raise ValueError(f"Selected hypothesis does not conclude a universal: {s}")
    # Perform substitution in the quantified formula
    var = s.conclusion.var
    formula = s.conclusion.formula
    new_conc = subst_var(formula, {var: term})
    new_sequent = Sequent(list(s.premises), new_conc)
    # Add the instantiated sequent as a hypothesis
    state.add_hyp(new_sequent)

@rule(['forall+', '∀+'], usage="""
Axiom ∀+:
    If Σ ⊢ A(`u) and `u does not occur in Σ, then Σ ⊢ ∀x A(x).
Usage: ∀+ <index> <free variable> <bound variable>
    <index> — 1-based index of an existing hypothesis: Σ ⊢ A(`u)
    <free variable> — the name of a free variable: `u
    <bound variable> — the name of a bound variable: x
Effect: Adds Σ ⊢ ∀x A(x) as a new hypothesis.
""")
def r_forall_intro(state, *params):
    if len(params) != 3:
        raise ValueError(r_forall_intro.usage)
    index = state.process_index_param(params[0])
    fv_name = params[1].strip(' `') # u
    v_name = params[2].strip() # x
    s = state.hyp(index)
    # Check fv_name and v_name are identifiers
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', fv_name) is None:
        raise ValueError(f"Invalid free variable name: {fv_name}")
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', v_name) is None:
        raise ValueError(f"Invalid bound variable name: {v_name}")
    # Check u doesn't occur free in Σ 
    if any(is_free_in(premise, fv_name) for premise in s.premises):
        raise ValueError(f"Variable {fv_name} occurs in the premises of the hypothesis {s}")
    # Check x doesn't occur bound in A
    if is_bound_in(s.conclusion, v_name):
        raise ValueError(f"Variable {v_name} already occurs in the conclusion of the hypothesis {s}")
    # Perform substitution in the formula
    new_sequent = Sequent(list(s.premises), ForAll(v_name, subst_fvar(s.conclusion, {fv_name: Var(v_name)})))
    # Add the quantified sequent as a hypothesis
    state.add_hyp(new_sequent)

@rule(['exists-', '∃-'], usage="""
Axiom ∃-:
    If Σ, A(`u) ⊢ B and u does not occur in Σ or B, then Σ, ∃x A(x) ⊢ B.
Usage: ∃- <index> <formula> <free variable> <bound variable>
    <index> — 1-based index of an existing hypothesis: Σ, A(`u) ⊢ B
    <formula> — a formula: A(`u)
    <free variable> — the name of a free variable: `u
    <bound variable> — the name of a bound variable: x
Effect: Adds Σ, ∃x A(x) ⊢ B as a new hypothesis.
""")
def r_exists_elim(state, *params):
    if len(params) != 4:
        raise ValueError(r_exists_elim.usage)
    index = state.process_index_param(params[0])
    formula = Parser(params[1]).parse_formula_only() # A(`u)
    fv_name = params[2].strip(' `') # `u
    v_name = params[3].strip() # x
    s = state.hyp(index)
    # Check fv_name and v_name are identifiers
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', fv_name) is None:
        raise ValueError(f"Invalid free variable name: {fv_name}")
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', v_name) is None:
        raise ValueError(f"Invalid bound variable name: {v_name}")
    # Check the chosen hypothesis' premises contain the formula
    if formula not in s.premises:
        raise ValueError(f"Cannot find {formula} in premises of hypothesis {s}")
    # Gather Σ = other premises
    Sigma = s.premises - {formula}
    # Check u doesn't occur free in Σ or in the conclusion B
    if any(is_free_in(premise, fv_name) for premise in Sigma):
        raise ValueError(f"Variable {fv_name} occurs in premises of {s}")
    if is_free_in(s.conclusion, fv_name):
        raise ValueError(f"Variable {fv_name} occurs in conclusion of {s}")
    # Check x doesn't occur bound in A
    if is_bound_in(formula, v_name):
        raise ValueError(f"Variable {v_name} already occurs in {formula}")
    # Finally add Σ, ∃xA(x) ⊢ B as a new hypothesis
    ex_formula = Exists(v_name, subst_fvar(formula, {fv_name: Var(v_name)}))
    new_sequent = Sequent(list(Sigma) + [ex_formula], s.conclusion)
    state.add_hyp(new_sequent)

@rule(['exists+', '∃+'], usage="""
Axiom ∃+:
    If Σ ⊢ A(t), then Σ ⊢ ∃x A(x).
Usage: ∃+ <index> <term> <formula>
    <index> — 1-based index of an existing hypothesis: Σ ⊢ A(t)
    <term> — a term: t
    <formula> — an ∃-quantified formula: ∃x A(x)
Effect: Adds Σ ⊢ ∃x A(x) as a new hypothesis.
""")
def r_exists_intro(state, *params):
    if len(params) != 3:
        raise ValueError(r_exists_intro.usage)
    index = state.process_index_param(params[0])
    term = Parser(params[1]).parse_term_only()
    formula = Parser(params[2]).parse_formula_only()
    # Check the formula is an Exists
    if not isinstance(formula, Exists):
        raise ValueError(f"Formula {formula} is not an ∃-quantified formula.")
    s = state.hyp(index)
    # Check the hypothesis' conclusion matches the term and the provided formula
    x = formula.var
    body = formula.formula
    if s.conclusion != subst_var(body, {x: term}):
        raise ValueError(f"Formula {s.conclusion} does not match the provided term {term} and formula {formula}.")
    # Finally add Σ ⊢ ∃x A(x) as a new hypothesis
    new_sequent = Sequent(list(s.premises), formula)
    state.add_hyp(new_sequent)

@rule(['eq-', '=-', '≈-'], usage="""
Axiom ≈-:
    If Σ ⊢ A(t1) and Σ ⊢ t1 ≈ t2, then Σ ⊢ A(t2).
Usage: ≈- <index1> <index2> <formula> <free variable>
    <index1> — 1-based index of an existing hypothesis: Σ ⊢ A(t1)
    <index2> — 1-based index of an existing hypothesis: Σ ⊢ t1 ≈ t2
    <formula> — a formula: A(`u), such that A(t1) is the result of substituting t1 for `u
    <free variable> — the name of a free variable: `u
Effect: Adds Σ ⊢ A(t2) as a new hypothesis.
""")
def r_eq_elim(state, *params):
    if len(params) != 4:
        raise ValueError(r_eq_elim.usage)
    index1 = state.process_index_param(params[0])
    index2 = state.process_index_param(params[1])
    formula = Parser(params[2]).parse_formula_only()
    fv_name = params[3].strip(' `') # `u
    s1 = state.hyp(index1)
    s2 = state.hyp(index2)
    # Check fv_name is an identifier
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', fv_name) is None:
        raise ValueError(f"Invalid free variable name: {fv_name}")
    # Obtain t1 and t2 from the second hypothesis
    if not isinstance(s2.conclusion, Atom) or s2.conclusion.name != "≈":
        raise ValueError(f"Hypothesis does not conclude an equality: {s2}")
    t1, t2 = s2.conclusion.args
    # Check the first hypothesis concludes A(t1)
    if s1.conclusion != subst_fvar(formula, {fv_name: t1}):
        raise ValueError(f"Formula {s1.conclusion} does not match the term {t1} and the provided formula {formula}.")
    # Check the second hypothesis has the same premises as the first
    if s1.premises != s2.premises:
        raise ValueError("Hypotheses must share the same premises.")
    # Finally add Σ ⊢ A(t2) as a new hypothesis
    new_conc = subst_fvar(formula, {fv_name: t2})
    new_sequent = Sequent(list(s1.premises), new_conc)
    state.add_hyp(new_sequent)

@rule(['eq+', '=+', '≈+'], usage="""
Axiom ≈+:
    If Σ ⊢ `u ≈ `u.
Usage: ≈+ <free variable>
    <free variable> — a free variable: `u
Effect: Adds ⊢ `u ≈ `u as a new hypothesis.
""")
def r_eq_intro(state, *params):
    if len(params) != 1:
        raise ValueError(r_eq_intro.usage)
    fv_name = params[0].strip(' `')
    # Check fv_name is an identifier
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', fv_name) is None:
        raise ValueError(f"Invalid free variable name: {fv_name}")
    # Create the equality formula
    eq_formula = Atom("≈", [FVar(fv_name), FVar(fv_name)])
    # Create a new sequent with the equality as the conclusion
    new_sequent = Sequent([], eq_formula)
    # Add the new sequent as a hypothesis
    state.add_hyp(new_sequent)

@rule('PA1', usage="""
Peano Axiom PA1:
    ⊢ ∀x(¬(s(x) ≈ 0))
Usage: PA1
Effect: Adds ⊢ ∀x(¬(s(x) ≈ 0)) as a new hypothesis.
""")
def r_PA1(state, *params):
    if len(params) != 0:
        raise ValueError(r_PA1.usage)
    formula = ForAll('x', Not(Atom("≈", [Func('s', [Var('x')]), Const('0')])))
    new_sequent = Sequent([], formula)
    state.add_hyp(new_sequent)

@rule('PA2', usage="""
Peano Axiom PA2:
    ⊢ ∀x∀y(s(x) ≈ s(y) → x ≈ y)
Usage: PA2
Effect: Adds ⊢ ∀x∀y(s(x) ≈ s(y) → x ≈ y) as a new hypothesis.
""")
def r_PA2(state, *params):
    if len(params) != 0:
        raise ValueError(r_PA2.usage)
    formula = ForAll('x', ForAll('y', Implies(Atom("≈", [Func('s', [Var('x')]), Func('s', [Var('y')])]), Atom("≈", [Var('x'), Var('y')]))))
    new_sequent = Sequent([], formula)
    state.add_hyp(new_sequent)

@rule('PA3', usage="""
Peano Axiom PA3:
    ⊢ ∀x(x + 0 ≈ x)
Usage: PA3
Effect: Adds ⊢ ∀x(x + 0 ≈ x) as a new hypothesis.
""")
def r_PA3(state, *params):
    if len(params) != 0:
        raise ValueError(r_PA3.usage)
    formula = ForAll('x', Atom("≈", [Func('+', [Var('x'), Const('0')]), Var('x')]))
    new_sequent = Sequent([], formula)
    state.add_hyp(new_sequent)

@rule('PA4', usage="""
Peano Axiom PA4:
    ⊢ ∀x∀y(x + s(y) ≈ s(x + y))
Usage: PA4
Effect: Adds ⊢ ∀x∀y(x + s(y) ≈ s(x + y)) as a new hypothesis.
""")
def r_PA4(state, *params):
    if len(params) != 0:
        raise ValueError(r_PA4.usage)
    formula = ForAll('x', ForAll('y', Atom("≈", [Func('+', [Var('x'), Func('s', [Var('y')])]), Func('s', [Func('+', [Var('x'), Var('y')])])])))
    new_sequent = Sequent([], formula)
    state.add_hyp(new_sequent)

@rule('PA5', usage="""
Peano Axiom PA5:
    ⊢ ∀x(x ⋅ 0 ≈ 0)
Usage: PA5
Effect: Adds ⊢ ∀x(x ⋅ 0 ≈ 0) as a new hypothesis.
""")
def r_PA5(state, *params):
    if len(params) != 0:
        raise ValueError(r_PA5.usage)
    formula = ForAll('x', Atom("≈", [Func('⋅', [Var('x'), Const('0')]), Const('0')]))
    new_sequent = Sequent([], formula)
    state.add_hyp(new_sequent)

@rule('PA6', usage="""
Peano Axiom PA6:
    ⊢ ∀x∀y(x ⋅ s(y) ≈ x ⋅ y + x)
Usage: PA6
Effect: Adds ⊢ ∀x∀y(x ⋅ s(y) ≈ x ⋅ y + x) as a new hypothesis.
""")
def r_PA6(state, *params):
    if len(params) != 0:
        raise ValueError(r_PA6.usage)
    formula = ForAll('x', ForAll('y', Atom("≈", [Func('⋅', [Var('x'), Func('s', [Var('y')])]), Func('+', [Func('⋅', [Var('x'), Var('y')]), Var('x')])])))
    new_sequent = Sequent([], formula)
    state.add_hyp(new_sequent)

@rule('PA7', usage="""
Peano Axiom PA7:
    ⊢ A(0) ∧ ∀x(A(x) → A(s(x))) → ∀x A(x)
Usage: PA7 <formula>
    <formula> — a formula: ∀x A(x)
Effect: Adds ⊢ A(0) ∧ ∀x(A(x) → A(s(x))) → ∀x A(x) as a new hypothesis.
""")
def r_PA7(state, *params):
    if len(params) != 1:
        raise ValueError(r_PA7.usage)
    formula = Parser(params[0]).parse_formula_only()
    if not isinstance(formula, ForAll):
        raise ValueError(f"Formula {formula} is not a ∀-quantified formula.")
    x = formula.var
    A_x = formula.formula
    A_0 = subst_var(A_x, {x: Const('0')})
    A_sx = subst_var(A_x, {x: Func('s', [Var(x)])})
    new_conc = Implies(And(A_0, ForAll(x, Implies(A_x, A_sx))), formula)
    new_sequent = Sequent([], new_conc)
    state.add_hyp(new_sequent)

@rule(['in', 'In', '∈'], usage="""
Theorem ∈:
    If A ∈ Σ, then Σ ⊢ A
Usage: ∈ <formulas> <index>
    <formulas> — a set of formulas: Σ
    <index> — 1-based index of a formula in Σ: A
Effect: Adds Σ ⊢ A as a new hypothesis.
""")
def r_in(state, *params):
    if len(params) != 2:
        raise ValueError(r_in.usage)
    formulas = Parser(params[0]).parse_formulas_only()
    index = int(params[1])
    if index < 1 or index > len(formulas):
        raise ValueError(f"Index {index} is out of range.")
    formula = formulas[index - 1]
    # Create a new sequent with the formula as the conclusion
    new_sequent = Sequent(formulas, formula)
    # Add the new sequent as a hypothesis
    state.add_hyp(new_sequent)

@rule(['not+', '¬+'], usage="""
Theorem ¬+:
    If Σ, A ⊢ B and Σ, A ⊢ ¬B, then Σ ⊢ ¬A.
Usage: ¬+ <index1> <index2> <formula>
    <index1> — 1-based index of an existing hypothesis: Σ, A ⊢ B
    <index2> — 1-based index of an existing hypothesis: Σ, A ⊢ ¬B
    <formula> — a formula: A
Effect: Adds Σ ⊢ ¬A as a new hypothesis.
""")
def r_not_intro(state, *params):
    if len(params) != 3:
        raise ValueError(r_not_intro.usage)
    index1 = state.process_index_param(params[0])
    index2 = state.process_index_param(params[1])
    s1 = state.hyp(index1)
    s2 = state.hyp(index2)
    # Get A and B
    A = Parser(params[2]).parse_formula_only()
    B = s1.conclusion
    # Check that the second hypothesis concludes ¬B
    if s2.conclusion != Not(B):
        raise ValueError(f"Conclusions of both hypotheses must match.")
    # Check that both hypotheses have the same premises
    if s1.premises != s2.premises:
        raise ValueError("Hypotheses must share the same premises.")
    # Check A is in the premises of both hypotheses
    if A not in s1.premises:
        raise ValueError(f"Formula {A} not in premises of hypothesis")
    new_hyp = Sequent(list(s1.premises - {A}), Not(A))
    state.add_hyp(new_hyp)

@rule(['inconsistency', 'Inconsistency'], usage="""
Theorem Inconsistency:
    A, ¬A ⊢ B
Usage: Inconsistency <formula1> <formula2>
    <formula1> — a formula: A
    <formula2> — a formula: B
Effect: Adds A, ¬A ⊢ B as a new hypothesis (ex falso quodlibet).
""")
def r_inconsistency(state, *params):
    if len(params) != 2:
        raise ValueError(r_inconsistency.usage)
    formula1 = Parser(params[0]).parse_formula_only()
    formula2 = Parser(params[1]).parse_formula_only()
    new_sequent = Sequent([formula1, Not(formula1)], formula2)
    state.add_hyp(new_sequent)

@rule(['flip-flop', 'Flip-Flop', 'flipflop', 'FlipFlop'], usage="""
Theorem FlipFlop:
    If A ⊢ B, then ¬B ⊢ ¬A
Usage: FlipFlop <index>
    <index> — 1-based index of an existing hypothesis: A ⊢ B
Effect: Adds ¬B ⊢ ¬A as a new hypothesis.
""")
def r_flipflop(state, *params):
    if len(params) != 1:
        raise ValueError(r_flipflop.usage)
    index = state.process_index_param(params[0])
    s = state.hyp(index)
    if len(s.premises) != 1:
        raise ValueError(f"Hypothesis must have exactly one premise: {s}")
    A = s.premises[0]
    B = s.conclusion
    new_sequent = Sequent([Not(B)], Not(A))
    state.add_hyp(new_sequent)

@rule(['=refl', '≈refl'], usage="""
Theorem ≈refl:
    ⊢ t ≈ t
Usage: ≈refl <term>
    <term> — a term: t
Effect: Adds ⊢ t ≈ t as a new hypothesis (reflexivity of equality).
""")
def r_eq_refl(state, *params):
    if len(params) != 1:
        raise ValueError(r_eq_refl.usage)
    term = Parser(params[0]).parse_term_only()
    formula = Atom("≈", [term, term])
    new_sequent = Sequent([], formula)
    state.add_hyp(new_sequent)

@rule(['=symm', '≈symm'], usage="""
Theorem ≈symm:
    t1 ≈ t2 ⊢ t2 ≈ t1
Usage: ≈symm <term1> <term2>
    <term1> — a term: t1
    <term2> — a term: t2
Effect: Adds t1 ≈ t2 ⊢ t2 ≈ t1 as a new hypothesis (symmetry of equality).
""")
def r_eq_symm(state, *params):
    if len(params) != 2:
        raise ValueError(r_eq_symm.usage)
    term1 = Parser(params[0]).parse_term_only()
    term2 = Parser(params[1]).parse_term_only()
    premise = Atom("≈", [term1, term2])
    conclusion = Atom("≈", [term2, term1])
    new_sequent = Sequent([premise], conclusion)
    state.add_hyp(new_sequent)

@rule(['=trans', '≈trans'], usage="""
Theorem ≈trans:
    t1 ≈ t2, t2 ≈ t3 ⊢ t1 ≈ t3
Usage: ≈trans <term1> <term2> <term3>
    <term1> — a term: t1
    <term2> — a term: t2
    <term3> — a term: t3
Effect: Adds t1 ≈ t2, t2 ≈ t3 ⊢ t1 ≈ t3 as a new hypothesis (transitivity of equality).
""")
def r_eq_trans(state, *params):
    if len(params) != 3:
        raise ValueError(r_eq_trans.usage)
    term1 = Parser(params[0]).parse_term_only()
    term2 = Parser(params[1]).parse_term_only()
    term3 = Parser(params[2]).parse_term_only()
    premise1 = Atom("≈", [term1, term2])
    premise2 = Atom("≈", [term2, term3])
    conclusion = Atom("≈", [term1, term3])
    new_sequent = Sequent([premise1, premise2], conclusion)
    state.add_hyp(new_sequent)
