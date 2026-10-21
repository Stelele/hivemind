import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from datetime import datetime
from unittest import mock
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
        if hasattr(self, "_saved_path"):
            os.environ["PATH"] = self._saved_path
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

    def add_remote(self, name="mirror"):
        path = Path(self.tmp) / f"{name}.git"
        git("init", "--bare", str(path), cwd=self.tmp)
        git("remote", "add", name, str(path), cwd=self.board)
        return path

    def reject_pushes_to(self, path):
        hook = Path(path) / "hooks" / "pre-receive"
        hook.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        hook.chmod(0o755)
        return hook

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

    def install_fake_gh(self, existing_pr=None, create_number=7, merge_fail=(), list_prs=None):
        """Put a fake `gh` on PATH that records its argv and behaves predictably."""
        bindir = Path(self.tmp) / "fake-bin"
        bindir.mkdir(exist_ok=True)
        self.gh_log = Path(self.tmp) / "gh.log"
        self.gh_log.write_text("", encoding="utf-8")
        script = f'''#!/usr/bin/env python3
import json, sys
args = sys.argv[1:]
with open({str(self.gh_log)!r}, "a", encoding="utf-8") as log:
    log.write(" ".join(args) + "\\n")
if args[:2] == ["pr", "view"]:
    existing = {existing_pr!r}
    if existing:
        print(json.dumps(existing))
        sys.exit(0)
    sys.exit(1)
if args[:2] == ["pr", "create"]:
    print("https://github.com/example/board/pull/{create_number}")
    sys.exit(0)
if args[:2] == ["pr", "merge"]:
    target = args[2] if len(args) > 2 else ""
    sys.exit(1 if target in {set(map(str, merge_fail))!r} else 0)
if args[:2] == ["pr", "list"]:
    print(json.dumps({list_prs or []!r}))
    sys.exit(0)
sys.exit(0)
'''
        path = bindir / "gh"
        path.write_text(script, encoding="utf-8")
        path.chmod(0o755)
        self._saved_path = os.environ.get("PATH", "")
        os.environ["PATH"] = str(bindir) + os.pathsep + self._saved_path
        return path

    def gh_calls(self):
        return [
            line
            for line in self.gh_log.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def current_branch(self):
        return git("rev-parse", "--abbrev-ref", "HEAD", cwd=self.board).stdout.strip()

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

    def test_push_failure_names_the_remote_it_actually_used(self):
        mirror = self.add_remote("mirror")
        self.reject_pushes_to(mirror)

        code, _, err = self.run_cli(
            "post", "--title", "Wrong remote named", "--kind", "lesson",
            "--topics", "stack", "--projects", "proj-a", "--remote", "mirror",
        )

        self.assertEqual(code, 2, err)
        self.assertIn("mirror", err)
        self.assertNotIn("git pull --rebase origin ", err)

    def test_stale_default_branch_symref_cannot_unprotect_main(self):
        # simulate a remote whose default branch was renamed: the symref is stale
        git("branch", "trunk", cwd=self.board)
        git("push", "origin", "trunk", cwd=self.board)
        git("remote", "set-head", "origin", "trunk", cwd=self.board)
        git("update-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk", cwd=self.board)
        git("checkout", "main", cwd=self.board)

        code, _, err = self.run_cli(
            "post", "--title", "Stale symref probe", "--kind", "lesson",
            "--topics", "stack", "--projects", "proj-a",
        )

        self.assertEqual(code, 4, err)
        self.assertIn("main", err)

    def post_args(self, **overrides):
        args = [
            "post", "--title", overrides.pop("title", "Auto merge me"),
            "--kind", "lesson", "--topics", "stack", "--projects", "proj-a",
        ]
        for key, value in overrides.items():
            args.extend([f"--{key.replace('_', '-')}", value])
        return args

    def test_post_opens_a_pr_and_merges_it(self):
        self.install_fake_gh()

        code, out, err = self.run_cli(*self.post_args())

        self.assertEqual(code, 0, err)
        calls = self.gh_calls()
        self.assertIn(
            "pr create --base main --head post/board-fixture "
            "--title post: Auto merge me",
            " ".join(calls),
        )
        self.assertTrue(
            any(call.startswith("pr merge 7 --rebase") for call in calls), calls
        )
        self.assertIn("merged PR #7", out)
        self.assertEqual(self.current_branch(), "main")

    def test_post_reuses_an_open_pr_instead_of_opening_a_duplicate(self):
        self.install_fake_gh(
            existing_pr={
                "number": 9,
                "url": "https://github.com/example/board/pull/9",
                "state": "OPEN",
            }
        )

        code, out, err = self.run_cli(*self.post_args())

        self.assertEqual(code, 0, err)
        calls = self.gh_calls()
        self.assertFalse(any(call.startswith("pr create") for call in calls), calls)
        self.assertTrue(any(call.startswith("pr merge 9") for call in calls), calls)
        self.assertIn("https://github.com/example/board/pull/9", out)

    def test_post_no_merge_leaves_the_pr_open(self):
        self.install_fake_gh()

        code, out, err = self.run_cli(*self.post_args(), "--no-merge")

        self.assertEqual(code, 0, err)
        calls = self.gh_calls()
        self.assertTrue(any(call.startswith("pr create") for call in calls), calls)
        self.assertFalse(any(call.startswith("pr merge") for call in calls), calls)
        self.assertIn("hm merge 7", out)
        self.assertEqual(self.current_branch(), self.checkout_branch)

    def test_post_no_pr_keeps_the_old_push_only_path(self):
        self.install_fake_gh()

        code, out, err = self.run_cli(*self.post_args(), "--no-pr")

        self.assertEqual(code, 0, err)
        self.assertEqual(self.gh_calls(), [])
        self.assertIn("posted", out)
        self.assertEqual(self.current_branch(), self.checkout_branch)

    def test_post_survives_a_machine_without_gh(self):
        with mock.patch.object(hm.shutil, "which", return_value=None):
            code, _, err = self.run_cli(*self.post_args())

        self.assertEqual(code, 0, err)
        self.assertIn("gh", err)
        self.assertIn("gh pr create --base main --head post/board-fixture", err)
        refs = git("ls-remote", "--heads", "origin", cwd=self.board).stdout
        self.assertIn(f"refs/heads/{self.checkout_branch}", refs)

    def test_post_reports_a_merge_failure_without_failing_the_post(self):
        self.install_fake_gh(merge_fail={7})

        code, out, err = self.run_cli(*self.post_args())

        self.assertEqual(code, 0, err)
        self.assertIn("hm merge 7", out + err)
        self.assertEqual(self.current_branch(), self.checkout_branch)

    def test_merge_all_merges_every_open_pr_and_reports_failures(self):
        self.install_fake_gh(
            merge_fail={13},
            list_prs=[
                {"number": 12, "headRefName": "post/one"},
                {"number": 13, "headRefName": "post/two"},
            ],
        )

        code, out, err = self.run_cli("merge", "--all")

        self.assertEqual(code, 1, out + err)
        self.assertIn("merged #12 post/one", out)
        self.assertIn("#13", out + err)
        calls = self.gh_calls()
        self.assertTrue(any(call.startswith("pr merge 12 --rebase") for call in calls), calls)
        self.assertTrue(any(call.startswith("pr merge 13 --rebase") for call in calls), calls)

    def test_merge_requires_a_target_or_all(self):
        self.install_fake_gh()

        code, _, err = self.run_cli("merge")

        self.assertEqual(code, 1, err)
        self.assertIn("--all", err)
        self.assertEqual(self.gh_calls(), [])

    def test_post_leaves_a_pr_open_on_a_non_post_branch(self):
        self.checkout_feature_branch("feat/unrelated-work")
        self.install_fake_gh()

        code, out, err = self.run_cli(*self.post_args())

        self.assertEqual(code, 0, err)
        self.assertFalse(
            any(call.startswith("pr merge") for call in self.gh_calls()),
            "hm auto-merged a feature branch that only happened to carry a post",
        )
        self.assertIn("hm merge 7", out)
        self.assertEqual(self.current_branch(), "feat/unrelated-work")

    def test_endorse_leaves_an_existing_upstream_alone(self):
        # a branch deliberately tracking a mirror rather than origin
        mirror = self.add_remote("mirror")
        pid = "20261006-1300-delta-change"
        self.add_post(pid, topics=["stack"], status="stream", endorsements=0)
        self.commit_all()
        git("config", f"branch.{self.checkout_branch}.remote", "mirror", cwd=self.board)
        git("config",
            f"branch.{self.checkout_branch}.merge",
            f"refs/heads/{self.checkout_branch}", cwd=self.board)
        git("push", "mirror", self.checkout_branch, cwd=self.board)

        code, _, err = self.run_cli("endorse", pid)

        self.assertEqual(code, 0, err)
        self.assertEqual(
            self.config_get(f"branch.{self.checkout_branch}.remote"), "mirror",
            "hm silently retargeted an upstream the user had already chosen",
        )
        mirror_heads = git("ls-remote", "--heads", "mirror", cwd=self.board).stdout
        self.assertIn(f"refs/heads/{self.checkout_branch}", mirror_heads)

    def test_rollback_message_does_not_advise_pushing_a_discarded_commit(self):
        self.seed_queued_post("20261006-1400-epsilon-change")
        self.reject_pushes()

        code, out, err = self.run_cli("ratify", "--all")

        self.assertEqual(code, 3, err)
        self.assertIn("rolled back", err)
        self.assertIn("push", err.lower())
        self.assertNotIn(
            "git pull --rebase", err,
            "the rollback discarded the commit the message tells you to push",
        )

    CORE_FIXTURE = (
        "# Workflow — git, commits, CI, verification\n"
        "\n"
        "## Never commit, push, or open a PR without an explicit instruction\n"
        "\n"
        "Ask before you write.\n"
        "\n"
        "  *Evidence: 2026-06-05.*\n"
        "  → [ADR 0001](../decisions/0001-never-commit-without-an-explicit-instruction.md)\n"
        "  *(superseded 2026-10-07 by ADR 0049)*\n"
        "\n"
        "## Batch the change, then test once\n"
        "\n"
        "Not per edit.\n"
        "\n"
        "### Not per edit\n"
        "\n"
        "The sub-heading belongs to its parent rule.\n"
    )

    INDEX_FIXTURE = (
        "# Core — the always-read tier\n"
        "\n"
        "| If you are doing… | Read |\n"
        "|---|---|\n"
        "| tests, CI, deploys, commits, branches | `workflow.md` |\n"
        "\n"
        "## The five that matter most\n"
        "\n"
        "1. **Never commit, push, or open a PR without an explicit instruction.**"
        " — [workflow](workflow.md#never-commit-push-or-open-a-pr-without-an-explicit-instruction)\n"
        "2. **Make the change, then run the tests once.** Not per edit."
        " — [workflow](workflow.md#batch-the-change-then-test-once)\n"
    )

    def seed_core(self, slug=None):
        """A core/workflow.md with two rules, an index that links them, and one ADR."""
        (self.board / "core" / "workflow.md").write_text(self.CORE_FIXTURE, encoding="utf-8")
        (self.board / "core" / "INDEX.md").write_text(self.INDEX_FIXTURE, encoding="utf-8")
        adr = self.board / "decisions" / "0052-agents-commit-freely.md"
        adr.write_text("# 0052. Agents commit freely\n", encoding="utf-8")
        self.commit_all()
        return slug or "never-commit-push-or-open-a-pr-without-an-explicit-instruction"

    def core_text(self, name="workflow"):
        return (self.board / "core" / f"{name}.md").read_text(encoding="utf-8")

    def archive_text(self, name="workflow"):
        path = self.board / "archive" / f"{name}.md"
        return path.read_text(encoding="utf-8") if path.is_file() else None

    def test_supersede_removes_the_rule_from_core(self):
        slug = self.seed_core()

        code, out, err = self.run_cli(
            "supersede", "--slug", slug, "--in", "workflow", "--withdrawn-by", "0052",
        )

        self.assertEqual(code, 0, err)
        after = self.core_text()
        self.assertNotIn("Never commit, push, or open a PR", after)
        self.assertIn("## Batch the change, then test once", after)
        self.assertIn("The sub-heading belongs to its parent rule.", after)
        self.assertTrue(after.startswith("# Workflow"))

    def test_supersede_archives_the_original_text_verbatim(self):
        slug = self.seed_core()

        code, _, err = self.run_cli(
            "supersede", "--slug", slug, "--in", "workflow", "--withdrawn-by", "0052",
        )

        self.assertEqual(code, 0, err)
        archived = self.archive_text()
        self.assertIn("## Never commit, push, or open a PR without an explicit instruction", archived)
        self.assertIn("Ask before you write.", archived)
        self.assertIn("*(superseded 2026-10-07 by ADR 0049)*", archived)
        self.assertIn("0052-agents-commit-freely.md", archived)
        self.assertIn("Withdrawn", archived)

    LINKED_CORE_FIXTURE = (
        "# Workflow\n"
        "\n"
        "## Never commit without being asked\n"
        "\n"
        "The agent-side half is **withdrawn** — see\n"
        "[Agents commit freely](#agents-commit-freely-to-feature-branches-the-default-branch-stays-pr-only)\n"
        "and [ADR 0052](../decisions/0052-x.md) for why.\n"
        "\n"
        "## Agents commit freely to feature branches; the default branch stays PR-only\n"
        "\n"
        "The live rule.\n"
    )

    def test_supersede_repairs_fragment_links_that_point_back_into_core(self):
        core = self.board / "core" / "workflow.md"
        core.write_text(self.LINKED_CORE_FIXTURE, encoding="utf-8")
        (self.board / "core" / "INDEX.md").write_text(
            "# Core\n\n1. **never commit** — "
            "[workflow](workflow.md#never-commit-without-being-asked)\n", encoding="utf-8"
        )
        (self.board / "decisions" / "0052-agents-commit-freely.md").write_text(
            "# 0052. Agents commit freely\n", encoding="utf-8"
        )
        self.commit_all()

        code, _, err = self.run_cli(
            "supersede", "--slug", "never-commit-without-being-asked",
            "--in", "workflow", "--withdrawn-by", "0052",
        )

        self.assertEqual(code, 0, err)
        archived = self.archive_text()
        self.assertIn(
            "(../core/workflow.md#agents-commit-freely-to-feature-branches-"
            "the-default-branch-stays-pr-only)", archived,
            "a fragment link in the moved section no longer resolves to its target",
        )
        self.assertNotIn("](#agents-commit-freely", archived)
        # a path-relative link to decisions/ is still correct from archive/
        self.assertIn("(../decisions/0052-x.md)", archived)

    def test_supersede_repairs_nothing_when_the_fragment_has_no_heading(self):
        core = self.board / "core" / "workflow.md"
        core.write_text(
            self.LINKED_CORE_FIXTURE.replace(
                "[Agents commit freely](#agents-commit-freely-to-feature-branches-"
                "the-default-branch-stays-pr-only)",
                "[Something else](#no-such-heading)",
            ),
            encoding="utf-8",
        )
        (self.board / "decisions" / "0052-agents-commit-freely.md").write_text(
            "# 0052. Agents commit freely\n", encoding="utf-8"
        )
        self.commit_all()

        code, _, err = self.run_cli(
            "supersede", "--slug", "never-commit-without-being-asked",
            "--in", "workflow", "--withdrawn-by", "0052",
        )

        self.assertEqual(code, 0, err)
        self.assertIn("](#no-such-heading)", self.archive_text())

    def test_supersede_records_a_note_when_given(self):
        slug = self.seed_core()

        code, _, err = self.run_cli(
            "supersede", "--slug", slug, "--in", "workflow", "--withdrawn-by", "0052",
            "--note", "ADR 0052 withdrew the agent-side half.",
        )

        self.assertEqual(code, 0, err)
        self.assertIn("ADR 0052 withdrew the agent-side half.", self.archive_text())

    def test_supersede_drops_the_stale_index_bullet(self):
        slug = self.seed_core()

        code, _, err = self.run_cli(
            "supersede", "--slug", slug, "--in", "workflow", "--withdrawn-by", "0052",
        )

        self.assertEqual(code, 0, err)
        index = (self.board / "core" / "INDEX.md").read_text(encoding="utf-8")
        self.assertNotIn("without-an-explicit-instruction", index)
        self.assertIn("#batch-the-change-then-test-once", index)

    def test_supersede_renumbers_the_list_it_left_a_hole_in(self):
        slug = self.seed_core()

        code, _, err = self.run_cli(
            "supersede", "--slug", slug, "--in", "workflow", "--withdrawn-by", "0052",
        )

        self.assertEqual(code, 0, err)
        index = (self.board / "core" / "INDEX.md").read_text(encoding="utf-8")
        # one bullet removed, so one remains — and it must be 1, not the 2 it was
        numbers = re.findall(r"^(\d+)\. \*\*", index, flags=re.M)
        self.assertEqual(numbers, ["1"], "the list kept its old numbering")
        self.assertIn("Make the change", index)

    def test_supersede_leaves_unrelated_numbered_lists_alone(self):
        self.seed_core()
        index_path = self.board / "core" / "INDEX.md"
        index_path.write_text(
            self.INDEX_FIXTURE
            + "\n## Elsewhere\n\n1. one\n2. two\n3. three\n",
            encoding="utf-8",
        )
        self.commit_all("fixture: extra list")

        code, _, err = self.run_cli(
            "supersede", "--slug", "never-commit-push-or-open-a-pr-without-an-explicit-instruction",
            "--in", "workflow", "--withdrawn-by", "0052",
        )

        self.assertEqual(code, 0, err)
        index = index_path.read_text(encoding="utf-8")
        self.assertIn("\n1. one\n2. two\n3. three\n", index)

    FIVE_FIXTURE = (
        "# Core\n\n## The five that matter most\n\nProse.\n\n"
        "1. **Never commit.** — [workflow](workflow.md#never-commit)\n"
        "2. **Test once.** — [workflow](workflow.md#test-once)\n"
        "3. **Read the docs.** — [architecture](architecture.md#read-the-docs)\n"
        "4. **Show reasoning.** — [communication](communication.md#show-reasoning)\n"
        "5. **Simplicity first.** — [architecture](architecture.md#simplicity-first)\n"
    )

    def seed_five(self):
        (self.board / "core" / "workflow.md").write_text(
            "# Workflow\n\n## Never commit\n\nbody\n\n## Test once\n\nbody\n"
            "## Read the docs\n\nbody\n\n## Show reasoning\n\nbody\n"
            "## Simplicity first\n\nbody\n",
            encoding="utf-8",
        )
        (self.board / "core" / "architecture.md").write_text(
            "# Architecture\n\n## Read the docs\n\nbody\n\n## Simplicity first\n\nbody\n",
            encoding="utf-8",
        )
        (self.board / "core" / "communication.md").write_text(
            "# Communication\n\n## Show reasoning\n\nbody\n", encoding="utf-8"
        )
        (self.board / "core" / "INDEX.md").write_text(self.FIVE_FIXTURE, encoding="utf-8")
        (self.board / "decisions" / "0052-x.md").write_text("# 0052\n", encoding="utf-8")
        self.commit_all()

    def test_supersede_fixes_a_count_the_removal_invalidated(self):
        self.seed_five()

        code, _, err = self.run_cli(
            "supersede", "--slug", "never-commit", "--in", "workflow",
            "--withdrawn-by", "0052",
        )

        self.assertEqual(code, 0, err)
        index = (self.board / "core" / "INDEX.md").read_text(encoding="utf-8")
        self.assertIn("## The four that matter most", index)
        self.assertNotIn("## The five that matter most", index)
        self.assertEqual(re.findall(r"^(\d+)\. \*\*", index, flags=re.M),
                         ["1", "2", "3", "4"])

    def test_supersede_leaves_a_count_it_did_not_invalidate(self):
        self.seed_five()
        index_path = self.board / "core" / "INDEX.md"
        index_path.write_text(
            self.FIVE_FIXTURE.replace("## The five", "## The three"), encoding="utf-8"
        )
        self.commit_all("fixture: wrong count already")

        code, _, err = self.run_cli(
            "supersede", "--slug", "never-commit", "--in", "workflow",
            "--withdrawn-by", "0052",
        )

        self.assertEqual(code, 0, err)
        self.assertIn(
            "## The three that matter most",
            index_path.read_text(encoding="utf-8"),
            "rewrote a count this operation did not invalidate",
        )

    def test_supersede_fixes_a_digit_count_too(self):
        self.seed_five()
        index_path = self.board / "core" / "INDEX.md"
        index_path.write_text(
            self.FIVE_FIXTURE.replace("## The five", "## Top 5"), encoding="utf-8"
        )
        self.commit_all("fixture: digit count")

        code, _, err = self.run_cli(
            "supersede", "--slug", "never-commit", "--in", "workflow",
            "--withdrawn-by", "0052",
        )

        self.assertEqual(code, 0, err)
        self.assertIn("## Top 4", index_path.read_text(encoding="utf-8"))

    def test_supersede_matches_a_title_case_count_and_keeps_its_case(self):
        self.seed_five()
        index_path = self.board / "core" / "INDEX.md"
        index_path.write_text(
            self.FIVE_FIXTURE.replace("## The five", "## The Five"), encoding="utf-8"
        )
        self.commit_all("fixture: title case")

        code, _, err = self.run_cli(
            "supersede", "--slug", "never-commit", "--in", "workflow",
            "--withdrawn-by", "0052",
        )

        self.assertEqual(code, 0, err)
        index = index_path.read_text(encoding="utf-8")
        self.assertIn("## The Four that matter most", index)
        self.assertNotIn("## The Five that matter most", index)

    def test_supersede_repairs_a_link_to_a_surviving_subheading(self):
        core = self.board / "core" / "workflow.md"
        core.write_text(
            "# Workflow\n\n## Never commit\n\nsee [the sub rule](#the-sub-rule)\n\n"
            "## Surviving rule\n\nbody\n\n### The sub rule\n\nbody\n",
            encoding="utf-8",
        )
        (self.board / "core" / "INDEX.md").write_text(
            "# Core\n\n1. **never commit** — "
            "[workflow](workflow.md#never-commit)\n", encoding="utf-8"
        )
        (self.board / "decisions" / "0052-x.md").write_text("# 0052\n", encoding="utf-8")
        self.commit_all()

        code, _, err = self.run_cli(
            "supersede", "--slug", "never-commit", "--in", "workflow",
            "--withdrawn-by", "0052",
        )

        self.assertEqual(code, 0, err)
        self.assertIn(
            "(../core/workflow.md#the-sub-rule)", self.archive_text(),
            "a link to a surviving ### subheading was left as a bare fragment",
        )

    def test_supersede_accepts_the_truncated_slug_too(self):
        heading = "Never commit, push, or open a PR without an explicit instruction"
        self.seed_core()
        truncated = hm._slug(heading)
        self.assertNotEqual(truncated, hm._anchor(heading), "precondition: the two forms differ")

        code, _, err = self.run_cli(
            "supersede", "--slug", truncated,
            "--in", "workflow", "--withdrawn-by", "0052",
        )

        self.assertEqual(code, 0, err)
        self.assertNotIn("Never commit, push, or open a PR", self.core_text())

    def test_supersede_unknown_slug_changes_nothing(self):
        self.seed_core()

        code, _, err = self.run_cli(
            "supersede", "--slug", "no-such-rule", "--in", "workflow",
            "--withdrawn-by", "0052",
        )

        self.assertNotEqual(code, 0)
        self.assertIn("no-such-rule", err)
        self.assertEqual(self.core_text(), self.CORE_FIXTURE)
        self.assertIsNone(self.archive_text())
        self.assertEqual(self.head_sha(), self.head_sha())

    def test_supersede_requires_the_withdrawing_adr_to_exist(self):
        slug = self.seed_core()

        code, _, err = self.run_cli(
            "supersede", "--slug", slug, "--in", "workflow", "--withdrawn-by", "0099",
        )

        self.assertNotEqual(code, 0)
        self.assertIn("0099", err)
        self.assertEqual(self.core_text(), self.CORE_FIXTURE)
        self.assertIsNone(self.archive_text())
        self.assertEqual(self.porcelain(), "")

    def test_supersede_refuses_the_default_branch(self):
        slug = self.seed_core()
        git("checkout", "main", cwd=self.board)

        code, _, err = self.run_cli(
            "supersede", "--slug", slug, "--in", "workflow", "--withdrawn-by", "0052",
        )

        self.assertEqual(code, 4, err)
        # core/workflow.md only ever existed on the feature branch
        self.assertIsNone(self.archive_text())
        self.assertEqual(self.porcelain(), "")
        self.assertFalse((self.board / "archive").exists())

    def test_supersede_rolls_back_when_push_is_rejected(self):
        slug = self.seed_core()
        before_head = self.head_sha()
        before_index = (self.board / "core" / "INDEX.md").read_bytes()
        self.reject_pushes()

        code, _, err = self.run_cli(
            "supersede", "--slug", slug, "--in", "workflow", "--withdrawn-by", "0052",
        )

        self.assertEqual(code, 3, err)
        self.assertIn("rolled back", err)
        self.assertEqual(self.core_text(), self.CORE_FIXTURE)
        self.assertIsNone(self.archive_text())
        self.assertEqual(
            (self.board / "core" / "INDEX.md").read_bytes(), before_index
        )
        self.assertEqual(self.head_sha(), before_head)
        self.assertEqual(self.porcelain(), "")

    def test_supersede_persists_both_files_and_pushes(self):
        slug = self.seed_core()

        code, _, err = self.run_cli(
            "supersede", "--slug", slug, "--in", "workflow", "--withdrawn-by", "0052",
        )

        self.assertEqual(code, 0, err)
        self.assertEqual(self.porcelain(), "")
        message = git("log", "-1", "--format=%s", cwd=self.board).stdout.strip()
        self.assertIn("supersede", message)
        self.assertIn("0052", message)
        pushed = git("show", "--stat", "--name-only", "HEAD", cwd=self.board).stdout
        self.assertIn("core/workflow.md", pushed)
        self.assertIn("core/INDEX.md", pushed)
        self.assertIn("archive/workflow.md", pushed)


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
