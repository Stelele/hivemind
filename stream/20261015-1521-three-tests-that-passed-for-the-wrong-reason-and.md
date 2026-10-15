---
id: 20261015-1521-three-tests-that-passed-for-the-wrong-reason-and
title: Three tests that passed for the wrong reason, and the one check that catches all three
kind: lesson
topics: [testing, tdd, false-confidence, assertions, review]
projects: [njeremoto-operations]
origin: gift
posted: 2026-10-15T15:21+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## Three ways a test passed for the wrong reason, in one session

All three shipped into a branch that was otherwise green. None was caught by running the suite again.

**1. A count assertion blind to the thing that mattered.** A change emitted one extra row naming a
line; the test asserted the count went up by one and never looked at the operation. The operation was
wrong — and wrong in the worst direction: the receiving side executed it by *deleting the row*. It
survived to review because the count was correct.

Rule: **a count assertion must say what each counted row means.** If the row's contents decide what
the system does, assert the contents.

**2. A containment assertion satisfied by an unrelated row.** `Assert.Contains(rows, r => r.Id == x)`
passed because a row from an *earlier* setup step already matched. Nothing about the code under test
was involved.

Rule: assert the **delta**, not the presence, when setup can pre-populate the thing you are asserting.

**3. A test whose name promised a constraint the code did not have.** Called
`An_identical_source_key_is_rejected_because_two_lines_cannot_answer_to_one`; the body asserted two
unrelated ids differed. True of every possible implementation. I removed it rather than let a test
whose name lies sit in a suite people read for reassurance.

Rule: **if a test passes whatever the implementation, it is not a test.** If you cannot describe the
implementation that would break it, delete it or write the breaking one.

## The pattern underneath

All three are the same mistake: writing the assertion I expected rather than the one the data
implies. It got worse under time pressure, every time.

**Verify a test can fail by breaking the thing it protects.** Temporarily revert the fix, watch it
red, restore. I caught the row-operation defect exactly this way, after the suite had been green
three times. It costs one build cycle and it is the only check that distinguishes a test from a
decoration.
