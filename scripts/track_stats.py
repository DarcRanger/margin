#!/usr/bin/env python3
"""
scripts/track_stats.py - GitHub clone traffic tracker for Margin.

Fetches 14-day rolling clone statistics from GitHub,
merges daily clone records into an authoritative historical dataset by UTC date,
and maintains stats/history.json as the single source of truth.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple


def create_ssl_context() -> ssl.SSLContext:
    """Create a reliable SSL context across platforms."""
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        try:
            return ssl.create_default_context()
        except Exception:
            return ssl._create_unverified_context()


def make_github_request(
    url: str, token: Optional[str] = None
) -> Tuple[Optional[Any], Optional[int]]:
    """Execute a GET request against the GitHub REST API.

    Returns (parsed_json_body, http_status_code).
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Margin-Stats-Tracker",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    ctx = create_ssl_context()

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data, resp.status
    except urllib.error.HTTPError as err:
        return None, err.code
    except Exception as err:
        print(f"[warn] Request failed for {url}: {err}", file=sys.stderr)
        return None, None


def fetch_clones(
    repo: str, token: Optional[str]
) -> Optional[List[Dict[str, Any]]]:
    """Fetch clone statistics from the repository traffic endpoint."""
    if not token:
        print(
            "[info] No TRAFFIC_TOKEN provided. Skipping GitHub clone traffic fetch."
        )
        return None

    url = f"https://api.github.com/repos/{repo}/traffic/clones"
    data, status = make_github_request(url, token)

    if status == 403 or status == 404:
        print(
            f"[warn] Traffic API returned status {status}. "
            "TRAFFIC_TOKEN may lack repository administration/push access. "
            "Skipping clone traffic fetch and retaining existing history.",
            file=sys.stderr,
        )
        return None

    if isinstance(data, dict) and "clones" in data:
        return data["clones"]

    return None


def load_history(filepath: str) -> Dict[str, Any]:
    """Load existing history or return an initial schema."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as err:
            print(
                f"[warn] Failed to parse existing {filepath}: {err}",
                file=sys.stderr,
            )

    return {
        "updated_at": None,
        "clones": {"total": 0, "unique": 0},
        "days": {},
    }


def merge_clone_records(
    history: Dict[str, Any], new_clones: Optional[List[Dict[str, Any]]]
) -> None:
    """Merge incoming clone records into the authoritative UTC date mapping."""
    if not new_clones:
        return

    days = history.setdefault("days", {})

    for item in new_clones:
        raw_ts = item.get("timestamp", "")
        # GitHub timestamp format: 2026-09-01T00:00:00Z -> date: 2026-09-01
        date_key = raw_ts[:10] if len(raw_ts) >= 10 else raw_ts
        if not date_key:
            continue

        count = int(item.get("count", 0))
        uniques = int(item.get("uniques", 0))

        # Record or update this specific UTC date
        days[date_key] = {
            "clones": count,
            "unique_cloners": uniques,
        }

    # Recalculate totals across all authoritative dates
    total_clones = sum(int(d.get("clones", 0)) for d in days.values())
    total_unique = sum(int(d.get("unique_cloners", 0)) for d in days.values())

    history["clones"]["total"] = total_clones
    history["clones"]["unique"] = total_unique


def format_metric_count(count: int) -> str:
    """Format an integer into clean notation (e.g., 12.4K, 1.2M, 307)."""
    if count >= 1_000_000:
        val = count / 1_000_000
        formatted = f"{val:.1f}M"
        return formatted.replace(".0M", "M")
    if count >= 1_000:
        val = count / 1_000
        formatted = f"{val:.1f}K"
        return formatted.replace(".0K", "K")
    return f"{count:,}"


def run_tracker(
    repo: str,
    traffic_token: Optional[str],
    history_path: str,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Execute the clone traffic tracking cycle."""
    history = load_history(history_path)

    # 1. Fetch clones and merge by UTC date
    clones = fetch_clones(repo, traffic_token)
    merge_clone_records(history, clones)

    # 2. Update timestamp
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    history["updated_at"] = now_utc

    total = history.get("clones", {}).get("total", 0)
    formatted = format_metric_count(total)

    if dry_run:
        print("[dry-run] history.json would contain:")
        print(json.dumps(history, indent=2))
    else:
        os.makedirs(os.path.dirname(os.path.abspath(history_path)), exist_ok=True)

        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, sort_keys=True)
            f.write("\n")

        print(
            f"[success] Updated {history_path} (total clones: {total} -> {formatted})"
        )

    return history


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Track GitHub clones for Margin"
    )
    parser.add_argument(
        "--repo",
        default=os.getenv("GITHUB_REPOSITORY", "prxshetty/margin"),
        help="GitHub repository in owner/repo format",
    )
    parser.add_argument(
        "--history-path",
        default=os.path.join("stats", "history.json"),
        help="Path to stats/history.json",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute stats without writing to disk",
    )

    args = parser.parse_args()

    traffic_token = os.getenv("TRAFFIC_TOKEN") or os.getenv("GITHUB_TOKEN")

    run_tracker(
        repo=args.repo,
        traffic_token=traffic_token,
        history_path=args.history_path,
        dry_run=args.dry_run,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
