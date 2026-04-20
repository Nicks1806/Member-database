"""
TWS Supabase Data Updater
=========================
Script ini dipakai Claude untuk push data baru ke Supabase.
Jalankan setiap ada import member/followup baru.

Usage:
  python update_supabase.py members  path/to/members.json
  python update_supabase.py followup path/to/followup.json
  python update_supabase.py stats
"""

import sys
import json
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone

SB_URL = "https://nfyqbkmvcaamwcpeiptp.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5meXFia212Y2FhbXdjcGVpcHRwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwODAwNDAsImV4cCI6MjA4OTY1NjA0MH0.fCX759LcYpCVS4x31IUxqjShW414zYcQ6Aq8L5XRkbc"

HEADERS = {
    "Content-Type": "application/json",
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Prefer": "return=representation"
}


def sb_request(method, path, body=None):
    url = f"{SB_URL}/rest/v1/{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode()), res.status
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f"  HTTP {e.code}: {err[:200]}")
        return None, e.code


def get_count(table):
    url = f"{SB_URL}/rest/v1/{table}?select=count"
    req = urllib.request.Request(url, headers={**HEADERS, "Prefer": "count=exact"})
    try:
        with urllib.request.urlopen(req) as res:
            cr = res.headers.get("Content-Range", "")
            if "/" in cr:
                return int(cr.split("/")[1])
            return 0
    except:
        return 0


def upsert_batch(table, records, key_col="email", batch_size=200):
    total = len(records)
    ok = 0
    errors = 0
    for i in range(0, total, batch_size):
        batch = records[i:i+batch_size]
        now = datetime.now(timezone.utc).isoformat()
        for r in batch:
            r["updated_at"] = now
        result, status = sb_request(
            "POST",
            f"{table}?on_conflict={key_col}",
            batch
        )
        if result is not None or status == 201:
            ok += len(batch)
        else:
            errors += len(batch)
        pct = min(100, int((i + len(batch)) / total * 100))
        print(f"  [{pct:3d}%] {i+len(batch)}/{total} — {'OK' if errors == 0 else f'{errors} errors'}", end="\r")
    print()
    return ok, errors


def cmd_stats():
    print("\n=== TWS Supabase Stats ===")
    for table in ["members", "followup", "audit_log"]:
        count = get_count(table)
        print(f"  {table:15s}: {count:,}")
    print()


def cmd_upsert_members(path):
    print(f"\nLoading members from: {path}")
    with open(path, encoding="utf-8") as f:
        records = json.load(f)
    print(f"  {len(records):,} records loaded")

    # Normalize
    normalized = []
    for r in records:
        normalized.append({
            "email": (r.get("email") or "").lower().strip(),
            "nama": (r.get("nama") or "").strip(),
            "phone": str(r.get("phone") or "").strip(),
            "memberships": r.get("memberships") or [],
            "total": r.get("total") or 0,
        })
    # Remove records with no email AND no phone
    normalized = [r for r in normalized if r["email"] or r["phone"]]
    print(f"  {len(normalized):,} valid records")

    print(f"\nUpserting to Supabase (table: members)...")
    ok, errors = upsert_batch("members", normalized, key_col="email")
    print(f"\n  Done: {ok:,} upserted, {errors:,} errors")
    cmd_stats()


def cmd_upsert_followup(path):
    print(f"\nLoading followup from: {path}")
    with open(path, encoding="utf-8") as f:
        records = json.load(f)
    print(f"  {len(records):,} records loaded")

    normalized = []
    for r in records:
        normalized.append({
            "nama": (r.get("nama") or "").strip(),
            "email": (r.get("email") or "").lower().strip(),
            "phone": str(r.get("phone") or "").strip(),
            "amount": str(r.get("amount") or ""),
            "pic": (r.get("pic") or "").strip(),
            "status": (r.get("status") or "Cold").strip(),
            "progress": (r.get("progress") or "").strip(),
            "source": (r.get("source") or "").strip(),
            "tanggal": r.get("tanggal") or None,
        })
    key_col = "phone"  # FU uses phone as unique key
    print(f"\nUpserting to Supabase (table: followup, key: phone)...")
    ok, errors = upsert_batch("followup", normalized, key_col=key_col)
    print(f"\n  Done: {ok:,} upserted, {errors:,} errors")
    cmd_stats()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1].lower()
    if cmd == "stats":
        cmd_stats()
    elif cmd == "members" and len(sys.argv) >= 3:
        cmd_upsert_members(sys.argv[2])
    elif cmd == "followup" and len(sys.argv) >= 3:
        cmd_upsert_followup(sys.argv[2])
    else:
        print(__doc__)
