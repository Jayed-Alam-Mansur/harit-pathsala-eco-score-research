# Can We Trust the Eco-Score?

A mathematical analysis of the Harit Pathsala (हरित पाठशाला) carbon footprint
calculator built at the Nepal Climate Hackathon 2025. The calculator asks a
student five questions about daily life and returns a single number from 0 to
100 — this project studies that number: which habits actually move it, how
precise it is, and how it behaves across a whole school. It concludes that the
formula is sound but its hard clamp silences 9.19% of students, and proposes a
logistic replacement that fixes this without changing a single emission factor.

**Researcher** · Jayed Alam Mansur — B.Tech Artificial Intelligence, Year 3,
Kathmandu University
**Supervised by** · [Mathematics Teacher] · Sandesh Thakuri

---

## Key findings

| # | Finding | Number |
|---|---|---|
| 1 | Students silenced by the floor — reported as exactly 0, with a gradient of zero in every category | **9.19%** |
| 2 | Real emissions spread across those silenced students, all shown the same score | **2.99 → 8.91 kg CO₂/day** |
| 3 | Uncertainty in any single score, from the emission factors alone (1σ) | **±5.92 points** |
| 4 | Variation explained once the clamped students are removed — the formula is not the problem | **R² = 0.9997** |
| 5 | Dead zone after replacing the clamp with the proposed logistic score | **9.19% → 0.25%** |

Supporting numbers: cooking moves the score **62×** more than stationery;
the population mean Eco-Score is **31.9** with **0.00%** reaching 100; the
household baseline (electricity + cooking + waste, before any commute) is
already **2.048 kg CO₂/day** against a floor at 3.0.

---

## What is here

```
research/
├── notebook/
│   ├── eco_score_research.ipynb   main research notebook, 7 sections
│   └── README.md                  notebook guide: sections, API, verification
├── webapp/
│   ├── app.py                     Streamlit web application, 4 pages
│   ├── model.py                   shared formula module (no Streamlit imports)
│   └── requirements.txt
├── figures/                       14 plots exported at 300 DPI
├── data/
│   ├── key_results.json           published + recomputed results
│   └── survey_template.md         real-survey specification (EN + नेपाली)
├── docs/
│   ├── research_notes.md          decisions, ambiguities, open items
│   └── presentation_script.md     spoken walkthrough of the whole story
├── final_story.html               self-contained narrative read / print-to-PDF
├── final_presentation.pptx        29-slide storytelling deck, speaker notes on every slide
├── webapp_guide.html              complete guide to the web app, with screenshots
└── README.md
```

`model.py` is imported by both the notebook and the web app, and the notebook
asserts that the two agree bit-for-bit — so the paper and the app can never
quote different numbers. **No file outside `research/` was modified.**

---

## How to run the notebook

```bash
cd research
pip install -r webapp/requirements.txt jupyter matplotlib seaborn
jupyter lab notebook/eco_score_research.ipynb
```

Then **Kernel → Restart & Run All**. It runs in about 13 seconds, writes all 14
figures to `figures/` at 300 DPI, and rewrites `data/key_results.json`.

Section 0 verifies the documented worked example (bus 2 km, 90 kWh, 1 cylinder,
0.6 kg waste, Rs 200) and raises `AssertionError` if any category disagrees with
`docs/calculator-math.md` to four decimal places, so a broken run fails loudly
rather than producing quiet nonsense.

Headless equivalent:

```bash
cd research/notebook
python -m nbconvert --to notebook --execute --inplace eco_score_research.ipynb
```

## How to run the web app

```bash
pip install -r research/webapp/requirements.txt
streamlit run research/webapp/app.py
```

Opens at `http://localhost:8501` with four pages: an interactive **Calculator**
scoring a student three ways, the **Research Findings**, **Understanding the
Math** (with an interactive Monte Carlo convergence demo), and **About This
Project** (with a class simulator and CSV export).

Run the notebook first — the Findings page embeds figures from `figures/`.

## How to replace the synthetic data with real survey data

The 10,000-student population in Section 4 is **synthetic**, because no survey
had been collected when this was written. To replace it:

1. Run the survey in `data/survey_template.md` (3 minutes, no PII, English and
   Nepali wording provided for all seven questions).
2. Export a CSV whose column names match exactly: `transport_mode`,
   `distance_km`, `electricity_kwh`, `has_solar`, `lpg_cylinders`,
   `waste_kg_day`, `stationery_npr`. These are the columns
   `generate_population()` produces, so it is a drop-in replacement.
3. In the notebook's Section 4, swap `pop = generate_population()` for
   `pd.read_csv(...)` plus the component block given at the top of
   `survey_template.md`.
4. Re-run from Section 4. The percentile boundaries, the logistic $F_0$ and $k$,
   and the floor percentage all recompute from the real data.
5. **Refit and republish `KEY_RESULTS` before quoting any number as a survey
   finding** — the current values describe the synthetic population.

At least 100 responses are needed before the median is stable enough to anchor
the logistic scale. Read `docs/research_notes.md` §2.2 first: a synthetic
population can expose structural behaviour of the scoring function, but it
cannot validate the emission factors or tell you the real floor percentage.

---

## References

1. **Nepal Electricity Authority**, *Annual Report 2022/23* — grid emission
   factor 0.23 kg CO₂/kWh; hydro/thermal mix (82% / 18%) and its year-to-year
   variation, used for the ±15% uncertainty on the grid factor.
2. **IPCC**, *2006 Guidelines for National Greenhouse Gas Inventories,
   Volume 2: Energy* — LPG combustion factor 1.51 kg CO₂/kg (carbon content ×
   44/12), and the open-burning and firewood factors used by the school tool.
3. **IPCC**, *2006 Guidelines, Volume 5: Waste* — landfill decomposition to CH₄
   and CO₂, basis of the 0.827 kg CO₂e/kg solid-waste factor.
4. **WRI / WBCSD**, *GHG Protocol Corporate Accounting and Reporting Standard* —
   scope definitions and the spend-based method behind the stationery factor
   (1.7285 kg CO₂e per 1000 NPR).
5. **UK DEFRA**, *2023 Greenhouse Gas Conversion Factors for Company Reporting* —
   cross-check for the vehicle factors (car 0.19, motorbike 0.066, bus 0.016
   kg CO₂/km) and for the passenger-load assumption behind the bus factor.
6. **Nepal Climate Hackathon 2025**, organiser's `Emission_factors.xlsx` — the
   authoritative source for every factor a student touches; mirrored in
   `src/logic.js` and documented in `docs/calculator-math.md`.
7. **C. E. Shannon**, *A Mathematical Theory of Communication*, Bell System
   Technical Journal, 1948 — entropy as the measure of how many distinguishable
   outcomes a scoring function produces, used to compare the three methods in
   Section 5.

---

## Version history

**v1.2** | 2026-08-06 | Added `final_presentation.pptx` — 29-slide dark deck for
projection, covering the full research plus the web app, with speaker notes on
every slide and live screenshots of all four pages. Added `webapp_guide.html` —
a complete self-contained guide to the application: how it works, every control
on every page, where each number comes from, how to change it, troubleshooting.

**v1.1** | 2026-08-06 | Added `final_story.html` — narrative companion to the
slide deck: one continuous long-form read, the same seven teacher questions
woven in at the point each was asked, 10 embedded figures, self-contained
single file, print-ready (A4, background graphics on).

**v1.0** | 2026-08-06 | Initial build complete — notebook (7 sections, 14
figures at 300 DPI), Streamlit web app (4 pages), shared model module, survey
template and research notes. All 30 published `KEY_RESULTS` recomputed from
scratch: 24 agree within 1%, 29 within 5%; deviations documented in
`docs/research_notes.md` §2.1.
