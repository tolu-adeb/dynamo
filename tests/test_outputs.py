import json
import re
from collections import Counter
from pathlib import Path

REPORT_PATH = Path("/app/report.json")
LOG_PATH = Path("/app/access.log")

REQUEST_LINE_RE = re.compile(
    r'"(?:GET|POST|PUT|DELETE|HEAD|PATCH|OPTIONS)\s+(\S+)\s+HTTP/\d\.\d"'
)

EXPECTED_KEYS = {"total_requests", "unique_ips", "top_path"}


def _expected_report():
    """Independently recompute the expected report from the raw log.

    Deliberately re-implemented (not imported) from solution/solve.py so the
    verifier grades the real outcome rather than re-running the same code
    the agent/solution used.
    """
    total = 0
    ips = set()
    paths = Counter()

    for raw_line in LOG_PATH.read_text().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        total += 1
        ips.add(line.split(" ", 1)[0])
        m = REQUEST_LINE_RE.search(line)
        if m:
            paths[m.group(1)] += 1

    assert paths, "no request paths could be parsed from the log; log or regex is broken"

    return {
        "total_requests": total,
        "unique_ips": len(ips),
        "top_path": paths.most_common(1)[0][0],
    }


def _load_report():
    assert REPORT_PATH.exists(), f"expected report at {REPORT_PATH}, but it does not exist"
    assert REPORT_PATH.stat().st_size > 0, f"{REPORT_PATH} exists but is empty"
    try:
        return json.loads(REPORT_PATH.read_text())
    except json.JSONDecodeError as e:
        raise AssertionError(f"{REPORT_PATH} is not valid JSON: {e}")


def test_report_shape():
    """instruction.md criterion 1: /app/report.json exists, is valid JSON,
    and contains exactly the keys total_requests, unique_ips, top_path
    with the correct types (no more, no fewer keys)."""
    report = _load_report()
    assert isinstance(report, dict), "report.json must contain a single JSON object"
    assert set(report.keys()) == EXPECTED_KEYS, (
        f"report.json keys {sorted(report.keys())} do not match "
        f"expected keys {sorted(EXPECTED_KEYS)}"
    )
    assert isinstance(report.get("total_requests"), int), "total_requests must be an int"
    assert isinstance(report.get("unique_ips"), int), "unique_ips must be an int"
    assert isinstance(report.get("top_path"), str), "top_path must be a string"


def test_total_requests():
    """instruction.md criterion 2: total_requests equals the number of
    non-empty lines in /app/access.log."""
    report = _load_report()
    expected = _expected_report()
    assert report.get("total_requests") == expected["total_requests"], (
        f"total_requests: got {report.get('total_requests')!r}, "
        f"expected {expected['total_requests']!r}"
    )


def test_unique_ips():
    """instruction.md criterion 3: unique_ips equals the count of distinct
    client IP addresses (first whitespace-delimited token of each line)."""
    report = _load_report()
    expected = _expected_report()
    assert report.get("unique_ips") == expected["unique_ips"], (
        f"unique_ips: got {report.get('unique_ips')!r}, "
        f"expected {expected['unique_ips']!r}"
    )


def test_top_path():
    """instruction.md criterion 4: top_path equals the request path that
    appears most often in the log."""
    report = _load_report()
    expected = _expected_report()
    assert report.get("top_path") == expected["top_path"], (
        f"top_path: got {report.get('top_path')!r}, "
        f"expected {expected['top_path']!r}"
    )
