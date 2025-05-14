import re
from lark.exceptions import UnexpectedInput
import shlex

from .parser import Parser
from .verifier import ProofState

class ProofScriptFailure(ValueError):
    """
    Exception raised when a proof script fails.
    line_failed: 0-based line number of the line that failed
    line_checked: 0-based line number of the last line that passed (or -1 if no lines have been checked)
    state: string showing the proof state at the line that passed
    message: string showing the error message
    """
    def __init__(self, line_failed, line_checked, state, message):
        super().__init__(message)
        self.line_failed = line_failed
        self.line_checked = line_checked
        self.state = state

# ASCII ETX (End of Text) control character
SCRIPT_END = '\x03'  # ASCII code 3

def preprocess_script(script):
    """
    Preprocess a proof script to transform comments and blank lines to empty strings.
    Stops at the end of script marker.
    """
    lines = []
    for line in script:
        # Clear whitespaces
        line = line.strip()
        # End of script marker, inserted by the VSCode extension
        if line == SCRIPT_END:
            break
        # Skip comments
        if re.match(r"^#", line):
            line = ""
        lines.append(line)
    return lines

def run_script(script):
    """
    Run a proof script of the following format:  
    Line 1: <sequent>  
    Lines 2–N: <rule> <params>

    Returns a string showing the final proof state.
    If at any point the proof fails, it raises ProofScriptFailure.
    """
    # Preprocess the script
    script = preprocess_script(script)

    # 0-based line number of the last line that checked
    line_checked = -1

    # Find the first non-blank line and parse it as a sequent
    for i, line in enumerate(script):
        if line:
            break
        line_checked = i
    else:
        # TODO: Return a more meaningful message
        return ""
    # Parse the sequent
    try:
        goal = Parser(script[i]).parse_sequent()
        line_checked = i
    except UnexpectedInput as e:
        raise ProofScriptFailure(i, line_checked, "N/A", f"Failed to parse sequent: {e}")
    # Initialize the proof state
    state = ProofState([], goal)
    line_closed = None # 0-based line number of the line that closed the proof
    # Process the remaining lines
    for lineNum, line in enumerate(script[i+1:], start=i+1):
        line = line.strip()
        # Skip blank lines
        if not line:
            line_checked = lineNum
            continue
        # Check if the proof is already closed
        if state.is_closed():
            raise ProofScriptFailure(lineNum, line_checked, str(state), f"Proof already completed at line {line_closed + 1}.")
        # Parse the line as a rule application
        tokens = shlex.split(line)
        name, *params = tokens
        try:
            state.apply(name, *params)
            line_checked = lineNum
            if state.is_closed():
                line_closed = lineNum
        except (ValueError, UnexpectedInput) as e:
            raise ProofScriptFailure(lineNum, line_checked, str(state), f"{e}")
    return str(state)
