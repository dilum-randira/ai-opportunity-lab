"""Offline hostname concentration review for cost research references.

Distinct hostnames do not prove independent providers or verified prices.
"""
from collections import Counter
from urllib.parse import urlsplit

from orderpilot.cost_sources import validate_cost_sources


def assess_source_concentration(rows: list, *, as_of: str) -> dict:
    """Flag repeated hosts and shared evidence-kind hosts without exposing URLs."""
    report = validate_cost_sources(rows, as_of=as_of)
    sources = [entry for entry in report["entries"]
               if entry["kind"] != "internal_assumption"]
    hosts = Counter(urlsplit(entry["source_url"]).hostname.lower() for entry in sources)
    by_host = {}
    for entry in sources:
        host = urlsplit(entry["source_url"]).hostname.lower()
        by_host.setdefault(host, set()).add(entry["kind"])
    overlap = sum(1 for kinds in by_host.values()
                  if {"provider_quote", "public_price_list"} <= kinds)
    return {
        "as_of": report["as_of"],
        "external_reference_count": len(sources),
        "distinct_hostname_count": len(hosts),
        "reused_hostname_count": sum(count > 1 for count in hosts.values()),
        "largest_hostname_reference_count": max(hosts.values(), default=0),
        "hostnames_shared_across_quote_and_price_list": overlap,
        "requires_independence_review": bool(overlap or any(n > 1 for n in hosts.values())),
        "verified_independent_providers": 0,
        "warning": "Hostname counts do not establish ownership, source independence, authenticity, or verified prices. Review manually.",
    }
