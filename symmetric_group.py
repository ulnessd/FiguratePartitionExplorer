# symmetric_group.py

"""
Tools for working with cycle types (conjugacy classes) of the symmetric group S_m.

We do NOT construct the full group; we only enumerate conjugacy classes via
partitions of m, and compute:

    - cycle type as a partition (lambda_1, lambda_2, ...)
    - class size
    - parity (even/odd)
    - example permutation in cycle notation (for illustration)
    - a generic ψ-term structure: product of ψ(q^ℓ) for each cycle length ℓ
"""

from __future__ import annotations
from typing import List, Dict, Tuple
import math


# ---------------------------------------------------------------------------
# Partitions of an integer m  (in non-increasing order)
# ---------------------------------------------------------------------------

def integer_partitions(n: int) -> List[Tuple[int, ...]]:
    """
    Return all integer partitions of n as tuples in non-increasing order.

    Example: integer_partitions(4) returns
        [(4,),
         (3, 1),
         (2, 2),
         (2, 1, 1),
         (1, 1, 1, 1)]
    """
    result: List[Tuple[int, ...]] = []

    def _helper(remaining: int, max_part: int, prefix: List[int]):
        if remaining == 0:
            result.append(tuple(prefix))
            return
        for k in range(min(remaining, max_part), 0, -1):
            prefix.append(k)
            _helper(remaining - k, k, prefix)
            prefix.pop()

    _helper(n, n, [])
    return result


# ---------------------------------------------------------------------------
# Class size and parity
# ---------------------------------------------------------------------------

def cycle_type_multiplicities(cycle_type: Tuple[int, ...]) -> Dict[int, int]:
    """
    Given a cycle type as a tuple of lengths, e.g. (3, 2, 2, 1),
    return a dict mapping length -> multiplicity, e.g. {3:1, 2:2, 1:1}.
    """
    mult: Dict[int, int] = {}
    for length in cycle_type:
        mult[length] = mult.get(length, 0) + 1
    return mult


def class_size_for_cycle_type(cycle_type: Tuple[int, ...], m: int) -> int:
    """
    Compute the size of the conjugacy class in S_m with the given cycle type.

    Formula:
        size = m! / ( ∏_ℓ ( ℓ^{m_ℓ} m_ℓ! ) )

    where m_ℓ is the multiplicity of cycles of length ℓ in the type.
    """
    mult = cycle_type_multiplicities(cycle_type)
    numerator = math.factorial(m)
    denom = 1
    for length, count in mult.items():
        denom *= (length ** count) * math.factorial(count)
    return numerator // denom


def parity_for_cycle_type(cycle_type: Tuple[int, ...], m: int) -> str:
    """
    Return 'even' or 'odd' for the parity of permutations of this cycle type.

    The sign of a permutation σ can be written as:
        sign(σ) = (-1)^{m - (# of cycles)}
    where 'cycles' includes 1-cycles.

    For a cycle type with r cycles (len(cycle_type) = r), we have:
        sign = (-1)^(m - r).
    """
    r = len(cycle_type)
    sign = (-1) ** (m - r)
    return "even" if sign == 1 else "odd"


# ---------------------------------------------------------------------------
# Example permutation and ψ-term structure
# ---------------------------------------------------------------------------

def example_permutation_string(cycle_type: Tuple[int, ...]) -> str:
    """
    Construct a simple example permutation in cycle notation with this cycle type.

    We simply use the symbols 1, 2, 3, ... and group them into cycles
    with the requested lengths.

    Example: cycle_type = (3, 1)  -> "(1 2 3)(4)"
    """
    cycles = []
    current = 1
    for length in cycle_type:
        cycle = [str(current + i) for i in range(length)]
        current += length
        if length == 1:
            cycles.append(f"({cycle[0]})")
        else:
            cycles.append("(" + " ".join(cycle) + ")")
    return "".join(cycles)


def psi_term_for_cycle_type(cycle_type: Tuple[int, ...]) -> str:
    """
    Return a string describing the generic ψ-term structure for this cycle type.

    If a cycle type has m_1 1-cycles, m_2 2-cycles, etc., the term is:

        ψ(q)^m_1 * ψ(q^2)^m_2 * ψ(q^3)^m_3 * ...

    We use a compact textual form like:
        "ψ(q)^2 ψ(q^2) ψ(q^3)^2"
    """
    mult = cycle_type_multiplicities(cycle_type)
    pieces: List[str] = []
    for length in sorted(mult.keys()):
        count = mult[length]
        if length == 1:
            base = "ψ(q)"
        else:
            base = f"ψ(q^{length})"
        if count == 1:
            pieces.append(base)
        else:
            pieces.append(f"{base}^{count}")
    return " ".join(pieces)


def index_pattern_description(cycle_type: Tuple[int, ...]) -> str:
    """
    Provide a short human-readable description of the index-equality pattern
    encoded by this cycle type.

    Example: (2, 1, 1) -> "one pair of equal indices, two distinct"
    """
    mult = cycle_type_multiplicities(cycle_type)
    parts: List[str] = []
    # We separate 1-cycles from others for nicer phrasing.
    singles = mult.get(1, 0)

    for length in sorted(mult.keys()):
        if length == 1:
            continue
        count = mult[length]
        if length == 2:
            unit = "pair"
        elif length == 3:
            unit = "triple"
        elif length == 4:
            unit = "4-tuple"
        else:
            unit = f"{length}-tuple"
        if count == 1:
            parts.append(f"one {unit} of equal indices")
        else:
            parts.append(f"{count} {unit}s of equal indices")

    if singles > 0:
        if singles == 1:
            parts.append("one single (distinct) index")
        else:
            parts.append(f"{singles} single (distinct) indices")

    if not parts:
        return "all indices distinct"

    # Join nicely
    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return parts[0] + " and " + parts[1]
    else:
        return ", ".join(parts[:-1]) + ", and " + parts[-1]


# ---------------------------------------------------------------------------
# Public API: conjugacy classes of S_m
# ---------------------------------------------------------------------------

def conjugacy_classes_Sm(m: int):
    """
    Return a list of dicts describing each conjugacy class of S_m.

    Each dict has keys:
        - 'cycle_type': tuple of ints
        - 'class_size': int
        - 'parity': 'even' or 'odd'
        - 'example': string (cycle notation)
        - 'psi_term': string describing ψ-term structure
        - 'index_pattern': human-readable description
    """
    parts = integer_partitions(m)
    classes = []
    for ct in parts:
        info = {
            "cycle_type": ct,
            "class_size": class_size_for_cycle_type(ct, m),
            "parity": parity_for_cycle_type(ct, m),
            "example": example_permutation_string(ct),
            "psi_term": psi_term_for_cycle_type(ct),
            "index_pattern": index_pattern_description(ct),
        }
        classes.append(info)
    return classes


# ---------------------------------------------------------------------------
# Simple self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    m = 4
    print(f"Conjugacy classes of S_{m}:")
    for c in conjugacy_classes_Sm(m):
        print(
            f"cycle_type={c['cycle_type']}, "
            f"class_size={c['class_size']}, "
            f"parity={c['parity']}, "
            f"example={c['example']}, "
            f"psi_term={c['psi_term']}, "
            f"pattern={c['index_pattern']}"
        )
