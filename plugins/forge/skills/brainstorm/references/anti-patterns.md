# Anti-patterns this skill blocks

Brainstorm exists to prevent the failure modes below. Each is a rationalization that produces wasted work; each is rejected by the hard gate.

## "This is too simple to need a design"

Every project goes through the gate — todo list, single-function utility, config change. "Simple" projects are where unexamined assumptions cause the most rework, because the design step is what surfaces those assumptions.

The design can be short. A few sentences is fine for a truly trivial change. But it must exist, be written down, and be approved.

## "I'll write the spec after I code, it'll be the same"

It won't. Specs written after the fact describe what was built, not what should have been built. They miss the alternatives that were never considered, the edge cases that were never enumerated, the scope decisions that were silently made.

Spec-before-code forces you to make those decisions explicitly. Spec-after-code rationalizes whatever you happened to do.

## "Let me just prototype it real quick"

Throwaway prototypes have their place — but they're not specs. If you prototype to learn, throw it away and brainstorm with the lessons. If you prototype and then "polish it up", you've skipped this skill.

If the user wants to explore in code first, that's a different skill (a prototype skill, when it exists). Brainstorm produces a spec, not a working binary.

## "The user said 'just build it'"

The user said "build it". They didn't say "build the wrong thing without telling me". Surface that there's a design step, present the design in a few sentences, get explicit approval. Two minutes of design saves an hour of rework.

If the user genuinely wants to skip the design step, that's their call — but it has to be an explicit override, not a silent skip.

## "I'll cover that case if it comes up"

Vague requirements produce vague code. If a corner of the design is "we'll figure that out later", either the case is out of scope (say so explicitly) or it's in scope and needs a decision now. "Later" tends to mean "during implementation, under time pressure, by whoever happens to be looking at it".

Pick one. Make it explicit. Move on.

## "Adjacent variants for consistency"

User asked for dev + prod. Producing dev, staging, prod, and CI "for consistency" is gold-plating. Brainstorm produces the design the user asked for. If you think a fourth environment is worth having, raise it as a question; don't smuggle it into the design.

Same shape: the user asked for one CLI command. Don't propose a CLI with five subcommands because it "feels more complete".

## "The design doc is the implementation plan"

It isn't. A design says what the system is and why; a plan says what tasks happen in what order. Conflating the two produces a document that's too vague to implement from and too detailed to review as a design.

Brainstorm produces the design. Planning happens in a separate skill, after design is approved.
