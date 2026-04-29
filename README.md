# PitLane: F1 Strategy & Performance Analytics

> **Newton School of Technology | Data Visualization & Analytics**
> A 2-week industry simulation capstone using Python, GitHub, and Tableau to convert raw data into actionable business intelligence.

---

## Project Overview

| Field | Details |
|---|---|
| **Project Title** | **PitLane: F1 Strategy & Performance Analytics** |
| **Sector** | Sports & Data Analytics |
| **Team ID** | DVA-E-Group-3 |
| **Section** | Section E |
| **Faculty Mentor** | Newton School Faculty |
| **Institute** | Newton School of Technology |
| **Submission Date** | April 2026 |

### Team Members

| Role                 | Name             | GitHub Username |
| -------------------- | ---------------- | --------------- |
| Project Lead         | Harsh            | `Harsh-sh7`     |
| Data Lead            | Vani Vashishtha  | `Vani-Max`      |
| ETL Lead             | Aryan Kumar      | `Ario2006`      |
| Analysis Lead        | Asad Ali         | `ali7540`       |
| Visualization Lead   | Vani Vashishtha  | `vani-max`      |
| Strategy Lead        | Dikshant Jangra  | `DikshantJangra`|
| PPT and Quality Lead | Anshu Yadav      | `Anshuxy`       |

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Harsh-sh7/Section_E_Group_3_PitLane.git

# Set up environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run analysis
jupyter notebook
```

---

## Business Problem

In the high-stakes world of Formula 1, races are often won or lost in the pit lane rather than on the track. Team Principals and Strategy Engineers need to optimize every second to maintain a competitive edge, yet the correlation between pit stop efficiency and final race outcomes is often obscured by seasonal noise. This project analyzes 70+ years of F1 data (1950-2017) to identify the "Golden Window" for pit strategy and decouple driver skill from machinery performance.

**Core Business Question**

> "How does pit stop duration and strategic lap-timing impact a team's probability of gaining/retaining track position, and which constructors have historically optimized this 'PitLane' advantage?"

**Decision Supported**

> This analysis enables Team Strategists to benchmark their pit crew performance against rivals and determine the statistical risk-reward of a 1-stop vs. 2-stop strategy across different circuit types, supported by era-specific reliability data.

---

## Dataset

| Attribute | Details |
|---|---|
| **Source Name** | Ergast Motor Racing Dataset (via Kaggle) |
| **Direct Access Link** | [Formula 1 World Championship (1950-2017)](https://www.kaggle.com/datasets/cjgdev/formula-1-race-data-19502017) |
| **Row Count** | 23,777 (Results) |
| **Column Count** | 85 meaningful columns in Master Table |
| **Time Period Covered** | 1950 to 2017 |
| **Format** | CSV (Relational) |

**Key Columns Used**

| Column Name | Description | Role in Analysis |
|---|---|---|
| `driver_alpha` | Points Per Race above car baseline | Primary Skill KPI |
| `reliability_index`| 1 - DNF Rate | Constructor Reliability |
| `median_pit_sec` | Median pit stop duration | Strategy Efficiency |
| `potential_points_lost` | Points forfeited due to DNF | Reliability Cost |

For full column definitions, see [`docs/data_dictionary.md`](docs/data_dictionary.md).

---

## KPI Framework

| KPI | Definition | Formula / Computation |
| ------------------------------- | ----------------------------------- | ---------------------------------------------- |
| **Driver Alpha** | Skill extracted above the car's potential | `PPR - Constructor_Avg_PPR` |
| **Reliability Index** | Season-long engineering stability | `1 - (Total_DNFs / Total_Entries)` |
| **Qualifying Advantage** | Head-to-head qualifying speed | `Q1_Time - Teammate_Avg_Q1` |
| **Pit Efficiency** | Crew execution speed | `Median(pit_stop_milliseconds)` |

Document KPI logic clearly in `notebooks/04_statistical_analysis.ipynb` and `notebooks/05_final_load_prep.ipynb`.

---

## Tableau Dashboard

| Item                 | Details                                    |
| -------------------- | ------------------------------------------ |
| **Dashboard URL**    | [F1 PitLane Final Dashboard](https://public.tableau.com/views/F1PitLaneFinalDashboard/Dashboard1-DriverSkillIntelligenceDecouplingPerformancefromMachinery19502017) |
| **Executive View**   | Driver Skill Intelligence - Decoupling Performance from Machinery |
| **Operational View** | Pit Stop Strategy Command Centre & Reliability Intelligence |
| **Main Filters**     | Era (Engine type), Constructor, Driver, Season |

Store dashboard screenshots in [`tableau/screenshots/`](tableau/screenshots/) and document the public links in [`tableau/dashboard_links.md`](tableau/dashboard_links.md).

---

## Key Insights

1. **Machinery over Skill**: Constructor performance (Beta) has a significantly stronger correlation with race wins than individual driver Alpha.
2. **Elite Skill Persists**: Top-tier drivers (e.g., Schumacher, Hamilton) show a statistically significant positive Alpha, extracted consistently across different teams.
3. **Era Reliability Gap**: Modern engine eras (Hybrid) show a 3x increase in reliability compared to the Pre-V10 era (which had a 56% average DNF rate).
4. **Grid Position Lock**: Grid position shows a strong positive correlation (ρ = 0.18) with finishing order, with Top-5 starters scoring 2.95 more points per race on average.
5. **Pit Stop Median**: Pit crew efficiency has reached a plateau in the Hybrid era, with median stops consistently under 24 seconds (total pit lane time).
6. **DNF Economic Cost**: Title contenders lose an average of 12-18% of potential points to mechanical DNFs per season in high-tension eras.
7. **Circuit Bias**: High-downforce circuits show a narrower "Golden Window" for pit strategy compared to high-speed power circuits.
8. **Mechanical vs. Accident**: 60% of all-time F1 retirements are mechanical, proving car engineering is the primary bottleneck for race completion.

---

## Recommendations

| #   | Insight                            | Recommendation                    | Expected Impact                         |
| --- | ---------------------------------- | --------------------------------- | --------------------------------------- |
| 1   | Machinery Dominance | Prioritize Car Beta development over high-cost driver acquisition. | Higher ROI on championship points. |
| 2   | DNF Economic Cost | Implement the "Points Lost to DNF" framework to prioritize hardware hardening. | Preservation of 10-15% of annual points. |
| 3   | Era Reliability Gap | Transition strategy models to modern reliability baselines (90%+) vs historical. | More aggressive race lap-timing. |

---

## Repository Structure

```text
Section_E_Group_3_PitLane/
|
|-- README.md
|
|-- data/
|   |-- raw/                         # 13 Original CSV files
|   |-- joined/                      # J1-J8 Intermediate tables
|   `-- processed/                   # MASTER_tableau_ready.csv
|
|-- notebooks/
|   |-- 01_extraction.ipynb
|   |-- 02_cleaning_01.ipynb
|   |-- 03_eda.ipynb
|   |-- 04_statistical_analysis.ipynb
|   `-- 05_final_load_prep.ipynb
|
|-- tableau/
|   |-- screenshots/                 # High-res dashboard captures
|   `-- dashboard_links.md           # Tableau Public URL
|
|-- reports/
|   |-- project_final_report.pdf     # Detailed analysis
|   `-- presentation_outline.md
|
|-- docs/
|   `-- data_dictionary.md           # 85-column definition
|
|-- DVA-oriented-Resume/
`-- DVA-focused-Portfolio/
```

---

## Core Logic & Statistical Testing

The project uses Ordinary Least Squares (OLS) regression and normalized efficiency metrics to decouple performance.

```python
# Statistical Model: Predicting Points from Grid Position
import statsmodels.api as sm

ols_data = J1_master_race_results[['grid', 'points']].dropna()
X = sm.add_constant(ols_data['grid'])
model = sm.OLS(ols_data['points'], X).fit()

# Result: Each forward grid position yields ~0.18 more points (p < 0.001)

# KPI Logic: Driver Alpha Calculation
# driver_alpha = ppr (Points Per Race) - constructor_avg_ppr
J2_driver_alpha['driver_alpha'] = J2_driver_alpha['ppr'] - J2_driver_alpha['constructor_avg_ppr']
```

---

## Analytical Pipeline

1. **Define** - Sports analytics sector selected; focus on F1 strategy and driver skill decoupling.
2. **Extract** - 13 relational tables sourced from Ergast/Kaggle (1950-2017).
3. **Clean and Transform** - Multi-stage Python pipeline (Notebooks 01-02) creating 8 analytical joins.
4. **Analyze** - Hypothesis testing using Spearman ρ, Welch t-test, and OLS regression (Notebook 04).
5. **Visualize** - Interactive 3-pillar Tableau dashboard with era and constructor filtering.
6. **Recommend** - Data-backed strategy for car development and reliability prioritization.
7. **Report** - Final PDF export of findings and executive summary.

---

## Tech Stack

| Tool | Status | Purpose |
| --- | --- | --- |
| Python (Pandas/SciPy) | Mandatory | ETL, Statistical Testing |
| Tableau Public | Mandatory | Visual Storytelling |
| GitHub | Mandatory | Version Control |
| Jupyter Notebooks | Mandatory | Reproducible Analysis |

---

## Contribution Matrix

| Team Member | Dataset Sourcing | ETL & Cleaning | EDA & Analysis | Statistical Analysis | Tableau Dashboard | Report Writing |
| ----------- | ---------------- | -------------- | -------------- | -------------------- | ----------------- | -------------- |
| Harsh | Owner | Support | Owner | Support | Owner | Support |
| Vani Vashishtha | Owner | Owner | Support | Support | Owner | Support |
| Aryan Kumar | Owner | Owner | Support | Owner | Owner | Owner |
| Asad Ali | Support | Support | Support | Owner | Owner | Support |
| Dikshant Jangra | Support | Support | Support | Owner | Support | Support |
| Anshu Yadav | Support | Owner | Support | Support | Support | Owner |

---

## Academic Integrity

All analysis, code, and recommendations in this repository are the original work of Team DVA-E-Group-3.

---
_Newton School of Technology - Data Visualization & Analytics | Capstone 2_

