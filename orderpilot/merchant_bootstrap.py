"""Reproducible, descriptive merchant-level bootstrap for paired time savings.

Resample independently grouped merchants, never their individual orders.
No identifiers, raw observations, or network access in the returned report.
"""
from decimal import Decimal
from random import Random

from .merchant_sensitivity import _seconds, MAX_MERCHANTS

MAX_REPLICATES = 5000


def merchant_bootstrap(pairs: list, *, replicates: int = 2000, seed: int = 0) -> dict:
    """Return a seeded percentile interval for mean merchant time savings.

    Percentiles use the nearest-rank empirical definition. This exploratory
    interval is not a causal effect, a validated confidence guarantee, or
    evidence of customer willingness to pay.
    """
    if not isinstance(pairs, list) or not 2 <= len(pairs) <= MAX_MERCHANTS:
        raise ValueError("pairs must contain 2..1000 distinct merchants")
    if type(replicates) is not int or not 100 <= replicates <= MAX_REPLICATES:
        raise ValueError("replicates must be an integer between 100 and 5000")
    if type(seed) is not int or not 0 <= seed <= 2**32 - 1:
        raise ValueError("seed must be an unsigned 32-bit integer")
    savings = []
    for row in pairs:
        if not isinstance(row, (tuple, list)) or len(row) != 4:
            raise ValueError("each merchant requires four fields")
        before, after, e1, e2 = row
        a, b = _seconds(before), _seconds(after)
        if type(e1) is not int or type(e2) is not int or e1 not in (0, 1) or e2 not in (0, 1):
            raise ValueError("error flags must be integers 0 or 1")
        savings.append(a - b)
    n = len(savings)
    rng = Random(seed)
    means = sorted(
        sum((savings[rng.randrange(n)] for _ in range(n)), Decimal(0)) / n
        for _ in range(replicates)
    )
    # 1-based nearest-rank indices for 2.5% and 97.5%.
    lower = means[max(0, (replicates * 25 + 999) // 1000 - 1)]
    upper = means[max(0, (replicates * 975 + 999) // 1000 - 1)]
    return {
        "merchant_count": n,
        "replicates": replicates,
        "seed": seed,
        "mean_saving_seconds": str(sum(savings, Decimal(0)) / n),
        "bootstrap_p025_seconds": str(lower),
        "bootstrap_p975_seconds": str(upper),
        "bootstrap_fraction_positive": str(Decimal(sum(x > 0 for x in means)) / replicates),
        "interpretation": "exploratory merchant-resampling percentiles; not causal or a confidence guarantee",
    }
