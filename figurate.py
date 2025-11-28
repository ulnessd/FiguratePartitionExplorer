"""
figurate.py

Figurate number generators and their associated power series.

Each generating function is returned as a coefficient list `coeffs` of length N+1,
where coeffs[n] is the coefficient of q^n. For the base figurate series, these
coefficients are 0 or 1:

    ψ_T(q)  = sum_{j >= 0} q^{T(j)}       (triangular numbers)
    σ(q)    = sum_{j >= 0} q^{j^2}        (squares)
    Γ_k(q)  = sum_{j >= 0} q^{C_k(j)}     (centered k-gonal numbers)

We do not apply any normalization here; these are just indicator series.
"""

from __future__ import annotations
from typing import List


# ---------------------------------------------------------------------------
# Helper functions: lists of figurate numbers up to a maximum n
# ---------------------------------------------------------------------------

def triangular_numbers_up_to(N: int) -> List[int]:
    """
    Return a list of all triangular numbers T(j) = j(j+1)/2 <= N, starting at j = 0.

    Example for N = 15:
        [0, 1, 3, 6, 10, 15]
    """
    values: List[int] = []
    j = 0
    while True:
        t = j * (j + 1) // 2
        if t > N:
            break
        values.append(t)
        j += 1
    return values


def square_numbers_up_to(N: int) -> List[int]:
    """
    Return a list of all perfect squares j^2 <= N, starting at j = 0.

    Example for N = 20:
        [0, 1, 4, 9, 16]
    """
    values: List[int] = []
    j = 0
    while True:
        s = j * j
        if s > N:
            break
        values.append(s)
        j += 1
    return values


def centered_polygonal_numbers_up_to(k: int, N: int) -> List[int]:
    """
    Return a list of centered k-gonal numbers C_k(j) <= N, starting at j = 0.

    We use the standard formula:
        C_k(j) = 1 + (k * j * (j - 1)) / 2   for j >= 0

    Example (k = 5, centered pentagonal) starting values:
        j = 0: 1
        j = 1: 1
        j = 2: 5
        j = 3: 12
        j = 4: 22
        ...

    Note: j = 0 and j = 1 both give C_k = 1; we include each value at most once
    in the returned list.
    """
    if k < 3:
        raise ValueError("k should be >= 3 for centered k-gonal numbers.")

    values_set = set()
    j = 0
    while True:
        ck = 1 + (k * j * (j - 1)) // 2
        if ck > N:
            break
        values_set.add(ck)
        j += 1

    # We return a sorted list of distinct values
    return sorted(values_set)


# ---------------------------------------------------------------------------
# Series generators
# ---------------------------------------------------------------------------

def triangular_series(N: int) -> List[int]:
    """
    Return the triangular-number generating function ψ_T(q) truncated at q^N.

        ψ_T(q) = sum_{j >= 0} q^{T(j)} = sum_{n=0}^N coeff[n] q^n

    where coeff[n] = 1 if n is triangular, otherwise 0.
    """
    coeffs = [0] * (N + 1)
    for t in triangular_numbers_up_to(N):
        coeffs[t] = 1
    return coeffs


def square_series(N: int) -> List[int]:
    """
    Return the square-number generating function σ(q) truncated at q^N.

        σ(q) = sum_{j >= 0} q^{j^2}
    """
    coeffs = [0] * (N + 1)
    for s in square_numbers_up_to(N):
        coeffs[s] = 1
    return coeffs


def centered_polygonal_series(k: int, N: int) -> List[int]:
    """
    Return the centered k-gonal generating function Γ_k(q) truncated at q^N.

        Γ_k(q) = sum_{j >= 0} q^{C_k(j)}

    Here we simply place a 1 at each exponent that is a centered k-gonal number.
    """
    coeffs = [0] * (N + 1)
    for c in centered_polygonal_numbers_up_to(k, N):
        coeffs[c] = 1
    return coeffs


# ---------------------------------------------------------------------------
# Simple self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    N = 60

    print("Triangular numbers up to", N, ":")
    print(triangular_numbers_up_to(N))
    print()

    print("Square numbers up to", N, ":")
    print(square_numbers_up_to(N))
    print()

    k = 5
    print(f"Centered {k}-gonal numbers up to {N}:")
    print(centered_polygonal_numbers_up_to(k, N))
    print()

    from series import pretty_print_series  # adjust import name if needed

    print("Triangular generating series ψ_T(q) up to q^20:")
    tri = triangular_series(20)
    print(pretty_print_series(tri))
    print()

    print("Square generating series σ(q) up to q^20:")
    sq = square_series(20)
    print(pretty_print_series(sq))
    print()

    print(f"Centered {k}-gonal generating series Γ_{k}(q) up to q^40:")
    cen = centered_polygonal_series(k, 40)
    print(pretty_print_series(cen))
