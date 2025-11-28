# bruteforce_partitions.py

"""
Brute-force enumeration of representations and partitions into figurate numbers.

We use the same figurate families as in figurate.py and partitions_gf.py:

    - triangular: T(j) = j(j+1)/2, including 0
    - square:     j^2, including 0
    - centered_k: centered k-gonal numbers C_k(j), j>=0 (no 0 term)

We provide:

    - count_ordered_representations: number of ordered m-tuples summing to n
    - count_unordered_partitions:   number of unordered m-tuples (nondecreasing)
    - count_unordered_distinct:     number of unordered m-tuples with distinct parts

Optionally we can collect explicit solutions up to a maximum.
"""

from __future__ import annotations
from typing import List, Literal, Optional, Tuple

from figurate import (
    triangular_numbers_up_to,
    square_numbers_up_to,
    centered_polygonal_numbers_up_to,
)

FigurateFamily = Literal["triangular", "square", "centered_k"]


# ---------------------------------------------------------------------------
# Helper: get figurate values up to n
# ---------------------------------------------------------------------------

def figurate_values_up_to(
    family: FigurateFamily, n: int, k: Optional[int] = None
) -> List[int]:
    """
    Return a sorted list of figurate values <= n, matching the generating
    functions used elsewhere.

    For triangular and square, this includes 0.
    For centered_k, the smallest value is 1.
    """
    if n < 0:
        return []

    if family == "triangular":
        vals = triangular_numbers_up_to(n)
    elif family == "square":
        vals = square_numbers_up_to(n)
    elif family == "centered_k":
        if k is None:
            raise ValueError("k is required for centered_k family.")
        vals = centered_polygonal_numbers_up_to(k, n)
    else:
        raise ValueError(f"Unknown figurate family: {family}")

    # Ensure sorted ascending, just in case
    vals = sorted(vals)
    return vals


# ---------------------------------------------------------------------------
# 1. Ordered representations: ψ(q)^m
# ---------------------------------------------------------------------------

def count_ordered_representations(
    values: List[int],
    m: int,
    target: int,
    max_examples: int = 50,
) -> Tuple[int, List[Tuple[int, ...]]]:
    """
    Count ordered m-tuples (v_1, ..., v_m) with v_i in values such that
    v_1 + ... + v_m = target.

    Returns (count, examples), where examples is a list of up to max_examples
    concrete tuples.
    """
    values = sorted([v for v in values if v <= target])
    count = 0
    examples: List[Tuple[int, ...]] = []
    tuple_so_far: List[int] = [0] * m

    def backtrack(pos: int, remaining: int):
        nonlocal count, examples

        if pos == m:
            if remaining == 0:
                count += 1
                if len(examples) < max_examples:
                    examples.append(tuple(tuple_so_far))
            return

        # For each allowed value, try it if it does not overshoot
        for v in values:
            if v > remaining:
                break
            tuple_so_far[pos] = v
            backtrack(pos + 1, remaining - v)

    backtrack(0, target)
    return count, examples


# ---------------------------------------------------------------------------
# 2. Unordered partitions (nondecreasing m-tuples)
# ---------------------------------------------------------------------------

def count_unordered_partitions(
    values: List[int],
    m: int,
    target: int,
    distinct: bool = False,
    max_examples: int = 50,
) -> Tuple[int, List[Tuple[int, ...]]]:
    """
    Count unordered partitions of 'target' into exactly m figurate numbers.

    We represent each partition as a nondecreasing m-tuple (p_1 <= ... <= p_m)
    with p_i in values and sum p_i = target.

    If distinct=True, we require p_1 < p_2 < ... < p_m.

    Returns (count, examples), where examples lists up to max_examples partitions.
    """
    values = sorted([v for v in values if v <= target])
    count = 0
    examples: List[Tuple[int, ...]] = []
    tuple_so_far: List[int] = [0] * m

    def backtrack(pos: int, start_index: int, remaining: int):
        nonlocal count, examples

        if pos == m:
            if remaining == 0:
                count += 1
                if len(examples) < max_examples:
                    examples.append(tuple(tuple_so_far))
            return

        # For nondecreasing sequences, we only choose indices >= start_index.
        for idx in range(start_index, len(values)):
            v = values[idx]
            if v > remaining:
                break

            # For distinct partitions, enforce strict increase of the value
            if distinct and pos > 0 and v <= tuple_so_far[pos - 1]:
                continue

            tuple_so_far[pos] = v
            # Next start index:
            next_start = idx if not distinct else idx + 1
            backtrack(pos + 1, next_start, remaining - v)

    backtrack(0, 0, target)
    return count, examples


def count_unordered_partitions_non_distinct(
    values: List[int],
    m: int,
    target: int,
    max_examples: int = 50,
) -> Tuple[int, List[Tuple[int, ...]]]:
    return count_unordered_partitions(values, m, target, distinct=False, max_examples=max_examples)


def count_unordered_partitions_distinct(
    values: List[int],
    m: int,
    target: int,
    max_examples: int = 50,
) -> Tuple[int, List[Tuple[int, ...]]]:
    return count_unordered_partitions(values, m, target, distinct=True, max_examples=max_examples)


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    fam = "triangular"
    m = 3
    n = 10

    vals = figurate_values_up_to(fam, n)
    print("Values:", vals)

    c_rep, ex_rep = count_ordered_representations(vals, m, n)
    print(f"Ordered representations (m={m}, n={n}):", c_rep)
    print("Examples:", ex_rep[:10])

    c_part, ex_part = count_unordered_partitions_non_distinct(vals, m, n)
    print(f"Unordered partitions (nondistinct):", c_part)
    print("Examples:", ex_part[:10])

    c_partd, ex_partd = count_unordered_partitions_distinct(vals, m, n)
    print(f"Unordered partitions (distinct):", c_partd)
    print("Examples:", ex_partd[:10])
