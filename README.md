# LiveOps Event Calendar Planner

A structured prompt skill that diagnoses your retention curve before producing a single event. Built by [Rahul Shah](https://linkedin.com/in/rahul-mshah) from his work shipping live events on mobile games at Moonfrog Labs, Parchis Club, and earlier studios.

Works on Claude, ChatGPT (Custom GPT), and Gemini (Gem).

---

## What this is

This is a prompt skill — a structured system prompt you paste into your AI tool of choice. Once installed, it turns that tool into a LiveOps planning discipline: it refuses to skip to the calendar until it has diagnosed the retention curve, picked a segment, and locked in one objective per event.

It is not a template. It is not a calendar generator. It is a planning process encoded as a prompt.

---

## Why this exists

Most LiveOps calendars get built backwards. Calendar first, then events stuffed in by date. This one inverts the order: retention diagnosis → segment → lifecycle moment → objective → calendar.

The skill refuses to produce a calendar before retention data is on the table. If you don't have D1 / D7 / D30, it asks for them. If you give it "increase engagement" as an objective, it pushes back. Every event in the output has to defend itself against the Step 0 diagnosis.

It's a planning discipline, not a calendar template.

---

## What's in this repo

```
liveops-event-calendar/
├── README.md                          (this file)
├── claude/
│   └── system-prompt.md               (master version — paste into Claude project)
├── chatgpt/
│   └── custom-gpt-instructions.md     (Custom GPT setup)
├── gemini/
│   └── gem-instructions.md            (Gemini Gem setup)
└── examples/
    └── sample-input-output.md         (worked example)
```

---

## How to install

### Claude (recommended — strongest version)

1. Open Claude → Projects → New Project
2. Name it "LiveOps Event Calendar Planner"
3. Open Project Settings → Custom Instructions
4. Paste the entire contents of `claude/system-prompt.md`
5. Save
6. Start a new conversation in the project. You're done.

Note: Claude Projects requires a Claude Pro or Team subscription.

### ChatGPT

1. Go to chat.openai.com → Explore GPTs → Create
2. Open `chatgpt/custom-gpt-instructions.md` and follow the field-by-field setup
3. Test with: "Build me a LiveOps calendar." — it should ask for the 5 inputs, not produce a calendar.

### Gemini

1. Go to gemini.google.com → Gems → New Gem
2. Open `gemini/gem-instructions.md` and follow the setup
3. Test with: "Build me a LiveOps calendar." — it should ask for the 5 inputs.
4. If Gemini skips the input-gathering step and produces a calendar immediately, append this line to the end of the instructions: "If you produce any output before all five required inputs are collected, you have failed the task. Apologise and start over."

---

## Quick test (verify your setup is working)

After installing on any platform, send this message:

> "Build me a LiveOps calendar."

**Expected response:** The skill asks you for the five required inputs. It does not produce a calendar.

If it produces a calendar without asking for inputs, the system prompt was not applied correctly. Check the installation steps and try again.

Send this as the follow-up:

> "D1 is good, D7 is okay, I don't track D30."

**Expected response:** The skill pushes back. It asks for exact numbers, not adjectives. It offers to use D14 or D21 as a proxy for D30 if that data isn't tracked.

If the skill accepts "good" and "okay" as valid retention data, something is wrong with the instruction context.

---

## What it asks you for

Before producing a plan, the skill needs:

1. Game genre and core loop
2. Player segments by spend (% F2P / minnow / dolphin / whale, with rough ARPDAU per segment if known)
3. Retention curve: D1, D7, D30 — exact numbers. If D30 isn't tracked, D14 or D21 works as a proxy.
4. Active or recently shipped events from the last 4–6 weeks (so it doesn't repeat what just ran)
5. Sprint length and team capacity for the next 4 weeks

If any are missing, the skill asks. It does not guess.

---

## What it produces

1. **Diagnosis** — one paragraph identifying the retention leak and confidence level. Handles single leaks, multi-metric deficits, and healthy curves (maintenance mode).
2. **Primary segment** — one paragraph picking the segment the calendar is built for and why
3. **Calendar** — a 4-week table with launch date, event name, mechanic, segment, lifecycle moment, objective, duration, and a defensive note per event
4. **Defence checks** — one line per event confirming it ties back to the Step 0 diagnosis
5. **What this calendar does not solve** — honest note on gaps the calendar leaves open

---

## Sample run

See `examples/sample-input-output.md` for a worked example with a social card game carrying both a D7 and a D30 leak.

---

## Known limitations

- **Events can't fix a D1 leak.** If D1 is below threshold, the skill will say so explicitly and build the calendar for D7/D30 survivors. But the root cause — broken onboarding or a weak first session — needs a product intervention, not a LiveOps event.
- **Capacity is self-reported.** The skill takes your word for what the team can ship. If you overstate capacity, the calendar will be overbuilt.
- **The skill does not track what you've shipped.** It asks for recent events each session. It has no memory between conversations.
- **Retention thresholds are benchmarks, not laws.** D1 35% is a reasonable casual floor — but a game with a very specific niche audience may perform differently. Use the thresholds as a starting frame, not an absolute verdict.

---

## License

MIT. Use it. Modify it. Fork it. Build a better one and send it back.

---

## Feedback

If you run this and the output is generic, that's a bug. File an issue with the input you gave and the output you got. The skill is meant to refuse generic and force specific.
