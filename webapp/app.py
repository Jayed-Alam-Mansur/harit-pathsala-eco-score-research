"""
app.py — Harit Pathsala Eco-Score research web application.

Four pages: an interactive calculator that scores a student three ways, the
research findings, the mathematics explained, and the project record.

Run with:   streamlit run research/webapp/app.py
All formulas come from model.py, which the notebook imports too, so this app
and the paper can never quote different numbers.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Make `model` importable no matter which directory streamlit was launched from.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from model import (
    EF, UNCERTAINTY, POPULATION, KEY_RESULTS, COLORS, TRANSPORT_MODES,
    F_MIN, F_MAX, SCORE_SLOPE,
    calculate_footprint, eco_score, eco_score_percentile, eco_score_logistic,
    eco_score_vec, eco_score_percentile_vec, eco_score_logistic_vec,
    generate_population, analytical_score_sd, monte_carlo_scores,
)

st.set_page_config(
    page_title="Harit Pathsala Eco-Score Research",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIGDIR, DATADIR = ROOT / "figures", ROOT / "data"


def _stretch():
    """Streamlit renamed `use_container_width` to `width` in 1.49.

    requirements.txt allows >= 1.32, so support both without emitting a
    deprecation warning on every widget.
    """
    try:
        major, minor = (int(p) for p in st.__version__.split(".")[:2])
        if (major, minor) >= (1, 49):
            return {"width": "stretch"}
    except Exception:
        pass
    return {"use_container_width": True}


STRETCH = _stretch()

K_LOG, F0_LOG = KEY_RESULTS["logistic_k"], KEY_RESULTS["logistic_F0"]
P_LOW, P_HIGH = KEY_RESULTS["percentile_F_low"], KEY_RESULTS["percentile_F_high"]

WORKED = dict(transport_mode="bus", distance_km=2.0,
              electricity_units_monthly=90, has_solar=False,
              lpg_cylinders_monthly=1.0, waste_kg_day=0.6,
              stationery_npr_monthly=200)
WORKED_SCORE = 41

MODE_LABEL = {"walk": "🚶 Walk", "bicycle": "🚲 Bicycle", "bus": "🚌 Bus",
              "motorbike": "🏍️ Motorbike", "car": "🚗 Car"}
WASTE_LABEL = {0.3: "Small (~0.3 kg)", 0.6: "Medium (~0.6 kg)", 1.2: "Large (~1.2 kg)"}
CATEGORIES = ["transport", "electricity", "cooking", "waste", "stationery"]


# ---------------------------------------------------------------- helpers
@st.cache_data(show_spinner=False)
def load_results_json() -> str:
    path = DATADIR / "key_results.json"
    if path.exists():
        return path.read_text()
    return json.dumps(KEY_RESULTS, indent=2)


@st.cache_data(show_spinner=False)
def value_count() -> int:
    def walk(o):
        if isinstance(o, dict):
            return sum(walk(v) for v in o.values())
        if isinstance(o, (list, tuple)):
            return sum(walk(v) for v in o)
        return 1
    try:
        return walk(json.loads(load_results_json()))
    except Exception:
        return len(KEY_RESULTS)


@st.cache_data(show_spinner=False)
def mc_for(transport_mode, distance_km, electricity_units_monthly, has_solar,
           lpg_cylinders_monthly, waste_kg_day, stationery_npr_monthly,
           n=1000, seed=42):
    return monte_carlo_scores(transport_mode, distance_km,
                              electricity_units_monthly, has_solar,
                              lpg_cylinders_monthly, waste_kg_day,
                              stationery_npr_monthly, n=n, seed=seed)


def show_figure(name: str, caption: str = ""):
    path = FIGDIR / name
    if path.exists():
        st.image(str(path), caption=caption, **STRETCH)
    else:
        st.warning(f"Figure `{name}` not found — run the notebook to generate "
                   f"`research/figures/`.")


def curves_figure(F_current=None, show_all=True, height=430):
    """The three scoring functions, optionally marking a student's position."""
    xs = np.linspace(0, 5, 500)
    fig = go.Figure()
    # dead zones of the original score
    for x0, x1 in [(0, F_MIN), (F_MAX, 5)]:
        fig.add_vrect(x0=x0, x1=x1, fillcolor="grey", opacity=0.13,
                      line_width=0, layer="below")
    fig.add_trace(go.Scatter(x=xs, y=eco_score_vec(xs), name="Original",
                             line=dict(color="#4472C4", width=3)))
    if show_all:
        fig.add_trace(go.Scatter(x=xs, y=eco_score_percentile_vec(xs),
                                 name="Percentile",
                                 line=dict(color="#ED7D31", width=2.5, dash="dash")))
        fig.add_trace(go.Scatter(x=xs, y=eco_score_logistic_vec(xs),
                                 name="Logistic ★",
                                 line=dict(color="#70AD47", width=3.5)))
    if F_current is not None:
        fig.add_vline(x=F_current, line=dict(color="#C00000", width=2, dash="dot"))
        pts = [("Original", eco_score(F_current), "#4472C4")]
        if show_all:
            pts += [("Percentile", eco_score_percentile(F_current), "#ED7D31"),
                    ("Logistic", eco_score_logistic(F_current), "#70AD47")]
        for label, val, colour in pts:
            fig.add_trace(go.Scatter(
                x=[F_current], y=[val], mode="markers", name=f"you · {label}",
                marker=dict(size=13, color=colour, line=dict(color="white", width=2)),
                hovertemplate=f"{label}: %{{y:.2f}}<extra></extra>", showlegend=False))
    fig.update_layout(
        height=height, margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title="Daily footprint F (kg CO₂/day)", yaxis_title="Score (0–100)",
        yaxis_range=[-3, 105], xaxis_range=[0, 5],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        hovermode="x unified")
    return fig


def breakdown_figure(components, height=330):
    cats = sorted(CATEGORIES, key=lambda c: components[c])
    vals = [components[c] for c in cats]
    fig = go.Figure(go.Bar(
        x=vals, y=[c.capitalize() for c in cats], orientation="h",
        marker_color=[COLORS[c] for c in cats],
        text=[f"{v:.4f}" for v in vals], textposition="outside",
        hovertemplate="%{y}: %{x:.4f} kg CO₂/day<extra></extra>"))
    fig.update_layout(height=height, margin=dict(l=10, r=60, t=30, b=10),
                      xaxis_title="kg CO₂ / day", showlegend=False,
                      xaxis_range=[0, max(vals) * 1.28 if max(vals) > 0 else 1])
    return fig


# ---------------------------------------------------------------- sidebar
st.sidebar.title("🌿 Harit Pathsala")
st.sidebar.caption("Eco-Score research · हरित पाठशाला")
page = st.sidebar.radio(
    "Go to",
    ["🏠 Calculator", "📊 Research Findings", "🎓 Understanding the Math",
     "📁 About This Project"],
    label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.caption(
    f"**{POPULATION['N']:,}** simulated students · seed {POPULATION['seed']}  \n"
    f"Mean Eco-Score **{KEY_RESULTS['population_mean_score']}** · "
    f"**{KEY_RESULTS['floor_pct']}%** at the floor")


# ============================================================ PAGE 1
if page == "🏠 Calculator":
    st.title("Your Eco-Score — Three Ways")
    st.caption("See how the original score compares to two mathematically "
               "calibrated alternatives")

    left, right = st.columns([1, 1.45], gap="large")

    with left:
        st.subheader("Your Daily Habits")
        transport_mode = st.selectbox(
            "How do you get to school?", TRANSPORT_MODES, index=2,
            format_func=lambda x: MODE_LABEL[x])
        distance_km = st.slider("One-way distance (km)", 0.5, 20.0, 2.0, 0.5)
        electricity = st.slider("Monthly electricity (kWh)", 10, 300, 90)
        has_solar = st.checkbox("Has rooftop solar?", False)
        lpg = st.slider("LPG cylinders per month", 0.25, 4.0, 1.0, 0.25)
        waste = st.selectbox("Daily household waste", [0.3, 0.6, 1.2],
                             format_func=lambda x: WASTE_LABEL[x], index=1)
        stationery = st.slider("Monthly stationery spend (NPR)", 0, 600, 200, 50)

    F, components = calculate_footprint(
        transport_mode, distance_km, electricity, has_solar, lpg, waste, stationery)
    S_orig = eco_score(F)
    S_pct = eco_score_percentile(F)
    S_log = eco_score_logistic(F)
    S_orig_int = int(round(S_orig))

    with right:
        m1, m2, m3 = st.columns(3)
        m1.metric("Original Score", f"{S_orig_int}",
                  delta=f"{S_orig_int - WORKED_SCORE:+d} vs worked example",
                  delta_color="normal")
        m2.metric("Percentile Method", f"{S_pct:.0f}")
        m3.metric("Logistic ★", f"{S_log:.0f}")

        c1, c2, c3 = st.columns(3)
        c1.metric("Daily", f"{F:.3f} kg CO₂")
        c2.metric("Monthly", f"{F * 30:.1f} kg CO₂")
        c3.metric("Yearly", f"{F * 365:.0f} kg CO₂")

        st.markdown("##### Where your footprint comes from")
        st.plotly_chart(breakdown_figure(components), **STRETCH)

        st.markdown("##### Where you land on each scoring curve")
        st.plotly_chart(curves_figure(F), **STRETCH)

    # ---- context box
    if F < F_MIN:
        st.success(
            f"**Very low footprint.** The original score gives 100 but cannot "
            f"tell you how much better you are than other low-footprint "
            f"students — everyone below {F_MIN} kg/day receives the same 100. "
            f"The logistic can: your logistic score is **{S_log}**.")
    elif F <= F_MAX:
        st.info(
            "**You are in the responsive zone.** The original score works "
            "correctly here. All three methods give similar results because "
            "the scoring formula is working as intended — every change in your "
            "habits moves your score.")
    else:
        st.error(
            f"**You are in the dead zone.** The original score gives you 0 — "
            f"but your actual footprint is {F:.2f} kg/day. The logistic still "
            f"shows your position: **{S_log}/100**. Every reduction in your "
            f"habits moves this score, while the original stays at 0 no matter "
            f"what you change.")

    # ---- uncertainty
    with st.expander("How reliable is this score?"):
        sd_F, sd_S = analytical_score_sd(components, transport_mode)
        lo, hi = S_orig - 2 * sd_S, S_orig + 2 * sd_S
        st.markdown(
            f"Your score of **{S_orig_int}** has a 95% confidence range of "
            f"**[{max(0, lo):.0f}, {min(100, hi):.0f}]** due to variability in "
            f"the emission factors themselves — the Nepal grid factor moves "
            f"±15% year to year, waste composition ±20%, and supply-chain "
            f"factors ±25%. One standard deviation is **±{sd_S:.2f} points** "
            f"(±{sd_F:.4f} kg CO₂/day)."
        )
        F_mc, S_mc = mc_for(transport_mode, distance_km, electricity, has_solar,
                            lpg, waste, stationery, n=1000)
        fig = go.Figure(go.Histogram(x=S_mc, nbinsx=45, marker_color="#70AD47",
                                     opacity=0.85, name="simulated"))
        fig.add_vline(x=S_orig, line=dict(color="#222", width=2),
                      annotation_text=f"reported {S_orig_int}")
        for s in (-1, 1):
            fig.add_vline(x=S_orig + s * sd_S, line=dict(color="#C00000",
                                                         width=1.5, dash="dash"))
        fig.update_layout(height=280, margin=dict(l=10, r=10, t=30, b=10),
                          xaxis_title="Eco-Score from 1,000 simulated worlds",
                          yaxis_title="draws", showlegend=False)
        st.plotly_chart(fig, **STRETCH)
        clamped = 100 * float(((S_mc <= 0) | (S_mc >= 100)).mean())
        if clamped > 0.5:
            st.warning(f"**{clamped:.1f}%** of those simulated worlds land on a "
                       f"clamp boundary. Near the boundary the reported score is "
                       f"not just uncertain — it is systematically distorted.")
        st.caption(f"Analytical SD {sd_S:.3f} pts · Monte Carlo SD "
                   f"{S_mc.std(ddof=1):.3f} pts (1,000 draws)")


# ============================================================ PAGE 2
elif page == "📊 Research Findings":
    st.title("What the Research Found")
    st.caption(f"Key results from the analysis of "
               f"{POPULATION['N']:,} simulated students")

    a, b, c, d = st.columns(4)
    a.metric("Mean Eco-Score", f"{KEY_RESULTS['population_mean_score']} / 100")
    b.metric("Floor Saturation", f"{KEY_RESULTS['floor_pct']}%",
             help="students scoring exactly 0")
    c.metric("Score Uncertainty", f"±{KEY_RESULTS['sd_score_analytical']} pts",
             help="one standard deviation")
    d.metric("Dead Zone Reduced",
             f"{KEY_RESULTS['dead_zone_logistic_pct']}%",
             delta=f"from {KEY_RESULTS['dead_zone_original_pct']}%",
             delta_color="inverse", help="with the logistic fix")

    st.divider()

    # ---------------- Finding 1
    with st.expander("**Finding 1 — Cooking and Electricity Control the Score**",
                     expanded=True):
        sens = {c: KEY_RESULTS[f"sensitivity_{c}"] for c in CATEGORIES}
        order = sorted(CATEGORIES, key=lambda c: sens[c])
        fig = go.Figure(go.Bar(
            x=[sens[c] for c in order], y=[c.capitalize() for c in order],
            orientation="h", marker_color=[COLORS[c] for c in order],
            text=[f"{sens[c]:.3f}" for c in order], textposition="outside"))
        fig.update_layout(height=330, margin=dict(l=10, r=70, t=20, b=10),
                          xaxis_title="Change in Eco-Score for a +10% increase "
                                      "in that habit")
        st.plotly_chart(fig, **STRETCH)
        st.error(f"### {KEY_RESULTS['sensitivity_ratio']:.0f}× ratio between "
                 f"cooking and stationery")
        st.markdown(
            f"A +10% change moves the score **{KEY_RESULTS['sensitivity_cooking']}** "
            f"points for cooking and **{KEY_RESULTS['sensitivity_electricity']}** "
            f"for electricity, but only **{KEY_RESULTS['sensitivity_stationery']}** "
            f"for stationery.\n\n"
            "> A student could spend the entire year buying less stationery and "
            "move their score by less than one point.\n\n"
            "In the responsive region the derivative is exactly "
            "∂S/∂xᵢ = −40·θᵢ, so this ranking is fixed by the emission factors "
            "and is the same for every student. Advice must follow this order.")
        show_figure("03_tornado_sensitivity.png")

    # ---------------- Finding 2
    with st.expander("**Finding 2 — A Score of 41 Could Mean Anywhere from 29 to 53**"):
        c1, c2, c3 = st.columns(3)
        c1.metric("Analytical SD", f"{KEY_RESULTS['sd_score_analytical']} pts")
        c2.metric("Monte Carlo SD", f"{KEY_RESULTS['sd_score_montecarlo']} pts")
        c3.metric("Agreement", f"{KEY_RESULTS['agreement_pct']}%",
                  help="difference between the two methods")
        F_mc, S_mc = mc_for(**WORKED, n=10000)
        fig = go.Figure(go.Histogram(x=S_mc, nbinsx=60, marker_color="#4472C4",
                                     opacity=0.85))
        fig.add_vline(x=WORKED_SCORE, line=dict(color="#222", width=2),
                      annotation_text="reported 41")
        for s, dash in [(1.96, "dash"), (-1.96, "dash")]:
            fig.add_vline(x=WORKED_SCORE + s * KEY_RESULTS["sd_score_analytical"],
                          line=dict(color="#C00000", width=1.5, dash=dash))
        fig.update_layout(height=340, margin=dict(l=10, r=10, t=30, b=10),
                          xaxis_title="Eco-Score across 10,000 simulated worlds",
                          yaxis_title="draws")
        st.plotly_chart(fig, **STRETCH)
        st.markdown(
            "> The emission factors are estimates, not exact numbers. The "
            "uncertainty in the input factors creates uncertainty in the "
            "output score.\n\n"
            "Two students whose scores differ by fewer than about **12 points** "
            "are not distinguishable given what we know about the factors. A "
            "classroom leaderboard built on single-point differences is reading "
            "noise. Variance is dominated by electricity (±15%) and waste "
            "(±20%) — so the way to make the score more precise is to measure "
            "the grid factor better, not to ask students more questions.")
        show_figure("05_uncertainty_analytical_vs_mc.png")

    # ---------------- Finding 3
    with st.expander("**Finding 3 — 9.19% of Students Are Silenced** ⚠️"):
        st.error(
            f"These students span footprints from "
            f"**{KEY_RESULTS['floored_F_min']} to {KEY_RESULTS['floored_F_max']} "
            f"kg/day** — a 3× difference in real emissions — all reported as the "
            f"same score: **0**.")
        show_figure("11_saturation_histogram.png",
                    "Every student above 3.0 kg CO₂/day receives the same score.")
        c1, c2, c3 = st.columns(3)
        c1.metric("At the floor (S = 0)", f"{KEY_RESULTS['floor_pct']}%")
        c2.metric("At the ceiling (S = 100)", f"{KEY_RESULTS['ceiling_pct']}%")
        c3.metric("Household baseline",
                  f"{KEY_RESULTS['household_baseline']} kg/day",
                  help="electricity + cooking + waste, before any commute")
        st.markdown(
            f"For every one of these students the gradient is exactly zero: "
            f"∇ₓS = **0** in all five categories. Halving their waste changes "
            f"their score by 0.000 points.\n\n"
            f"The cause is visible in the third metric. Electricity, cooking and "
            f"waste alone — before a student travels a single kilometre — "
            f"average **{KEY_RESULTS['household_baseline']} kg CO₂/day**, already "
            f"82% of the way to the 3.0 kg/day floor. The boundaries were chosen "
            f"for a footprint scale these emission factors do not produce, so a "
            f"student in an ordinary Nepali household starts near the floor "
            f"regardless of any choice they personally control.")

    # ---------------- Finding 4
    with st.expander("**Finding 4 — The Formula Is Perfect. The Clamp Is Broken.**"):
        c1, c2 = st.columns(2)
        c1.metric("R² — all students", f"{KEY_RESULTS['r2_full']:.4f}")
        c2.metric("R² — unsaturated only", f"{KEY_RESULTS['r2_unsaturated']:.4f}",
                  delta=f"+{KEY_RESULTS['r2_unsaturated'] - KEY_RESULTS['r2_full']:.4f}")
        show_figure("10_regression_fit.png")
        st.markdown(
            "> When we remove the students caught at the floor, the scoring "
            "system explains 99.97% of the variation between students. The "
            "formula is working exactly as designed. The clamp is the entire "
            "problem.\n\n"
            "The remaining 0.03% is not model error either — it is exactly the "
            "variance of rounding the score to a whole number for display "
            "(1/12 ≈ 0.083 points²). There is nothing left to improve in the "
            "arithmetic.")

    # ---------------- Finding 5
    with st.expander("**Finding 5 — Two Better Alternatives**"):
        st.plotly_chart(curves_figure(height=460), **STRETCH)
        table = pd.DataFrame({
            "Method": ["Original (min–max)", "Percentile", "Logistic ★"],
            "Dead zone %": [KEY_RESULTS["dead_zone_original_pct"],
                            KEY_RESULTS["dead_zone_percentile_pct"],
                            KEY_RESULTS["dead_zone_logistic_pct"]],
            "Entropy (nats)": [KEY_RESULTS["entropy_original"],
                               KEY_RESULTS["entropy_percentile"],
                               KEY_RESULTS["entropy_logistic"]],
            "Preserves ranking": ["no — ties at 0", "no — ties at both ends",
                                  f"yes, ρ = {KEY_RESULTS['spearman_logistic']:.6f}"],
            "Never saturates": ["no", "no", "yes"],
        }).set_index("Method")
        st.dataframe(table, **STRETCH)
        st.success(
            f"**Recommendation — use the logistic score** "
            f"(k = {K_LOG}, F₀ = {F0_LOG}) for the reported Eco-Score. It cuts "
            f"the dead zone from {KEY_RESULTS['dead_zone_original_pct']}% to "
            f"{KEY_RESULTS['dead_zone_logistic_pct']}%, preserves the footprint "
            f"ranking exactly, and agrees with the current score where the "
            f"current score works (r = {KEY_RESULTS['pearson_logistic_vs_orig']}). "
            f"**Use the percentile method where a threshold interpretation "
            f"matters** — its boundaries can be set from a policy target rather "
            f"than from the population.")
        st.warning(
            "**The trade-off:** the logistic score is population-relative. F₀ is "
            "the population median, so 50 means *typical for this population*, "
            "not 1.75 kg CO₂/day. It must be refitted when the population "
            "changes, scores are not comparable across populations unless "
            "(k, F₀) is pinned, and if everyone improves the average score does "
            "not move. The absolute kg CO₂/day figure must stay on screen "
            "beside it.")
        show_figure("14_final_recommendation.png")


# ============================================================ PAGE 3
elif page == "🎓 Understanding the Math":
    st.title("The Mathematics Behind the Score")

    # ---------------- 1
    with st.expander("**Where the Formula Came From**", expanded=True):
        st.markdown("The footprint is a linear weighted sum of five activities:")
        st.latex(r"F = \sum_{i=1}^{5} \theta_i x_i")
        st.markdown("and the score is a clamped affine map of that total:")
        st.latex(r"S(F) = \text{clamp}\left(0, 100, 100 - \frac{F - 0.5}{2.5} "
                 r"\times 100\right)")
        st.markdown(
            "which is min–max normalisation between $F_{min}=0.5$ and "
            "$F_{max}=3.0$ kg CO₂/day, giving a constant slope of **−40 points "
            "per kg CO₂/day** in between.")
        st.divider()
        st.markdown("##### Each emission factor is a physical derivation, not a guess")
        st.markdown("**LPG cooking.** A Nepali cylinder holds 14.2 kg of LPG. "
                    "IPCC 2006 gives 1.51 kg CO₂ per kg of LPG burned "
                    "(carbon content × 44/12 molecular weight ratio):")
        st.latex(r"14.2\ \text{kg} \times 1.51\ \frac{\text{kg CO}_2}{\text{kg}} "
                 r"= 21.442\ \frac{\text{kg CO}_2}{\text{cylinder}}")
        st.markdown("**Bus travel.** Diesel emits 2.68 kg CO₂ per litre. A Nepali "
                    "bus manages about 4 km per litre and carries about 40 "
                    "passengers, so one passenger-kilometre is:")
        st.latex(r"\frac{2.68}{4 \times 40} = 0.016\ "
                 r"\frac{\text{kg CO}_2}{\text{passenger-km}}")
        st.markdown("The same reasoning gives motorbike 2.31 ÷ 35 = 0.066 and "
                    "car 2.31 ÷ 12 = 0.19 kg CO₂/km. This is why sharing a bus "
                    "is roughly **12× cleaner per kilometre** than driving alone.")
        st.markdown("**Electricity.** Nepal's grid is about 82% hydro and 18% "
                    "thermal (NEA Annual Report 2022/23), giving 0.23 kg CO₂/kWh "
                    "— low by world standards, which is why electricity is not "
                    "the villain here that it would be elsewhere.")
        st.dataframe(pd.DataFrame([
            {"factor": k, "value": v,
             "uncertainty": f"±{UNCERTAINTY[k]*100:.0f}%" if k in UNCERTAINTY else "—"}
            for k, v in EF.items()]).set_index("factor"),
            **STRETCH, height=320)

    # ---------------- 2
    with st.expander("**What is Sensitivity Analysis?**"):
        st.markdown(
            "A sensitivity analysis asks: *if one habit changes a little, how "
            "much does the answer change?* Mathematically that is a **partial "
            "derivative** — the slope of the output with respect to one input "
            "while everything else is held still.\n\n"
            "Because the footprint is linear, the chain rule gives a result "
            "that is unusually clean:")
        st.latex(r"\frac{\partial S}{\partial x_i} = \frac{dS}{dF}\cdot"
                 r"\frac{\partial F}{\partial x_i} = \begin{cases}"
                 r"-40\,\theta_i & 0.5 \le F \le 3.0 \\ 0 & \text{otherwise}"
                 r"\end{cases}")
        st.markdown(
            "The second line is the whole problem in one symbol. In a dead zone "
            "the derivative is not small — it is **exactly zero**. No change to "
            "any habit, of any size, produces any change in the reported score.")
        st.divider()
        st.markdown("##### Try it")
        cat = st.selectbox("Pick a category to vary",
                           CATEGORIES, index=2, format_func=str.capitalize)
        keymap = {"transport": "distance_km",
                  "electricity": "electricity_units_monthly",
                  "cooking": "lpg_cylinders_monthly",
                  "waste": "waste_kg_day",
                  "stationery": "stationery_npr_monthly"}
        base_val = WORKED[keymap[cat]]
        mults = np.linspace(0, 2, 120)
        scores, foots = [], []
        for m in mults:
            inp = dict(WORKED)
            inp[keymap[cat]] = base_val * m
            f, _ = calculate_footprint(**inp)
            foots.append(f)
            scores.append(eco_score(f))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=mults * 100, y=scores, mode="lines",
                                 line=dict(color=COLORS[cat], width=3.5),
                                 name="Eco-Score"))
        fig.add_vline(x=100, line=dict(color="#222", width=1.5, dash="dot"),
                      annotation_text="worked example")
        fig.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10),
                          xaxis_title=f"{cat} activity as % of the worked example "
                                      f"(100% = {base_val})",
                          yaxis_title="Eco-Score", yaxis_range=[-3, 105])
        st.plotly_chart(fig, **STRETCH)
        swing = max(scores) - min(scores)
        st.caption(
            f"Varying **{cat}** from 0% to 200% moves the footprint from "
            f"{min(foots):.3f} to {max(foots):.3f} kg CO₂/day and the score by "
            f"**{swing:.1f} points** in total. Flat segments are dead zones — "
            f"the score has stopped listening there.")

    # ---------------- 3
    with st.expander("**What is Monte Carlo Simulation?**"):
        st.markdown(
            "#### 1. Monte Carlo in algorithms\n"
            "In Design & Analysis of Algorithms, a *Monte Carlo algorithm* uses "
            "randomness as a **computational trick** to answer a question that "
            "is completely deterministic. Whether 561 is prime is a fixed fact; "
            "Miller–Rabin flips coins only to reach that fact faster than trial "
            "division, accepting a bounded probability of being wrong. "
            "Randomised QuickSort picks a random pivot for the same reason — the "
            "sorted order was never in doubt. The randomness lives in the "
            "*method*, never in the problem.\n\n"
            "#### 2. Monte Carlo in statistics\n"
            "Here the randomness **is** the problem. The Nepal grid emission "
            "factor genuinely differs from year to year as the hydro/thermal "
            "mix shifts with rainfall and imports. That variation is a fact "
            "about the physical world, not about our algorithm. We are not "
            "approximating a number we could have computed exactly — we are "
            "characterising a distribution that really exists.\n\n"
            "#### 3. Why we needed it here\n"
            "Because the footprint is linear, the variance formula is exact and "
            "simulation is merely a check on the algebra — the two agree to "
            f"**{KEY_RESULTS['agreement_pct']}%**. But the clamp is *not* a "
            "linear function. Once a student sits near F = 3.0, part of the "
            "distribution is squashed onto the boundary: the mean shifts, the "
            "shape becomes asymmetric, and a point mass appears at zero. No "
            "closed-form standard deviation describes that. Only simulation "
            "reveals how many students pile up there — for a student at 2.818 "
            f"kg/day it is **{KEY_RESULTS['near_boundary_clamp_pct']}%** of all "
            "plausible worlds.")
        st.divider()
        st.markdown("##### Watch the estimate converge")
        n_sim = st.slider("Number of simulations", 100, 10000, 2000, 100)
        F_mc, S_mc = mc_for(**WORKED, n=10000)
        ns = np.unique(np.linspace(50, n_sim, 90).astype(int))
        running = [S_mc[:n].std(ddof=1) for n in ns]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ns, y=running, mode="lines",
                                 line=dict(color="#4472C4", width=2.5),
                                 name="Monte Carlo estimate"))
        fig.add_hline(y=KEY_RESULTS["sd_score_analytical"],
                      line=dict(color="#C00000", width=2, dash="dash"),
                      annotation_text=f"analytical "
                                      f"{KEY_RESULTS['sd_score_analytical']}")
        fig.update_layout(height=330, margin=dict(l=10, r=10, t=30, b=10),
                          xaxis_title="number of simulations N",
                          yaxis_title="estimated SD of the score (points)")
        st.plotly_chart(fig, **STRETCH)
        st.caption(
            f"At N = {n_sim:,} the estimate is **{S_mc[:n_sim].std(ddof=1):.3f}** "
            f"points against an analytical **{KEY_RESULTS['sd_score_analytical']}**. "
            f"The error shrinks like 1/√N — a hundred times more simulations buys "
            f"only ten times more precision, which is why 10,000 is the sensible "
            f"stopping point rather than a million.")

    # ---------------- 4
    with st.expander("**Why the Logistic?**"):
        st.latex(r"S_{\text{logistic}}(F) = \frac{100}{1 + e^{\,k(F - F_0)}}")
        st.markdown(
            f"**F₀ = {F0_LOG} kg CO₂/day** is the *centre*: the footprint that "
            f"scores exactly 50. We set it to the population median, so a score "
            f"of 50 means \"a typical student\".\n\n"
            f"**k = {K_LOG}** is the *steepness*: how sharply the score falls "
            f"as the footprint grows. It was fitted by minimising the squared "
            f"difference against the original score, so the new scale agrees "
            f"with the old one wherever the old one worked.\n\n"
            "The curve never reaches 0 or 100 — it only approaches them. That "
            "is the entire point: **there is always somewhere left to go**, in "
            "both directions, so every student's effort registers.")
        F_probe = st.slider("Move a student's footprint (kg CO₂/day)",
                            0.0, 9.0, 3.5, 0.1)
        st.plotly_chart(curves_figure(F_probe, height=420),
                        **STRETCH)
        p1, p2, p3 = st.columns(3)
        p1.metric("Original", f"{eco_score(F_probe):.2f}")
        p2.metric("Percentile", f"{eco_score_percentile(F_probe):.2f}")
        p3.metric("Logistic ★", f"{eco_score_logistic(F_probe):.2f}")
        if F_probe > F_MAX:
            st.error(f"At {F_probe:.1f} kg/day the original score is stuck at 0 "
                     f"while the logistic still reports "
                     f"{eco_score_logistic(F_probe):.2f} — and still moves when "
                     f"the student improves.")
        st.divider()
        st.markdown("##### Information carried by each score")
        st.markdown(
            "Shannon entropy over 20 score bins measures how many genuinely "
            "distinguishable outcomes a scoring method produces. The maximum "
            "with 20 bins is ln(20) = 2.996 nats.")
        ent = go.Figure(go.Bar(
            x=["Original", "Logistic ★", "Percentile"],
            y=[KEY_RESULTS["entropy_original"], KEY_RESULTS["entropy_logistic"],
               KEY_RESULTS["entropy_percentile"]],
            marker_color=["#4472C4", "#70AD47", "#ED7D31"],
            text=[f"{KEY_RESULTS['entropy_original']:.3f}",
                  f"{KEY_RESULTS['entropy_logistic']:.3f}",
                  f"{KEY_RESULTS['entropy_percentile']:.3f}"],
            textposition="outside"))
        ent.add_hline(y=float(np.log(20)), line=dict(color="#C00000", dash="dash"),
                      annotation_text="maximum ln(20) = 2.996")
        ent.update_layout(height=330, margin=dict(l=10, r=10, t=30, b=10),
                          yaxis_title="entropy (nats)", yaxis_range=[0, 3.25])
        st.plotly_chart(ent, **STRETCH)
        st.info(
            "**The trade-off.** The percentile method scores highest on entropy "
            "because it is built to spread the middle 90% across the full range "
            "— but it still clamps both tails, so it still creates ties and it "
            "*adds* a ceiling problem the original did not have. The logistic "
            "gives up a little entropy to guarantee something more valuable: a "
            "strictly positive gradient everywhere, and an exactly preserved "
            "ranking.\n\n"
            "Its cost is that the scale is **relative to a population**, not to "
            "an absolute threshold. Where the question is \"is this student "
            "under a sustainable limit?\", use the percentile method with "
            "boundaries set from policy instead.")


# ============================================================ PAGE 4
else:
    st.title("About This Project")

    left, right = st.columns([1.4, 1], gap="large")

    with left:
        st.markdown("### Where it started")
        st.markdown(
            "Harit Pathsala (हरित पाठशाला) was built at the **Nepal Climate "
            "Hackathon 2025** as a carbon-footprint calculator for school "
            "students. It asks five questions about daily life — how you travel "
            "to school, your home electricity, cooking gas, waste and "
            "stationery — and returns a single number between 0 and 100 called "
            "the Eco-Score. Teachers show it to students, students compare it "
            "with each other, and a school dashboard averages it across a class.")

        st.markdown("### What we studied, and why")
        st.markdown(
            "A number that students are ranked by deserves to be checked. This "
            "project asks one question: **can we trust the Eco-Score?** Not "
            "\"is the arithmetic right\" — that is easy to verify — but the "
            "harder questions: which habits actually move it, how precise it "
            "is given that emission factors are estimates, and whether it "
            "behaves sensibly across a whole school rather than for one "
            "example student.\n\n"
            "The work is a mathematics project: partial derivatives for "
            "sensitivity, variance propagation and Monte Carlo simulation for "
            "uncertainty, a 10,000-student synthetic population for validation, "
            "and information theory to compare scoring functions.")

        st.markdown("### What we found")
        st.markdown(
            f"The formula is sound — over the students it can actually score, "
            f"it explains **{KEY_RESULTS['r2_unsaturated']*100:.2f}%** of the "
            f"variation between them. The problem is the hard clamp at 3.0 kg "
            f"CO₂/day. **{KEY_RESULTS['floor_pct']}%** of a plausible school is "
            f"pinned at exactly 0, and those students span "
            f"{KEY_RESULTS['floored_F_min']}–{KEY_RESULTS['floored_F_max']} kg "
            f"CO₂/day — a threefold difference in real emissions reported as "
            f"one identical number, with a gradient of exactly zero in every "
            f"category. Nobody at all reaches 100.\n\n"
            f"Alongside that: cooking and electricity dominate the score "
            f"(**{KEY_RESULTS['sensitivity_ratio']:.0f}×** the influence of "
            f"stationery), and any single score carries about "
            f"**±{KEY_RESULTS['sd_score_analytical']} points** of uncertainty "
            f"from the emission factors alone.")

        st.markdown("### What we recommend")
        st.markdown(
            f"Replace the clamp with a **logistic score** centred on the "
            f"population median (k = {K_LOG}, F₀ = {F0_LOG}). Nothing about the "
            f"physics changes — the emission factors and the footprint "
            f"calculation stay exactly as they are. Only the map from footprint "
            f"to score changes, and with it the dead zone falls from "
            f"**{KEY_RESULTS['dead_zone_original_pct']}% to "
            f"{KEY_RESULTS['dead_zone_logistic_pct']}%** while the ranking of "
            f"students is preserved exactly.\n\n"
            "Two caveats worth stating to any teacher who uses this: the "
            "logistic scale is relative to the population it was fitted to and "
            "must be refitted when that population changes, and the absolute "
            "kg CO₂/day figure should stay visible beside the score, because "
            "that is the number with absolute meaning. The synthetic population "
            "should also be replaced with a real student survey — the "
            "specification for one is in `research/data/survey_template.md`.")

    with right:
        st.info(
            f"""**Project details**

**Researcher** · Jayed Alam Mansur
**Institution** · Kathmandu University
**Department** · Artificial Intelligence, Year 3
**Supervised by** · [Mathematics Teacher] · Sandesh Thakuri

**Notebook** · `eco_score_research.ipynb`
**Figures** · 14 plots at 300 DPI
**Key results** · `key_results.json` ({value_count()} values)
**Population** · {POPULATION['N']:,} students, seed {POPULATION['seed']}
""")

        st.download_button("Download Key Results JSON", load_results_json(),
                           "key_results.json", "application/json",
                           **STRETCH)

        st.markdown("#### Try it on a class")
        with st.expander("Class simulator", expanded=False):
            N = st.number_input("Number of students", 10, 200, 40, step=5)
            seed = st.number_input("Random seed", 0, 9999, 7, step=1)
            if st.button("Generate class", **STRETCH):
                spec = dict(POPULATION, N=int(N), seed=int(seed))
                cls = generate_population(spec=spec)
                cls["S_percentile"] = eco_score_percentile_vec(cls.F.values)
                cls["S_logistic"] = eco_score_logistic_vec(cls.F.values)
                st.session_state["class_df"] = cls

            cls = st.session_state.get("class_df")
            if cls is not None:
                methods = [("Original", "S", "#4472C4"),
                           ("Percentile", "S_percentile", "#ED7D31"),
                           ("Logistic ★", "S_logistic", "#70AD47")]
                summary = pd.DataFrame([{
                    "Method": name,
                    "Mean": round(cls[col].mean(), 1),
                    "SD": round(cls[col].std(ddof=1), 1),
                    "% at floor": round(100 * float((cls[col] <= 0).mean()), 1),
                    "% at ceiling": round(100 * float((cls[col] >= 100).mean()), 1),
                } for name, col, _ in methods]).set_index("Method")
                st.dataframe(summary, **STRETCH)

                cols = st.columns(3)
                for (name, col, colour), c in zip(methods, cols):
                    fig = go.Figure(go.Histogram(x=cls[col], nbinsx=18,
                                                 marker_color=colour, opacity=.85))
                    fig.update_layout(height=210, margin=dict(l=5, r=5, t=28, b=5),
                                      title=dict(text=name, font=dict(size=12)),
                                      xaxis_range=[0, 100], showlegend=False,
                                      xaxis_title=None, yaxis_title=None)
                    c.plotly_chart(fig, **STRETCH)

                st.caption(
                    f"Class of {len(cls)}: mean footprint {cls.F.mean():.3f} kg "
                    f"CO₂/day. The original pins "
                    f"{100*float((cls.S<=0).mean()):.1f}% at zero; the logistic "
                    f"pins {100*float((cls.S_logistic<=0).mean()):.1f}%.")

                st.download_button(
                    "Download class CSV", cls.to_csv(index=False),
                    f"harit_class_{int(N)}_seed{int(seed)}.csv", "text/csv",
                    **STRETCH)

    st.divider()
    st.caption("Harit Pathsala Eco-Score research · v1.0 · "
               "All emission factors from the Nepal Climate Hackathon 2025 "
               "organiser's Emission_factors.xlsx via src/logic.js")
