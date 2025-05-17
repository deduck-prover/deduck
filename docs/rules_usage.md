# Rule Usage

## Index
### Axioms
- [Ref/ref](#refref)
- [+](#plus)
- [not-/¬-](#notminus¬minus)
- [imp-/→-](#impminus→minus)
- [imp+/→+](#impplus→plus)
- [and-/∧-](#andminus∧minus)
- [and+/∧+](#andplus∧plus)
- [or-/∨-](#orminus∨minus)
- [or+/∨+](#orplus∨plus)
- [iff-l/↔-l](#iffminusl↔minusl)
- [iff-r/↔-r](#iffminusr↔minusr)
- [iff+/↔+](#iffplus↔plus)
- [forall-/∀-](#forallminus∀minus)
- [forall+/∀+](#forallplus∀plus)
- [exists-/∃-](#existsminus∃minus)
- [exists+/∃+](#existsplus∃plus)
- [eq-/=-/≈-](#eqminus=minus≈minus)
- [eq+/=+/≈+](#eqplus=plus≈plus)

### Peano Axioms
- [PA1](#pa1)
- [PA2](#pa2)
- [PA3](#pa3)
- [PA4](#pa4)
- [PA5](#pa5)
- [PA6](#pa6)
- [PA7](#pa7)

### Proven Theorems
- [in/In/∈](#inin∈)
- [not+/¬+](#notplus¬plus)
- [inconsistency/Inconsistency](#inconsistencyinconsistency)
- [flip-flop/Flip-Flop/flipflop/FlipFlop](#flipminusflopflipminusflopflipflopflipflop)
- [=refl/≈refl](#=refl≈refl)
- [=symm/≈symm](#=symm≈symm)
- [=trans/≈trans](#=trans≈trans)

### Other Rules
- [exact](#exact)
- [rm](#rm)

---

<a name="exact"></a>

## exact

```
Usage: exact [index]
    [index] — 1-based index of an existing hypothesis (optional; defaults to last hypothesis)
Effect: Discharges the goal if its conclusion exactly matches the selected hypothesis.
```


<a name="rm"></a>

## rm

```
Usage: rm <index>
    <index> — 1-based index of an existing hypothesis
Effect: Removes the selected hypothesis from the current goal.
```


<a name="refref"></a>

## Ref/ref

```
Axiom Ref:
    A ⊢ A
Usage: Ref <formula>
    <formula> — a formula: A
Effect: Adds A ⊢ A as a new hypothesis.
```


<a name="plus"></a>

## +

```
Axiom +:
    If Σ ⊢ A, then Σ, Σ' ⊢ A
Usage: + <index> <formulas>
    <index> — 1-based index of an existing hypothesis: Σ ⊢ A
    <formulas> — comma-separated list of formulas: Σ'
Effect: Adds Σ, Σ' ⊢ A as a new hypothesis.
```


<a name="notminus¬minus"></a>

## not-/¬-

```
Axiom ¬-:
    If Σ, ¬A ⊢ B and Σ, ¬A ⊢ ¬B, then Σ ⊢ A
Usage: ¬- <index1> <index2> [formula]
    <index1> — 1-based index of an existing hypothesis: Σ, ¬A ⊢ B
    <index2> — 1-based index of an existing hypothesis: Σ, ¬A ⊢ ¬B
    [formula] — a formula: A (optional; if not provided, DeDuck will infer A as the only formula such that ¬A appears in the premises of both selected hypotheses)
Effect: Adds Σ ⊢ A as a new hypothesis.
```


<a name="impminus→minus"></a>

## imp-/→-

```
Axiom →-:
    If Σ ⊢ A → B and Σ ⊢ A, then Σ ⊢ B
Usage: →- <index1> <index2>
    <index1> — 1-based index of an existing hypothesis: Σ ⊢ A → B
    <index2> — 1-based index of an existing hypothesis: Σ ⊢ A
Effect: Adds Σ ⊢ B as a new hypothesis.
```


<a name="impplus→plus"></a>

## imp+/→+

```
Axiom →+:
    If Σ, A ⊢ B, then Σ ⊢ A → B
Usage: →+ <index> [formula]
    <index> — 1-based index of an existing hypothesis: Σ, A ⊢ B
    [formula] — a formula: A (optional; if not provided, DeDuck will infer A as the only formula in the selected hypothesis)
Effect: Adds Σ ⊢ A → B as a new hypothesis.
```


<a name="andminus∧minus"></a>

## and-/∧-

```
Axiom ∧-:
    If Σ ⊢ A ∧ B, then Σ ⊢ A and Σ ⊢ B
Usage: ∧- <index>
    <index> — 1-based index of an existing hypothesis: Σ ⊢ A ∧ B
Effect: Adds Σ ⊢ A and Σ ⊢ B as new hypotheses.
```


<a name="andplus∧plus"></a>

## and+/∧+

```
Axiom ∧+:
    If Σ ⊢ A and Σ ⊢ B, then Σ ⊢ A ∧ B
Usage: ∧+ <index1> <index2>
    <index1> — 1-based index of an existing hypothesis: Σ ⊢ A
    <index2> — 1-based index of an existing hypothesis: Σ ⊢ B
Effect: Adds Σ ⊢ A ∧ B as a new hypothesis.
```


<a name="orminus∨minus"></a>

## or-/∨-

```
Axiom ∨-:
    If Σ, A ⊢ C and Σ, B ⊢ C, then Σ, A ∨ B ⊢ C
Usage: ∨- <index1> <index2> [<formulas> <formula1> <formula2>]
    <index1> — 1-based index of an existing hypothesis: Σ, A ⊢ C
    <index2> — 1-based index of an existing hypothesis: Σ, B ⊢ C
    [<formulas> <formula1> <formula2>] — specifies all of the followig: a comma-separated list of formulas Σ, a formula A, and a formula B (optional; if not provided, DeDuck will infer A and B as the distinct pair of formulas that differ in the premises of both selected hypotheses)
Effect: Adds Σ, A ∨ B ⊢ C as a new hypothesis.
```


<a name="orplus∨plus"></a>

## or+/∨+

```
Axiom ∨+:
    If Σ ⊢ A, then Σ ⊢ A ∨ B and Σ ⊢ B ∨ A.
Usage: ∨+ <index> <formula>
    <index> — 1-based index of an existing hypothesis: Σ ⊢ A
    <formula> — a formula: B
Effect: Adds Σ ⊢ A ∨ B and Σ ⊢ B ∨ A as new hypotheses.
```


<a name="iffminusl↔minusl"></a>

## iff-l/↔-l

```
Axiom ↔-l:
    If Σ ⊢ A ↔ B and Σ ⊢ A, then Σ ⊢ B.
Usage: ↔-l <index1> <index2>
    <index1> — 1-based index of an existing hypothesis: Σ ⊢ A ↔ B
    <index2> — 1-based index of an existing hypothesis: Σ ⊢ A
Effect: Adds Σ ⊢ B as a new hypothesis.
```


<a name="iffminusr↔minusr"></a>

## iff-r/↔-r

```
Axiom ↔-r:
    If Σ ⊢ A ↔ B and Σ ⊢ B, then Σ ⊢ A.
Usage: ↔-r <index1> <index2>
    <index1> — 1-based index of an existing hypothesis: Σ ⊢ A ↔ B
    <index2> — 1-based index of an existing hypothesis: Σ ⊢ B
Effect: Adds Σ ⊢ A as a new hypothesis.
```


<a name="iffplus↔plus"></a>

## iff+/↔+

```
Axiom ↔+:
    If Σ, A ⊢ B and Σ, B ⊢ A, then Σ ⊢ A ↔ B.
Usage: ↔+ <index1> <index2>
    <index1> — 1-based index of an existing hypothesis: Σ, A ⊢ B
    <index2> — 1-based index of an existing hypothesis: Σ, B ⊢ A
Effect: Adds Σ ⊢ A ↔ B as a new hypothesis.
```


<a name="forallminus∀minus"></a>

## forall-/∀-

```
Axiom ∀-:
    If Σ ⊢ ∀x A(x), then Σ ⊢ A(t).
Usage: ∀- <index> <term>
    <index> — 1-based index of an existing hypothesis: Σ ⊢ ∀x A
    <term> — a term: t
Effect: Adds Σ ⊢ A(t) as a new hypothesis.
```


<a name="forallplus∀plus"></a>

## forall+/∀+

```
Axiom ∀+:
    If Σ ⊢ A(`u) and `u does not occur in Σ, then Σ ⊢ ∀x A(x).
Usage: ∀+ <index> <free variable> <bound variable>
    <index> — 1-based index of an existing hypothesis: Σ ⊢ A(`u)
    <free variable> — the name of a free variable: `u
    <bound variable> — the name of a bound variable: x
Effect: Adds Σ ⊢ ∀x A(x) as a new hypothesis.
```


<a name="existsminus∃minus"></a>

## exists-/∃-

```
Axiom ∃-:
    If Σ, A(`u) ⊢ B and u does not occur in Σ or B, then Σ, ∃x A(x) ⊢ B.
Usage: ∃- <index> <formula> <free variable> <bound variable>
    <index> — 1-based index of an existing hypothesis: Σ, A(`u) ⊢ B
    <formula> — a formula: A(`u)
    <free variable> — the name of a free variable: `u
    <bound variable> — the name of a bound variable: x
Effect: Adds Σ, ∃x A(x) ⊢ B as a new hypothesis.
```


<a name="existsplus∃plus"></a>

## exists+/∃+

```
Axiom ∃+:
    If Σ ⊢ A(t), then Σ ⊢ ∃x A(x).
Usage: ∃+ <index> <term> <formula>
    <index> — 1-based index of an existing hypothesis: Σ ⊢ A(t)
    <term> — a term: t
    <formula> — an ∃-quantified formula: ∃x A(x)
Effect: Adds Σ ⊢ ∃x A(x) as a new hypothesis.
```


<a name="eqminus=minus≈minus"></a>

## eq-/=-/≈-

```
Axiom ≈-:
    If Σ ⊢ A(t1) and Σ ⊢ t1 ≈ t2, then Σ ⊢ A(t2).
Usage: ≈- <index1> <index2> <formula> <free variable>
    <index1> — 1-based index of an existing hypothesis: Σ ⊢ A(t1)
    <index2> — 1-based index of an existing hypothesis: Σ ⊢ t1 ≈ t2
    <formula> — a formula: A(`u), such that A(t1) is the result of substituting t1 for `u
    <free variable> — the name of a free variable: `u
Effect: Adds Σ ⊢ A(t2) as a new hypothesis.
```


<a name="eqplus=plus≈plus"></a>

## eq+/=+/≈+

```
Axiom ≈+:
    If Σ ⊢ `u ≈ `u.
Usage: ≈+ <free variable>
    <free variable> — a free variable: `u
Effect: Adds ⊢ `u ≈ `u as a new hypothesis.
```


<a name="pa1"></a>

## PA1

```
Peano Axiom PA1:
    ⊢ ∀x(¬(s(x) ≈ 0))
Usage: PA1
Effect: Adds ⊢ ∀x(¬(s(x) ≈ 0)) as a new hypothesis.
```


<a name="pa2"></a>

## PA2

```
Peano Axiom PA2:
    ⊢ ∀x∀y(s(x) ≈ s(y) → x ≈ y)
Usage: PA2
Effect: Adds ⊢ ∀x∀y(s(x) ≈ s(y) → x ≈ y) as a new hypothesis.
```


<a name="pa3"></a>

## PA3

```
Peano Axiom PA3:
    ⊢ ∀x(x + 0 ≈ x)
Usage: PA3
Effect: Adds ⊢ ∀x(x + 0 ≈ x) as a new hypothesis.
```


<a name="pa4"></a>

## PA4

```
Peano Axiom PA4:
    ⊢ ∀x∀y(x + s(y) ≈ s(x + y))
Usage: PA4
Effect: Adds ⊢ ∀x∀y(x + s(y) ≈ s(x + y)) as a new hypothesis.
```


<a name="pa5"></a>

## PA5

```
Peano Axiom PA5:
    ⊢ ∀x(x ⋅ 0 ≈ 0)
Usage: PA5
Effect: Adds ⊢ ∀x(x ⋅ 0 ≈ 0) as a new hypothesis.
```


<a name="pa6"></a>

## PA6

```
Peano Axiom PA6:
    ⊢ ∀x∀y(x ⋅ s(y) ≈ x ⋅ y + x)
Usage: PA6
Effect: Adds ⊢ ∀x∀y(x ⋅ s(y) ≈ x ⋅ y + x) as a new hypothesis.
```


<a name="pa7"></a>

## PA7

```
Peano Axiom PA7:
    ⊢ A(0) ∧ ∀x(A(x) → A(s(x))) → ∀x A(x)
Usage: PA7 <formula>
    <formula> — a formula: ∀x A(x)
Effect: Adds ⊢ A(0) ∧ ∀x(A(x) → A(s(x))) → ∀x A(x) as a new hypothesis.
```


<a name="inin∈"></a>

## in/In/∈

```
Theorem ∈:
    If A ∈ Σ, then Σ ⊢ A
Usage: ∈ <formulas> <index>
    <formulas> — a set of formulas: Σ
    <index> — 1-based index of a formula in Σ: A
Effect: Adds Σ ⊢ A as a new hypothesis.
```


<a name="notplus¬plus"></a>

## not+/¬+

```
Theorem ¬+:
    If Σ, A ⊢ B and Σ, A ⊢ ¬B, then Σ ⊢ ¬A.
Usage: ¬+ <index1> <index2> <formula>
    <index1> — 1-based index of an existing hypothesis: Σ, A ⊢ B
    <index2> — 1-based index of an existing hypothesis: Σ, A ⊢ ¬B
    <formula> — a formula: A
Effect: Adds Σ ⊢ ¬A as a new hypothesis.
```


<a name="inconsistencyinconsistency"></a>

## inconsistency/Inconsistency

```
Theorem Inconsistency:
    A, ¬A ⊢ B
Usage: Inconsistency <formula1> <formula2>
    <formula1> — a formula: A
    <formula2> — a formula: B
Effect: Adds A, ¬A ⊢ B as a new hypothesis (ex falso quodlibet).
```


<a name="flipminusflopflipminusflopflipflopflipflop"></a>

## flip-flop/Flip-Flop/flipflop/FlipFlop

```
Theorem FlipFlop:
    If A ⊢ B, then ¬B ⊢ ¬A
Usage: FlipFlop <index>
    <index> — 1-based index of an existing hypothesis: A ⊢ B
Effect: Adds ¬B ⊢ ¬A as a new hypothesis.
```


<a name="=refl≈refl"></a>

## =refl/≈refl

```
Theorem ≈refl:
    ⊢ t ≈ t
Usage: ≈refl <term>
    <term> — a term: t
Effect: Adds ⊢ t ≈ t as a new hypothesis (reflexivity of equality).
```


<a name="=symm≈symm"></a>

## =symm/≈symm

```
Theorem ≈symm:
    t1 ≈ t2 ⊢ t2 ≈ t1
Usage: ≈symm <term1> <term2>
    <term1> — a term: t1
    <term2> — a term: t2
Effect: Adds t1 ≈ t2 ⊢ t2 ≈ t1 as a new hypothesis (symmetry of equality).
```


<a name="=trans≈trans"></a>

## =trans/≈trans

```
Theorem ≈trans:
    t1 ≈ t2, t2 ≈ t3 ⊢ t1 ≈ t3
Usage: ≈trans <term1> <term2> <term3>
    <term1> — a term: t1
    <term2> — a term: t2
    <term3> — a term: t3
Effect: Adds t1 ≈ t2, t2 ≈ t3 ⊢ t1 ≈ t3 as a new hypothesis (transitivity of equality).
```
