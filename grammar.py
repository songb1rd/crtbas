import re
import shlex
from typing import List


_RE_LINE = re.compile(r"^(?P<rule>\w+)\s*:(?P<form>[\w\s\W]*)$")
_RE_ALTS = re.compile(r"((?P<word>\w+)(?:\s*(?P=word))*)")
_RE_TOKE = re.compile(r"^(?P<name>[A-Z]+)\s*('|\")(?P<value>[\w\[\]!£$%^*()])\2$")

# with open("./crt/grammar.crt") as inf:
#     body = inf.read()

body = """
A 'a';
B 'b';
C 'c';

start: A B C
""".strip()

split = [part for part in map(str.strip, body.split(";")) if part]
rules = {}
token = {}

for line in split:
    line = line.replace("\n", "")

    while "  " in line:
        line = line.replace("  ", " ")

    match = _RE_LINE.match(line)

    if match is None:
        match = _RE_TOKE.match(line)

        if match is None:
            sys.exit("oof")

        name, value, = match.group("name"), match.group("value")
        token[name] = value
        continue

    rule, form, = match[1].strip(), match[2].strip()

    shlexd_form = shlex.split(form, posix=False)

    alts: List[List[str]] = []

    if "|" in shlexd_form:
        while True:
            start = 0
            end = shlexd_form.index("|")

            sl = shlexd_form[start:end]
            alts.append(sl)

            # print(">>", sl)

            if "|" not in shlexd_form[end + 1:]:
                if sl := shlexd_form[end + 1:]:
                    # print("<<", sl)
                    alts.append(sl)
                break
            else:
                start = end
                end = shlexd_form.index("|", start)
    else:
        sl = shlexd_form
        # print("II", sl)
        alts.append(sl)

    rules[rule] = alts

import pprint

# pprint.pprint(rules)
# pprint.pprint(token)

def draw_rule_enum(rules, name: str = "Target"):
    body = [
        f"#enum {name} {{"
    ]

    for rule in rules:
        body.append(f"    {rule},")

    body.append("}")

    return "\n".join(body)

def draw_target_switch(rules, name: str = "T%", stem: str = "Target"):
    body = [
        f"#branch {name} {{"
    ]

    for rule in rules:
        body.append(f"    {{{stem}.{rule}}} => {{_match_rule_{rule}}}")

    body.append("}")

    return "\n".join(body)


INIT = f"""
{draw_rule_enum(rules)}

{{start}} LET T% = {{Target.start}}
LET LINE$ = "abc"
LET S% = LEN(LINE$)

{{step}} IF S% = I% THEN GOTO {{done}}
LET C$ = MID$(LINE$, I$, 1)

{draw_target_switch(rules)}

I = I + 1
GOTO {{step}}
{{match}} 
""".strip()

output = INIT.split("\n")

for rule, alts in rules.items():
    output.append(f"\n{{_match_rule_{rule}}} REM {rule!r}")

    for alt in alts:
        token = "C$"
        dest = "{hell}"

        prev = []
        for form in alt:
            prev.append(form)
            chain = "_".join(prev)
            output.append(f"{{_match_rule_{rule}_{chain}}} REM {form}")

output.append("{done} END")

print("\n".join(output))
