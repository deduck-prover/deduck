import sys
import argparse
from .script import run_script, ProofScriptFailure

def main():
    asciiArt ='''
      __
  >(o )___    DeDuck
   ( ._> /    "No quacks, just facts."
  ~~~~~~~~~~

  Programming formal-deduction proofs
  
  CS 245 Logic and Computation (Spring 2025)
  University of Waterloo
  
  © Yizhou Zhang
  Version: 0.1.0''';

    parser = argparse.ArgumentParser(description=asciiArt, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('file', type=str, help='Path to the proof script file')
    args = parser.parse_args()

    try:
        with open(args.file, 'r') as f:
            script_lines = f.readlines()
        
        try:
            result = run_script(script_lines)
            print(result)
            sys.exit(0)
        except ProofScriptFailure as e:
            print(f"Proof failed at line {e.line_failed + 1}:", file=sys.stderr)
            print(f"Last successful line: {e.line_checked + 1}", file=sys.stderr)
            print(f"State at failure:", file=sys.stderr)
            print(e.state, file=sys.stderr)
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main() 