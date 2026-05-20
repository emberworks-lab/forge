# Rationalizations this skill blocks

Each row is a thought that, if entertained, produces a guess-and-check fix and skips the four phases. The "reality" column is what's actually true.

| Rationalization | Reality |
|---|---|
| "Issue is simple, no need for the process." | Simple bugs have root causes too. The process is fast on simple bugs — minutes, not hours. |
| "Emergency, no time for systematic debugging." | Systematic debugging is FASTER than guess-and-check. Thrash is what costs hours. |
| "Just try this first, then investigate properly." | The first fix sets the framing for everything that follows. If it's wrong, every later step inherits the wrong frame. |
| "I'll write the test after I confirm the fix works." | Untested fixes don't stick. Six weeks later the same bug returns with a new face and no regression catch. |
| "Multiple fixes at once saves time." | You can't isolate which one worked. The ones that didn't are now silent bugs. |
| "Reference implementation is too long; I'll adapt the pattern." | Partial understanding guarantees bugs. Read the reference completely or pick a different pattern. |
| "I see the problem, let me fix it." | Seeing a symptom is not understanding the cause. Verify with evidence first. |
| "One more fix attempt." (after 2+ failures) | Three failures = wrong abstraction, not wrong line. Stop and question the architecture (see `architectural-escape-hatch.md`). |
| "It's probably X." | "Probably" is not evidence. Reproduce, instrument, observe, then claim. |
| "Skip the test, I'll manually verify." | Manual verification is one moment in time. The test is permanent. |
| "The pattern says X but I'll adapt it differently." | If you have to adapt it without understanding why X, you're guessing. Either understand why or pick a different pattern. |
| "I don't fully understand this, but this might work." | "Might" is not a fix. Say "I don't understand X" out loud and re-investigate. |

## Why this list exists

The four-phase workflow is rigid by design. The rigidity is what produces correct fixes; the moment you allow exceptions, the discipline collapses. The rationalizations above are the most common entry points for collapse — each one feels reasonable in isolation, and each one short-circuits a phase.

When you catch yourself making one of these arguments, that's the signal to stop and return to Phase 1.
