# Sample Input / Output

A worked example to show what the skill produces when fed real-shaped data.

---

## INPUT

> **Genre and core loop:** Social card game, daily play with weekend tournaments
> **Segments:** 92% F2P, 5% minnow, 2.5% dolphin, 0.5% whale. ARPDAU $0.04
> **Retention:** D1 38%, D7 14%, D30 4.5%
> **Recent events:** Weekend tournament (1 week ago), daily login streak (running continuously)
> **Capacity:** 1 small event + 1 large event in the next 4 weeks

---

## OUTPUT

### Diagnosis

Two leaks. D7 at 14% is borderline below the casual threshold of 15% — habit formation is working but only just. D30 at 4.5% is the real problem; the mid-game has no shape between day 14 and day 30 and the cohort drops out. **Confidence: medium.** I'd want to see the day-by-day curve between D14 and D28 to confirm the drop-off shape, but the headline numbers point at a D30 leak as the priority.

Implication for the calendar: focus on D30 with secondary D7 reinforcement. Avoid running anything that competes for attention with the Day 14-21 window where the leak likely sits.

### Primary segment

Habituating users (day 7 to 30), F2P primary, minnow secondary. This is the cohort that's at risk of falling off before they form a real habit, and it's also the largest segment by far. A whale event right now would not move the needle on the leak.

### Calendar

| Week | Day | Event | Mechanic | Segment | Lifecycle | Objective | Duration | Defence note |
|---|---|---|---|---|---|---|---|---|
| 1 | Mon | Master Series | 7-day mini-tournament with tier progression | F2P / minnow | Habituating (D7-D30) | Lift D30 | 7 days | If it underperforms, the tier completion data tells us whether the issue is reward thresholds or matchmaking depth |
| 2 | — | (recovery week — no large event, daily streak continues) | — | — | — | — | — | Lets the cohort consume Week 1 results and prevents event fatigue |
| 3 | Wed | Comeback Bonus | Return-and-win pop-up for users who skipped 3+ days | F2P | At-risk | Reactivate | 4 days | Catches the at-risk users before they cross the 14-day churn line |
| 4 | Mon | Squad Push | Team-based goal with shared rewards | F2P / minnow | Habituating (D7-D30) | Drive social action | 7 days | Social ties compound retention across the D14-D30 critical window; if it fails, social mechanics are not the lever |

### Defence checks

- **Master Series** ties to the D30 leak by giving habituating users a 7-day progression shape — exactly the missing structure between Week 1 and Week 4.
- **Comeback Bonus** ties to the D30 leak by reducing churn at the at-risk handoff before users cross the 14-day inactivity line.
- **Squad Push** ties to the D30 leak because social bonds are the strongest known retention compounder for this lifecycle window in social card games.

### What this calendar does not solve

- ARPDAU lift in dolphin and whale segments. There is no monetisation event for paying users in this calendar. If revenue is also slipping, that's a separate calendar.
- D1 onboarding is healthy enough at 38% but not great. Improving D1 by 3-4 points would compound through the rest of the funnel; that's a product change, not a LiveOps event.
- Long-term mid-game depth beyond 4 weeks. This calendar plugs the leak; it does not redesign the game.
