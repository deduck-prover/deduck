"""
Entry point for the VSCode extension.
"""

import sys
import json
from .script import run_script, ProofScriptFailure

if __name__ == "__main__":
    while True:
        try:
            result = run_script(sys.stdin)
            print(result, file=sys.stdout)
        except ProofScriptFailure as e:
            error_json = {
                "lineFailed": e.line_failed,
                "lineChecked": e.line_checked,
                "state": e.state,
                "message": str(e)
            }
            print(json.dumps(error_json), file=sys.stderr)
        sys.stdout.flush()
        sys.stderr.flush()
