# Clean Code

Language-agnostic principles for writing code that is readable, maintainable, and honest. No platform-specific syntax. Applies equally to Dart, TypeScript, Go, Python, and similar.

---

## Names

**Reveal intent.** A name should answer why something exists and how it is used — without needing a comment. Prefer `calculateTotalPrice()` over `calc()`.

**Avoid encodings and noise.** Type prefixes (`strName`), implementation suffixes (`managerImpl`), and redundant context (`UserUserProfile`) obscure rather than clarify.

**Use pronounceable names.** If you can't say it in a code review, it's harder to discuss and remember. Avoid abbreviations that save keystrokes but lose meaning.

**Make names searchable.** Single-letter names and unexplained short forms are impossible to grep. Reserve them only for trivial loop counters in small, obvious scopes.

**Name booleans as questions.** `isActive`, `hasError`, `canSubmit` read naturally in conditionals and document the assertion they represent.

**Distinguish concepts consistently.** Pick one word per concept across the codebase (`fetch`, `get`, and `retrieve` should not mean the same thing in different modules).

---

## Functions

**Small, and smaller still.** A function should fit on one screen and have one level of abstraction throughout. If you need to scroll to read a function, it's too long.

**Do one thing.** If a function has sections, comments separating them, or a name with "and", it's doing more than one thing. Extract each concern into its own function.

**Descend one level of abstraction.** Each function calls helpers that are one level more concrete. Mixing high-level orchestration with low-level detail in the same function forces readers to context-switch constantly.

**Limit arguments.** Zero is ideal; one is common; two is acceptable; three needs justification; four or more is a signal to introduce a parameter object.

**No flag arguments.** Passing a boolean to control behavior forks the function into two. Extract two explicitly named functions instead.

**Avoid output arguments.** A function that modifies its argument instead of returning a value surprises callers. Return the result; let the caller decide what to do with it.

**Return early.** Handle preconditions and error cases at the top. The happy path flows unindented through the bottom of the function.

---

## Comments

**Explain why, not what.** Well-named code explains what it does. Comments should explain the reasoning behind a non-obvious decision, a constraint from the outside world, or a trade-off.

**Legal and intent comments are acceptable.** License headers, `TODO`/`FIXME` markers with a ticket reference, and warnings about known gotchas add value.

**Avoid redundant comments.** `// increment i` above `i++` adds noise and gets out of sync. Delete it.

**Delete commented-out code.** Version control has the history. Commented-out blocks confuse readers and never get cleaned up.

**Update comments with the code.** A stale comment is worse than no comment — it actively misleads. If you change behavior, change the comment.

---

## Formatting

**Vertical openness.** Blank lines separate concepts. Related lines of code group together without blank lines between them. The eye uses whitespace to parse structure.

**Vertical density.** Lines that are tightly related — a variable declaration and its first use — belong close together. Readers should not need to scroll to follow a logical sequence.

**Dependent functions near each other.** A function and the helper it calls should live close in the file. Top-down reading should flow naturally: the caller above, the callee below.

**Consistent style, enforced by tooling.** Don't bikeshed indentation, brace placement, or quote style in review. Agree once, autoformat always. Reserve review energy for logic.

---

## Error Handling

**Return errors; don't hide them.** Use typed error returns, Result types, or checked exceptions. Callers must be able to handle failures — don't make failures invisible.

**Use exceptions for exceptional conditions.** Errors that represent programming mistakes or truly unexpected failures warrant exceptions. Expected failures (invalid input, not found) should be part of the return type.

**Never swallow errors silently.** An empty catch block or a `_ = err` is a debugging nightmare. Log, propagate, or handle — choose one explicitly.

**Provide context with errors.** An error message should include what operation failed and on what input. "not found" is useless; "user not found: id=42" is actionable.

**Separate error paths from happy paths.** Error-handling code mixed into the main flow obscures the algorithm. Use early returns, guard clauses, or dedicated error types to keep the paths visually distinct.

---

## Boundaries

**Wrap third-party APIs.** Don't scatter external library calls throughout your codebase. Introduce an interface or adapter at the seam. Swapping implementations or mocking in tests then costs one file, not dozens.

**Write learning tests.** When adopting an external dependency, write small tests that verify the behavior you rely on. They document your assumptions and break visibly when the library updates in a breaking way.

**Define integration seams.** Layer boundaries (UI → domain → infrastructure) should be defined by interfaces you control, not by the concrete types of your dependencies. This keeps each layer independently testable.

**Keep third-party types out of domain objects.** A domain model that imports an ORM annotation or an HTTP request type couples your core logic to infrastructure details. Map at the boundary; keep the domain clean.

---

## When to Apply

These principles pay off most when:

- The codebase will be maintained beyond the current sprint.
- More than one person works in the same module.
- You're reviewing code and struggling to understand intent without running it.
- A change that should be simple requires touching many unrelated layers.
- Tests are hard to write because behavior is tangled with side effects.

Apply them proportionally. A 10-line script and a production service deserve different levels of rigor. The goal is sustainable delivery, not aesthetic purity.
