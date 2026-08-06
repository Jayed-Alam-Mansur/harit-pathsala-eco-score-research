# Presentation Script — telling the Eco-Score story

A spoken walkthrough of the web app that covers the whole research, in order,
with the *reason* for every step. Written to be read aloud.

**Format:** each beat has 🖱️ **DO** (what to click), 🗣️ **SAY** (what to say),
and 💡 **WHY** (the reasoning — for you, not the audience; this is the part that
answers "why did we even do this?").

**Timings:** full version ≈ 10 minutes. A 3-minute version is at the end.

---

## The one-sentence version

> *We built a calculator that gives students a score out of 100. I checked
> whether that score can be trusted. The maths inside it is right — but it has a
> hard cut-off that gives 9% of students the same score of zero no matter how
> different they really are, and no matter how hard they try. I found out why,
> measured it, and fixed it.*

If you remember nothing else, remember that. Everything below is evidence for
that one paragraph.

---

## The story arc (why it's in this order)

Every good investigation answers questions in the order a sceptic would ask them:

| Act | The sceptic asks | Where in the app |
|---|---|---|
| 1 | Is your arithmetic even right? | Calculator |
| 2 | Which habits actually move this number? | Finding 1 |
| 3 | How precise is one score? | Finding 2 |
| 4 | Does it work for a whole school, not one student? | Finding 3 |
| 5 | So is the formula wrong? | Finding 4 |
| 6 | Can you do better? | Finding 5 |
| 7 | What are you *not* claiming? | About |

**Don't reorder these.** Act 5 only lands because Act 4 built the suspicion, and
Act 6 only earns trust because Act 5 cleared the formula of blame.

---

# ACT 1 — The number that decides things

### Beat 1.1 · Open on the Calculator

🖱️ **DO** — Open the app on **🏠 Calculator**. Leave the default sliders alone
(bus, 2 km, 90 kWh, 1 cylinder, medium waste, Rs 200).

🗣️ **SAY**
> "This is Harit Pathsala. We built it at the Nepal Climate Hackathon in 2025.
> A student answers five questions about their daily life — how they get to
> school, home electricity, cooking gas, waste, and stationery — and it returns
> one number out of 100. It's called the Eco-Score.
>
> This student scores **41**.
>
> Here's the thing about that number. Teachers show it to students. Students
> compare it with each other. A dashboard averages it across a class. So it
> isn't decoration — it's used to judge people. And nobody had ever checked it.
> That's what this project is."

💡 **WHY** — You must establish *stakes* before method. The audience needs to
feel that the number matters before they care whether it's correct. "Nobody had
ever checked it" is your research gap in six words.

### Beat 1.2 · Prove the arithmetic first

🖱️ **DO** — Point at the breakdown bars (cooking, electricity, waste,
transport, stationery), then at the "1.976 kg CO₂" tile.

🗣️ **SAY**
> "Before criticising anything I had to prove I could reproduce it. This student
> emits **1.976 kg of CO₂ per day**. Every one of those five bars is checked
> against the project documentation to four decimal places, automatically, every
> time the notebook runs. If a single emission factor ever changes, the notebook
> refuses to run and tells you which one broke.
>
> So nothing after this point is a disagreement about arithmetic. The arithmetic
> is verified. What I'm questioning is the *scale* — the step that turns 1.976
> kilograms into the number 41."

💡 **WHY** — This is the most important credibility move in the whole talk. A
supervisor's first instinct is "did you just make a mistake?" You close that door
immediately, and you separate two things people confuse: **the footprint
calculation** (physics, correct) versus **the scoring function** (a design
choice, questionable). Everything you found lives in the second one.

### Beat 1.3 · Show the three curves

🖱️ **DO** — Scroll to the "Where you land on each scoring curve" chart. Point at
the grey shaded bands on the left and right.

🗣️ **SAY**
> "This is the scoring rule. Zero point five kilograms a day gets you 100. Three
> kilograms a day gets you 0. Straight line in between.
>
> Look at the grey areas. Below 0.5 everybody gets 100. Above 3.0 everybody gets
> 0. The line has gone flat. Hold on to that picture — the flat parts are the
> entire finding."

💡 **WHY** — Plant the visual now, cash it in during Act 4. People accept a
conclusion far more readily if they saw the cause ten minutes earlier and
half-noticed it themselves.

---

# ACT 2 — Which habits actually matter?

### Beat 2.1 · The 62× ratio

🖱️ **DO** — Go to **📊 Research Findings** → open **Finding 1**.

🗣️ **SAY**
> "First real question: if a student wants a better score, what should they
> actually change?
>
> I took the derivative of the score with respect to each habit. In plain terms:
> if you increase one habit by 10% and leave everything else alone, how many
> points do you lose?
>
> Cooking: **2.86 points**. Electricity: **2.76**. Waste: **1.99**. Transport:
> **0.26**. Stationery: **0.046**.
>
> Cooking matters **62 times** more than stationery. A student could stop buying
> notebooks and pens entirely — for the whole year — and move their score by
> less than one point."

💡 **WHY** — Two reasons this act exists. First, it's the *useful* result: it
tells the app what advice to give, and the honest answer is that four of the five
questions barely matter. Second, it introduces derivatives gently, so that in
Act 4 when you say "the derivative is exactly zero", the audience already knows
what a derivative means here.

### Beat 2.2 · The maths behind it (optional, if asked)

🗣️ **SAY**
> "Why is the ranking so clean? Because the footprint is a simple weighted sum —
> each habit multiplied by its emission factor. So the derivative of the score
> with respect to any habit is just **−40 times that habit's emission factor**.
> It's the same ordering for every student in the country. That's convenient for
> giving advice, but it also means the app can't really personalise anything."

💡 **WHY** — Shows you understand *why* the result holds, not just that it does.
This is the difference between a report and research.

---

# ACT 3 — How much can one score be trusted?

### Beat 3.1 · The factors are estimates

🖱️ **DO** — Open **Finding 2**.

🗣️ **SAY**
> "Second question. That score of 41 — how precise is it?
>
> Here's something people forget. The number 0.23 kilograms of CO₂ per unit of
> electricity is not a constant like pi. It's an estimate the Nepal Electricity
> Authority publishes each year, and it moves as the hydro-to-thermal mix changes
> with rainfall and imports. Across their 2018 to 2023 reports it swings about
> **15%**. Waste composition varies about 20% between households. Supply-chain
> factors, 25%.
>
> So I stopped treating the emission factors as fixed numbers and treated them as
> what they are: **random variables**."

💡 **WHY** — This reframe is the conceptual heart of Act 3. Your audience thinks
of 0.23 as a fact. Once they accept it's an estimate with a spread, uncertainty
propagation becomes obviously necessary rather than academic decoration.

### Beat 3.2 · Two methods, one answer

🗣️ **SAY**
> "I measured the resulting uncertainty two independent ways.
>
> **Algebraically** — because the footprint is a linear sum, the variances just
> add. That gives a standard deviation of **5.92 points**.
>
> **By simulation** — I generated 10,000 versions of the world, each with
> slightly different emission factors drawn from those spreads, and scored the
> same student in every one. That gives **5.99 points**.
>
> They agree to **1.29%**. Two completely different methods, same answer — which
> is how you know neither one is a mistake.
>
> What it means: a score of **41** is really somewhere between **29 and 53**.
> So if two students are 10 points apart, you cannot honestly say one is greener
> than the other. A classroom leaderboard built on small differences is ranking
> noise."

💡 **WHY** — "Two methods agreeing" is the most persuasive structure in applied
maths. And the [29, 53] translation is what makes it matter — always convert a
standard deviation into a sentence about people.

### Beat 3.3 · The question your DAA lecturer will ask

🗣️ **SAY** *(only if asked, but be ready — it's the most likely question)*
> "Someone always asks: isn't Monte Carlo that thing from Design and Analysis of
> Algorithms? Same name, opposite purpose.
>
> In algorithms — Miller-Rabin, randomised QuickSort — the problem is completely
> deterministic. Whether 561 is prime is a fixed fact. You flip coins only to
> reach the answer *faster*. The randomness is in your method.
>
> Here the randomness is in the **world**. The grid factor genuinely does differ
> from year to year. I'm not approximating something I could have computed
> exactly — I'm describing a spread that really exists.
>
> And there's a place where I *had* to simulate, which I'll show you in a second."

💡 **WHY** — Answering this pre-emptively signals you know why you chose your
tools instead of copying them. It's also, bluntly, the question most likely to
expose a student who doesn't understand their own method.

---

# ACT 4 — The twist

### Beat 4.1 · One student is not a school

🖱️ **DO** — Open **Finding 3**. Let the saturation histogram fill the screen.
Pause before speaking.

🗣️ **SAY**
> "Everything so far was about one example student. But a scoring system has to
> work for a whole school. Since we have no survey data yet, I simulated
> **10,000 students** with realistic Nepali distributions — commute modes, NEA
> billing ranges, LPG use, waste, spending.
>
> Then I scored all of them. Look at the red bar on the left."

🖱️ **DO** — Point at the red spike at zero.

🗣️ **SAY**
> "**9.19%** of the school scores exactly **zero**.
>
> And here's the part that actually matters. Those students are not the same as
> each other. Their real footprints run from **2.99 to 8.91 kilograms per day**.
> That is a **threefold difference** in actual emissions — the heaviest emitter
> in the school and someone just over the line — and the app tells all of them
> the identical thing: **zero**.
>
> Worse than that. Remember the derivative from earlier? For every one of these
> students it is **exactly zero**. Not small. Zero. If one of them halves their
> waste tomorrow, their score changes by nought point nought nought nought.
> The app has stopped listening to them.
>
> Meanwhile at the other end — **nobody**, not one student out of ten thousand,
> reaches 100. The reward end of the scale is unreachable."

💡 **WHY** — This is your climax. Slow down here. The rhetorical structure is:
a number (9.19%), then the number's *meaning* (3× spread collapsed), then the
consequence for a real child (effort produces no feedback). Numbers alone don't
land; consequences do.

Use the thermometer analogy if faces look blank:
> *"It's a thermometer that stops at 40 degrees. A patient at 40, one at 41, one
> at 42 — all read the same. And as the patient gets worse, the reading doesn't
> move."*

### Beat 4.2 · Why the floor fills up

🖱️ **DO** — Point at the "Household baseline · 2.048 kg/day" tile.

🗣️ **SAY**
> "Why are so many students stuck there? This tile explains it. Electricity,
> cooking and waste alone — before a student travels a single kilometre or buys
> a single pen — already average **2.048 kilograms a day**. The floor is at 3.0.
>
> So an ordinary Nepali student starts at **82% of the way to zero points**
> because of household decisions they don't control. The boundaries were chosen
> for a scale these emission factors simply don't produce."

💡 **WHY** — Diagnosis, not just symptoms. Anyone can report "9% score zero";
explaining *why* the threshold is misplaced is what makes it research. It also
pre-empts "so just move the boundary" — you'll address that in Act 6.

---

# ACT 5 — Who is guilty?

### Beat 5.1 · Clearing the formula

🖱️ **DO** — Open **Finding 4**. Point at the two R² numbers.

🗣️ **SAY**
> "Now the important question: is the formula wrong?
>
> I regressed the score against the footprint across all 10,000 students. R² is
> **0.85** — meaning the score fails to reflect about 15% of what's happening.
>
> Then I removed only the students stuck at the floor and ran it again. R² jumps
> to **0.9997**.
>
> Read that carefully. Among the students the system can actually score, it
> explains **99.97%** of the variation between them. It is almost perfect.
>
> In fact I can account for the missing 0.03% exactly — it's the rounding to a
> whole number for display. Nothing else.
>
> **So the formula is not broken. The clamp is the entire problem.** That single
> sentence is the finding this project exists to prove."

💡 **WHY** — This is the intellectual turn that elevates the whole project. A
weak version of this research says "the score is bad". Yours says precisely
*which component* is bad and proves the rest is sound. That's the difference
between complaining and diagnosing — and it's why the fix in Act 6 is small
instead of a rewrite.

---

# ACT 6 — The fix

### Beat 6.1 · Replace the cliff with a curve

🖱️ **DO** — Open **Finding 5**. Point at the green logistic curve.

🗣️ **SAY**
> "If the clamp is the problem, replace the clamp. Nothing else. The emission
> factors don't change, the footprint doesn't change — only the last step, the
> map from kilograms to a score.
>
> I tested two options and recommend the **logistic curve** — the green one. It's
> an S-shape centred on the population median, 2.19 kilograms a day, which
> becomes the score-50 point.
>
> The key property: it **never goes flat**. It approaches 0 and 100 but never
> reaches them. There is always somewhere left to go, in both directions, so
> every student's effort registers."

### Beat 6.2 · The four numbers that justify it

🗣️ **SAY**
> "Four results.
>
> **One** — students getting no feedback drops from **9.19% to 0.25%**.
>
> **Two** — the ranking is preserved *exactly*. Spearman correlation of
> **1.000000**. If student A really emits less than student B, A scores higher.
> Always. The old score couldn't promise that, because it tied 919 students at
> zero.
>
> **Three** — where the old score worked, the new one agrees with it: correlation
> **0.9972**. So we're not throwing away the old scale, we're extending it.
>
> **Four** — information content, measured by Shannon entropy, rises from
> **2.644 to 2.765 nats**. The score is literally able to say more distinct
> things about students than it could before."

💡 **WHY** — Point two is the strongest single argument and most people miss it.
A score that produces ties is failing at its only job — distinguishing. Point
three is the political argument: it's an extension, not a repudiation, so the
hackathon team has nothing to be defensive about.

### Beat 6.3 · Show it live — the moment that convinces people

🖱️ **DO** — Go back to **🏠 Calculator**. Set transport to **Car** and distance
to **7 km**. Leave everything else at the defaults.

🗣️ **SAY**
> "Let me show you the difference instead of describing it. This student drives
> 7 km to school. Footprint 4.57 kilograms a day. The original score says **0**.
>
> Now watch both tiles while they improve."

🖱️ **DO** — Drag distance down one step at a time: **7 → 6 → 5 → 4 → 3 km**.
Point at "Original Score" staying at 0, then at "Logistic ★" climbing.

> | distance | footprint | Original | Logistic |
> |---|---|---|---|
> | 7 km | 4.57 | **0** | 2 |
> | 6 km | 4.19 | **0** | 3 |
> | 5 km | 3.81 | **0** | 6 |
> | 4 km | 3.43 | **0** | 11 |
> | 3 km | 3.05 | **0** | 18 |

🗣️ **SAY**
> "The original score: zero, zero, zero, zero, zero. This student has cut their
> commute by more than half — a real, hard change — and the app has told them
> five times that their effort is worth nothing.
>
> The logistic score goes from 2 to 18. It saw every step. That is the entire
> project, in one slider."

⚠️ **Stay inside 7 km → 3 km.** Beyond about 8 km the logistic also rounds to 0
on the tile, and the contrast you're demonstrating disappears. Below 2.6 km the
original wakes up and starts moving too. This window is where the point is
visible.

💡 **WHY** — Never end on a table when you can end on a live demonstration. The
audience sees the failure and the fix in the same three seconds, with no numbers
to interpret. If you only have two minutes, do *this beat alone*.

---

# ACT 7 — What I'm not claiming

### Beat 7.1 · The honest ending

🖱️ **DO** — Go to **📁 About This Project**.

🗣️ **SAY**
> "Three limitations, stated deliberately.
>
> **One — the population is simulated, not surveyed.** No student data has been
> collected yet. So '9.19%' is what these emission factors produce on a plausible
> Nepali school, not a measured fact about a real one. What *is* robust is the
> structural finding: a scoring function with a zero gradient over a region where
> real students live. That doesn't depend on my distributions. I've written the
> survey — questions in English and Nepali, three minutes, no personal data — and
> the code drops the real data straight in.
>
> **Two — the logistic score is relative to a population.** Fifty means 'typical
> for this group', not '1.75 kilograms'. It has to be refitted if the population
> changes, and two schools can't compare scores unless they pin the same
> settings. That's why the kilograms figure must stay on screen next to the
> score.
>
> **Three — I assumed the emission factors vary independently.** They probably
> don't. If they're correlated, the true uncertainty is *larger* than my 5.92
> points. So that figure is a lower bound, not a final answer.
>
> All of this is documented in the research notes, including five published
> numbers I could not reproduce exactly to the last digit, and by how much."

💡 **WHY** — Volunteering your weaknesses is not modesty, it's strategy. Every
limitation you name yourself is a question your examiner cannot ask you. And
naming the reproducibility gaps before anyone finds them is what separates
honest work from polished work.

### Beat 7.2 · Close

🗣️ **SAY**
> "So — can we trust the Eco-Score? Mostly yes, and now we know exactly where it
> stops being trustworthy, why, for how many students, and what to do instead.
> The fix is one function. The physics never changes."

---

# The 3-minute version

If you're cut short, run only these:

1. **Calculator, defaults** — *"One number out of 100. Students are compared by
   it. Nobody had checked it. The arithmetic is verified — I'm questioning the
   scale."* (30 s)
2. **Finding 3, the red spike** — *"9.19% of a school scores exactly zero. Their
   real footprints range 2.99 to 8.91 — a threefold difference, one number. And
   their score can't move, however hard they try."* (60 s)
3. **Finding 4, the two R² values** — *"Remove those students and the formula
   explains 99.97% of everything. The formula isn't broken. The clamp is."* (30 s)
4. **Calculator, car at 15 km, drag the slider down** — *"Original stays at zero
   the whole way. The logistic moves. That's the fix."* (60 s)

---

# Questions you will be asked

**"Why not just move the boundary from 3.0 to 9.0?"**
> That fixes the floor and destroys the middle. Stretch the line to 9 kg and
> almost everyone bunches into a narrow band near the top, because the population
> is concentrated between 1.4 and 3.2 — you'd trade a floor problem for a
> resolution problem. The logistic gives resolution where the students actually
> are and still never flattens. And I did test the simpler fix: the percentile
> method, boundaries at the 5th and 95th percentile. It has the highest entropy
> of the three, but it still clamps both tails, so it still creates ties — and it
> adds a ceiling problem the original didn't have.

**"Isn't a simulated population just making up your results?"**
> It would be if I claimed 9.19% is a fact about a real school. I don't. The
> distributions come from published sources, they were fixed before any score was
> computed, and I did not tune them to produce a nice answer — the mean score of
> 31.9 with nobody reaching 100 is an uncomfortable result and I reported it as
> it came. What the simulation establishes is structural: a region of zero
> gradient that contains real students. Change my assumptions and the percentage
> moves; the flat region doesn't.

**"Why is your mean score only 31.9? That seems too harsh."**
> Because that's what these emission factors produce on this population. The
> household baseline alone is 2.048 kg/day against a floor at 3.0. I deliberately
> did not adjust the distributions to reach a friendlier average — the harshness
> *is* the evidence that the boundaries are miscalibrated.

**"Did you change the original app?"**
> No. Not one line. `src/logic.js` is untouched. All of this lives in a separate
> `research/` folder, and the notebook asserts that its formulas match the app's
> exactly, so the two can never drift apart.

**"Is 10,000 students enough?"**
> Yes, and I show it. On the Understanding the Math page there's a slider that
> runs the simulation from 100 to 10,000 draws and plots the estimate settling
> onto the analytical answer. Error falls like one over root N — a hundred times
> more simulations buys ten times more precision, so 10,000 is the sensible
> stopping point.

**"What would you do next?"**
> Run the survey — I need at least 100 real responses before the median is stable
> enough to anchor the logistic scale. Then refit, republish the numbers, and
> only then propose changing the live app. And quantify whether the emission
> factors are correlated, since that's my weakest assumption.

---

# Delivery notes

- **Pause after "9.19%".** Let it sit for two seconds. It's your one moment of
  drama; don't rush past it.
- **Say "kilograms of CO₂ per day", not "F".** Symbols on a slide, words in
  speech.
- **Always convert statistics into people.** Not "SD is 5.92" but "a 41 is really
  somewhere between 29 and 53".
- **Never say "the app is bad".** Say "the app is right about the physics and
  miscalibrated in one function". You built it; you're improving it, not
  disowning it.
- **If the projector fails**, you can still tell the whole story with four
  numbers on a whiteboard: 62×, ±5.92, 9.19%, 0.9997.
