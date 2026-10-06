#!/usr/bin/env python3
# Post pages render the frontmatter as a card and never the markdown body: the .md file
# is the single source of truth for prose, linked out with "View source on GitHub", so
# this build needs no markdown renderer and cannot drift from the repository's own text.

import argparse
import html
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GITHUB = "https://github.com/Stelele/hivemind/blob/main"
KINDS = ("decision", "lesson", "preference", "inspiration", "observation", "question")
LIST_KEYS = ("topics", "projects")
CORE_FILES = ("stack", "code-style", "architecture", "testing", "workflow", "communication")
KEY_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*): ?(.*)$")
FOLDED = {"|", ">", "|-", ">-", "|+", ">+", "|2", ">2"}
HEADING_RE = re.compile(r"^#\s+(.+?)\s*$")
STATUS_RE = re.compile(r"^\*\*Status:\*\*\s*(.+?)\s*$")
DATE_RE = re.compile(r"^\*\*Date:\*\*\s*(.+?)\s*$")
ADR_NUM_RE = re.compile(r"^(\d+)")
NUM_PREFIX_RE = re.compile(r"^\d+\.\s*")
UNSAFE_RE = re.compile(r"[^A-Za-z0-9._-]+")

SEARCH_JS = """(function () {
  var input = document.getElementById("search");
  var box = document.getElementById("search-results");
  if (!input || !box) return;
  var base = document.body.getAttribute("data-base") || "/", cache = null;
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function chip(kind) {
    var k = String(kind || "").toLowerCase().replace(/[^a-z0-9-]+/g, "");
    return k ? "chip chip-" + k : "chip";
  }
  function load() {
    if (cache) return Promise.resolve(cache);
    return fetch(base + "search-index.json")
      .then(function (r) {
        if (!r.ok) throw new Error("no index");
        return r.json();
      })
      .then(function (data) {
        cache = data;
        return data;
      });
  }
  function render() {
    var q = input.value.trim().toLowerCase();
    if (!q) {
      box.hidden = true;
      box.innerHTML = "";
      return;
    }
    load()
      .then(function (posts) {
        var terms = q.split(/\\s+/);
        var hits = posts.filter(function (p) {
          var hay = [p.title, (p.topics || []).join(" "), p.kind].join(" ").toLowerCase();
          return terms.every(function (t) {
            return hay.indexOf(t) !== -1;
          });
        }).slice(0, 10);
        box.hidden = hits.length === 0;
        box.innerHTML = hits
          .map(function (p) {
            return (
              '<a class="sres" href="' + base + "post/" + encodeURIComponent(p.id) + '.html">' +
              '<span class="sres-t">' + esc(p.title) + "</span>" +
              '<span class="' + chip(p.kind) + '">' + esc(p.kind || "") + "</span></a>"
            );
          })
          .join("");
      })
      .catch(function () {
        box.hidden = true;
        box.innerHTML = "";
      });
  }
  input.addEventListener("input", render);
})();
"""


def esc(value):
    return html.escape(str(value), quote=True)


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")[:48].strip("-")


def safe_name(text):
    return UNSAFE_RE.sub("-", str(text)).strip("-")


def as_list(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    return list(value)


def as_text(value):
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return ", ".join(str(item) for item in value)
    return str(value)


def parse_value(raw, key, where):
    if raw == "-":
        return [] if key in LIST_KEYS else ""
    if raw in FOLDED:
        raise ValueError(f"{where}: folded scalars are not supported")
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        return [part.strip() for part in inner.split(",") if part.strip()]
    if key in LIST_KEYS:
        return [part.strip() for part in raw.split(",") if part.strip()]
    return raw


def parse_frontmatter(text, where):
    lines = text.split("\n")
    if not lines or lines[0] != "---":
        raise ValueError(f"{where}: missing opening frontmatter delimiter")
    meta = {}
    closed = False
    index = 1
    while index < len(lines):
        line = lines[index]
        if line == "---":
            closed = True
            break
        if line == "":
            index += 1
            continue
        if line[:1] in (" ", "\t"):
            raise ValueError(f"{where}:{index + 1}: indented line")
        match = KEY_RE.match(line)
        if not match:
            raise ValueError(f"{where}:{index + 1}: malformed frontmatter line")
        key = match.group(1)
        if key in meta:
            raise ValueError(f"{where}:{index + 1}: duplicate key '{key}'")
        meta[key] = parse_value(match.group(2), key, f"{where}:{index + 1}")
        index += 1
    if not closed:
        raise ValueError(f"{where}: missing closing frontmatter delimiter")
    return meta


def make_post(meta, path):
    post_id = safe_name(as_text(meta.get("id")).strip() or path.stem)
    posted = as_text(meta.get("posted")).strip()
    title = as_text(meta.get("title")).strip() or post_id
    topics = [as_text(v).strip() for v in as_list(meta.get("topics"))]
    projects = [as_text(v).strip() for v in as_list(meta.get("projects"))]
    try:
        endorsements = int(str(meta.get("endorsements", "0")).strip() or 0)
    except ValueError:
        endorsements = 0
    return {
        "id": post_id,
        "title": title,
        "kind": as_text(meta.get("kind")).strip().lower(),
        "topics": [v for v in topics if v],
        "projects": [v for v in projects if v],
        "endorsements": endorsements,
        "status": as_text(meta.get("status")).strip(),
        "posted": posted,
        "date": posted[:10] if len(posted) >= 10 else posted,
        "origin": as_text(meta.get("origin")).strip(),
        "supersedes": as_text(meta.get("supersedes")).strip(),
        "promoted": as_text(meta.get("promoted-to")).strip(),
        "ts": post_timestamp(posted),
        "source": f"{GITHUB}/stream/{safe_name(post_id)}.md",
    }


def post_timestamp(posted):
    if not posted:
        return 0.0
    try:
        return datetime.fromisoformat(posted).timestamp()
    except ValueError:
        return 0.0


def load_posts():
    posts = []
    skipped = 0
    stream = REPO / "stream"
    if stream.is_dir():
        for path in sorted(stream.glob("*.md")):
            try:
                meta = parse_frontmatter(path.read_text(encoding="utf-8"), path.name)
                posts.append(make_post(meta, path))
            except (OSError, ValueError):
                skipped += 1
    return posts, skipped


def load_adrs():
    adrs = []
    folder = REPO / "decisions"
    if not folder.is_dir():
        return adrs
    for path in sorted(folder.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        number = ADR_NUM_RE.match(path.name)
        label = number.group(1) if number else str(len(adrs) + 1).zfill(4)
        adrs.append({
            "number": label,
            "anchor": f"adr-{label}",
            "title": heading_of(text, path.stem),
            "status": line_field(text, STATUS_RE),
            "date": line_field(text, DATE_RE),
            "href": f"{GITHUB}/decisions/{path.name}",
        })
    return adrs


def heading_of(text, fallback):
    for line in text.split("\n"):
        match = HEADING_RE.match(line)
        if match:
            return NUM_PREFIX_RE.sub("", match.group(1)).strip()
    return fallback


def line_field(text, pattern):
    for line in text.split("\n"):
        match = pattern.match(line)
        if match:
            return match.group(1).strip()
    return ""


def newest_first(posts):
    return sorted(posts, key=lambda p: (-p["ts"], p["id"]))


def by_score(posts):
    return sorted(posts, key=lambda p: (-p["endorsements"], -p["ts"], p["id"]))


def group_posts(posts, field):
    groups = {}
    for post in posts:
        for value in post[field]:
            key = slug(value)
            if not key:
                continue
            entry = groups.setdefault(key, {"name": value, "posts": []})
            entry["posts"].append(post)
    return groups


def kind_chip(kind):
    if not kind:
        return ""
    suffix = f" chip-{kind}" if kind in KINDS else ""
    return f'<span class="chip{suffix}">{esc(kind)}</span>'


def post_list(posts, base):
    if not posts:
        return '<p class="empty">No posts yet.</p>'
    head = (
        '<div class="list-head"><span>Title</span><span>Kind</span>'
        '<span>Score</span><span>Posted</span></div>'
    )
    rows = "".join(
        f'<a class="row" href="{esc(base)}post/{esc(post["id"])}.html">'
        f'<span class="r-title">{esc(post["title"])}</span>'
        f'<span class="r-kind">{kind_chip(post["kind"])}</span>'
        f'<span class="score">{post["endorsements"]}</span>'
        f'<span class="r-date">{esc(post["date"])}</span></a>'
        for post in posts
    )
    return f'<div class="list">{head}{rows}</div>'


def pill(label, href, count=None):
    badge = f' <span class="pill-n">{count}</span>' if count is not None else ""
    return f'<a class="pill" href="{esc(href)}">{esc(label)}{badge}</a>'


def pills(groups, base, prefix):
    return "".join(
        pill(entry["name"], f'{base}{prefix}/{key}.html', len(entry["posts"]))
        for key, entry in sorted(groups.items(), key=lambda kv: kv[1]["name"].lower())
    )


def tag_pills(values, base, prefix):
    return "".join(pill(value, f"{base}{prefix}/{slug(value)}.html") for value in values)


def nav(base, active):
    parts = []
    for href, label, key in (("", "Home", "home"), ("core.html", "Core", "core"),
                             ("decisions.html", "Decisions", "decisions")):
        current = ' aria-current="page"' if key == active else ""
        parts.append(f'<a href="{esc(base + href)}"{current}>{label}</a>')
    return "".join(parts)


def layout(title, base, body, active=""):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<link rel="stylesheet" href="{esc(base)}assets/style.css">
</head>
<body data-base="{esc(base)}">
<header class="site-header">
<div class="wrap header-inner">
<a class="brand" href="{esc(base)}">hivemind</a>
<nav class="nav" aria-label="Main">{nav(base, active)}</nav>
<div class="search">
<label class="sr-only" for="search">Search posts</label>
<input id="search" type="search" placeholder="Search posts" autocomplete="off">
<div id="search-results" class="search-results" hidden></div>
</div>
</div>
</header>
<main class="wrap">
{body}
</main>
<footer class="site-footer"><div class="wrap"><p>hivemind — generated from this repository by <code>tools/build_site.py</code>. Every post links back to its markdown source.</p></div></footer>
<script src="{esc(base)}assets/search.js" defer></script>
</body>
</html>
"""


def index_page(posts, topics, projects, base):
    parts = [
        "<h1>hivemind</h1>",
        '<p class="lede">One file per post in <code>stream/</code> — decisions, lessons, '
        "preferences, questions. Ranked by endorsement, then by date.</p>",
    ]
    browse = []
    if topics:
        browse.append(
            f'<div class="pillrow"><span class="pill-label">Topics</span>'
            f'{pills(topics, base, "topic")}</div>'
        )
    if projects:
        browse.append(
            f'<div class="pillrow"><span class="pill-label">Projects</span>'
            f'{pills(projects, base, "project")}</div>'
        )
    if browse:
        parts.append('<section class="browse">' + "".join(browse) + "</section>")
    parts.append(f"<section><h2>Posts</h2>{post_list(by_score(posts), base)}</section>")
    return layout("hivemind", base, "\n".join(parts), "home")


def browse_page(name, posts, groups, base, prefix):
    count = len(posts)
    parts = [
        f"<h1>{esc(name)}</h1>",
        f'<p class="lede">{count} post{"s" if count != 1 else ""}</p>',
        f'<div class="pillrow">{pills(groups, base, prefix)}</div>',
        post_list(newest_first(posts), base),
    ]
    return layout(f"{name} · hivemind", base, "\n".join(parts))


def post_page(post, base):
    topic_row = tag_pills(post["topics"], base, "topic") \
        if post["topics"] else '<span class="muted">none</span>'
    project_row = tag_pills(post["projects"], base, "project") \
        if post["projects"] else '<span class="muted">none</span>'
    facts = [
        f'<div><dt>id</dt><dd><code>{esc(post["id"])}</code></dd></div>',
        f'<div><dt>status</dt><dd>{esc(post["status"] or "-")}</dd></div>',
        f'<div><dt>origin</dt><dd>{esc(post["origin"] or "-")}</dd></div>',
        f'<div><dt>posted</dt><dd>{esc(post["posted"] or "-")}</dd></div>',
    ]
    if post["supersedes"] and post["supersedes"] != "-":
        facts.append(
            f'<div><dt>supersedes</dt><dd><code>{esc(post["supersedes"])}</code></dd></div>'
        )
    if post["promoted"] and post["promoted"] != "-":
        facts.append(
            f'<div><dt>promoted to</dt><dd><code>{esc(post["promoted"])}</code></dd></div>'
        )
    body = [
        '<article class="card post">',
        '<div class="post-top">',
        kind_chip(post["kind"]) or '<span class="chip">post</span>',
        f'<span class="score score-lg">{post["endorsements"]}</span>',
        f'<span class="muted">{post["endorsements"]} endorsement'
        f'{"s" if post["endorsements"] != 1 else ""}</span>',
        f'<span class="muted">{esc(post["date"])}</span>',
        "</div>",
        f'<h1>{esc(post["title"])}</h1>',
        f'<div class="pillrow"><span class="pill-label">Topics</span>{topic_row}</div>',
        f'<div class="pillrow"><span class="pill-label">Projects</span>{project_row}</div>',
        '<dl class="facts">' + "".join(facts) + "</dl>",
        f'<a class="btn-source" href="{esc(post["source"])}">View source on GitHub</a>',
        '<p class="note">This page shows the post&rsquo;s frontmatter only. The prose lives '
        "in the markdown file — one source of truth, rendered exactly as written.</p>",
        "</article>",
    ]
    return layout(f"{post['title']} · hivemind", base, "\n".join(body))


def core_page(base, adrs):
    head = '<div class="list-head list-head-wide"><span>File</span><span>Document</span></div>'
    rows = []
    for name in CORE_FILES:
        path = REPO / "core" / f"{name}.md"
        try:
            title = heading_of(path.read_text(encoding="utf-8"), name)
        except OSError:
            title = name
        rows.append(
            f'<a class="row" href="{esc(GITHUB)}/core/{name}.md">'
            f'<span class="r-title">{esc(name)}.md</span>'
            f'<span class="r-sub">{esc(title)}</span></a>'
        )
    adr_rows = "".join(
        f'<li><a href="{esc(base)}decisions.html#{esc(adr["anchor"])}">'
        f'{esc(adr["number"])}. {esc(adr["title"])}</a></li>'
        for adr in adrs
    )
    body = [
        "<h1>Core</h1>",
        '<p class="lede">The ratified tier: six files treated as law, each rule backed by '
        "a numbered decision record.</p>",
        f'<div class="list list-wide">{head}{"".join(rows)}</div>',
        f"<h2>Decisions ({len(adrs)})</h2>",
        '<ol class="adrs">' + adr_rows + "</ol>",
    ]
    return layout("Core · hivemind", base, "\n".join(body), "core")


def decisions_page(base, adrs):
    items = []
    for adr in adrs:
        meta = []
        if adr["status"]:
            meta.append(f'<span class="pill">{esc(adr["status"])}</span>')
        if adr["date"]:
            meta.append(f'<span class="muted">{esc(adr["date"])}</span>')
        items.append(
            f'<li id="{esc(adr["anchor"])}"><a href="{esc(adr["href"])}">'
            f'{esc(adr["number"])}. {esc(adr["title"])}</a>'
            f'<span class="adr-meta">{"".join(meta)}</span></li>'
        )
    body = [
        "<h1>Decisions</h1>",
        f'<p class="lede">{len(adrs)} records, each linking to its file in the repository.</p>',
        '<ol class="adrs">' + "".join(items) + "</ol>",
    ]
    return layout("Decisions · hivemind", base, "\n".join(body), "decisions")


def search_index(posts):
    return [
        {
            "id": post["id"],
            "title": post["title"],
            "kind": post["kind"],
            "topics": post["topics"],
            "projects": post["projects"],
            "endorsements": post["endorsements"],
            "status": post["status"],
            "posted": post["posted"],
        }
        for post in newest_first(posts)
    ]


def write_file(root, relative, content):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def human_size(total):
    if total < 1024:
        return f"{total} B"
    if total < 1024 * 1024:
        return f"{total / 1024:.1f} KB"
    return f"{total / (1024 * 1024):.1f} MB"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build the static hivemind site.")
    parser.add_argument("--out", default="_site", help="output directory (default: _site)")
    parser.add_argument("--base-url", default="/",
                        help="prefix for every internal link (default: /)")
    args = parser.parse_args(argv)

    style = REPO / "assets" / "style.css"
    if not style.is_file():
        print(f"missing stylesheet: {style}", file=sys.stderr)
        return 1

    out = Path(args.out)
    if not out.is_absolute():
        out = REPO / out
    out = out.resolve()
    if out in (REPO.resolve(), Path("/"), Path.home().resolve()):
        print(f"refusing to build into {out}", file=sys.stderr)
        return 1

    base = args.base_url or "/"
    if not base.endswith("/"):
        base += "/"

    posts, skipped = load_posts()
    adrs = load_adrs()
    topics = group_posts(posts, "topics")
    projects = group_posts(posts, "projects")

    pages = {
        "index.html": index_page(posts, topics, projects, base),
        "core.html": core_page(base, adrs),
        "decisions.html": decisions_page(base, adrs),
    }
    for key, entry in topics.items():
        pages[f"topic/{key}.html"] = browse_page(entry["name"], entry["posts"], topics, base, "topic")
    for key, entry in projects.items():
        pages[f"project/{key}.html"] = browse_page(entry["name"], entry["posts"], projects, base, "project")
    for post in posts:
        pages[f"post/{post['id']}.html"] = post_page(post, base)

    if out.exists():
        shutil.rmtree(out)
    for relative, content in pages.items():
        write_file(out, relative, content)
    write_file(out, "search-index.json",
               json.dumps(search_index(posts), separators=(",", ":")))
    write_file(out, "assets/search.js", SEARCH_JS)
    shutil.copyfile(style, out / "assets" / "style.css")

    total = sum(path.stat().st_size for path in out.rglob("*") if path.is_file())
    if skipped:
        print(f"skipped {skipped} file(s) with unparseable frontmatter")
    print(f"built {len(pages)} pages, {len(posts)} posts, {len(topics)} topics, "
          f"{len(projects)} projects -> {out} ({human_size(total)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
