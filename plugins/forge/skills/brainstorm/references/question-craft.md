# Question craft

Brainstorming runs on questions. Bad questions waste turns and produce vague specs; good questions converge fast.

## One per message

Never bundle. "What's the auth model and which database and what's the deploy target?" is three questions; the user will answer the easiest and skip the rest. Ask one, get the answer, ask the next.

If a topic needs depth, break it into a sequence: "Are users individual or team-based?" → "If team, do teams share data or only billing?" → "What's the membership model — invite-only, open, self-serve?"

## Multiple choice when possible

Multiple-choice answers are cheaper to give than open-ended ones, and they force you to think about the option space before asking. Default shape:

> A) <option> — <tradeoff>
> B) <option> — <tradeoff>
> C) <option> — <tradeoff>
>
> Recommend A because <reason>. Pick one or describe a fourth.

Open-ended is fine when the option space is genuinely unbounded — pricing, naming, copy. Don't force multiple choice on things that aren't a choice.

## Focus on intent, not implementation

Early in the conversation, drill into purpose:

- What's the user trying to do?
- What does success look like?
- What's the failure mode you're trying to avoid?

These shape the design. Implementation questions ("Redis or Postgres for the queue?") come later, after the purpose is fixed.

## Surface scope problems immediately

If the answers to early questions reveal that the project is actually three projects, stop clarifying details and surface that. Don't burn ten turns refining a corner of something that needs to be split first.

Signal: each new question reveals a new subsystem the user hadn't mentioned. That's a decomposition signal, not a clarification signal.

## Examples

**Good** (focused, single-axis, recommends):

> Auth: A) email + password, B) magic link only, C) OAuth via Google/GitHub. I'd recommend C — least friction, no password storage liability. Which fits?

**Bad** (bundled, vague, no recommendation):

> What are your thoughts on auth and how do you want users to sign up and is there a password reset flow?

**Good** (scope check):

> You've mentioned chat, file uploads, billing, and analytics. That's four subsystems; I'd suggest we pick one to spec first and treat the others as follow-ups. Which is the highest priority?

**Bad** (proceeds anyway):

> Got it, building a platform with chat, files, billing, and analytics. Question 1 of 47: should chat be real-time or polled?
