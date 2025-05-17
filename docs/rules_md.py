import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'deduckprover'))
from deduckprover import verifier

OUTPUT_MD = os.path.join(os.path.dirname(__file__), 'rules_usage.md')

def get_rules_from_verifier():
    rules = []
    for name, fn in verifier.dict_rules.items():
        usage = getattr(fn, 'usage', None)
        if usage is not None and not any(fn is r[2] for r in rules):
            aliases = [n for n, f in verifier.dict_rules.items() if f is fn]
            rules.append(('/'.join(aliases), usage.strip(), fn))
    return [(name, usage) for name, usage, _ in rules]

def generate_markdown(rules):
    axioms = []
    peano_axioms = []
    theorems = []
    others = []
    for name, usage in rules:
        usage_lower = usage.lower()
        if usage_lower.startswith('peano axiom'):
            peano_axioms.append((name, usage))
        elif usage_lower.startswith('axiom'):
            axioms.append((name, usage))
        elif usage_lower.startswith('theorem'):
            theorems.append((name, usage))
        else:
            others.append((name, usage))
    md = []
    md.append('# Rule Usage')
    md.append('')
    md.append('## Index')
    def anchor_for(name):
        return name.lower().replace(' ', '-').replace(',', '').replace('/', '').replace('+', 'plus').replace('-', 'minus')
    def section(title, items):
        if not items:
            return
        md.append(f'### {title}')
        for name, _ in items:
            md.append(f'- [{name}](#{anchor_for(name)})')
        md.append('')
    section('Axioms', axioms)
    section('Peano Axioms', peano_axioms)
    section('Proven Theorems', theorems)
    section('Other Rules', others)
    md.append('---')
    for name, usage in rules:
        anchor = anchor_for(name)
        md.append(f'\n<a name="{anchor}"></a>')
        md.append(f'\n## {name}\n')
        md.append('```')
        md.append(usage)
        md.append('```\n')
    return '\n'.join(md)

def main():
    rules = get_rules_from_verifier()
    md = generate_markdown(rules)
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"Wrote rule usage Markdown to {OUTPUT_MD}")

if __name__ == '__main__':
    main()
