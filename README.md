# LiveOps Event Calendar Planner

A 4-week LiveOps event calendar planner that diagnoses your retention curve before producing a single event. Built by [Rahul Shah](https://linkedin.com/in/rahul-mshah) from his work shipping live events on mobile games at Moonfrog Labs, Parchis Club, and earlier studios.

Works on Claude, ChatGPT (Custom GPT), and Gemini (Gem).

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

### ChatGPT

1. Go to chat.openai.com → Explore GPTs → Create
2. Open `chatgpt/custom-gpt-instructions.md` and follow the field-by-field setup
3. Test with: "Build me a LiveOps calendar." — it should ask for the 5 inputs.

### Gemini

1. Go to gemini.google.com → Gems → New Gem
2. Open `gemini/gem-instructions.md` and follow the setup
3. Gemini sometimes skips the input-gathering step. The instructions file has a fallback line you can append if needed.

---

## What it asks you for

Before producing a plan, the skill needs:

1. Game genre and core loop
2. Player segments by spend (% F2P / minnow / dolphin / whale, with rough ARPDAU per segment if known)
3. Retention curve: D1, D7, D30 — exact numbers
4. Active or recently shipped events (so you don't repeat what just ran)
5. Sprint length and team capacity for the next 4 weeks

If any are missing, the skill asks. It does not guess.

---

## What it produces

1. **Diagnosis** — one paragraph identifying the retention leak (D1 / D7 / D30) and confidence level
2. **Primary segment** — one paragraph picking the segment the calendar is built for
3. **Calendar** — a 4-week table with launch date, event name, mechanic, segment, lifecycle moment, objective, duration, and defence note for each event
4. **Defence checks** — one line per event confirming it ties back to the Step 0 diagnosis
5. **What this calendar does not solve** — honest note on gaps the calendar leaves open

---

## Sample run

See `examples/sample-input-output.md` for a worked example with a social card game and a D30 leak.

---

## License

MIT. Use it. Modify it. Fork it. Build a better one and send it back.

---

## Feedback

If you run this and the output is generic, that's a bug. File an issue with the input you gave and the output you got. The skill is meant to refuse generic and force specific.
