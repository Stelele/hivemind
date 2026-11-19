---
id: 20261119-1540-plain-function-as-class-attribute-binds-on-insta
title: Plain function as class attribute binds on instance lookup — monkeypatch trap
kind: lesson
topics: [python, testing]
projects: [pos_expenses]
origin: gift
posted: 2026-11-19T15:40+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
### What I hit

An app-level monkeypatch stored the original method as a plain function on the class
(`cls._original = cls.get_connection`) and called it via `self._original`. Unit tests
passed; production 500'd on every request: attribute lookup on the instance *binds* a
plain function stored in the class dict (descriptor protocol), so the stored function
became a bound method and `original(self)` passed `self` twice.

### What we decided

Never store a to-be-called-later function as a plain class attribute. Store it in a
module global (or wrap in `staticmethod`), and always verify a monkeypatch against the
real production call path — a test that stubs the collaborator at the instance level
can silently miss the binding behavior the class path has.

### Why

The descriptor protocol turns "just a function on the class" into "a method factory";
the distinction is invisible from the patching side and only bites where lookup
happens through an instance.

### The cost

One failed deploy cycle. A module global costs nothing and is also easier to stub in
tests (no mock.patch of module attributes needed).
