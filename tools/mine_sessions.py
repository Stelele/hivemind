#!/usr/bin/env python3
"""Extract and triage user prompts from the local opencode session database.

The database holds every credential the user has ever pasted into a prompt, so
redaction runs before anything reaches disk. The corpus is a local scratch
artefact: nothing here is meant to be committed.
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

SQL = """
select s.directory, p.time_created, json_extract(p.data,'$.text') as text
from part p
join message m on m.id = p.message_id
join session s on s.id = p.session_id
where json_extract(m.data,'$.role') = 'user'
  and json_extract(p.data,'$.type') = 'text'
  and coalesce(json_extract(p.data,'$.synthetic'), 0) = 0
  and json_extract(p.data,'$.text') not like '%<system-reminder>%'
order by p.time_created
"""

PRIVATE_KEY = re.compile(
    r"-----BEGIN[A-Z ]*PRIVATE KEY-----[\s\S]*?-----END[A-Z ]*PRIVATE KEY-----"
)
JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")
BEARER = re.compile(r"\b[Bb]earer\s+[A-Za-z0-9._~+/=-]{12,}")
API_KEY = re.compile(
    r"\b(?:sk-[A-Za-z0-9_-]{16,}"
    r"|ghp_[A-Za-z0-9]{20,}"
    r"|gho_[A-Za-z0-9]{20,}"
    r"|ghu_[A-Za-z0-9]{20,}"
    r"|github_pat_[A-Za-z0-9_]{20,}"
    r"|AKIA[A-Z0-9]{16}"
    r"|AIza[0-9A-Za-z_-]{30,}"
    r"|xox[baprs]-[A-Za-z0-9-]{10,})"
)
URI_CREDENTIALS = re.compile(
    r"\b(?:postgres(?:ql)?|mysql|mariadb|mongodb(?:\+srv)?|redis|amqp|ftp|ssh)"
    r"://[^\s:@/]+:[^\s@/]+@[^\s]+",
    re.IGNORECASE,
)
SERVER_PASSWORD = re.compile(
    r"(?:Server|Data Source)\s*=\s*[^;\n]+;\s*(?:Password|Pwd)\s*=\s*[^\s;]+",
    re.IGNORECASE,
)
CRED_KEY = (
    r"password|passwd|pwd|secret|token|api[_-]?key|apikey|client[_-]?secret"
    r"|refresh[_-]?token|access[_-]?token|private[_-]?key|access[_-]?key"
    r"|auth[_-]?token|authorization|credential|psks?|pre[-_]shared[-_]key"
    r"|passphrase|wifi[-_]?(?:key|psk)|break[-_]glass|app[_-]?secret"
    r"|shared[_-]?secret|[a-z0-9_]*password"
)
ASSIGNMENT = re.compile(
    r"((?:" + CRED_KEY + r")s?[\"']?\s*[:=]\s*)"
    r"[\"']?([^\s\"',;}{)]{6,})",
    re.IGNORECASE,
)
QUOTED_ASSIGNMENT = re.compile(
    r"((?:" + CRED_KEY + r")s?[\"']?\s*[:=]\s*)[\"']([^\"']*)[\"']",
    re.IGNORECASE,
)
CREDENTIAL_LINE = re.compile(CRED_KEY, re.IGNORECASE)
PROSE_CREDENTIAL = re.compile(
    r"((?:" + CRED_KEY + r")\b[^.\n]{0,40}?(?:is|are|:|=|->|→)\s*)"
    r"((?:and\s+|,\s*)?[\"'`]?[^\s\"'`,.;]{6,})",
    re.IGNORECASE,
)


SIBLING = re.compile(r"((?:and|,)\s*)`([^`]{12,})`")


def _has_digit_and_mixed(token):
    return bool(re.search(r"[0-9]", token)) and sum(
        bool(re.search(p, token)) for p in (r"[a-z]", r"[A-Z]", r"[^A-Za-z0-9]")
    ) >= 2


def scrub_line(line):
    line = PROSE_CREDENTIAL.sub(lambda m: f"{m.group(1)}[REDACTED:prose]", line)
    line = ASSIGNMENT.sub(lambda m: f"{m.group(1)}[REDACTED:assignment]", line)
    line = QUOTED_ASSIGNMENT.sub(lambda m: f"{m.group(1)}[REDACTED:quoted]", line)
    if CREDENTIAL_LINE.search(line):
        line = SIBLING.sub(
            lambda m: f"{m.group(1)}`[REDACTED:sibling]`"
            if _has_digit_and_mixed(m.group(2))
            else m.group(0),
            line,
        )
    return line

BARE_REF = re.compile(
    r"^@?[~./\w -]*\.(?:md|py|ts|tsx|js|jsx|mjs|cjs|vue|cs|csproj|fs|json|yml|yaml"
    r"|toml|ini|cfg|sh|bash|sql|css|scss|html|txt|lock|env|xml|proto)(?:\s+.*)?$"
)

FLAGS = (
    (
        "corrects",
        r"\bactually\b|\bno i want\b|\bnot what i\b|that ?wasn'?t what|\bi said\b"
        r"|instead of|that'?s wrong|^\s*no[,!.]|\bdon'?t\b|\bstop\b|\bshouldn'?t\b",
    ),
    (
        "preference",
        r"\bi want\b|\bi prefer\b|\balways\b|\bnever\b|make sure|\bmust\b"
        r"|\bi like\b|\bgo with\b|\bmy rule\b",
    ),
    (
        "architecture",
        r"architect|\bstructur|\blayer|separat|coupl|refactor|\bservic|\bdesign"
        r"|\bpattern|cqrs|mediatr|\bddd\b|\bclean arch|\bboundar",
    ),
    (
        "stack",
        r"migrat|upgrad|\breplace|\bswitch|sqlite|postgres|nuxt|dotnet|\bfrappe\b"
        r"|erpnext|typescript|\bpython\b|\bflutter\b|\bgo lang",
    ),
    (
        "workflow",
        r"\bcommit|\bbranch|pull request|\bci\b|deploy|\bworkflow\b|\breview\b|\bpr\b",
    ),
)

COMPILED_FLAGS = tuple((name, re.compile(pattern, re.IGNORECASE | re.MULTILINE)) for name, pattern in FLAGS)


def redact(text):
    for pattern in (PRIVATE_KEY, JWT, BEARER, API_KEY, URI_CREDENTIALS, SERVER_PASSWORD):
        kind = {
            id(PRIVATE_KEY): "private-key",
            id(JWT): "jwt",
            id(BEARER): "bearer",
            id(API_KEY): "api-key",
            id(URI_CREDENTIALS): "connection-string",
            id(SERVER_PASSWORD): "connection-string",
        }[id(pattern)]
        text = pattern.sub(f"[REDACTED:{kind}]", text)
    return "\n".join(scrub_line(line) for line in text.split("\n"))


def is_bare_ref(text):
    stripped = text.strip()
    if not stripped:
        return True
    return bool(BARE_REF.match(stripped)) and len(stripped) < 200


def local_iso(millis):
    return datetime.fromtimestamp(millis / 1000).astimezone().isoformat(timespec="seconds")


def truncate(text, limit=160):
    flat = " ".join(text.split())
    return flat if len(flat) <= limit else flat[: limit - 1] + "…"


def fetch(db_path):
    uri = f"file:{db_path}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    try:
        return connection.execute(SQL).fetchall()
    finally:
        connection.close()


def extract_rows(db_path, max_len):
    rows = fetch(db_path)
    out = []
    for directory, created, text in rows:
        if not text:
            continue
        text = text.strip()
        if not text or len(text) > max_len or is_bare_ref(text):
            continue
        out.append(
            {
                "ts": local_iso(created),
                "project": os.path.basename(directory.rstrip("/")) or directory,
                "worktree": directory,
                "flags": [name for name, rx in COMPILED_FLAGS if rx.search(text)],
                "text": redact(text),
            }
        )
    return rows, out


def write_jsonl(path, records):
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_summary(path, raw_count, records):
    projects = Counter(r["project"] for r in records)
    flag_counts = Counter(f for r in records for f in r["flags"])
    candidates = [r for r in records if {"corrects", "preference"} & set(r["flags"])][:200]

    lines = [
        "# Hivemind session corpus",
        "",
        f"_Extracted {datetime.now().astimezone().isoformat(timespec='seconds')}_",
        "",
        "Scratch triage aid. Not committed. Everything here was redacted before writing.",
        "",
        "## Totals",
        "",
        "| metric | count |",
        "|---|---|",
        f"| prompts matching the SQL filter | {raw_count} |",
        f"| prompts retained after filtering | {len(records)} |",
        f"| distinct projects | {len(projects)} |",
        f"| prompts with at least one flag | {sum(1 for r in records if r['flags'])} |",
        "",
        "## Per project",
        "",
        "| project | prompts | corrects | preference |",
        "|---|---|---|---|",
    ]
    for name, count in projects.most_common():
        subset = [r for r in records if r["project"] == name]
        lines.append(
            f"| {name} | {count} | "
            f"{sum(1 for r in subset if 'corrects' in r['flags'])} | "
            f"{sum(1 for r in subset if 'preference' in r['flags'])} |"
        )

    lines += [
        "",
        "## Per flag",
        "",
        "| flag | prompts |",
        "|---|---|",
    ]
    for name in [f for f, _ in FLAGS]:
        lines.append(f"| {name} | {flag_counts.get(name, 0)} |")

    lines += [
        "",
        f"## Candidates ({len(candidates)} shown, capped at 200)",
        "",
        "| ts | project | flags | text |",
        "|---|---|---|---|",
    ]
    for record in candidates:
        flags = ", ".join(record["flags"]) or "-"
        lines.append(
            f"| {record['ts']} | {record['project']} | {flags} | {truncate(record['text'])} |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="~/.local/share/opencode/opencode.db")
    parser.add_argument("--out-dir", default="~/.cache/hivemind")
    parser.add_argument("--max-len", type=int, default=4000)
    parser.add_argument("--no-summary", action="store_true")
    args = parser.parse_args(argv)

    db_path = Path(args.db).expanduser()
    if not db_path.exists():
        print(f"database not found: {db_path}", file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    started = time.monotonic()
    raw_count, records = extract_rows(db_path, args.max_len)
    print(
        f"sql rows: {raw_count}  retained: {len(records)}  "
        f"({time.monotonic() - started:.1f}s)",
        file=sys.stderr,
    )

    jsonl = out_dir / "prompts.jsonl"
    write_jsonl(jsonl, records)
    print(f"wrote {jsonl}", file=sys.stderr)

    if not args.no_summary:
        summary = out_dir / "summary.md"
        write_summary(summary, raw_count, records)
        print(f"wrote {summary}", file=sys.stderr)

    projects = sorted({r["project"] for r in records})
    print(f"retained {len(records)} prompts across {len(projects)} projects")
    print(f"projects: {', '.join(projects)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())