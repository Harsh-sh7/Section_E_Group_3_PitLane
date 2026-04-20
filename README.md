# NST DVA Capstone 2 - Project Repository

> **Newton School of Technology | Data Visualization & Analytics**
> A 2-week industry simulation capstone using Python, GitHub, and Tableau to convert raw data into actionable business intelligence.

---

## Before You Start

1. Rename the repository using the format `SectionName_TeamID_ProjectName`.
2. Fill in the project details and team table below.
3. Add the raw dataset to `data/raw/`.
4. Complete the notebooks in order from `01` to `05`.
5. Publish the final dashboard and add the public link in `tableau/dashboard_links.md`.
6. Export the final report and presentation as PDFs into `reports/`

### Quick Start

If you are working locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

If you are working in Google Colab:

- Upload or sync the notebooks from `notebooks/`
- Keep the final `.ipynb` files committed to GitHub
- Export any cleaned datasets into `data/processed/`

---

## Project Overview

| Field | Details |
|---|---|
| **Project Title** | **PitLane: F1 Strategy & Performance Analytics** |
| **Sector** | Sports & Data Analytics |
| **Team ID** | DVA-E-Group-3 |
| **Section** | Section E |
| **Faculty Mentor** | _To be filled by team_ |
| **Institute** | Newton School of Technology |
| **Submission Date** | April 2026 |

### Team Members

| Role                 | Name   | GitHub Username |
| -------------------- | ------ | --------------- |
| Project Lead         | Harsh           | `Harsh-sh7`      |
| Data Lead            | Vani Vashishtha | `Vani-Max`       |
| ETL Lead             | Aryan Kumar     | `Ario2006`       |
| Analysis Lead        | Asad Ali        | `ali7540`        |
| Visualization Lead   | Vani Vashishtha | `Vani-Max`       |
| Strategy Lead        | Asad Ali        | `ali7540`        |
| Analysis Lead        | Dikshant Jangra | `DikshantJangra` |
| PPT and Quality Lead | Anshu Yadav     | `Anshuxy`        |

---

## Business Problem

In the high-stakes world of Formula 1, races are often won or lost in the pit lane rather than on the track. Team Principals and Strategy Engineers need to optimize every second to maintain a competitive edge, yet the correlation between pit stop efficiency and final race outcomes is often obscured by seasonal noise. This project analyzes 70+ years of F1 data to identify the "Golden Window" for pit strategy and track position retention.

**Core Business Question**

> "How does pit stop duration and strategic lap-timing impact a team's probability of gaining/retaining track position, and which constructors have historically optimized this 'PitLane' advantage?"

**Decision Supported**

> This analysis will enable Team Strategists to benchmark their pit crew performance against rivals and determine the statistical risk-reward of a 1-stop vs. 2-stop strategy across different circuit types.

---

## Dataset

| Attribute | Details |
|---|---|
| **Source Name** | Ergast Motor Racing Dataset (via Kaggle) |
| **Direct Access Link** | [Formula 1 World Championship (1950-2023)](https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020) |
| **Row Count** | 23,000+ (results.csv) |
| **Column Count** | 18+ meaningful columns across 13 files |
| **Time Period Covered** | 1950 to 2023 |
| **Format** | CSV (Relational) |

**Key Columns Used**

| Column Name | Description | Role in Analysis |
|---|---|---|
| `milliseconds` | Final race time in ms | Performance KPI |
| `pit_stop_duration`| Time spent in pit stall | Strategy KPI |
| `positionOrder` | Final finishing position | Outcome Variable |
| `statusId` | Reason for DNF (Engine, Collision) | Reliability Metric |

For full column definitions, see [`docs/data_dictionary.md`](docs/data_dictionary.md).

---

## KPI Framework

| KPI                             | Definition                          | Formula / Computation                          |
| ------------------------------- | ----------------------------------- | ---------------------------------------------- |
| _e.g. Monthly Revenue Growth %_ | _What business outcome this tracks_ | _Show the exact formula or notebook reference_ |
| _e.g. Customer Churn Rate_      | _What business outcome this tracks_ | _Show the exact formula or notebook reference_ |
| _e.g. Repeat Purchase Rate_     | _What business outcome this tracks_ | _Show the exact formula or notebook reference_ |

Document KPI logic clearly in `notebooks/04_statistical_analysis.ipynb` and `notebooks/05_final_load_prep.ipynb`.

---

## Tableau Dashboard

| Item                 | Details                                    |
| -------------------- | ------------------------------------------ |
| **Dashboard URL**    | _Paste Tableau Public link here_           |
| **Executive View**   | _Describe the high-level KPI summary view_ |
| **Operational View** | _Describe the detailed drill-down view_    |
| **Main Filters**     | _List the interactive filters used_        |

Store dashboard screenshots in [`tableau/screenshots/`](tableau/screenshots/) and document the public links in [`tableau/dashboard_links.md`](tableau/dashboard_links.md).

---

## Key Insights

_List 8-12 major findings from the analysis, written in decision language. Each insight should tell the reader what to think or act upon, not merely describe a chart._

1. _Insight 1_
2. _Insight 2_
3. _Insight 3_
4. _Insight 4_
5. _Insight 5_
6. _Insight 6_
7. _Insight 7_
8. _Insight 8_

---

## Recommendations

_Provide 3-5 specific, actionable business recommendations, each linked directly to an insight above._

| #   | Insight                            | Recommendation                    | Expected Impact                         |
| --- | ---------------------------------- | --------------------------------- | --------------------------------------- |
| 1   | _Which insight does this address?_ | _What should the stakeholder do?_ | _What measurable impact do you expect?_ |
| 2   | _Which insight does this address?_ | _What should the stakeholder do?_ | _What measurable impact do you expect?_ |
| 3   | _Which insight does this address?_ | _What should the stakeholder do?_ | _What measurable impact do you expect?_ |

---

## Repository Structure

```text
SectionName_TeamID_ProjectName/
|
|-- README.md
|
|-- data/
|   |-- raw/                         # Original dataset (never edited)
|   `-- processed/                   # Cleaned output from ETL pipeline
|
|-- notebooks/
|   |-- 01_extraction.ipynb
|   |-- 02_cleaning.ipynb
|   |-- 03_eda.ipynb
|   |-- 04_statistical_analysis.ipynb
|   `-- 05_final_load_prep.ipynb
|
|-- scripts/
|   `-- etl_pipeline.py
|
|-- tableau/
|   |-- screenshots/
|   `-- dashboard_links.md
|
|-- reports/
|   |-- README.md
|   |-- project_report_template.md
|   `-- presentation_outline.md
|
|-- docs/
|   `-- data_dictionary.md
|
|-- DVA-oriented-Resume/
`-- DVA-focused-Portfolio/
```

---

## Analytical Pipeline

The project follows a structured 7-step workflow:

1. **Define** - Sector selected, problem statement scoped, mentor approval obtained.
2. **Extract** - Raw dataset sourced and committed to `data/raw/`; data dictionary drafted.
3. **Clean and Transform** - Cleaning pipeline built in `notebooks/02_cleaning.ipynb` and optionally `scripts/etl_pipeline.py`.
4. **Analyze** - EDA and statistical analysis performed in notebooks `03` and `04`.
5. **Visualize** - Interactive Tableau dashboard built and published on Tableau Public.
6. **Recommend** - 3-5 data-backed business recommendations delivered.
7. **Report** - Final project report and presentation deck completed and exported to PDF in `reports/`.

---

## Tech Stack

| Tool                       | Status    | Purpose                                            |
| -------------------------- | --------- | -------------------------------------------------- |
| Python + Jupyter Notebooks | Mandatory | ETL, cleaning, analysis, and KPI computation       |
| Google Colab               | Supported | Cloud notebook execution environment               |
| Tableau Public             | Mandatory | Dashboard design, publishing, and sharing          |
| GitHub                     | Mandatory | Version control, collaboration, contribution audit |
| SQL                        | Optional  | Initial data extraction only, if documented        |

**Recommended Python libraries:** `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`, `statsmodels`

---

## Evaluation Rubric

| Area                        | Marks   | Focus                                                       |
| --------------------------- | ------- | ----------------------------------------------------------- |
| Problem Framing             | 10      | Is the business question clear and well-scoped?             |
| Data Quality and ETL        | 15      | Is the cleaning pipeline thorough and documented?           |
| Analysis Depth              | 25      | Are statistical methods applied correctly with insight?     |
| Dashboard and Visualization | 20      | Is the Tableau dashboard interactive and decision-relevant? |
| Business Recommendations    | 20      | Are insights actionable and well-reasoned?                  |
| Storytelling and Clarity    | 10      | Is the presentation professional and coherent?              |
| **Total**                   | **100** |                                                             |

> Marks are awarded for analytical thinking and decision relevance, not chart quantity, visual decoration, or code length.

---

## Submission Checklist

**GitHub Repository**

- [ ] Public repository created with the correct naming convention (`SectionName_TeamID_ProjectName`)
- [ ] All notebooks committed in `.ipynb` format
- [ ] `data/raw/` contains the original, unedited dataset
- [ ] `data/processed/` contains the cleaned pipeline output
- [ ] `tableau/screenshots/` contains dashboard screenshots
- [ ] `tableau/dashboard_links.md` contains the Tableau Public URL
- [ ] `docs/data_dictionary.md` is complete
- [ ] `README.md` explains the project, dataset, and team
- [ ] All members have visible commits and pull requests

**Tableau Dashboard**

- [ ] Published on Tableau Public and accessible via public URL
- [ ] At least one interactive filter included
- [ ] Dashboard directly addresses the business problem

**Project Report**

- [ ] Final report exported as PDF into `reports/`
- [ ] Cover page, executive summary, sector context, problem statement
- [ ] Data description, cleaning methodology, KPI framework
- [ ] EDA with written insights, statistical analysis results
- [ ] Dashboard screenshots and explanation
- [ ] 8-12 key insights in decision language
- [ ] 3-5 actionable recommendations with impact estimates
- [ ] Contribution matrix matches GitHub history

**Presentation Deck**

- [ ] Final presentation exported as PDF into `reports/`
- [ ] Title slide through recommendations, impact, limitations, and next steps

**Individual Assets**

- [ ] DVA-oriented resume updated to include this capstone
- [ ] Portfolio link or project case study added

---

## Contribution Matrix

This table must match evidence in GitHub Insights, PR history, and committed files.

| Team Member      | Dataset and Sourcing | ETL and Cleaning | EDA and Analysis | Statistical Analysis | Tableau Dashboard | Report Writing | PPT and Viva |
| ---------------- | -------------------- | ---------------- | ---------------- | -------------------- | ----------------- | -------------- | ------------ |
| Harsh Aakya      | Owner   | Support | Support | Support | Support | Support | Owner   |
| Vani Vashishtha  | Owner   | Support | Support | Support | Owner   | Owner   | Support |
| Aryan Kumar      | Support | Owner   | Support | Support | Support | Support | Support |
| Asad Ali         | Support | Support | Support | Owner   | Support | Owner   | Support |
| Dikshant Jangra  | Support | Support | Owner   | Owner   | Support | Support | Support |
| Anshu Yadav      | Support | Support | Support | Support | Support | Support | Owner   |

_Declaration: We confirm that the above contribution details are accurate and verifiable through GitHub Insights, PR history, and submitted artifacts._

**Team Lead Name:** **************\_**************

**Date:** ******\_\_\_******

---

## Academic Integrity

All analysis, code, and recommendations in this repository must be the original work of the team listed above. Free-riding is tracked via GitHub Insights and pull request history. Any mismatch between the contribution matrix and actual commit history may result in individual grade adjustments.

---

_Newton School of Technology - Data Visualization & Analytics | Capstone 2_
