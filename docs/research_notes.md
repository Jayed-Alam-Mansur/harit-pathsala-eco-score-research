# Research Notes — decisions, ambiguities and things a reader should question

Companion to `research/notebook/eco_score_research.ipynb`. This file records the
judgement calls that the notebook makes but does not argue for, so a supervisor
can check them rather than take them on trust.

---

## 1. Decisions that shape the results

### 1.1 The five emission factors were never touched

Every factor comes from `src/logic.js` in the parent project (originally the
hackathon organiser's `Emission_factors.xlsx`). Nothing was refitted, rounded or
"improved". Section 0 of the notebook asserts agreement with the documented
worked example to four decimal places and halts if any category disagrees, and
also asserts that `webapp/model.py` — the module the Streamlit app imports —
produces bit-identical results. **The research is about the scoring map
$F \mapsto S$, not about the physics.**

### 1.2 Derivatives are computed on the *unrounded* score

The app displays a rounded score. Using the rounded score for derivative work
silently corrupts the analysis: a +10% stationery change moves the score by
0.046 points, which 2-decimal rounding quantises to 0.04 (a 13% error), and a
numerical slope taken across a rounded function collapses to 0 or to a
quantisation step. An early run of this notebook reported the stationery
sensitivity as −0.040 and a dead zone of 27.9% for the logistic — both were
rounding artefacts, not findings.

All elasticities and dead-zone calculations therefore use the exact
(clamped but unrounded) score functions `eco_score_exact` / `*_ev`. Display
rounding is reintroduced deliberately in exactly one place: §1.4 below.

### 1.3 "Dead zone" is defined by the gradient, not by the clamp

A student is counted as being in a dead zone when

$$\left|\frac{dS}{dF}\right| < 1 \text{ point per kg CO}_2\text{/day}$$

evaluated numerically. This definition was chosen because it is the only one
that applies fairly to all three scoring methods. For the original and the
percentile score it selects exactly the clamped set (their slope is either the
full linear slope or zero). For the logistic — which never truly saturates — it
selects the far tail where the curve has flattened enough that a student's
effort would not register on a displayed score. Reporting "0% saturated" for the
logistic would be technically true and practically misleading; this definition
avoids that.

### 1.4 The $R^2$ regression uses the integer-rounded score

$S$ is an exact affine function of $F$ inside the responsive region, so
regressing the full-precision score on $F$ over unsaturated students returns
$R^2 = 1.000000$ exactly — a true but uninformative number. The app reports the
score as an integer (`Math.round` in `src/logic.js`), so the notebook regresses
the integer score: the number a student actually sees. That gives
$R^2 = 0.9997$, and the notebook verifies that the missing $0.0003$ is precisely
the variance of uniform $\pm 0.5$ rounding ($1/12$) divided by the variance of
the score. **The headline "the formula explains 99.97% of the variation" is
therefore a statement about the deployed system, not a fitted result.**

### 1.5 The synthetic population's draw order is pinned

The seven variables are independent, so the order in which they consume the
seeded RNG stream changes only which draws land on which variable — never the
marginal distributions, and never any conclusion. It is nevertheless pinned in
`POPULATION['draw_order']` so the notebook, the web app and the published
results are bit-identical across machines. The order used
(`mode, lpg, distance, stationery, electricity, solar, waste`) is the one that
reproduces the published `KEY_RESULTS`; see §2.1.

### 1.6 The near-boundary student is a constructed profile

Section 3.7 needs a student sitting just below the clamp. The profile used —
motorbike 3 km, 45 kWh/month, 1.5 cylinders, 1.2 kg waste, Rs 200 — was chosen
to land on $F \approx 2.818$ kg/day, the footprint quoted in the published
results. It is a realistic Nepali profile (LPG-heavy, electricity-light) but it
is *selected*, not sampled, and the exact clamp percentage depends on that
choice. The qualitative finding — that a large fraction of plausible worlds
collapse onto zero near the boundary — holds for any profile in that region.

### 1.7 The population was not tuned to a target

The distributions were fixed from Nepali sources before any score was computed.
The resulting mean Eco-Score of **31.9**, with **nobody** reaching 100, is
simply what these emission factors produce on this population. It was not
adjusted, and it should not be — an uncomfortable mean is the finding.

---

## 2. Ambiguities and known deviations

### 2.1 Two of the published numbers cannot be reproduced exactly

The notebook recomputes all 30 numeric entries of `KEY_RESULTS` from scratch and
prints a validation table in Section 6. **24 of 30 agree to within 1%, 29 of 30
to within 5%.** The exceptions worth naming:

| Result | Published | Recomputed | Why |
|---|---|---|---|
| `percentile_F_low` | 1.404 | 1.393 | 0.78% — the 5th percentile is set by the low tail, which is dominated by the ~5% of solar households; small differences in which draws become solar move it |
| `floored_F_max` | 8.91 | 9.03 | 1.35% — a single extreme student (car + long commute); the maximum of a heavy-tailed sample is the least stable statistic in the analysis |
| `dead_zone_logistic_pct` | 0.25 | 0.30 | 20% *relative*, but 0.05 percentage points *absolute* — about five students out of 10,000 |
| `logistic_k` | 1.7202 | 1.7385 | 1.06% — refitted against a population that differs slightly; downstream metrics are unchanged to three decimals |
| `r2_full` | 0.8538 | 0.8639 | 1.18% — sensitive to the same extreme floored students as `floored_F_max` |

No amount of reordering the RNG stream reproduced `percentile_F_low = 1.404`
exactly; every ordering tried landed in 1.387–1.393. The residual is a genuine
implementation difference between two runs of the same specification, not a
disagreement about method. **No conclusion in this project depends on any of
these five numbers**, and the notebook prints the deviation rather than hiding
it.

The published values are retained as canonical in `model.py` so the paper, the
web app and the notebook quote one consistent set. The recomputed values are
written to `data/key_results.json` under `recomputed`, with per-key deviations
under `validation`.

### 2.2 A synthetic population cannot validate the model

It can only expose structural behaviour of the scoring function. It cannot tell
us whether the emission factors are right, whether Nepali students really
commute 3 km on average, or whether the floor percentage in a *real* school is
9% or 20%. Everything in Section 4 is conditional on the assumed marginals.
The diagnosis (a scoring map with zero gradient over a region containing real
students) is structural and survives changes to those marginals; the specific
percentages do not. Replace the population using
`research/data/survey_template.md` and refit before quoting any number as a
survey finding.

### 2.3 Emission factors are assumed independent

Variance propagation and the Monte Carlo both treat the five factors as
uncorrelated. They are probably not: the grid factor and the LPG factor both
depend on fuel import prices and both are published by processes with shared
methodology. Positive correlation would make the true SD of the score *larger*
than the 5.92 reported, so **±5.92 points should be read as a lower bound.**

### 2.4 The uncertainty percentages are documented estimates, not measurements

±15% on the grid factor is supported by the spread in NEA annual reports
2018–2023. The others (±10% bus, ±8% motorbike, ±10% car, ±5% LPG, ±20% waste,
±25% stationery) are reasoned estimates from the physical sources of variation,
not confidence intervals from a published study. They set the scale of the
uncertainty analysis, and a reader who disagrees with them can change one dict
and rerun.

### 2.5 The model ignores several real emission sources

Food, water, air travel, mixed-mode commutes and firewood cooking are all absent
from the student calculator. Firewood matters most: it has a *higher* factor
(1.747 kg CO₂/kg) than LPG, so households cooking on wood are currently recorded
as if they cook on nothing, which understates their footprint. This is a
limitation of the calculator inherited by the research, not introduced by it.

### 2.6 The logistic score is population-relative

Stated in the notebook's Section 5.2 and repeated in the app, because it is the
one thing a teacher could easily get wrong: $F_0$ is the median of the
population the score was fitted to. A score of 50 means "typical for this
population", not "1.75 kg CO₂/day". Consequences: the fit must be redone when
the population changes; scores are not comparable across schools unless
$(k, F_0)$ is pinned and published; and if everyone improves, the mean score
does not move. **The absolute kg CO₂/day figure must stay on screen beside the
score.**

---

## 3. Open items

- `[Mathematics Teacher]` is a placeholder in `README.md` and on the app's About
  page — replace with the supervisor's name before submission.
- No real survey data has been collected. Everything in Section 4 and Section 5
  is conditional on the synthetic population.
- The proposed logistic score is **not** wired into the parent application.
  `src/logic.js` is unmodified, as required. Adopting it means changing one
  function there and refitting $(k, F_0)$ on real data first.
- Correlation between emission factors (§2.3) has not been quantified; doing so
  would need the underlying NEA and IPCC methodology documents.
- The near-boundary analysis (§1.6) uses one constructed profile. A sweep across
  the whole boundary region would be a stronger result.
