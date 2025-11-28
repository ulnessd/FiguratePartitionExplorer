"""
series.py

A small truncated power series engine for generating-function experiments.

Representation:
    A series is represented as a list of integers `coeffs` of length N+1, where
    coeffs[n] is the coefficient of q^n, and N is the truncation order.

All operations here take an explicit truncation order N and always return a new
list of length N+1. Inputs are never modified in-place.

This module is deliberately lightweight and dependency-free.
"""

from __future__ import annotations
from typing import List


def _ensure_length(a: List[int], N: int) -> List[int]:
    """
    Return a copy of `a` of length exactly N+1.
    If a is shorter, pad with zeros. If longer, truncate.
    """
    if len(a) == N + 1:
        return a[:]  # copy
    elif len(a) < N + 1:
        return a[:] + [0] * (N + 1 - len(a))
    else:
        return a[: N + 1]


def zero_series(N: int) -> List[int]:
    """Return the zero series of length N+1: 0 + 0*q + ... + 0*q^N."""
    return [0] * (N + 1)


def one_series(N: int) -> List[int]:
    """Return the constant 1 series: 1 + 0*q + ... + 0*q^N."""
    coeffs = [0] * (N + 1)
    coeffs[0] = 1
    return coeffs


def add_series(a: List[int], b: List[int], N: int) -> List[int]:
    """
    Truncated series addition: c = a + b (mod q^{N+1}).

    a, b can be any length; they will be padded or truncated to length N+1.
    """
    a_ = _ensure_length(a, N)
    b_ = _ensure_length(b, N)
    return [a_[n] + b_[n] for n in range(N + 1)]


def sub_series(a: List[int], b: List[int], N: int) -> List[int]:
    """
    Truncated series subtraction: c = a - b (mod q^{N+1}).
    """
    a_ = _ensure_length(a, N)
    b_ = _ensure_length(b, N)
    return [a_[n] - b_[n] for n in range(N + 1)]


def scalar_mul_series(a: List[int], scalar: int, N: int) -> List[int]:
    """
    Multiply series by a scalar integer: c = scalar * a.
    """
    a_ = _ensure_length(a, N)
    return [scalar * c for c in a_]


def mul_series(a: List[int], b: List[int], N: int) -> List[int]:
    """
    Truncated Cauchy product of two series: c = a * b (mod q^{N+1}).

    c[n] = sum_{k=0}^n a[k] * b[n-k], for n = 0..N.
    """
    a_ = _ensure_length(a, N)
    b_ = _ensure_length(b, N)
    out = [0] * (N + 1)

    # Simple convolution with truncation
    for i in range(N + 1):
        ai = a_[i]
        if ai == 0:
            continue
        # j can go from 0 up to N - i
        max_j = N - i
        # Use local variable for speed
        for j in range(max_j + 1):
            bj = b_[j]
            if bj != 0:
                out[i + j] += ai * bj

    return out


def pow_series(base: List[int], exponent: int, N: int) -> List[int]:
    """
    Truncated power of a series: base(q)^exponent (mod q^{N+1}).

    Uses exponentiation by squaring for efficiency.
    Assumes exponent >= 0.
    """
    if exponent < 0:
        raise ValueError("Negative exponents are not supported for series.")

    # base^0 = 1
    if exponent == 0:
        return one_series(N)
    if exponent == 1:
        return _ensure_length(base, N)

    result = one_series(N)
    factor = _ensure_length(base, N)
    e = exponent

    # Binary exponentiation
    while e > 0:
        if e & 1:
            result = mul_series(result, factor, N)
        factor = mul_series(factor, factor, N)
        e >>= 1

    return result


def shift_series(a: List[int], k: int, N: int) -> List[int]:
    """
    Multiply a series by q^k: c(q) = q^k * a(q), truncated at q^N.

    Effect on coefficients:
        c[n] = a[n-k] for n >= k, else 0.
    """
    if k < 0:
        raise ValueError("Negative shifts are not supported.")
    a_ = _ensure_length(a, N)
    out = [0] * (N + 1)
    for n in range(k, N + 1):
        out[n] = a_[n - k]
    return out


def compose_q_to_qk(a: List[int], k: int, N: int) -> List[int]:
    """
    Compute the series for a(q^k) from a(q), truncated at q^N.

    If a(q) = sum_{n>=0} a_n q^n, then:
        a(q^k) = sum_{n>=0} a_n q^{k n}.

    Coefficient-wise:
        c[m] = a_{m/k} if k divides m, else 0.
    """
    if k <= 0:
        raise ValueError("k must be positive in q -> q^k substitution.")

    a_ = a[:]  # no need to enforce length; we read only existing indices
    out = [0] * (N + 1)

    # For each n with a_n != 0, it contributes to index m = k * n
    max_n = (N // k)
    for n in range(min(len(a_) - 1, max_n) + 1):
        coeff = a_[n]
        if coeff != 0:
            m = k * n
            if m <= N:
                out[m] += coeff

    return out


def pretty_print_series(a: List[int]) -> str:
    """
    Create a human-readable string for a series, e.g.:

        [1, 0, 3] -> "1 + 3 q^2"

    This is just for debugging / console use, not for LaTeX output.
    """
    terms = []
    for n, c in enumerate(a):
        if c == 0:
            continue
        if n == 0:
            terms.append(f"{c}")
        elif n == 1:
            terms.append(f"{c} q")
        else:
            terms.append(f"{c} q^{n}")
    if not terms:
        return "0"
    return " + ".join(terms)


# Simple self-test when run as a script
if __name__ == "__main__":
    N = 10

    # Example: (1 + q)^3
    a = [1, 1]  # 1 + q
    a3 = pow_series(a, 3, N)
    print("(1 + q)^3 up to q^10:")
    print(pretty_print_series(a3))

    # Example: a(q^2) where a(q) = 1 + q + q^2
    b = [1, 1, 1]
    b_q2 = compose_q_to_qk(b, 2, N)
    print("\n(1 + q + q^2) with q -> q^2:")
    print(pretty_print_series(b_q2))
