import contextlib
import importlib.util
import io
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from datetime import datetime
from importlib.machinery import SourceFileLoader
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HM_PATH = REPO / "hm"

_loader = SourceFileLoader("hm", str(HM_PATH))
_spec = importlib.util.spec_from_loader("hm", _loader)
hm = importlib.util.module_from_spec(_spec)
_loader.exec_module(hm)

DEFAULT_BODY = "## What I hit\n\nSomething happened here.\n"


def git(*args, cwd):
    proc = subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True
    )
    if proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {proc.stderr}")
    return proc


class HmTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="hivemind-test-")
        self.board = Path(self.tmp) / "board"
        self.origin = Path(self.tmp) / "origin.git"
        self.board.mkdir()
        git("init", "-b", "main", cwd=self.board)
        git("config", "user.email", "test@example.com", cwd=self.board)
        git("config", "user.name", "Test User", cwd=self.board)
        git("config", "commit.gpgsign", "false", cwd=self.board)
        (self.board / ".gitignore").write_text(
            ".hivemind-tmp/\n__pycache__/\n", encoding="utf-8"
        )
        for name in ("core", "stream", "queue", "decisions", "index"):
            (self.board / name).mkdir()
        (self.board / "README.md").write_text("board\n", encoding="utf-8")
        git("add", "-A", cwd=self.board)
        git("commit", "-m", "init", cwd=self.board)
        git("init", "--bare", str(self.origin), cwd=self.tmp)
        git("symbolic-ref", "HEAD", "refs/heads/main", cwd=self.origin)
        git("remote", "add", "origin", str(self.origin), cwd=self.board)
        git("push", "-u", "origin", "main", cwd=self.board)
        git("remote", "set-head", "origin", "-a", cwd=self.board)
        os.environ["HIVEMIND_BOARD"] = str(self.board)
        self.checkout_feature_branch()

    def tearDown(self):
        os.environ.pop("HIVEMIND_BOARD", None)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def checkout_feature_branch(self, name="post/board-fixture"):
        git("checkout", "-b", name, cwd=self.board)
        self.checkout_branch = name
        return name

    def reject_pushes(self):
        """Install a pre-receive hook on the bare origin that refuses every push.

        The upstream is established first, so the rejection happens at the hook
        rather than at git's 'no upstream branch' check.
        """
        git("push", "-u", "origin", self.checkout_branch, cwd=self.board)
        hook = self.origin / "hooks" / "pre-receive"
        hook.write_text(
            "#!/bin/sh\n"
            'echo "remote: GH003: Protected branch update failed."\n'
            'echo "remote: Changes must be made through a pull request."\n'
            "exit 1\n",
            encoding="utf-8",
        )
        hook.chmod(0o755)
        return hook

    def head_sha(self):
        return git("rev-parse", "HEAD", cwd=self.board).stdout.strip()

    def config_get(self, key):
        proc = subprocess.run(
            ["git", "config", "--get", key], cwd=str(self.board),
            capture_output=True, text=True,
        )
        return proc.stdout.strip()

    def is_ancestor(self, ancestor, descendant):
        return (
            subprocess.run(
                ["git", "merge-base", "--is-ancestor", ancestor, descendant],
                cwd=str(self.board), capture_output=True, text=True,
            ).returncode == 0
        )

    def advance_remote_main(self, message="other: lands a commit on main"):
        other = Path(self.tmp) / "other"
        git("clone", str(self.origin), str(other), cwd=self.tmp)
        git("config", "user.email", "other@example.com", cwd=other)
        git("config", "user.name", "Other User", cwd=other)
        (other / "elsewhere.md").write_text("x\n", encoding="utf-8")
        git("add", "-A", cwd=other)
        git("commit", "-m", message, cwd=other)
        git("push", "origin", "main", cwd=other)
        return git("rev-parse", "HEAD", cwd=other).stdout.strip()

    def run_cli(self, *args):
        out = io.StringIO()
        err = io.StringIO()
        code = 0
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                hm.main(list(args))
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 1
        return code, out.getvalue(), err.getvalue()

    def meta(self, pid, **overrides):
        meta = {
            "id": pid,
            "title": overrides.pop("title", f"Title for {pid}"),
            "kind": overrides.pop("kind", "decision"),
            "topics": overrides.pop("topics", ["stack"]),
            "projects": overrides.pop("projects", ["proj-a"]),
            "origin": "tester",
            "posted": "2026-10-03T14:32+01:00",
            "endorsements": overrides.pop("endorsements", 0),
            "status": overrides.pop("status", "stream"),
            "promoted-to": "-",
            "supersedes": "-",
        }
        meta.update(overrides)
        return meta

    def add_post(self, pid, body=DEFAULT_BODY, **overrides):
        path = self.board / "stream" / f"{pid}.md"
        path.write_text(hm.dump_post(self.meta(pid, **overrides), body), encoding="utf-8")
        return path

    def commit_all(self, message="fixture"):
        git("add", "-A", cwd=self.board)
        git("commit", "-m", message, cwd=self.board)

    def porcelain(self):
        return git("status", "--porcelain", cwd=self.board).stdout.strip()

    def read_post(self, pid):
        return hm.load_post(self.board / "stream" / f"{pid}.md")

    def inbox_rows(self):
        path = self.board / "queue" / "inbox.md"
        if not path.is_file():
            return []
        return [
            line
            for line in path.read_text(encoding="utf-8").splitlines()
            if re.match(r"^\|\s*\d{8}-\d{4}-", line)
        ]

    def snapshot_core(self):
        core = self.board / "core"
        return {
            str(path.relative_to(core)): path.read_bytes()
            for path in sorted(core.rglob("*"))
            if path.is_file()
        }

    def snapshot_board(self):
        out = {}
        for name in ("core", "stream", "queue", "decisions", "index"):
            folder = self.board / name
            for path in sorted(folder.rglob("*")):
                if path.is_file():
                    out[str(path.relative_to(self.board))] = path.read_bytes()
        return out

    def seed_queued_post(self, pid, title="Alpha change", topic="stack"):
        """A post sitting in the queue, with its inbox row, committed on this branch."""
        self.add_post(
            pid,
            kind="decision",
            title=title,
            topics=[topic],
            status="queued",
            endorsements=3,
        )
        inbox = self.board / "queue" / "inbox.md"
        inbox.parent.mkdir(parents=True, exist_ok=True)
        inbox.write_text(
            "# Queue\n\n| title | kind | score | project links |\n"
            "| --- | --- | --- | --- |\n"
            f"| {pid} | {title} | 3 | proj-a |\n",
            encoding="utf-8",
        )
        self.commit_all()
        return pid

    def assert_rejected(self, text):
        path = Path(self.tmp) / f"junk-{abs(hash(text))}.md"
        path.write_text(text, encoding="utf-8")
        sink = io.StringIO()
        with contextlib.redirect_stderr(sink):
            with self.assertRaises(SystemExit) as ctx:
                hm.load_post(path)
        self.assertNotEqual(ctx.exception.code, 0, f"rejected with code 0: {text!r}")
        self.assertTrue(sink.getvalue().strip())

    def test_frontmatter_roundtrip(self):
        meta = {
            "id": "20261003-1432-pinia-over-vuex",
            "title": "Pinia over Vuex for new stores",
            "kind": "decision",
            "topics": ["vue", "state-management"],
            "projects": ["njeremoto-operations", "cms-system"],
            "origin": "agent-name",
            "posted": "2026-10-03T14:32+01:00",
            "endorsements": "2",
            "status": "stream",
            "promoted-to": "",
            "supersedes": "",
        }
        body = "## What I hit\n\nBody with a [bracket] and punctuation.\n"
        path = Path(self.tmp) / "roundtrip.md"
        path.write_text(hm.dump_post(meta, body), encoding="utf-8")
        parsed_meta, parsed_body = hm.load_post(path)
        self.assertEqual(parsed_meta, meta)
        self.assertEqual(parsed_body, body)
        self.assertEqual(parsed_meta["topics"], ["vue", "state-management"])
        self.assertEqual(parsed_meta["projects"], ["njeremoto-operations", "cms-system"])
        again = hm.load_post(path)
        self.assertEqual(again[0], parsed_meta)
        self.assertEqual(again[1], parsed_body)

    def test_frontmatter_rejects_junk(self):
        self.assert_rejected("---\nkey:\n  nested: 1\n---\nbody\n")
        self.assert_rejected("---\ntitle: |\n  literal text\n---\nbody\n")
        self.assert_rejected("---\ntitle: >\n  folded text\n---\nbody\n")
        self.assert_rejected("---\n\tkind: decision\n---\nbody\n")
        self.assert_rejected("---\n    kind: decision\n---\nbody\n")
        self.assert_rejected("---\nkind: decision\nkind: lesson\n---\nbody\n")
        self.assert_rejected("---\nkind: decision\n")
        self.assert_rejected("kind: decision\n---\nbody\n")
        self.assert_rejected("---\nkind: decision\n---\nbody\n---\nstatus: promoted\n")
        self.assert_rejected("---\nkind:decision\n---\nbody\n")

    def test_make_id(self):
        fixed = datetime(2026, 10, 3, 14, 32)
        pid = hm.make_id("Pinia over Vuex for New Stores!", fixed)
        self.assertRegex(pid, r"^\d{8}-\d{4}-[a-z0-9-]+$")
        self.assertEqual(pid, "20261003-1432-pinia-over-vuex-for-new-stores")

        class FixedDatetime:
            @staticmethod
            def now():
                return datetime(2026, 10, 3, 14, 32)

        original = hm.datetime
        hm.datetime = FixedDatetime
        try:
            args = (
                "post",
                "--title", "Pinia over Vuex for new stores",
                "--kind", "decision",
                "--topics", "stack",
                "--projects", "proj-a",
                "--origin", "origin",
            )
            code, _, err = self.run_cli(*args)
            self.assertEqual(code, 0, err)
            code, _, err = self.run_cli(*args)
            self.assertNotEqual(code, 0)
            self.assertIn("already exists", err)
        finally:
            hm.datetime = original

    def test_endorse_threshold(self):
        pid = "20261003-1400-pinia-over-vuex"
        self.add_post(pid, kind="decision", status="stream", endorsements=0)
        self.commit_all()

        code, _, err = self.run_cli("endorse", pid)
        self.assertEqual(code, 0, err)
        code, _, err = self.run_cli("endorse", pid)
        self.assertEqual(code, 0, err)
        meta, _ = self.read_post(pid)
        self.assertEqual(meta["status"], "stream")
        self.assertEqual(meta["endorsements"], "2")
        self.assertEqual(self.inbox_rows(), [])

        code, _, err = self.run_cli("endorse", pid)
        self.assertEqual(code, 0, err)
        meta, _ = self.read_post(pid)
        self.assertEqual(meta["status"], "queued")
        self.assertEqual(meta["endorsements"], "3")
        rows = self.inbox_rows()
        self.assertEqual(len(rows), 1)
        self.assertIn(pid, rows[0])

        code, _, err = self.run_cli("endorse", pid)
        self.assertEqual(code, 0, err)
        self.assertEqual(len(self.inbox_rows()), 1)

    def test_question_never_queues(self):
        pid = "20261003-1500-open-question"
        self.add_post(pid, kind="question", status="stream", endorsements=0, topics=["workflow"])
        self.commit_all()
        for _ in range(4):
            code, _, err = self.run_cli("endorse", pid)
            self.assertEqual(code, 0, err)
        meta, _ = self.read_post(pid)
        self.assertEqual(meta["status"], "stream")
        self.assertEqual(meta["endorsements"], "4")
        self.assertEqual(self.inbox_rows(), [])
        inbox = self.board / "queue" / "inbox.md"
        self.assertTrue(not inbox.is_file() or not inbox.read_text().strip())

    def test_ratify_is_atomic(self):
        existing = b"# Stack\n\nExisting rules stay here.\n"
        (self.board / "core" / "stack.md").write_bytes(existing)
        self.add_post(
            "20261001-0900-alpha-change",
            kind="decision",
            title="Alpha change",
            topics=["stack"],
            status="queued",
            endorsements=3,
        )
        self.add_post(
            "20261002-0900-beta-change",
            kind="decision",
            title="Beta change",
            topics=["stack"],
            status="queued",
            endorsements=3,
        )
        self.commit_all()
        before = self.snapshot_core()
        self.assertEqual(self.porcelain(), "")

        original = hm.next_adr_number
        calls = {"n": 0}

        def flaky():
            calls["n"] += 1
            if calls["n"] >= 2:
                raise RuntimeError("induced failure")
            return original()

        hm.next_adr_number = flaky
        try:
            code, _, err = self.run_cli("ratify", "--all")
        finally:
            hm.next_adr_number = original

        self.assertEqual(code, 3)
        self.assertIn("rolled back", err)
        self.assertEqual(self.snapshot_core(), before)
        self.assertEqual(self.porcelain(), "")
        self.assertEqual(list((self.board / "decisions").glob("*.md")), [])
        self.assertFalse((self.board / ".hivemind-tmp").exists())

    def test_ratify_appends_only(self):
        existing = "# Stack\n\nExisting rules stay here.\nDo not edit me.\n"
        (self.board / "core" / "stack.md").write_text(existing, encoding="utf-8")
        pid = "20261004-1100-pinia-over-vuex"
        self.add_post(
            pid,
            kind="decision",
            title="Pinia over Vuex for new stores",
            topics=["stack", "vue"],
            projects=["proj-a", "proj-b"],
            status="queued",
            endorsements=3,
        )
        self.commit_all()

        code, _, err = self.run_cli("ratify", "--all")
        self.assertEqual(code, 0, err)
        after = (self.board / "core" / "stack.md").read_text(encoding="utf-8")
        self.assertTrue(after.startswith(existing))
        self.assertEqual(after[: len(existing)], existing)
        self.assertNotEqual(after, existing)
        self.assertIn("## Pinia over Vuex for new stores", after)
        self.assertIn("Something happened here.", after)
        meta, _ = self.read_post(pid)
        self.assertEqual(meta["status"], "promoted")
        self.assertEqual(meta["promoted-to"], "core/stack.md#pinia-over-vuex-for-new-stores")
        self.assertEqual(self.porcelain(), "")

    def test_adr_numbering(self):
        first = "20261001-0800-first-move"
        self.add_post(first, title="First move", topics=["stack"], status="queued", endorsements=3)
        self.commit_all()
        code, _, err = self.run_cli("ratify", "--all")
        self.assertEqual(code, 0, err)

        second = "20261002-0800-second-move"
        self.add_post(second, title="Second move", topics=["architecture"], status="queued", endorsements=3)
        self.commit_all()
        code, _, err = self.run_cli("ratify", "--all")
        self.assertEqual(code, 0, err)

        names = sorted(path.name for path in (self.board / "decisions").glob("*.md"))
        self.assertEqual(
            names,
            ["0001-first-move.md", "0002-second-move.md"],
        )
        self.assertEqual(hm.next_adr_number(), 3)
        self.assertEqual(self.porcelain(), "")

    def test_index_regen(self):
        pid = "20261005-1000-state-management-call"
        self.add_post(
            pid,
            kind="decision",
            title="State management call",
            topics=["vue", "stack"],
            projects=["proj-a"],
            status="queued",
            endorsements=3,
        )
        self.commit_all()
        code, _, err = self.run_cli("ratify", "--all")
        self.assertEqual(code, 0, err)

        by_topic = (self.board / "index" / "by-topic.md").read_text(encoding="utf-8")
        self.assertIn("## vue", by_topic)
        self.assertIn("State management call", by_topic)
        self.assertIn("Generated file", by_topic)
        by_project = (self.board / "index" / "by-project.md").read_text(encoding="utf-8")
        self.assertIn("## proj-a", by_project)
        new = (self.board / "index" / "new.md").read_text(encoding="utf-8")
        self.assertIn("State management call", new)




    def test_ratify_rolls_back_when_push_is_rejected(self):
        pid = self.seed_queued_post("20261006-1000-alpha-change")
        before = self.snapshot_board()
        before_head = self.head_sha()
        self.reject_pushes()

        code, _, err = self.run_cli("ratify", "--all")

        self.assertEqual(code, 3, err)
        self.assertIn("rolled back", err)
        self.assertEqual(self.snapshot_board(), before)
        self.assertEqual(self.head_sha(), before_head)
        meta, _ = self.read_post(pid)
        self.assertEqual(meta["status"], "queued")
        self.assertEqual(len(self.inbox_rows()), 1)
        self.assertEqual(self.porcelain(), "")
        self.assertFalse((self.board / ".hivemind-tmp").exists())

    def test_push_failure_does_not_rebase_local_history(self):
        pid = "20261006-1100-beta-change"
        self.add_post(pid, topics=["stack"], status="stream", endorsements=0)
        self.commit_all()
        parent_before = self.head_sha()
        remote_main = self.advance_remote_main()
        self.reject_pushes()

        code, _, err = self.run_cli("endorse", pid)

        self.assertEqual(code, 2, err)
        # the endorsement is a fresh commit on top of what was already there...
        self.assertEqual(
            git("rev-parse", "HEAD^", cwd=self.board).stdout.strip(), parent_before
        )
        # ...and nothing was rebased onto the new remote main
        self.assertFalse(
            self.is_ancestor(remote_main, "HEAD"),
            "hm silently rebased local history onto the new remote main",
        )
        self.assertFalse((self.board / ".git" / "rebase-merge").exists())
        self.assertFalse((self.board / ".git" / "rebase-apply").exists())
        self.assertEqual(self.porcelain(), "")

    def test_writes_refused_on_the_default_branch(self):
        git("checkout", "main", cwd=self.board)

        code, _, err = self.run_cli(
            "post", "--title", "Stranded on main", "--kind", "lesson",
            "--topics", "stack", "--projects", "proj-a",
        )

        self.assertEqual(code, 4, err)
        self.assertIn("main", err)
        self.assertEqual(self.porcelain(), "")
        self.assertEqual(list((self.board / "stream").glob("*.md")), [])
        self.assertEqual(self.head_sha(), git("rev-parse", "main", cwd=self.board).stdout.strip())

    def test_endorse_and_ratify_also_refuse_the_default_branch(self):
        pid = self.seed_queued_post("20261006-1000-alpha-change")
        head_before = self.head_sha()
        git("checkout", "main", cwd=self.board)

        code, _, err = self.run_cli("endorse", pid)
        self.assertEqual(code, 4, err)

        code, _, err = self.run_cli("ratify", "--all")
        self.assertEqual(code, 4, err)

        git("checkout", self.checkout_branch, cwd=self.board)
        self.assertEqual(self.head_sha(), head_before)
        meta, _ = self.read_post(pid)
        self.assertEqual(meta["status"], "queued")

    def test_guard_follows_the_remote_default_branch_not_the_word_main(self):
        git("branch", "trunk", cwd=self.board)
        git("push", "-u", "origin", "trunk", cwd=self.board)
        git("remote", "set-head", "origin", "trunk", cwd=self.board)
        git("checkout", "trunk", cwd=self.board)

        code, _, err = self.run_cli(
            "post", "--title", "Stranded on trunk", "--kind", "lesson",
            "--topics", "stack", "--projects", "proj-a",
        )

        self.assertEqual(code, 4, err)
        self.assertIn("trunk", err)
        self.assertEqual(list((self.board / "stream").glob("*.md")), [])

    def test_endorse_pushes_a_branch_that_has_no_upstream(self):
        pid = "20261006-1200-gamma-change"
        self.add_post(pid, topics=["stack"], status="stream", endorsements=0)
        self.commit_all()
        self.assertEqual(
            self.config_get(f"branch.{self.checkout_branch}.merge"), ""
        )

        code, _, err = self.run_cli("endorse", pid)

        self.assertEqual(code, 0, err)
        meta, _ = self.read_post(pid)
        self.assertEqual(meta["endorsements"], "1")
        refs = git("ls-remote", "--heads", "origin", cwd=self.board).stdout
        self.assertIn(f"refs/heads/{self.checkout_branch}", refs)


class AdrSectionMappingTest(unittest.TestCase):
    def test_post_sections_map_into_adr(self):
        body = (
            "## What I hit\n\nThe thing broke.\n\n"
            "## What we decided\n\nDo the other thing.\n\n"
            "## Why\n\nBecause of reasons.\n\n"
            "## The cost\n\nYou give up speed.\n"
        )
        context, decision, consequences = hm._split_post_sections(body)
        self.assertIn("The thing broke.", context)
        self.assertIn("Because of reasons.", context)
        self.assertEqual(decision.strip(), "Do the other thing.")
        self.assertEqual(consequences.strip(), "You give up speed.")

    def test_post_sections_tolerate_missing_headings(self):
        context, decision, consequences = hm._split_post_sections("just prose, no headings")
        self.assertEqual(decision, "")
        self.assertEqual(consequences, "")
        self.assertEqual(context, "")

    def test_adr_text_has_no_empty_sections(self):
        meta = {"title": "A rule", "projects": "x, y"}
        body = "## What I hit\n\nA\n\n## What we decided\n\nB\n\n## The cost\n\nC\n"
        text = hm._adr_text(meta, body, 9, "2026-10-06")
        for section in ("## Context", "## Decision", "## Consequences"):
            tail = text.split(section, 1)[1].lstrip("\n").strip()
            self.assertNotEqual(tail, "", f"{section} is empty")


class CoreSectionShapeTest(unittest.TestCase):
    def test_demote_headings_nests_body_under_rule(self):
        body = "## What I hit\n\nA\n\n## The cost\n\nB\n"
        out = hm._ratify_section(body, "", "some-rule-slug", "Some rule slug")
        lines = out.splitlines()
        self.assertEqual(lines[0], "## Some rule slug")
        self.assertIn("### What I hit", lines)
        self.assertIn("### The cost", lines)
        self.assertNotIn("## What I hit", lines)

    def test_demote_headings_leaves_fenced_code_alone(self):
        body = "## Real\n\n```\n## not a heading\n```\n"
        out = hm._ratify_section(body, "", "slug", "Title")
        self.assertIn("## not a heading", out.splitlines())

    def test_demote_is_cumulative_for_deeper_levels(self):
        body = "### Already nested\n"
        out = hm._ratify_section(body, "", "slug", "Title")
        self.assertIn("#### Already nested", out.splitlines())

    def test_title_is_preferred_over_slug(self):
        out = hm._ratify_section("x", "", "truncated-slug", "Full Title With API")
        self.assertTrue(out.startswith("## Full Title With API"))


if __name__ == "__main__":
    unittest.main()
