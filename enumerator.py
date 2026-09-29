"""Bottom-up enumerative program synthesizer for tiny arithmetic problems.

DSL (Polish / prefix notation):
    E ::= x | y | 0 | 1 | 2 | + E E | - E E | * E E
x is the first input (i_1) and y is the second input (i_2).

Programs are enumerated in order of increasing size (number of tokens) and the
first one that matches every input/output example is returned.
"""
import sys

MAX_SIZE = 11 # give up beyond this many tokens (the search grows fast)

# Binary operators and how to apply them to two integers.
OPS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
}


def load_examples(path):
    """Read lines like '1, 2, 3' into a list of (x, y, expected_output)."""
    examples = []
    with open(path) as f:
        for line in f:
            if line.strip():
                x, y, out = (int(p) for p in line.split(","))
                examples.append((x, y, out))
    return examples


def synthesize(examples, max_size=MAX_SIZE):
    """Return (program string, number of programs kept) or (None, count)."""
    target = tuple(o for _, _, o in examples)

    # by_size[n] is a list of (token_list, outputs) for programs with n tokens.
    # 'outputs' is the tuple of results on every example, computed once so we
    # never re-evaluate a program from scratch.
    by_size = {}

    # 'seen' holds output tuples we already have. If a new program behaves
    # identically to an earlier (smaller or equal) one, it can never lead to a
    # smaller solution, so we prune it. This keeps the search tractable.
    seen = set()
    count = 0

    def add(size, tokens, outputs):
        """Record a program unless an equivalent one already exists."""
        nonlocal count
        if outputs in seen:
            return None
        seen.add(outputs)
        by_size.setdefault(size, []).append((tokens, outputs))
        count += 1
        # Return the program if it solves the problem.
        return tokens if outputs == target else None

    # Size 1: the terminals.
    terminals = {
        "x": tuple(x for x, _, _ in examples),
        "y": tuple(y for _, y, _ in examples),
        "0": (0,) * len(examples),
        "1": (1,) * len(examples),
        "2": (2,) * len(examples),
    }
    for tok, outs in terminals.items():
        if add(1, [tok], outs):
            return tok, count

    # Larger sizes: an operator token plus a left and right subprogram.
    # size = 1 (operator) + left_size + right_size.
    for size in range(3, max_size + 1):
        for op, fn in OPS.items():
            for left_size in range(1, size - 1):
                right_size = size - 1 - left_size
                for l_toks, l_out in by_size.get(left_size, []):
                    for r_toks, r_out in by_size.get(right_size, []):
                        outs = tuple(fn(a, b) for a, b in zip(l_out, r_out))
                        found = add(size, [op] + l_toks + r_toks, outs)
                        if found:
                            return " ".join(found), count
    return None, count  # nothing found up to max_size


if __name__ == "__main__":
    prog, n = synthesize(load_examples(sys.argv[1]))
    print(prog)
