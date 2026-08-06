# Student Survey Template — replacing the synthetic population

> **3 minutes · no personally identifiable information (PII) collected.**
> Do not ask for name, address, phone number, roll number, or anything that
> could identify a household. Collect grade and section only if class-level
> comparison is needed. A student must be able to answer every question from
> memory or from a single electricity bill.

## Why this exists

Section 4 of `eco_score_research.ipynb` validates the Eco-Score against a
**synthetic** population of 10,000 students, because no real survey data existed
when the analysis was written. Every distribution in `POPULATION` was chosen from
published Nepali sources — but they are still assumptions.

This template specifies the survey that replaces them. The seven variables below
map **one-to-one** onto the columns `generate_population()` produces, so a CSV
collected with these exact column names is a drop-in replacement:

```python
import pandas as pd
from model import EF, eco_score_vec

pop = pd.read_csv('data/student_survey_responses.csv')
pop['transport_ef']  = pop.transport_mode.map(EF)
pop['c_transport']   = pop.transport_ef * pop.distance_km * 2
pop['c_electricity'] = pop.electricity_kwh / 30 * np.where(pop.has_solar, EF['solar_kwh'], EF['grid_kwh'])
pop['c_cooking']     = pop.lpg_cylinders * EF['lpg_per_cylinder'] / 30
pop['c_waste']       = pop.waste_kg_day * EF['waste_per_kg']
pop['c_stationery']  = pop.stationery_npr / 30 * EF['stationery_per_npr']
pop['F'] = pop[[f'c_{c}' for c in ['transport','electricity','cooking','waste','stationery']]].sum(axis=1)
pop['S'] = eco_score_vec(pop.F.values)
```

Everything downstream — the percentile boundaries, the logistic $F_0$ and $k$,
the floor percentage — then recomputes from real data. **Re-fit and re-publish
`KEY_RESULTS` after doing this**; the numbers in the current paper describe the
synthetic population and must not be quoted as survey findings.

---

## Q1 — Transport mode

| | |
|---|---|
| **English** | How do you usually travel to school? |
| **नेपाली** | तपाईं सामान्यतया विद्यालय कसरी आउनुहुन्छ? |
| **Input type** | select (single choice, required) |
| **Options** | Walk / Bicycle / Bus / Motorbike / Car — हिँडेर / साइकल / बस / मोटरसाइकल / कार |
| **Allowed values** | `walk`, `bicycle`, `bus`, `motorbike`, `car` |
| **CSV column** | `transport_mode` |

*Note:* if a student uses more than one mode, ask for the one covering the
longest part of the journey. Mixed-mode commutes are a known limitation of the
current model — it assumes a single mode for the whole trip.

## Q2 — Commute distance

| | |
|---|---|
| **English** | How far is your school from your home, one way? (in kilometres) |
| **नेपाली** | तपाईंको घरबाट विद्यालय एकतर्फी कति टाढा छ? (किलोमिटरमा) |
| **Input type** | slider (step 0.5) |
| **Allowed range** | 0.5 – 20.0 km |
| **CSV column** | `distance_km` |

*Note:* the formula doubles this for the round trip — do **not** ask students to
enter the return journey separately. Expect a right-skewed distribution; the
synthetic model assumes an arithmetic mean of 3.0 km.

## Q3 — Home electricity

| | |
|---|---|
| **English** | How many units (kWh) of electricity did your home use last month? Check the NEA bill. |
| **नेपाली** | गत महिना तपाईंको घरमा कति युनिट (kWh) बिजुली खपत भयो? NEA को बिल हेर्नुहोस्। |
| **Input type** | number |
| **Allowed range** | 10 – 300 kWh per month |
| **CSV column** | `electricity_kwh` |

*Note:* this is the single hardest question to answer accurately, and it drives
the largest share of score variance. Ask students to bring the bill, or send the
question home the day before. Mark estimated answers with an `electricity_estimated`
boolean if you can — it lets the analysis check whether estimates bias the result.

## Q4 — Rooftop solar

| | |
|---|---|
| **English** | Does your home have rooftop solar panels? |
| **नेपाली** | तपाईंको घरको छतमा सोलार प्यानल छ? |
| **Input type** | select (Yes / No) — छ / छैन |
| **Allowed values** | `TRUE`, `FALSE` |
| **CSV column** | `has_solar` |

*Note:* solar water heaters are **not** solar panels — say so explicitly when
asking, or the "yes" rate will be inflated. The synthetic model assumes 5%.

## Q5 — Cooking gas

| | |
|---|---|
| **English** | How many LPG gas cylinders does your household use in a month? |
| **नेपाली** | तपाईंको घरपरिवारले एक महिनामा कति ग्यास सिलिन्डर प्रयोग गर्छ? |
| **Input type** | slider (step 0.25) |
| **Allowed range** | 0.25 – 4.0 cylinders per month |
| **CSV column** | `lpg_cylinders` |

*Note:* one Nepali cylinder is 14.2 kg. Most households take longer than a month
to finish one, so phrase it as "if a cylinder lasts two months, answer 0.5".
Households cooking with firewood cannot be represented by this question — record
them separately (`cook_fuel`) rather than forcing a zero, as firewood has a
*higher* emission factor (1.747 kg CO₂/kg), not a lower one.

## Q6 — Daily waste

| | |
|---|---|
| **English** | How much waste does your household throw away each day? |
| **नेपाली** | तपाईंको घरपरिवारले दैनिक कति फोहोर फाल्छ? |
| **Input type** | select (single choice) |
| **Options** | Small, about 0.3 kg — थोरै (करिब ०.३ के.जी.) · Medium, about 0.6 kg — मध्यम (करिब ०.६ के.जी.) · Large, about 1.2 kg — धेरै (करिब १.२ के.जी.) |
| **Allowed values** | `0.3`, `0.6`, `1.2` |
| **CSV column** | `waste_kg_day` |

*Note:* show a physical reference (one full shopping bag ≈ 1.2 kg) — students
cannot estimate kilograms of rubbish reliably without one.

## Q7 — Stationery spending

| | |
|---|---|
| **English** | How much do you spend on notebooks, pens and paper in a month? (NPR) |
| **नेपाली** | तपाईं एक महिनामा कापी, कलम र कागजमा कति खर्च गर्नुहुन्छ? (रु.) |
| **Input type** | slider (step 50) |
| **Allowed range** | 0 – 600 NPR per month |
| **CSV column** | `stationery_npr` |

*Note:* this category has the weakest effect on the score by a factor of 62, and
the widest factor uncertainty (±25%). It is worth keeping for completeness but is
the first question to drop if the survey must be shortened.

---

## Optional context columns (no PII)

| Question | CSV column | Values |
|---|---|---|
| Which grade are you in? | `grade` | 6–10 |
| Which district is your school in? | `district` | district name |
| Response date | `survey_date` | YYYY-MM-DD |

## Expected CSV header

```csv
transport_mode,distance_km,electricity_kwh,has_solar,lpg_cylinders,waste_kg_day,stationery_npr,grade,district,survey_date
bus,2.0,90,FALSE,1.0,0.6,200,8,Kathmandu,2026-08-06
```

## Data quality checklist before analysis

- [ ] Every value inside the allowed range above (clip, do not delete, outliers)
- [ ] No PII column present in the file that leaves the school
- [ ] At least 100 responses before refitting the logistic $F_0$ and $k$;
      fewer than that and the median is too noisy to anchor a scoring scale
- [ ] Record the response rate — if only motivated students answer, the sample
      is biased low and the floor percentage will be **understated**
- [ ] Note how many electricity answers were estimated rather than read from a bill
