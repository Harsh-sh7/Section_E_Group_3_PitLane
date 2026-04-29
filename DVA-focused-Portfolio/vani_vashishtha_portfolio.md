# Pitlane F1 Dashboard – Data Visualization Case Study

## Problem Statement & Context
In Formula 1, performance is often debated—does a driver win because of skill, the car, or external race conditions? This project aims to uncover the key factors influencing race outcomes using data-driven analysis. The primary stakeholders include F1 enthusiasts, analysts, and teams seeking performance insights.

---

## Dataset Source & Scope
- **Source:** Kaggle (Formula 1 dataset)  
- **Scope:** Historical race data including drivers, constructors, lap times, circuits, and results  
- **Tools Used:** Python (Google Colab), Tableau  

---

## Data Cleaning & Transformation
- Removed missing and inconsistent records across race results  
- Standardized driver and constructor names  
- Merged multiple datasets (drivers, results, races, constructors)  
- Created calculated fields such as:
  - Win rate  
  - Podium frequency  
  - Constructor dominance index  

---

## KPI Framework
- **Driver Performance Metrics:** Wins, podium finishes, average finishing position  
- **Constructor Performance:** Total wins, consistency across seasons  
- **Race Factors:** Circuit-based performance trends  
- **Comparative Metrics:** Driver vs Constructor contribution  

---

## Key Insights
-  Constructor performance has a stronger correlation with wins than individual driver skill.
-  Top drivers still outperform teammates consistently within the same team, highlighting skill impact.
-  certain circuits favor specific constructors due to car design advantages.
-  winning consistency is more dependent on season-long car reliability than isolated performances.
-  Mid-tier teams show high variability, indicating external race conditions play a role.  

---

## Dashboard
- Built an interactive Tableau dashboard to explore:
  - Driver vs Constructor performance  
  - Seasonal trends  
  - Circuit-level insights  

**Portfolio Link:**  
[https://dva-portfolio-git-main-vani-maxs-projects.vercel.app/](https://dva-portfolio-kappa-snowy.vercel.app/)

---

## Recommendations & Expected Impact
- Teams should prioritize car development for circuit-specific strengths  
- Driver evaluation should consider performance relative to teammates  
- Strategy teams can use historical circuit trends for race planning  
- Analysts can leverage similar frameworks for predictive modeling  

---

## Outcome
This project demonstrates how data visualization can break down complex sports analytics into actionable insights, combining data cleaning, exploratory analysis, and storytelling through dashboards.
