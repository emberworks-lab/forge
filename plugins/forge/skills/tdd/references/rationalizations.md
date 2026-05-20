# Rationalizations this skill blocks

Each row is something you might think when the test-first discipline feels inconvenient. The "reality" column is why the thought is wrong.

| Rationalization | Reality |
|---|---|
| "Too simple to need a test." | Simple code breaks. The test takes 30 seconds. If it's simple, you'll write the test in less time than this row took to read. |
| "I'll write the test after." | Tests written after pass immediately. Passing immediately proves nothing — it might be testing the wrong thing, or the implementation, or a mock. |
| "Tests after achieve the same goal." | They don't. Tests-after answer "what does this code do?". Tests-first answer "what should this code do?". Only the second question designs the API. |
| "I already manually tested it." | Manual testing is one moment in time. The test is permanent. Manual coverage is whatever you remembered; automated coverage is whatever you enumerated. |
| "Deleting hours of work is wasteful." | Sunk cost fallacy. The time is already spent. The choice now is: rewrite with TDD (hours, high confidence) or keep going with code you can't trust (debt, low confidence). |
| "Keep the existing code as reference; write the tests first." | You'll adapt it. That's tests-after with a fig leaf. Delete it. |
| "Need to explore first; I'll TDD after." | Fine — explore. Then throw the exploration away and TDD from scratch. "Adapting the exploration" is tests-after. |
| "This is hard to test, the design must be unclear." | Yes. Listen to the test. Code that's hard to test is code that's hard to use. Fix the design. |
| "TDD will slow me down." | TDD is faster than debugging. Pragmatic means fewer bugs, not less ceremony. |
| "Manual testing is faster." | Manual testing is faster for the first run and slower for every subsequent run. You'll run the test hundreds of times across the project's life. |
| "Existing code has no tests." | You're improving the code. Add tests as you go. The lack of tests is the bug you're also fixing. |
| "TDD is dogmatic, being pragmatic means adapting." | TDD IS pragmatic: finds bugs before commit, prevents regressions, documents behavior, enables refactor. "Pragmatic shortcut" usually means "skip the test and pay later". |
| "It's about the spirit, not the ritual." | The ritual produces the spirit. Skipping the ritual doesn't keep the spirit; it loses both. |
| "This case is different because…" | It isn't. Every case has felt different in the moment. The discipline is what survives the moment. |

## Why the list exists

The cycle is rigid by design. Every rationalization above feels reasonable in isolation; each one is a wedge that splits the discipline. Once any of them is allowed once, the next case is easier to wave through, and the cycle becomes a suggestion rather than a rule.

The fix is to recognize the rationalization, name it, and discard it. The list above gives names to the most common forms.

## The "spirit not ritual" trap in detail

This one deserves its own paragraph because it's the most seductive.

The argument: "TDD is about the goals — finding bugs, preventing regressions, designing better APIs — not about the specific test-first-then-code dance. If I write the tests right after the code, I get the same goals."

The flaw: you don't. The goals aren't downstream of the artifacts (tests + code); they're downstream of the *order* of producing them.

- "Find bugs" requires watching the test fail for the right reason. You can't do that after the code passes.
- "Design better APIs" requires writing the test before the API exists, so the test demands the API the consumer would want. After the code exists, the test ratifies whatever you happened to build.
- "Prevent regressions" works either way — but only this one. Two of three goals require the order.

Tests-after gets you coverage. It does not get you TDD.
