from .syntax import pretty_formulas

# Rule decorator and registry
dict_rules = {}

def rule(name, usage=None):
    """Decorator to register a proof rule with optional usage/help text. Supports multiple names (aliases)."""
    # Type check for name
    if not (isinstance(name, str) or isinstance(name, (list, tuple))):
        raise InternalError("Rule name must be a string or a list/tuple of strings.")
    if isinstance(name, (list, tuple)):
        for n in name:
            if not isinstance(n, str):
                raise InternalError("All rule names in the list/tuple must be strings.")
    def decorator(fn):
        fn.rule_name = name
        fn.usage = usage
        # Support multiple names (aliases)
        names = name if isinstance(name, (list, tuple)) else [name]
        for n in names:
            dict_rules[n] = fn
        return fn
    return decorator

class UnknownRule(ValueError):
    """Exception raised for unknown rule applications."""
    def __init__(self, rule_name):
        super().__init__(f"Unknown rule: {rule_name}")

class ProofState:
    
    def __init__(self, hyps, goal):
        self.hyps = hyps
        self.goal = goal

    def current(self):
        return (self.hyps, self.goal)

    def discharge(self):
        self.goal = None
        self.hyps = None

    def is_closed(self):
        return self.goal is None or self.hyps is None

    def apply(self, rule_name, *args):
        if rule_name not in dict_rules:
            raise UnknownRule(rule_name)
        dict_rules[rule_name](self, *args)

    def hyp(self, index):
        """
        Get a hypothesis from the current goal.  
        index: 0-based index of the hypothesis to get.  
        """
        return self.hyps[index]

    def add_hyp(self, hyp):
        self.hyps.append(hyp)

    def remove_hyp(self, index):
        """
        Remove a hypothesis from the current goal.  
        index: 0-based index of the hypothesis to remove.  
        """
        self.hyps = self.hyps[:index] + self.hyps[index+1:]

    def last_hyp(self):
        """
        Returns the last hypothesis.  
        Raises ValueError if there are no hypotheses.
        """
        if len(self.hyps) == 0:
            raise ValueError("No hypotheses available.")
        return self.hyps[-1]

    def process_index_param(self, input):
        """
        Process 1-based index parameter for rules that require it.  
        input: string representing the 1-based index.  
        Returns 0-based index.  
        Raises ValueError if the index is out of range.
        """
        try:
            index_from_one = int(input)
        except ValueError:
            raise ValueError("Invalid index format. Must be an integer.")
        if index_from_one < 1 or index_from_one > len(self.hyps):
            raise ValueError("Invalid index for hypotheses.")
        return index_from_one - 1

    def __str__(self):
        if self.is_closed():
            return "Q.E.D."
        else:
            # Create a 3-column table with as many rows as hypotheses
            # Column 1: Hypothesis number (right-aligned)
            # Column 2: Hypothesis premises (left-aligned)
            # Column 3: Hypothesis conclusion (left-aligned)
            table = []
            for i, a in enumerate(self.hyps):
                table.append([f"({i+1})", pretty_formulas(a.premises), f"{a.conclusion}"])
            # Add padding to the table to make it look nice
            for row in table:
                row[0] = row[0].rjust(max(len("(10)"), max(len(row[0]) for row in table)))
                row[1] = row[1].ljust(max(len(row[1]) for row in table))
                row[2] = row[2].ljust(max(len(row[2]) for row in table))
            
            lines = []
            lines.append("Hypotheses:")
            for row in table:
                lines.append(f"{row[0]} {row[1]} ⊢ {row[2]}")
            lines.append("Goal:")
            lines.append(f"     {self.goal}")
            return "\n".join(lines)

from .rules import *
