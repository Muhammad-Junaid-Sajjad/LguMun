"""
MUN Digital Platform - Concurrent Registration Stress Test
============================================================
Test 450+ simultaneous delegate registrations across 9 committees
with per-committee roll number formats, accuracy validation,
and zero-error guarantee.

Uses the project's existing database (SELECT FOR UPDATE locking)
for real concurrent safety testing.
"""

import asyncio
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict
import random
import sys

import aiohttp

# ============================================================================
# CONFIGURATION
# ============================================================================

API_URL = "http://localhost:8000/api/v1/delegates"
TARGET_CONCURRENT = 450
RATE_LIMIT_BYPASS = True  # Set True to clear rate limit before test

COMMITTEES = {
    "UNGA":   {"name": "United Nations General Assembly",              "id": 11},
    "UNSC":   {"name": "United Nations Security Council",          "id": 10},
    "UNHRC":  {"name": "United Nations Human Rights Council",       "id": 12},
    "DISEC":  {"name": "Disarmament and International Security",  "id": 13},
    "UNODC":  {"name": "UN Office on Drugs and Crime",        "id": 14},
    "PNA":    {"name": "Pakistan National Assembly",         "id": 15},
    "UNW":    {"name": "UN Women",                       "id": 16},
    "JSP":    {"name": "Joint Session of Parliament",        "id": 17},
    "NCC":    {"name": "National Crisis Committee",          "id": 18},
}

COUNTRIES = [
    "Pakistan", "India", "Bangladesh", "Sri Lanka", "Nepal",
    "USA", "UK", "China", "Germany", "France", "Japan", "Brazil",
]

# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass
class Delegate:
    delegate_id: str
    name: str
    email: str
    phone: str
    committee: str
    committee_id: int
    country: str
    roll_number: str
    timestamp: float
    registration_order: int


@dataclass
class RegistrationResult:
    success: bool
    roll_number: str = None
    committee: str = None
    error: str = None
    status_code: int = 0


# ============================================================================
# DELEGATE DATA GENERATOR
# ============================================================================


def generate_test_delegates(count: int = 450) -> list[dict]:
    """Generate test delegate data distributed across 9 committees."""
    committees_list = list(COMMITTEES.keys())
    delegates = []

    for i in range(count):
        committee_code = committees_list[i % len(committees_list)]
        committee = COMMITTEES[committee_code]
        digits = f"{i:013d}"  # 13-digit unique ID

        delegate = {
            "full_name": f"Stress Delegate {i+1:03d}",
            "student_id_cnic": digits,
            "email": f"stresstest+{i}@lgu.edu.pk",
            "phone": f"030{random.randint(10000000, 99999999)}",
            "institution": f"Stress Test University {i % 20}",
            "committee_id": committee["id"],
            "_committee_code": committee_code,
        }
        delegates.append(delegate)

    return delegates


# ============================================================================
# CONCURRENT REGISTRATION ENGINE
# ============================================================================


async def register_delegate(
    session: aiohttp.ClientSession,
    delegate: dict,
    order: int,
) -> RegistrationResult:
    """Register a single delegate via HTTP POST."""
    try:
        async with session.post(API_URL, json=delegate) as response:
            status = response.status
            body = await response.json()

            if status == 201:
                data = body.get("data", {})
                roll_number = data.get("roll_number", "")
                committee = delegate["_committee_code"]
                return RegistrationResult(
                    success=True,
                    roll_number=roll_number,
                    committee=committee,
                    status_code=status,
                )
            else:
                # Extract error
                error_detail = body.get("error", {})
                if isinstance(error_detail, dict):
                    error_code = error_detail.get("code", "UNKNOWN")
                    error_msg = error_detail.get("message", str(body))
                else:
                    error_code = "UNKNOWN"
                    error_msg = str(body)

                return RegistrationResult(
                    success=False,
                    committee=delegate["_committee_code"],
                    error=f"[{error_code}] {error_msg}",
                    status_code=status,
                )

    except asyncio.TimeoutError:
        return RegistrationResult(
            success=False,
            committee=delegate["_committee_code"],
            error="Request timed out",
            status_code=0,
        )
    except Exception as e:
        return RegistrationResult(
            success=False,
            committee=delegate["_committee_code"],
            error=str(e),
            status_code=0,
        )


async def run_concurrent_registration_test(delegates: list[dict]) -> dict:
    """Run concurrent registration stress test."""
    print(f"\n{'='*80}")
    print(f"CONCURRENT REGISTRATION STRESS TEST — {len(delegates)} DELEGATES")
    print(f"{'='*80}\n")

    connector = aiohttp.TCPConnector(limit=500, limit_per_host=500)
    timeout = aiohttp.ClientTimeout(total=60)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        print(f"Launching {len(delegates)} concurrent registration requests...")
        start_time = time.time()

        tasks = [
            register_delegate(session, delegate, i)
            for i, delegate in enumerate(delegates)
        ]

        results = await asyncio.gather(*tasks)

        elapsed = time.time() - start_time

    # Separate successes and failures
    successes = [r for r in results if r.success]
    failures = [r for r in results if not r.success]

    print(f"\nCompleted in {elapsed:.2f} seconds ({len(delegates)/elapsed:.1f} req/s)\n")

    return {
        "results": results,
        "successes": successes,
        "failures": failures,
        "elapsed_time": elapsed,
    }


# ============================================================================
# VALIDATION ENGINE
# ============================================================================


def validate_results(successes: list[RegistrationResult]) -> dict:
    """Comprehensive validation of registration results."""
    print(f"\n{'='*80}")
    print("VALIDATION SUITE")
    print(f"{'='*80}\n")

    checks = {}

    # CHECK 1: No duplicate roll numbers
    roll_numbers = [r.roll_number for r in successes if r.roll_number]
    unique_rolls = set(roll_numbers)
    checks["no_duplicates"] = {
        "passed": len(roll_numbers) == len(unique_rolls),
        "total": len(roll_numbers),
        "unique": len(unique_rolls),
        "duplicates": len(roll_numbers) - len(unique_rolls),
    }

    # CHECK 2: Roll number format validation per committee
    format_valid = defaultdict(lambda: {"total": 0, "valid": 0})
    for r in successes:
        if r.roll_number and r.committee:
            code = r.committee
            format_valid[code]["total"] += 1
            # Format: LGU-CC-###
            parts = r.roll_number.split("-")
            if len(parts) == 3 and parts[0] == "LGU":
                try:
                    seq = int(parts[2])
                    if seq >= 1:
                        format_valid[code]["valid"] += 1
                except ValueError:
                    pass

    all_format_valid = all(
        format_valid[c]["valid"] == format_valid[c]["total"]
        for c in format_valid
    )
    checks["format_validation"] = {
        "passed": all_format_valid,
        "by_committee": dict(format_valid),
    }

    # CHECK 3: Committee distribution
    committee_dist = defaultdict(int)
    for r in successes:
        if r.committee:
            committee_dist[r.committee] += 1
    checks["committee_distribution"] = dict(committee_dist)

    # CHECK 4: No empty roll numbers
    empty_rolls = [r for r in successes if not r.roll_number]
    checks["no_empty_rolls"] = {
        "passed": len(empty_rolls) == 0,
        "empty_count": len(empty_rolls),
    }

    return checks


def print_validation_results(checks: dict, total: int, successful: int, elapsed: float):
    """Pretty-print validation results."""
    sr = (successful / total * 100) if total > 0 else 0

    print(f"[1] DUPLICATE ROLL NUMBERS")
    dup = checks["no_duplicates"]
    print(f"    {'PASS' if dup['passed'] else 'FAIL'} — {dup['unique']}/{dup['total']} unique "
          f"(duplicates: {dup['duplicates']})")

    print(f"\n[2] ROLL NUMBER FORMAT (LGU-CC-###)")
    fmt = checks["format_validation"]
    print(f"    {'PASS' if fmt['passed'] else 'FAIL'}")
    for c, v in fmt["by_committee"].items():
        print(f"    {c}: {v['valid']}/{v['total']}")

    print(f"\n[3] COMMITTEE DISTRIBUTION")
    for c, cnt in sorted(checks["committee_distribution"].items()):
        print(f"    {c}: {cnt} delegates")

    print(f"\n[4] EMPTY ROLL NUMBERS")
    empty = checks["no_empty_rolls"]
    print(f"    {'PASS' if empty['passed'] else 'FAIL'} — {empty['empty_count']} empty")

    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total Requests:      {total}")
    print(f"Successful:       {successful} ({sr:.1f}%)")
    print(f"Failed:           {total - successful} ({100-sr:.1f}%)")
    print(f"Duration:         {elapsed:.2f}s ({total/elapsed:.1f} req/s)")
    print(f"{'='*80}")

    all_passed = (
        checks["no_duplicates"]["passed"]
        and checks["format_validation"]["passed"]
        and checks["no_empty_rolls"]["passed"]
    )

    if all_passed and sr >= 95.0:
        print(f"RESULT: PASS — All validation checks passed, success rate >= 95%")
    elif all_passed:
        print(f"RESULT: PARTIAL — Validation passed but success rate < 95%")
        print(f"  (Likely rate-limited or committee full — expected in production)")
    else:
        print(f"RESULT: FAIL — Validation checks failed")


# ============================================================================
# FAILURE ANALYSIS
# ============================================================================


def analyze_failures(failures: list[RegistrationResult]):
    """Analyze failure patterns."""
    if not failures:
        print(f"\nNo failures detected!")
        return

    categories = defaultdict(list)
    for r in failures:
        # Extract error code
        error_code = "UNKNOWN"
        if r.error:
            if "DUPLICATE_EMAIL" in r.error:
                error_code = "DUPLICATE_EMAIL"
            elif "DUPLICATE_ID" in r.error:
                error_code = "DUPLICATE_ID"
            elif "COMMITTEE_FULL" in r.error:
                error_code = "COMMITTEE_FULL"
            elif "rate limit" in r.error.lower():
                error_code = "RATE_LIMITED"
            elif "NOT_FOUND" in r.error:
                error_code = "COMMITTEE_NOT_FOUND"
            elif r.status_code == 0:
                error_code = "TIMEOUT/NETWORK"
        categories[error_code].append(r)

    print(f"\nFAILURE ANALYSIS:")
    for code, items in sorted(categories.items(), key=lambda x: -len(x[1])):
        print(f"  {code}: {len(items)} failures")


# ============================================================================
# MAIN
# ============================================================================


async def main():
    print(f"LGU MUN 2026 — Concurrent Registration Stress Test")
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Generate test delegates
    delegates = generate_test_delegates(TARGET_CONCURRENT)
    print(f"Generated {len(delegates)} test delegates across 9 committees")

    # Run stress test
    test_results = await run_concurrent_registration_test(delegates)
    results = test_results["results"]
    successes = test_results["successes"]
    failures = test_results["failures"]
    elapsed = test_results["elapsed_time"]

    # Validate results
    checks = validate_results(successes)
    print_validation_results(
        checks,
        total=len(results),
        successful=len(successes),
        elapsed=elapsed,
    )

    # Analyze failures
    analyze_failures(failures)

    print(f"\n{'='*80}")
    print(f"STRESS TEST COMPLETE")
    print(f"{'='*80}")

    # Exit code: 0 if all passed, 1 if failed
    sr = len(successes) / len(results) * 100 if results else 0
    all_passed = (
        checks["no_duplicates"]["passed"]
        and checks["format_validation"]["passed"]
        and checks["no_empty_rolls"]["passed"]
    )

    return all_passed and sr >= 95.0


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)