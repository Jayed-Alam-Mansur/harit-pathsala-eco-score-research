# `eco_score_research.ipynb` — notebook guide

Everything you need to open, run, read, verify and extend the main research
notebook. For the project as a whole see [`../README.md`](../README.md); for the
judgement calls behind the analysis see
[`../docs/research_notes.md`](../docs/research_notes.md).

| | |
|---|---|
| **Question** | Can we trust the Harit Pathsala Eco-Score? |
| **Sections** | 7 (numbered 0–6) |
| **Cells** | 63 — 32 markdown, 31 code |
| **Figures** | 14, written to `../figures/` at 300 DPI |
| **Runtime** | ~8 s compute, ~14 s wall including kernel start |
| **Outputs written** | `../figures/*.png` (14), `../data/key_results.json` |
| **Inputs read** | `../webapp/model.py` only — no data files, no network |
| **Determinism** | Fully seeded (seed 42). Same machine, same numbers, every run. |

---

## Quick start

```bash
# from the repository root
pip install -r research/webapp/requirements.txt jupyter matplotlib seaborn
jupyter lab research/notebook/eco_score_research.ipynb
```

Then **Kernel → Restart & Run All**.

Headless (what CI or a supervisor's check should run):

```bash
cd research/notebook
python -m nbconvert --to notebook --execute --inplace eco_score_research.ipynb
```

The notebook locates `research/` by walking up from the kernel's working
directory until it finds `webapp/model.py`, so it runs correctly from
`research/notebook/`, from `research/`, or from the repository root.

### Dependencies

`numpy`, `pandas`, `scipy`, `statsmodels`, `matplotlib`, `seaborn`, plus
`jupyter`/`nbconvert` to execute it. Everything except the last two is already in
`../webapp/requirements.txt`. Built and verified against Python 3.12.3, NumPy
1.26.4, pandas 2.1.4, SciPy 1.14.1, statsmodels 0.14.6, matplotlib 3.10.0.

`pandas.io.formats.style` (used once for a coloured emission-factor table) needs
`jinja2`; if it is missing the cell falls back to a plain text table rather than
failing.

---

## What each section does

### Section 0 — Setup and Verification · 6 md + 6 code

Imports, plot styling, the `EF` / `UNCERTAINTY` / `POPULATION` dictionaries, the
four scoring functions, and — the part that matters — **verification**. It
recomputes the worked example documented in `docs/calculator-math.md`
(bus 2 km · 90 kWh · 1 cylinder · 0.6 kg waste · Rs 200), prints a
computed-vs-expected table, and calls `np.testing.assert_almost_equal` on every
category to 4 decimals. If any factor or formula has drifted, the notebook stops
here with a named `AssertionError` instead of producing quiet nonsense.

It then asserts that `../webapp/model.py` — the module the Streamlit app imports
— agrees with the notebook on every function and on the whole population, so the
app and the paper can never quote different numbers.

**Prints:** `Daily total: 1.976457 kg CO₂/day | Eco-Score: 41 ✓`
**Writes:** `../data/key_results.json` (published values; rewritten in §6)

### Section 1 — Model Definition · 3 md + 3 code · figures 01–02

States the model algebraically: $F=\sum\theta_i x_i$ is linear in both the
activities and the factors, and $S$ is a clamped affine map of $F$ with a
piecewise derivative that is $-40$ in the middle and $0$ at both ends. Builds the
emission-factor table with each factor's physical derivation, then plots the
scoring function with its two dead zones shaded, and the worked example's
category breakdown.

### Section 2 — Sensitivity Analysis · 4 md + 3 code · figures 03–04

Derives $\partial S/\partial x_i = -40\,\theta_i$ in the responsive region and
exactly $0$ elsewhere, then measures the discrete elasticity — the score change
from a realistic **+10%** increase in each habit, which is comparable across
categories in a way raw derivatives are not (km vs kWh vs NPR).

The heatmap contrasts three archetypes: a low-footprint student ($F=0.30$,
ceiling), the worked example ($F=1.98$, responsive) and a high-footprint student
($F=4.22$, floor). Hatched cells mark clamped zones, where every elasticity is
exactly zero.

**Headline:** cooking **−2.859**, electricity **−2.760**, waste **−1.985**,
transport **−0.256**, stationery **−0.046** → a **62×** ratio.

### Section 3 — Uncertainty Quantification · 5 md + 6 code · figures 05–07

Treats each emission factor as $\theta_i \sim \mathcal{N}(\mu_i, (\mu_i u_i)^2)$
clipped positive, and answers "how precise is a score?" twice over:

1. **Analytically** — because $F$ is linear in $\theta$, $\operatorname{Var}(F)=\sum(c_i u_i)^2$
   propagates exactly, and $\operatorname{SD}(S)=40\operatorname{SD}(F)$.
2. **By Monte Carlo** — 10,000 draws of the factor vector, seed 42.

They agree to **1.29%** (5.92 vs 5.99 points), which is the point: inside the
responsive region simulation only confirms the algebra. §3.7 then moves the
student to $F\approx2.818$, just below the clamp, where the algebra stops
applying — the clamp is not affine, so the distribution becomes asymmetric with a
point mass on zero, and ~19.8% of plausible worlds report 0 instead of 7.

The closing markdown answers **"is this the same Monte Carlo as in DAA?"**
directly: there, randomness is a computational trick applied to a deterministic
question; here the randomness is a property of the physical world.

### Section 4 — Model Validation · 6 md + 5 code · figures 08–11

Generates **10,000 synthetic students** and studies how the score behaves over a
whole school rather than one example. The log-normal commute is parameterised
through $\mu = \ln(\bar x) - \sigma^2/2$ so the *arithmetic* mean is 3.00 km —
the one place this is easy to get wrong, and the section says so.

Covers the population distributions, per-category correlation with the score
(including how much signal clamping destroys), an OLS regression of score on
footprint, and the saturation analysis.

**Headline:** mean $F$ **2.246 kg CO₂/day**, mean score **31.9**, **9.19%** at
the floor, **0.00%** at the ceiling, floored students spanning **2.99–8.91
kg/day**, $R^2$ **0.8639** overall vs **0.9997** unsaturated.

### Section 5 — Calibration Improvement · 5 md + 6 code · figures 12–14

The proposed contribution. Two replacements for the clamp, both leaving $F$ and
every emission factor untouched:

- **Method A — percentile:** boundaries at the population's 5th/95th percentile.
- **Method B — logistic (recommended):** $S=100/(1+e^{k(F-F_0)})$ with $F_0$ the
  population median and $k$ fitted by `scipy.optimize.minimize_scalar` against
  the original score.

Compares all three on mean, spread, floor/ceiling, **dead zone** and **Shannon
entropy** over 20 bins, and closes by stating the trade-off plainly: the logistic
score is population-relative, must be refitted when the population changes, and
requires the absolute kg CO₂/day figure to stay visible beside it.

### Section 6 — Summary and Conclusions · 2 md + 2 code

Prints the **validation table** — all 30 published `KEY_RESULTS` recomputed from
scratch with per-key deviation — then seven conclusions, each carrying its
number. The final cell asserts all 14 figures exist and rewrites
`../data/key_results.json` with published values, recomputed values, deviations,
the emission factors, the population spec and a summary block (187 values).

---

## Reference — what the notebook defines

### Scoring functions

| Function | Purpose |
|---|---|
| `calculate_footprint(...)` | five inputs → `(daily_total, components)` |
| `eco_score(F)` | original clamped min–max score, rounded to 2 dp |
| `eco_score_percentile(F, F_low, F_high)` | Method A |
| `eco_score_logistic(F, k, F0)` | Method B (recommended) |
| `eco_score_v` · `_percentile_v` · `_logistic_v` | vectorised twins, same rounding |
| `eco_score_exact` · `*_ev` | **unrounded** twins — used for all derivatives |

> **Why two families.** The app rounds the score for display, and rounding
> destroys derivatives: a +10% stationery change moves the score by 0.046 points,
> which 2-dp rounding quantises to 0.04, and a numerical slope across a rounded
> function collapses to 0 or a quantisation step. Every elasticity and dead-zone
> calculation uses the `_exact` / `_ev` family. This is not cosmetic — an early
> draft reported stationery as −0.040 and the logistic dead zone as 27.9%, both
> pure rounding artefacts. See `../docs/research_notes.md` §1.2.

### Analysis helpers

| Function | Returns |
|---|---|
| `elasticity(inputs, pct=0.10)` | `(S0, F0, DataFrame)` of per-category score change |
| `analytical_sd(components, mode)` | `(sd_F, sd_S, variance_parts)` |
| `draw_factor(key, n)` · `monte_carlo(inputs, n, seed)` | factor draws · `(F_samples, S_samples)` |
| `generate_population(spec)` | 10,000-row DataFrame, identical to `model.generate_population()` |
| `entropy_nats(x, bins=20)` | Shannon entropy in nats |
| `dead_zone_pct(score_fn, F)` | % of students with $\lvert dS/dF\rvert < 1$ pt per kg/day |
| `savefig(fig, name)` | writes to `../figures/` at 300 DPI |

### Key objects

`EF`, `UNCERTAINTY`, `POPULATION`, `KEY_RESULTS` (published), `COMPUTED`
(recomputed, filled as sections run), `COLORS`, `WORKED_INPUTS`, `ARCHETYPES`,
`NEAR` (near-boundary profile), `N_MC` (10,000).

Useful DataFrames after a full run: `pop` (the population, with `F`, `S`,
`S_pct`, `S_log`), `elas` (elasticities), `comparison` (three-method table),
`validation` (published vs recomputed), `ef_table`, `ctab`.

### Figure index

| # | File | Section | Shows |
|---|---|---|---|
| 01 | `01_eco_score_function.png` | 1 | $S(F)$ with both dead zones shaded |
| 02 | `02_worked_example_breakdown.png` | 1 | category breakdown of the worked example |
| 03 | `03_tornado_sensitivity.png` | 2 | elasticity per category |
| 04 | `04_elasticity_heatmap.png` | 2 | 3 archetypes × 5 categories, clamped cells hatched |
| 05 | `05_uncertainty_analytical_vs_mc.png` | 3 | variance formula vs 10,000-run simulation |
| 06 | `06_monte_carlo_f_vs_s.png` | 3 | all draws, clamped ones flagged |
| 07 | `07_near_boundary_breakdown.png` | 3 | point mass forming on zero near the clamp |
| 08 | `08_population_distributions.png` | 4 | daily / score / monthly / yearly |
| 09 | `09_correlation_bars.png` | 4 | per-category correlation and signal retention |
| 10 | `10_regression_fit.png` | 4 | $R^2$ all students vs unsaturated only |
| 11 | `11_saturation_histogram.png` | 4 | **the key finding** — the floor spike |
| 12 | `12_scoring_functions_comparison.png` | 5 | three curves over the population density |
| 13 | `13_score_distribution_comparison.png` | 5 | same students, three scoring methods |
| 14 | `14_final_recommendation.png` | 5 | the recommended logistic curve |

---

## Verifying a run

A correct execution satisfies all of these; the notebook checks the starred ones
itself and stops if they fail.

- ★ Section 0 prints `Daily total: 1.976457 kg CO₂/day | Eco-Score: 41 ✓`
- ★ every worked-example category matches the docs to 4 decimals
- ★ `model.py` agrees with the notebook on all functions and the full population
- ★ all 14 figures exist at the end (Section 6 asserts it)
- zero error cells across the notebook
- stationery has the **lowest** sensitivity (−0.046), not transport (−0.256)
- population mean score lands in 25–45 (**31.9**) — *not* tuned to a target
- logistic dead zone below 1% (**0.30%**)
- Section 6's validation table: 24 of 30 published values within 1%, 29 within 5%

One-liner:

```bash
python - <<'PY'
import nbformat
nb = nbformat.read('eco_score_research.ipynb', as_version=4)
errs = sum(1 for c in nb.cells if any(o.output_type=='error' for o in c.get('outputs',[])))
T = '\n'.join(o.text for c in nb.cells for o in c.get('outputs',[]) if o.output_type=='stream')
print('errors:', errs, '| verified:', 'Eco-Score: 41 ✓' in T, '| figures:', '14/14' in T)
PY
```

---

## Extending it

**Replace the synthetic population with real survey data.** Run the survey in
[`../data/survey_template.md`](../data/survey_template.md), then in Section 4
swap `pop = generate_population()` for `pd.read_csv(...)` plus the component
block given at the top of that file. Sections 4–6 recompute unchanged. Refit and
republish `KEY_RESULTS` before quoting anything as a survey finding — and read
`../docs/research_notes.md` §2.2 first on what a synthetic population can and
cannot establish.

**Change the uncertainty assumptions.** Edit the `UNCERTAINTY` dict in Section 0
and rerun. Note that the factors are assumed independent; positive correlation
would make the true SD *larger*, so ±5.92 points is a lower bound
(`research_notes.md` §2.3).

**Try different scoring boundaries.** Section 5 recomputes Method A's
percentiles from whatever population is loaded. To change the published
constants used elsewhere, edit `eco_score_percentile`'s defaults in **both** the
notebook and `../webapp/model.py` — Section 0's cross-check will fail loudly if
they drift apart, which is the intended behaviour.

**Add a figure.** Use `savefig(fig, 'NN_name.png')` and add the filename to
`EXPECTED_FIGURES` in the last cell, or the completeness assertion will not cover
it.

### Things to be careful about

- Cells are **order-dependent**: `COMPUTED` accumulates across sections and
  Section 6 reads it. Always Restart & Run All rather than re-running cells
  piecemeal.
- Use the `_exact` / `_ev` score functions for anything involving a slope,
  difference or derivative.
- `POPULATION['draw_order']` is pinned deliberately. The variables are
  independent so the order changes no distribution and no conclusion, but
  changing it will shift the last digits of every population statistic.
- The notebook never modifies anything outside `research/`; `src/logic.js` is
  read-only reference.

---

*Part of the Harit Pathsala Eco-Score research project · v1.0 · 2026-08-06
Jayed Alam Mansur — B.Tech Artificial Intelligence, Year 3, Kathmandu University*
