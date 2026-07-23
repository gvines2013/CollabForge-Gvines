#!/usr/bin/env python3
"""CollabForge — browse and drill the CCIE Collaboration Design-item bank.

Usage:
    python3 tools/collabforge.py list                 # all 15 items by domain
    python3 tools/collabforge.py show D4              # concepts, scenario, questions
    python3 tools/collabforge.py quiz                 # one random question, self-graded
    python3 tools/collabforge.py quiz --domain 5      # weight to a blueprint domain (1-7)
    python3 tools/collabforge.py quiz --item D11      # from a specific item
    python3 tools/collabforge.py check                # validate every item YAML

No dependencies beyond Python 3 + PyYAML  (pip install pyyaml).
"""
import argparse, glob, os, random, sys, textwrap

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required:  pip install pyyaml")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS = os.path.join(ROOT, "items")

DOMAIN_OF = {  # blueprint domain number per item
    "D1": 1, "D2": 1, "D9": 1, "D10": 1, "D3": 2, "D6": 3, "D11": 3, "D12": 3,
    "D5": 4, "D13": 4, "D4": 5, "D7": 5, "D14": 6, "D8": 7, "D15": 7,
}


def load_items():
    out = {}
    for f in glob.glob(os.path.join(ITEMS, "*.yaml")):
        y = yaml.safe_load(open(f, encoding="utf-8"))
        out[y["id"]] = y
    return out


def wrap(s, w=92, indent=""):
    return textwrap.fill(str(s), width=w, initial_indent=indent, subsequent_indent=indent)


def cmd_list(items, _):
    by_dom = {}
    for dn, y in items.items():
        by_dom.setdefault(DOMAIN_OF.get(dn, 0), []).append((dn, y["title"]))
    print("\nCollabForge — CCIE Collaboration v3.1 Design item bank")
    print("15 items · 60 scenario questions · 6 matrix · 4 drag-and-drop\n")
    for dom in sorted(by_dom):
        print(f"  Domain {dom}")
        for dn, title in sorted(by_dom[dom], key=lambda x: int(x[0][1:])):
            print(f"    {dn:<4} {title}")
        print()


def cmd_show(items, args):
    y = items.get(args.target and args.target.upper())
    if not y:
        sys.exit(f"Unknown item '{args.target}'. Try: python3 tools/collabforge.py list")
    print(f"\n{'='*94}\n{y['id']} · {y['title']}\n{y['domain']}\n{'='*94}")
    print("\nConcepts & theory  (read: concept → worked example → exam angle, then re-derive from memory)\n")
    for t in y["topics"]:
        print(f"  Topic {t['n']} · {t['title']}")
        print(wrap(t["concept"], indent="    "))
        if t.get("exam_angle"):
            print(wrap("Exam angle: " + t["exam_angle"], indent="    → "))
        print()
    if y.get("decide_fast"):
        print("Decide fast — requirement → design answer")
        for p in y["decide_fast"]:
            print(f"    {p['requirement']:<48} →  {p['answer']}")
        print()
    sc = y.get("scenario", {})
    if sc:
        print("Worked scenario")
        print(wrap("Ask: " + sc.get("customer_ask", ""), indent="    "))
        for m in sc.get("model_answer", []):
            print(wrap(m, indent="    - "))
        print()
    print(f"{len(y['questions'])} self-test questions — run:  python3 tools/collabforge.py quiz --item {y['id']}\n")


def ask(q, item):
    print(f"\n{item['id']} · {item['domain']}")
    print(wrap(q["stem"]))
    print("(multiple answers — enter letters separated by space, e.g. 'a c')\n")
    opts = list(q["options"])
    random.shuffle(opts)
    letters = "abcdefgh"
    for i, o in enumerate(opts):
        print(f"    {letters[i]}) {o['text']}")
    try:
        raw = input("\nyour answer > ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print(); return
    picked = {l for l in raw.replace(",", " ").split()}
    correct = {letters[i] for i, o in enumerate(opts) if o["correct"]}
    got = picked == correct
    print("\n  " + ("✅ correct!" if got else "❌ not quite") + "\n")
    for i, o in enumerate(opts):
        mark = "✅" if o["correct"] else "  "
        you = " ← you" if letters[i] in picked else ""
        print(f"    {mark} {o['text']}{you}")
    print()


def cmd_quiz(items, args):
    pool = list(items.values())
    if args.item:
        pool = [items[args.item.upper()]] if args.item.upper() in items else []
    elif args.domain:
        pool = [y for dn, y in items.items() if DOMAIN_OF.get(dn) == int(args.domain)]
    if not pool:
        sys.exit("No items match that filter.")
    item = random.choice(pool)
    q = random.choice(item["questions"])
    ask(q, item)


def cmd_check(items, _):
    problems = []
    for dn, y in items.items():
        if len(y.get("topics", [])) != 5:
            problems.append(f"{dn}: expected 5 topics, got {len(y.get('topics', []))}")
        for q in y.get("questions", []):
            if not any(o["correct"] for o in q["options"]):
                problems.append(f"{dn}/{q['id']}: no correct option")
    if problems:
        print("Issues:\n  " + "\n  ".join(problems)); sys.exit(1)
    print(f"OK — {len(items)} items valid, "
          f"{sum(len(y['questions']) for y in items.values())} questions, "
          f"{sum(1 for y in items.values() for q in y['questions'] for o in q['options'] if o['correct'])} correct options.")


def main():
    p = argparse.ArgumentParser(description="Browse and drill the CollabForge design-item bank.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    s = sub.add_parser("show"); s.add_argument("target")
    q = sub.add_parser("quiz"); q.add_argument("--domain"); q.add_argument("--item")
    sub.add_parser("check")
    args = p.parse_args()
    items = load_items()
    {"list": cmd_list, "show": cmd_show, "quiz": cmd_quiz, "check": cmd_check}[args.cmd](items, args)


if __name__ == "__main__":
    main()
