"""A classic C-like preprocessor.

Directive precedence ::

    * include
    * enum
    * define
    * undef
    * branch
    * switch
"""

import shlex
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Set
from pathlib import Path

from . import Output, File

__all__ = []

@dataclass
class Context:
    source: File = field(init=True, repr=False)
    labels: Dict[str, str] = field(default_factory=dict)
    included: List["File"] = field(default_factory=list)
    mapped: defaultdict = field(default_factory=(lambda: defaultdict(list)))

    def process_include(self, line: int, include_path: str):
        path = self.source.path.parent.joinpath(include_path)

        with open(path) as included_file:
            mapping = dict(enumerate(included_file))

        self.source.mapping[line] = file = File(mapping, path)
        self.included.append(file)

    def process_enum(self, line: int, *args):
        stem, _, = args
        sequence = sorted(list(self.source.mapping.keys()))
        end = line

        ticker = 0
        for key in sequence[line + 1:]:
            source = self.source.mapping[key].strip()

            if source == "}":
                end = key
                break

            assert source[-1] == ",", f"Possibly missing COMMA \",\" on {line=!r}"

            source = source[:-1]

            if "=" in source:
                assert source.count("=") == 1, f"Expected only one EQUALS \"=\" on {line=!r}"
                leaf, value = source.split("=", maxsplit=1)
                value = value.strip()

                assert value.isdigit(), f"Enum values must only be digits. (Got {value=!r})"
                assert int(value) >= ticker, f"Can't reset enum values past previous."

                ticker = int(value)
                ticker += 1
            else:
                leaf = source
                value = ticker
                ticker += 1

            self.source.mapping[key] = f"#define {stem}.{leaf} {value}"
            self.mapped["define"].append((key, [f"{stem}.{leaf}", f"{value}"]))
        else:
            raise RuntimeError("Ran out of runway.")

        self.source.mapping[line] = ""
        self.source.mapping[end] = ""

    def process_define(self, line: int, *args):
        name, *rest = args

        self.labels[name.strip()] = " ".join(rest).strip()
        self.source.mapping[line] = ""

    def process_undef(self, line: int, *args):
        name, *_ = args

        self.labels.pop(name, None)
        self.source.mapping[line] = ""

    def process_switch(self, line: int, *args):
        subject, _, = args
        subject = subject.strip()

        sequence = sorted(list(self.source.mapping.keys()))
        for key in sequence[line + 1:]:
            source = self.source.mapping[key].strip()

            if source == "}":
                end = key
                break

            assert "=>" in source, f"Missing fat arrow => on {line=!r}"

            target, branch, = source.split("=>", maxsplit=1)
            target = target.strip()
            branch = branch.strip()

            self.source.mapping[key] = f"IF {subject} = {target} THEN {branch}"
        else:
            raise RuntimeError("Ran out of runway.")

        self.source.mapping[line] = ""
        self.source.mapping[end] = ""

    def process_branch(self, line: int, *args):
        subject, _, = args
        subject = subject.strip()

        self.source.mapping[line] = f"#switch {subject} {{"
        self.mapped["switch"].append((line, args))

        sequence = sorted(list(self.source.mapping.keys()))
        for key in sequence[line + 1:]:
            source = self.source.mapping[key].strip()

            if source == "}":
                end = key
                break

            assert "=>" in source, f"Missing fat arrow => on {line=!r}"

            target, branch, = source.split("=>", maxsplit=1)
            target = target.strip()
            branch = branch.strip()

            self.source.mapping[key] = f"{target} => GOTO {branch}"
        else:
            raise RuntimeError("Ran out of runway.")


def scan(source: File) -> Dict[int, str]:
    """Scan a source map for lines containing pre-processor directives."""
    directives = {}

    for n, line in source.mapping.items():
        if (trimmed := line.strip()) and trimmed[0] == "#":
            assert trimmed[0] == "#", repr(trimmed)

            op, *args = shlex.split(trimmed[1:])
            op = op.strip()

            directives[n] = (op, args)

    return directives


def process(
    source: File,
    *,
    include: bool = True,
    enum: bool = True,
    define: bool = True,
    undef: bool = True,
    branch: bool = True,
    switch: bool = True,
) -> Context:
    context = Context(source=source)
    scanned = scan(source)

    for n, (op, args) in scanned.items():
        context.mapped[op].append((n, args))

    directives: List[Tuple[str, bool, Callable[..., ...]]]
    directives = [
        ("include", include, context.process_include),
        ("enum", enum, context.process_enum),
        ("define", define, context.process_define),
        ("undef", undef, context.process_undef),
        ("branch", branch, context.process_branch),
        ("switch", switch, context.process_switch),
    ]

    passes = [(op, func) for (op, flag, func) in directives if flag]

    for op, handler in passes:
        for n, args in context.mapped.pop(op, []):
            args = [n, *args]
            handler(*args)

    return context
