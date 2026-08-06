"""
model.py — shared formula module for the Harit Pathsala Eco-Score research.

Pure Python / NumPy / pandas. No Streamlit, no matplotlib, no I/O at import
time. Imported by both `research/webapp/app.py` and
`research/notebook/eco_score_research.ipynb` so the notebook and the web app
can never drift apart.

Source of truth for the emission factors: `src/logic.js` (`EF`) in the parent
project, which in turn comes from the Nepal Climate Hackathon 2025 organiser's
`Emission_factors.xlsx`. Nothing in this file changes a published number.

Researcher : Jayed Alam Mansur — B.Tech Artificial Intelligence, Year 3
Institution: Kathmandu University
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = [
    "EF", "UNCERTAINTY", "POPULATION", "KEY_RESULTS", "COLORS",
    "TRANSPORT_MODES", "F_MIN", "F_MAX", "SCORE_SLOPE",
    "calculate_footprint", "eco_score", "eco_score_percentile",
    "eco_score_logistic", "generate_population",
    "analytical_score_sd", "monte_carlo_scores",
]

# ---------------------------------------------------------------------------
# 1. EMISSION FACTORS  (source of truth — do not change any number)
# ---------------------------------------------------------------------------

EF = {
    # Transport — kg CO2 per km (the formula doubles these for the round trip)
    # Derived: fuel combustion factor / fuel efficiency / passenger count
    'walk':       0.000,
    'bicycle':    0.000,
    'bus':        0.016,   # 2.68 kg CO2/L / (4 km/L x 40 passengers)
    'motorbike':  0.066,   # 2.31 kg CO2/L / 35 km/L
    'car':        0.190,   # 2.31 kg CO2/L / 12 km/L

    # Electricity — kg CO2 per kWh
    # Nepal grid: 82% hydro, 18% thermal — NEA Annual Report 2022/23
    'grid_kwh':  0.230,
    'solar_kwh': 0.040,    # rooftop solar lifecycle estimate

    # Cooking — LPG combustion
    # IPCC 2006: LPG carbon content x (44/12) molecular weight ratio
    'lpg_per_kg':        1.510,
    'lpg_cylinder_kg':  14.200,
    'lpg_per_cylinder': 21.442,   # 14.2 x 1.510 = 21.442 (derived, verified)

    # Waste — kg CO2e per kg solid waste to landfill
    # Accounts for decomposition to CH4 and CO2, converted to CO2e
    'waste_per_kg': 0.827,

    # Stationery — kg CO2e per NPR spent
    # Spend-based supply chain lifecycle factor (1.7285 kg CO2e / 1000 NPR)
    'stationery_per_npr': 0.0017284768211920529,
}

TRANSPORT_MODES = ['walk', 'bicycle', 'bus', 'motorbike', 'car']

# ---------------------------------------------------------------------------
# 2. FACTOR UNCERTAINTY  (relative standard deviation of each emission factor)
# ---------------------------------------------------------------------------

UNCERTAINTY = {
    # Nepal grid mix varies +/-15% year to year (NEA data 2018-2023)
    'grid_kwh':       0.15,

    # Bus passenger load varies (peak vs off-peak)
    'bus':            0.10,

    # Motorbike fuel efficiency varies by model and maintenance
    'motorbike':      0.08,

    # Car fuel efficiency varies by model and traffic
    'car':            0.10,

    # LPG cylinder fill weight varies by supplier
    'lpg_per_cylinder': 0.05,

    # Waste composition varies significantly by household
    'waste_per_kg':   0.20,

    # Supply chain emission factors have high uncertainty
    'stationery_per_npr': 0.25,
}

# ---------------------------------------------------------------------------
# 3. SYNTHETIC POPULATION SPECIFICATION
# ---------------------------------------------------------------------------

POPULATION = {
    'N': 10000,
    'seed': 42,

    # Transport mode shares (Nepal student survey estimates)
    'mode_probs': {
        'walk':       0.20,
        'bicycle':    0.10,
        'bus':        0.40,
        'motorbike':  0.25,
        'car':        0.05,
    },

    # One-way commute distance.
    # Log-normal parameterised so the ARITHMETIC mean is 3.00 km
    # (mu = ln(mean) - sigma^2/2, NOT mu = ln(mean)).
    'distance': {
        'distribution': 'lognormal',
        'mean_km': 3.00,
        'sigma':   0.80,
        'clip': (0.5, 20.0),
    },

    # Monthly electricity (kWh) — NEA billing data range
    'electricity': {
        'distribution': 'normal',
        'mean': 90.0,
        'std':  35.0,
        'clip': (10.0, 300.0),
    },

    # Solar panel penetration — ~5% of Nepal households
    'solar_probability': 0.05,

    # LPG cylinders per month
    'lpg': {
        'distribution': 'normal',
        'mean': 1.20,
        'std':  0.40,
        'clip': (0.25, 4.0),
    },

    # Daily waste — three discrete levels
    'waste': {
        'values': [0.3, 0.6, 1.2],
        'probs':  [0.3, 0.5, 0.2],
    },

    # Monthly stationery spend (NPR)
    'stationery': {
        'distribution': 'normal',
        'mean': 200.0,
        'std':   80.0,
        'clip': (50.0, 600.0),
    },

    # Order in which the variables consume the seeded RNG stream. The variables
    # are mutually independent, so this order changes only WHICH draws land on
    # WHICH variable, never the marginal distributions. It is pinned here so
    # the notebook, the web app and the published results are bit-identical.
    'draw_order': ['mode', 'lpg', 'distance', 'stationery',
                   'electricity', 'solar', 'waste'],
}

# ---------------------------------------------------------------------------
# 4. PUBLISHED RESEARCH RESULTS
#    These are the canonical numbers quoted in the paper and the web app.
#    The notebook recomputes every one of them and reports the deviation in
#    its Section 6 validation table.
# ---------------------------------------------------------------------------

KEY_RESULTS = {
    # Sensitivity (Section 2) — score points per +10% activity increase
    'sensitivity_cooking':     -2.859,
    'sensitivity_electricity': -2.760,
    'sensitivity_waste':       -1.985,
    'sensitivity_transport':   -0.256,
    'sensitivity_stationery':  -0.046,
    'sensitivity_ratio':        62.0,   # cooking / stationery

    # Uncertainty (Section 3)
    'sd_score_analytical':      5.92,   # points
    'sd_score_montecarlo':      5.99,   # points
    'agreement_pct':            1.29,   # % difference
    'near_boundary_clamp_pct': 19.60,   # % samples clamped at 2.818 kg/day

    # Population (Section 4)
    'population_mean_F':        2.246,  # kg CO2/day
    'population_mean_score':   31.9,
    'floor_pct':                9.19,   # % scoring exactly 0
    'ceiling_pct':              0.00,   # % scoring exactly 100
    'r2_full':                  0.8538,
    'r2_unsaturated':           0.9997,
    'floored_F_min':            2.99,   # kg/day — lowest footprint at floor
    'floored_F_max':            8.91,   # kg/day — highest footprint at floor
    'household_baseline':       2.048,  # kg/day before transport/stationery

    # Calibration (Section 5)
    'logistic_k':               1.7202,
    'logistic_F0':              2.1883,
    'entropy_original':         2.644,  # nats (20 bins)
    'entropy_logistic':         2.765,
    'entropy_percentile':       2.931,
    'dead_zone_original_pct':   9.19,
    'dead_zone_logistic_pct':   0.25,
    'dead_zone_percentile_pct': 10.27,
    'spearman_logistic':        1.000000,
    'pearson_logistic_vs_orig': 0.9972,

    # Method A boundaries (Section 5) — 5th / 95th percentile of population F
    'percentile_F_low':         1.404,
    'percentile_F_high':        3.227,
}

# Category colours, shared by the notebook figures and the web app charts.
COLORS = {
    'transport':   '#4472C4',
    'electricity': '#ED7D31',
    'cooking':     '#FFC000',
    'waste':       '#70AD47',
    'stationery':  '#AE97A0',
}

# ---------------------------------------------------------------------------
# 5. THE MODEL
# ---------------------------------------------------------------------------

F_MIN, F_MAX = 0.5, 3.0                      # original min-max boundaries
SCORE_SLOPE = -100.0 / (F_MAX - F_MIN)       # = -40 points per kg/day


def calculate_footprint(transport_mode, distance_km,
                        electricity_units_monthly, has_solar,
                        lpg_cylinders_monthly,
                        waste_kg_day,
                        stationery_npr_monthly):
    """Daily carbon footprint in kg CO2/day.

    Returns ``(daily_total, components)`` where ``components`` is a dict with
    the five category contributions, all in kg CO2/day.
    """
    transport   = EF[transport_mode] * distance_km * 2
    electricity = (electricity_units_monthly / 30) * (
                    EF['solar_kwh'] if has_solar else EF['grid_kwh'])
    cooking     = (lpg_cylinders_monthly * EF['lpg_per_cylinder']) / 30
    waste       = waste_kg_day * EF['waste_per_kg']
    stationery  = (stationery_npr_monthly / 30) * EF['stationery_per_npr']

    daily_total = transport + electricity + cooking + waste + stationery
    components  = {
        'transport':   transport,
        'electricity': electricity,
        'cooking':     cooking,
        'waste':       waste,
        'stationery':  stationery,
    }
    return daily_total, components


def eco_score(daily_kg):
    """Original Eco-Score: min-max normalisation, S = (F_max - F)/(F_max - F_min) x 100.

    Expanded: 100 - ((F - 0.5) / 2.5) x 100, clamped to [0, 100].
    Slope is -40 points per kg/day throughout the linear region.
    """
    raw = 100 - ((daily_kg - 0.5) / 2.5) * 100
    return max(0.0, min(100.0, round(raw, 2)))


def eco_score_percentile(F, F_low=1.404, F_high=3.227):
    """Method A — percentile-based boundaries.

    F_low / F_high default to the 5th and 95th percentile of the synthetic
    population, so a score of 50 means "median student" rather than
    "1.75 kg/day".
    """
    raw = 100 - ((F - F_low) / (F_high - F_low)) * 100
    return max(0.0, min(100.0, round(raw, 2)))


def eco_score_logistic(F, k=1.7202, F0=2.1883):
    """Method B — logistic score (recommended).

    F0 is the population median (the score-50 point) and k controls how
    sharply the score falls around it. Never saturates, so every student keeps
    a distinct, responsive score.
    """
    return round(100 / (1 + np.exp(k * (F - F0))), 2)


# Vectorised twins of the three scoring functions, for whole-population work.

def eco_score_vec(F):
    return np.clip(np.round(100 - ((np.asarray(F, float) - F_MIN) /
                                   (F_MAX - F_MIN)) * 100, 2), 0.0, 100.0)


def eco_score_percentile_vec(F, F_low=1.404, F_high=3.227):
    return np.clip(np.round(100 - ((np.asarray(F, float) - F_low) /
                                   (F_high - F_low)) * 100, 2), 0.0, 100.0)


def eco_score_logistic_vec(F, k=1.7202, F0=2.1883):
    return np.round(100 / (1 + np.exp(k * (np.asarray(F, float) - F0))), 2)


# ---------------------------------------------------------------------------
# 6. SYNTHETIC POPULATION
# ---------------------------------------------------------------------------

def generate_population(N=None, seed=None, spec=POPULATION):
    """Draw a synthetic student population and score every student.

    Returns a DataFrame with the raw survey-style inputs, the five component
    footprints, the daily total ``F`` and the original Eco-Score ``S``.

    Uses the legacy ``np.random.seed`` stream so the published results are
    reproducible exactly; ``spec['draw_order']`` pins which variable consumes
    which part of that stream.
    """
    N = int(spec['N'] if N is None else N)
    seed = int(spec['seed'] if seed is None else seed)

    modes = list(spec['mode_probs'].keys())
    probs = list(spec['mode_probs'].values())

    d = spec['distance']
    # Solve for the log-space mu that yields the requested ARITHMETIC mean:
    #   E[X] = exp(mu + sigma^2/2)  =>  mu = ln(E[X]) - sigma^2 / 2
    mu = np.log(d['mean_km']) - d['sigma'] ** 2 / 2

    np.random.seed(seed)
    col = {}
    for name in spec['draw_order']:
        if name == 'mode':
            col['transport_mode'] = np.random.choice(modes, size=N, p=probs)
        elif name == 'distance':
            col['distance_km'] = np.clip(
                np.random.lognormal(mu, d['sigma'], N), *d['clip'])
        elif name == 'electricity':
            e = spec['electricity']
            col['electricity_kwh'] = np.clip(
                np.random.normal(e['mean'], e['std'], N), *e['clip'])
        elif name == 'solar':
            col['has_solar'] = np.random.random(N) < spec['solar_probability']
        elif name == 'lpg':
            l = spec['lpg']
            col['lpg_cylinders'] = np.clip(
                np.random.normal(l['mean'], l['std'], N), *l['clip'])
        elif name == 'waste':
            w = spec['waste']
            col['waste_kg_day'] = np.random.choice(
                w['values'], size=N, p=w['probs'])
        elif name == 'stationery':
            s = spec['stationery']
            col['stationery_npr'] = np.clip(
                np.random.normal(s['mean'], s['std'], N), *s['clip'])
        else:                                            # pragma: no cover
            raise ValueError(f"unknown draw_order entry: {name}")

    pop = pd.DataFrame(col)[['transport_mode', 'distance_km',
                             'electricity_kwh', 'has_solar', 'lpg_cylinders',
                             'waste_kg_day', 'stationery_npr']]

    pop['transport_ef']  = pop['transport_mode'].map(EF).astype(float)
    pop['c_transport']   = pop['transport_ef'] * pop['distance_km'] * 2
    pop['c_electricity'] = (pop['electricity_kwh'] / 30) * np.where(
        pop['has_solar'], EF['solar_kwh'], EF['grid_kwh'])
    pop['c_cooking']     = pop['lpg_cylinders'] * EF['lpg_per_cylinder'] / 30
    pop['c_waste']       = pop['waste_kg_day'] * EF['waste_per_kg']
    pop['c_stationery']  = (pop['stationery_npr'] / 30) * EF['stationery_per_npr']

    pop['F'] = pop[['c_transport', 'c_electricity', 'c_cooking',
                    'c_waste', 'c_stationery']].sum(axis=1)
    pop['S'] = eco_score_vec(pop['F'].values)
    return pop


# ---------------------------------------------------------------------------
# 7. UNCERTAINTY HELPERS
# ---------------------------------------------------------------------------

def analytical_score_sd(components, transport_mode):
    """First-order propagation of emission-factor uncertainty.

    Because F is linear in the factors, Var(F) = sum_i (c_i * u_i)^2 where c_i
    is the category's contribution and u_i its relative uncertainty.
    Returns ``(sd_F, sd_S)``; sd_S = 40 * sd_F holds in the linear region.
    """
    rel = {
        'transport':   UNCERTAINTY.get(transport_mode, 0.0),
        'electricity': UNCERTAINTY['grid_kwh'],
        'cooking':     UNCERTAINTY['lpg_per_cylinder'],
        'waste':       UNCERTAINTY['waste_per_kg'],
        'stationery':  UNCERTAINTY['stationery_per_npr'],
    }
    var = sum((components[k] * rel[k]) ** 2 for k in rel)
    sd_F = float(np.sqrt(var))
    return sd_F, abs(SCORE_SLOPE) * sd_F


def monte_carlo_scores(transport_mode, distance_km, electricity_units_monthly,
                       has_solar, lpg_cylinders_monthly, waste_kg_day,
                       stationery_npr_monthly, n=10000, seed=42):
    """Propagate factor uncertainty by simulation instead of by formula.

    Every emission factor becomes Normal(mu = point estimate,
    sigma = mu x relative uncertainty), clipped to stay positive. Returns
    ``(F_samples, S_samples)`` with the original clamped Eco-Score applied.
    """
    np.random.seed(seed)

    def draw(key):
        mu = EF[key]
        u = UNCERTAINTY.get(key, 0.0)
        if u == 0.0 or mu == 0.0:
            return np.full(n, mu, dtype=float)
        return np.clip(np.random.normal(mu, mu * u, n), 0.0, None)

    th_transport   = draw(transport_mode)
    th_grid        = draw('grid_kwh')
    th_lpg         = draw('lpg_per_cylinder')
    th_waste       = draw('waste_per_kg')
    th_stationery  = draw('stationery_per_npr')

    elec_factor = EF['solar_kwh'] if has_solar else th_grid
    F = (th_transport * distance_km * 2
         + (electricity_units_monthly / 30) * elec_factor
         + lpg_cylinders_monthly * th_lpg / 30
         + waste_kg_day * th_waste
         + (stationery_npr_monthly / 30) * th_stationery)
    return F, eco_score_vec(F)
