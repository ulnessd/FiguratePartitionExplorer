# partitions_gf.py

"""
Build partition-type generating functions using the symmetric-group method.

For a chosen figurate family S (triangular, square, centered k-gonal), m, and
truncation N, we compute:

    - representations(q) = ψ(q)^m
    - P_m(q)             = (1/m!) * Σ |C_i| * C_i(q)
    - P_m_distinct(q)    = (1/m!) * Σ sign(C_i) * |C_i| * C_i(q)

where C_i(q) = ∏_ℓ ψ(q^ℓ)^{m_ℓ} for the cycle-type multiplicities m_ℓ.
"""

from __future__ import annotations
from typing import Dict, List, Literal, Optional

import math

from series import (
    zero_series,
    one_series,
    mul_series,
    pow_series,
    compose_q_to_qk,
    scalar_mul_series,
)
from figurate import triangular_series, square_series, centered_polygonal_series
from symmetric_group import conjugacy_classes_Sm, cycle_type_multiplicities


FigurateFamily = Literal["triangular", "square", "centered_k"]


def base_figurate_series(
    family: FigurateFamily, N: int, k: Optional[int] = None
) -> List[int]:
    """
    Return the base generating function ψ(q) (or analogous) for the chosen S.

    family:
        "triangular"  -> T(j) = j(j+1)/2
        "square"      -> j^2
        "centered_k"  -> centered k-gonal C_k(j)

    k:
        Required if family == "centered_k".
    """
    if family == "triangular":
        return triangular_series(N)
    elif family == "square":
        return square_series(N)
    elif family == "centered_k":
        if k is None:
            raise ValueError("Parameter k is required for centered_k family.")
        return centered_polygonal_series(k, N)
    else:
        raise ValueError(f"Unknown figurate family: {family}")


def class_generating_series(
    cycle_type, base_series: List[int], N: int
) -> List[int]:
    """
    Given a cycle type (tuple of lengths) and base ψ(q) series, compute

        C_i(q) = ∏_ℓ ψ(q^ℓ)^{m_ℓ}

    where m_ℓ are the multiplicities of cycles of length ℓ.
    """
    mult = cycle_type_multiplicities(cycle_type)
    result = one_series(N)

    for length, count in mult.items():
        # ψ(q^ℓ)
        psi_q_l = compose_q_to_qk(base_series, length, N)
        # ψ(q^ℓ)^{count}
        psi_power = pow_series(psi_q_l, count, N)
        # multiply into running product
        result = mul_series(result, psi_power, N)

    return result


def build_partition_generating_functions(
    family: FigurateFamily,
    m: int,
    N: int,
    k: Optional[int] = None,
    compute_distinct: bool = True,
) -> Dict[str, object]:
    """
    Build the main generating functions for the chosen figurate family and m:

        - representations: ψ(q)^m
        - P:               partitions (unordered)
        - P_distinct:      distinct partitions (if compute_distinct=True)

    Returns a dict with keys:

        'family', 'm', 'N', 'k'

        'representations' : List[int]
        'P'               : List[int]
        'P_distinct'      : Optional[List[int]]

        'class_data'      : list of dicts, one per conjugacy class:
            - 'cycle_type'
            - 'class_size'
            - 'parity'       ('even' or 'odd')
            - 'example'
            - 'psi_term'
            - 'index_pattern'
            - 'C_series'     (List[int])  # C_i(q)
    """
    if m <= 0:
        raise ValueError("m must be positive.")

    base = base_figurate_series(family, N, k)
    classes = conjugacy_classes_Sm(m)

    # representations = ψ(q)^m
    representations = pow_series(base, m, N)

    # We'll build integer sums:
    #   sum_P[n]        = Σ |C_i| * C_i(q)[n]
    #   sum_P_distinct[n] = Σ sign(C_i)*|C_i|*C_i(q)[n]
    sum_P = zero_series(N)
    sum_P_distinct = zero_series(N) if compute_distinct else None

    m_factorial = math.factorial(m)

    # Attach C_i(q) to each class dict for later inspection in the GUI
    for c in classes:
        ct = c["cycle_type"]
        class_size = c["class_size"]
        parity = c["parity"]

        C_i = class_generating_series(ct, base, N)
        c["C_series"] = C_i

        # sum_P += |C_i| * C_i(q)
        scaled = scalar_mul_series(C_i, class_size, N)
        sum_P = [a + b for a, b in zip(sum_P, scaled)]

        # For distinct partitions, include sign
        if compute_distinct and sum_P_distinct is not None:
            sign = 1 if parity == "even" else -1
            scaled_sign = scalar_mul_series(C_i, sign * class_size, N)
            sum_P_distinct = [a + b for a, b in zip(sum_P_distinct, scaled_sign)]

    # Divide by m! to get final coefficients (integer division)
    P = [coeff // m_factorial for coeff in sum_P]
    P_distinct = (
        [coeff // m_factorial for coeff in sum_P_distinct]
        if compute_distinct and sum_P_distinct is not None
        else None
    )

    return {
        "family": family,
        "m": m,
        "N": N,
        "k": k,
        "representations": representations,
        "P": P,
        "P_distinct": P_distinct,
        "class_data": classes,
    }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Simple test: triangles, m=2, N=30
    data = build_partition_generating_functions("triangular", m=2, N=30)
    print("Computed for triangles, m=2, N=30")
    print("First few coefficients of P(q):")
    print(data["P"][:20])
    print("First few coefficients of P_distinct(q):")
    print(data["P_distinct"][:20])
