"""
etl_pipeline.py
===============
End-to-end F1 analytics ETL pipeline. Reads cleaned CSVs, builds 8 joined
analysis tables, and exports 5 Tableau-ready production files.

Usage:
    python scripts/etl_pipeline.py
    python scripts/etl_pipeline.py --stage joins
    python scripts/etl_pipeline.py --stage production
    python scripts/etl_pipeline.py --stage all --input data/processed --joins data/joined --prod data/production --verbose

Pipeline Stages:
    Stage 1 — Load & Enrich:  Reads 13 cleaned CSVs, adds derived columns
    Stage 2 — Build Joins:    Produces 8 joined tables (J1 to J8)
    Stage 3 — Production:     Produces 5 Tableau-ready CSVs + 1 master flat table

Joined outputs (data/joined/):
    J1_master_race_results.csv       23,777 rows — Core race results (all pillars)
    J2_driver_alpha.csv               3,397 rows — Driver vs teammate alpha (Pillar A)
    J3_qualifying_analysis.csv        7,516 rows — Qualifying enriched (Pillar A)
    J4_championship_progression.csv  23,777 rows — Cumulative points by round (Pillar A)
    J5_pit_strategy.csv               2,782 rows — Pit strategy + outcomes (Pillar B)
    J6_lap_by_lap.csv               426,633 rows — Lap-level data + pit events (Pillar B)
    J7_reliability_dnf.csv          23,777 rows — DNF analysis by era (Pillar C)
    J8_constructor_reliability.csv    1,041 rows — Constructor reliability index (Pillar C)

Production outputs (data/production/):
    DB1_driver_alpha_season.csv, DB2_pit_strategy.csv,
    DB3_reliability_dnf.csv, DB4_championship_story.csv,
    MASTER_tableau_ready.csv
"""

import argparse
import logging
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# ═══════════════════════════════════════════════════════════════════
# 0. CONSTANTS
# ═══════════════════════════════════════════════════════════════════

FILE_MAP = {
    "circuits":              ["Clean_Circuits_Data.csv",       "circuits.csv"],
    "constructors":          ["Constructors_Clean_Data.csv",   "constructors.csv"],
    "constructor_results":   ["Constructor_Results_Clean.csv", "constructor_results.csv"],
    "constructor_standings": ["Constructor_Standings.csv",     "constructor_standings.csv"],
    "driver_standings":      ["Driver_Standings.csv",          "driver_standings.csv"],
    "drivers":               ["Clean_Drivers_Data.csv",        "drivers.csv"],
    "lap_times":             ["Lap_Times_Clean.csv",           "lap_times.csv"],
    "pit_stops":             ["Cleaned_Pit_Stops.csv",         "pit_stops.csv"],
    "qualifying":            ["Cleaned_Qualifying_Data.csv",   "qualifying.csv"],
    "races":                 ["Cleaned_Races.csv",             "races.csv"],
    "results":               ["Cleaned_Results.csv",           "results.csv"],
    "seasons":               ["Cleaned_Seasons.csv",           "seasons.csv"],
    "status":                ["Cleaned_Status.csv",            "status.csv"],
}

ERA_BOUNDARIES = [
    (1900, 1994, "Pre-V10"),
    (1995, 2005, "V10"),
    (2006, 2013, "V8"),
    (2014, 2100, "Hybrid"),
]

MECHANICAL_STATUSES = frozenset({
    "Alternator", "Battery", "Brake Duct", "Brakes",
    "Clutch", "Crankshaft", "Cv Joint", "Differential",
    "Driveshaft", "Drivetrain", "Electrical", "Electronics",
    "Engine", "Engine Fire", "Engine Misfire", "Ers",
    "Exhaust", "Front Wing", "Fuel", "Fuel Leak",
    "Fuel Pressure", "Fuel Pump", "Fuel System", "Gearbox",
    "Halfshaft", "Handling", "Hydraulics", "Ignition",
    "Injection", "Mechanical", "Oil Leak", "Oil Line",
    "Oil Pressure", "Oil Pump", "Out Of Fuel", "Overheating",
    "Pneumatics", "Power Loss", "Power Unit", "Radiator",
    "Rear Wing", "Broken Wing", "Stalled", "Steering",
    "Suspension", "Technical", "Throttle", "Transmission",
    "Turbo", "Tyre", "Tyre Puncture", "Vibrations",
    "Water Leak", "Water Pump", "Wheel", "Wheel Bearing",
    "Wheel Nut", "Wheel Rim",
})

ACCIDENT_STATUSES = frozenset({
    "Accident", "Collision", "Collision Damage",
    "Fatal Accident", "Fire", "Heat Shield Fire",
    "Safety", "Spun Off",
})

MIN_RACING_LAP_MS = 60_000
MAX_RACING_LAP_MS = 300_000
MIN_PIT_MS = 2_000
MAX_PIT_MS = 120_000

log = logging.getLogger("etl_pipeline")


def get_points_table(year: int) -> dict:
    if year <= 1959:  return {1: 8,  2: 6,  3: 4,  4: 3,  5: 2}
    if year == 1960:  return {1: 8,  2: 6,  3: 4,  4: 3,  5: 2, 6: 1}
    if year <= 1990:  return {1: 9,  2: 6,  3: 4,  4: 3,  5: 2, 6: 1}
    if year <= 2002:  return {1: 10, 2: 6,  3: 4,  4: 3,  5: 2, 6: 1}
    if year <= 2009:  return {1: 10, 2: 8,  3: 6,  4: 5,  5: 4, 6: 3, 7: 2, 8: 1}
    return             {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}


# ═══════════════════════════════════════════════════════════════════
# 1. LOGGING SETUP
# ═══════════════════════════════════════════════════════════════════

def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    fmt = logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s", datefmt="%H:%M:%S")

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)

    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(log_dir / "etl_pipeline.log", mode="a")
    fh.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(console)
    root.addHandler(fh)


# ═══════════════════════════════════════════════════════════════════
# 2. UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def assign_era(year: int) -> str:
    for lo, hi, label in ERA_BOUNDARIES:
        if lo <= year <= hi:
            return label
    return "Unknown"


def classify_dnf(status_str) -> str:
    if pd.isna(status_str):
        return "Other DNF"
    s = str(status_str).strip()
    if s == "Finished" or s.startswith("+"):
        return "Finished"
    s_title = s.title()
    if s_title in MECHANICAL_STATUSES:
        return "Mechanical DNF"
    if s_title in ACCIDENT_STATUSES:
        return "Accident DNF"
    return "Other DNF"


def qual_time_to_ms(time_str) -> float:
    if pd.isna(time_str):
        return np.nan
    t = str(time_str).strip()
    try:
        if ":" in t:
            m, s = t.split(":", 1)
            return (int(m) * 60 + float(s)) * 1000
        return float(t) * 1000
    except Exception:
        return np.nan


def load_table(key: str, input_dir: Path) -> pd.DataFrame:
    for fname in FILE_MAP[key]:
        for p in [input_dir / fname, input_dir / fname.replace("_", " ")]:
            if p.exists():
                df = pd.read_csv(p, encoding="latin1", low_memory=False)
                log.info(f"  Loaded {key:25s} <- {p.name}  ({len(df):,} rows, {len(df.columns)} cols)")
                return df
    tried = [f for f in FILE_MAP[key]] + [f.replace("_", " ") for f in FILE_MAP[key]]
    raise FileNotFoundError(f"Could not find '{key}' in {input_dir}. Tried: {tried}")


def save_csv(df: pd.DataFrame, directory: Path, filename: str) -> Path:
    path = directory / filename
    df.to_csv(path, index=False)
    size_kb = path.stat().st_size / 1024
    log.info(f"  Saved {filename:45s}  {len(df):>8,} rows  {len(df.columns):>3} cols  {size_kb:>8,.0f} KB")
    return path


# ═══════════════════════════════════════════════════════════════════
# 3. STAGE 1 — LOAD AND ENRICH RAW TABLES
# ═══════════════════════════════════════════════════════════════════

def load_and_enrich(input_dir: Path) -> dict:
    log.info("Stage 1: Loading and enriching cleaned tables")
    t_stage = time.time()

    tables = {key: load_table(key, input_dir) for key in FILE_MAP}

    # ── Races ──
    r = tables["races"]
    r["era"] = r["year"].apply(assign_era)
    r.rename(columns={"name": "race_name"}, inplace=True)
    r["date"] = pd.to_datetime(r["date"], errors="coerce")
    for col in ("url", "time"):
        if col in r.columns:
            r.drop(columns=[col], inplace=True)
    tables["races"] = r

    # ── Drivers ──
    d = tables["drivers"]
    if "full_name" not in d.columns:
        d["full_name"] = d["forename"].str.strip() + " " + d["surname"].str.strip()
    d["dob"] = pd.to_datetime(d["dob"], dayfirst=True, errors="coerce")
    if "birth_year" not in d.columns:
        d["birth_year"] = d["dob"].dt.year
    tables["drivers"] = d

    # ── Constructors ──
    tables["constructors"].rename(columns={"name": "constructor_name"}, inplace=True)

    # ── Circuits ──
    tables["circuits"].rename(columns={"name": "circuit_name"}, inplace=True)

    # ── Status ──
    tables["status"]["dnf_category"] = tables["status"]["status"].apply(classify_dnf)

    # ── Results ──
    res = tables["results"]
    res["is_dnf"] = (res["position"] == 0).astype(int)
    res["is_win"] = (res["positionOrder"] == 1).astype(int)
    res["is_podium"] = (res["positionOrder"] <= 3).astype(int)
    res["is_points_finish"] = (res["points"] > 0).astype(int)
    res["is_pole"] = (res["grid"] == 1).astype(int)
    res["grid_vs_finish"] = res["grid"] - res["positionOrder"]
    res.loc[res["grid"] == 0, "grid_vs_finish"] = np.nan
    tables["results"] = res

    # ── Qualifying ──
    q = tables["qualifying"]
    for col in ("q1", "q2", "q3"):
        q[f"{col}_ms"] = q[col].apply(qual_time_to_ms)
    q["best_qual_ms"] = q[["q3_ms", "q2_ms", "q1_ms"]].bfill(axis=1).iloc[:, 0]
    tables["qualifying"] = q

    # ── Pit stops ──
    pit = tables["pit_stops"]
    pit["duration_ms"] = pit["milliseconds"]
    pit["is_valid_stop"] = pit["milliseconds"].between(MIN_PIT_MS, MAX_PIT_MS)
    tables["pit_stops"] = pit

    # ── Lap times ──
    lt = tables["lap_times"]
    lt["is_racing_lap"] = lt["milliseconds"].between(MIN_RACING_LAP_MS, MAX_RACING_LAP_MS)
    tables["lap_times"] = lt

    total_rows = sum(len(df) for df in tables.values())
    log.info(f"  Stage 1 complete: {len(tables)} tables, {total_rows:,} total rows ({time.time() - t_stage:.1f}s)")
    return tables


# ═══════════════════════════════════════════════════════════════════
# 4. STAGE 2 — BUILD JOINED TABLES
# ═══════════════════════════════════════════════════════════════════

def build_joins(tables: dict, output_dir: Path) -> dict:
    log.info("Stage 2: Building joined tables")
    t_stage = time.time()
    joins = {}

    # ── J1 — Master Race Results ──────────────────────────────────
    log.info("  Building J1_master_race_results ...")
    expected = len(tables["results"])
    J1 = (
        tables["results"]
        .merge(tables["races"][["raceId", "race_name", "year", "round", "circuitId", "date", "era"]],
               on="raceId", how="left")
        .merge(tables["circuits"][["circuitId", "circuit_name", "location", "country", "lat", "lng"]],
               on="circuitId", how="left")
        .merge(tables["drivers"][["driverId", "full_name", "nationality", "dob", "birth_year"]],
               on="driverId", how="left")
        .merge(tables["constructors"][["constructorId", "constructor_name", "nationality"]],
               on="constructorId", how="left", suffixes=("_driver", "_constructor"))
        .merge(tables["status"][["statusId", "status", "dnf_category"]],
               on="statusId", how="left")
    )
    assert len(J1) == expected, f"J1 row count changed: expected {expected}, got {len(J1)}"
    save_csv(J1, output_dir, "J1_master_race_results.csv")
    joins["J1"] = J1

    # ── J2 — Driver Alpha ─────────────────────────────────────────
    log.info("  Building J2_driver_alpha ...")
    season = J1.groupby(["driverId", "full_name", "year", "constructorId", "constructor_name", "era"]).agg(
        races=("raceId", "count"),
        season_points=("points", "sum"),
        wins=("is_win", "sum"),
        podiums=("is_podium", "sum"),
        dnfs=("is_dnf", "sum"),
        avg_finish_pos=("positionOrder", "mean"),
        avg_grid_pos=("grid", "mean"),
        avg_grid_delta=("grid_vs_finish", "mean"),
    ).reset_index()

    season["ppr"] = season["season_points"] / season["races"]
    season["win_rate"] = season["wins"] / season["races"]
    season["dnf_rate"] = season["dnfs"] / season["races"]

    constr_avg = season.groupby(["constructorId", "year"])["ppr"].mean().reset_index()
    constr_avg.rename(columns={"ppr": "constructor_avg_ppr"}, inplace=True)
    season = season.merge(constr_avg, on=["constructorId", "year"], how="left")
    season["driver_alpha"] = season["ppr"] - season["constructor_avg_ppr"]

    career = season.groupby(["driverId", "full_name"]).agg(
        total_seasons=("year", "count"),
        total_races=("races", "sum"),
        career_points=("season_points", "sum"),
        career_wins=("wins", "sum"),
        career_podiums=("podiums", "sum"),
        career_dnfs=("dnfs", "sum"),
        career_alpha=("driver_alpha", "mean"),
        avg_ppr=("ppr", "mean"),
    ).reset_index()
    career["career_win_rate"] = career["career_wins"] / career["total_races"]
    career["career_dnf_rate"] = career["career_dnfs"] / career["total_races"]

    J2 = season.merge(
        career[["driverId", "career_alpha", "avg_ppr", "total_races", "career_wins", "career_dnf_rate"]],
        on="driverId", how="left"
    )
    save_csv(J2, output_dir, "J2_driver_alpha.csv")
    joins["J2"] = J2

    # ── J3 — Qualifying Analysis ──────────────────────────────────
    log.info("  Building J3_qualifying_analysis ...")
    J3 = (
        tables["qualifying"]
        .merge(tables["races"][["raceId", "race_name", "year", "round", "circuitId", "era"]],
               on="raceId", how="left")
        .merge(tables["circuits"][["circuitId", "circuit_name", "country"]],
               on="circuitId", how="left")
        .merge(tables["drivers"][["driverId", "full_name", "nationality"]],
               on="driverId", how="left")
        .merge(tables["constructors"][["constructorId", "constructor_name"]],
               on="constructorId", how="left")
        .merge(tables["results"][["raceId", "driverId", "positionOrder", "points", "grid", "is_dnf", "grid_vs_finish"]],
               on=["raceId", "driverId"], how="left")
    )

    team_avg = J3.groupby(["raceId", "constructorId"])["q1_ms"].transform("mean")
    J3["q1_vs_team_avg_ms"] = J3["q1_ms"] - team_avg
    J3["reached_q2"] = J3["q2_ms"].notna().astype(int)
    J3["reached_q3"] = J3["q3_ms"].notna().astype(int)
    save_csv(J3, output_dir, "J3_qualifying_analysis.csv")
    joins["J3"] = J3

    # ── J4 — Championship Progression ─────────────────────────────
    log.info("  Building J4_championship_progression ...")
    J4 = J1[["year", "raceId", "round", "race_name", "country", "era",
             "driverId", "full_name", "constructorId", "constructor_name",
             "points", "is_win", "is_podium", "is_dnf", "positionOrder", "grid"]].copy()
    J4.sort_values(["year", "driverId", "round"], inplace=True)
    J4["cumulative_points"] = J4.groupby(["year", "driverId"])["points"].cumsum()
    J4["cumulative_wins"] = J4.groupby(["year", "driverId"])["is_win"].cumsum()
    J4["championship_pos"] = (
        J4.groupby(["year", "round"])["cumulative_points"]
        .rank(ascending=False, method="min")
        .astype(int)
    )
    leader_pts = J4.groupby(["year", "round"])["cumulative_points"].transform("max")
    J4["gap_to_leader"] = leader_pts - J4["cumulative_points"]
    save_csv(J4, output_dir, "J4_championship_progression.csv")
    joins["J4"] = J4

    # ── J5 — Pit Strategy ─────────────────────────────────────────
    log.info("  Building J5_pit_strategy ...")
    valid_pits = tables["pit_stops"][tables["pit_stops"]["is_valid_stop"]]
    pit_summary = valid_pits.groupby(["raceId", "driverId"]).agg(
        total_stops=("stop", "max"),
        total_pit_ms=("milliseconds", "sum"),
        median_pit_ms=("milliseconds", "median"),
        min_pit_ms=("milliseconds", "min"),
        first_pit_lap=("lap", "min"),
        last_pit_lap=("lap", "max"),
    ).reset_index()
    pit_summary["total_pit_sec"] = pit_summary["total_pit_ms"] / 1000
    pit_summary["median_pit_sec"] = pit_summary["median_pit_ms"] / 1000
    pit_summary["strategy"] = pit_summary["total_stops"].map(
        {1: "1-Stop", 2: "2-Stop", 3: "3-Stop"}
    ).fillna("4+ Stops")
    pit_summary["pit_time_per_stop_sec"] = pit_summary["total_pit_sec"] / pit_summary["total_stops"]

    J5 = (
        pit_summary
        .merge(tables["races"][["raceId", "race_name", "year", "round", "circuitId", "era"]],
               on="raceId", how="left")
        .merge(tables["circuits"][["circuitId", "circuit_name", "country"]],
               on="circuitId", how="left")
        .merge(tables["drivers"][["driverId", "full_name"]],
               on="driverId", how="left")
        .merge(tables["results"][["raceId", "driverId", "constructorId", "positionOrder", "points",
                                   "grid", "laps", "is_dnf", "grid_vs_finish", "statusId"]],
               on=["raceId", "driverId"], how="left")
        .merge(tables["constructors"][["constructorId", "constructor_name"]],
               on="constructorId", how="left")
        .merge(tables["status"][["statusId", "status", "dnf_category"]],
               on="statusId", how="left")
    )
    save_csv(J5, output_dir, "J5_pit_strategy.csv")
    joins["J5"] = J5

    # ── J6 — Lap by Lap ──────────────────────────────────────────
    log.info("  Building J6_lap_by_lap (large table — ~426k rows) ...")
    pit_laps = tables["pit_stops"][tables["pit_stops"]["is_valid_stop"]][
        ["raceId", "driverId", "lap", "milliseconds", "is_valid_stop"]
    ].copy()
    pit_laps.rename(columns={"milliseconds": "pit_duration_ms"}, inplace=True)
    pit_laps["pit_stop_lap"] = True

    J6 = (
        tables["lap_times"]
        .merge(tables["races"][["raceId", "year", "round", "race_name", "era"]],
               on="raceId", how="left")
        .merge(tables["drivers"][["driverId", "full_name"]],
               on="driverId", how="left")
        .merge(tables["results"][["raceId", "driverId", "constructorId"]].drop_duplicates(),
               on=["raceId", "driverId"], how="left")
        .merge(tables["constructors"][["constructorId", "constructor_name"]],
               on="constructorId", how="left")
        .merge(pit_laps[["raceId", "driverId", "lap", "pit_duration_ms", "pit_stop_lap", "is_valid_stop"]],
               on=["raceId", "driverId", "lap"], how="left")
    )
    J6["pit_stop_lap"] = J6["pit_stop_lap"].fillna(False)
    J6["lap_time_sec"] = J6["milliseconds"] / 1000
    J6.sort_values(["raceId", "driverId", "lap"], inplace=True)
    J6["prev_position"] = J6.groupby(["raceId", "driverId"])["position"].shift(1)
    J6["position_change"] = J6["prev_position"] - J6["position"]
    save_csv(J6, output_dir, "J6_lap_by_lap.csv")
    joins["J6"] = J6

    # ── J7 — Reliability DNF Analysis ─────────────────────────────
    log.info("  Building J7_reliability_dnf ...")
    J7 = J1[[
        "resultId", "raceId", "race_name", "year", "round", "era", "date",
        "driverId", "full_name", "nationality_driver",
        "constructorId", "constructor_name", "nationality_constructor",
        "circuit_name", "country",
        "grid", "positionOrder", "laps", "points",
        "statusId", "status", "dnf_category",
        "is_dnf", "is_win", "is_podium",
    ]].copy()

    race_laps = J1.groupby("raceId")["laps"].max().reset_index().rename(columns={"laps": "total_race_laps"})
    J7 = J7.merge(race_laps, on="raceId", how="left")
    J7["laps_pct_completed"] = np.where(
        J7["total_race_laps"] > 0,
        J7["laps"] / J7["total_race_laps"] * 100,
        np.nan,
    )

    def _pts_lost(row):
        if not row["is_dnf"]:
            return 0.0
        tbl = get_points_table(row["year"])
        return float(tbl.get(int(row["positionOrder"]), 0.0))

    J7["potential_points_lost"] = J7.apply(_pts_lost, axis=1)
    save_csv(J7, output_dir, "J7_reliability_dnf.csv")
    joins["J7"] = J7

    # ── J8 — Constructor Reliability Index ────────────────────────
    log.info("  Building J8_constructor_reliability ...")
    season_rel = J7.groupby(["constructorId", "constructor_name", "year", "era"]).agg(
        entries=("resultId", "count"),
        total_dnfs=("is_dnf", "sum"),
        mechanical_dnfs=("dnf_category", lambda x: (x == "Mechanical DNF").sum()),
        accident_dnfs=("dnf_category", lambda x: (x == "Accident DNF").sum()),
        other_dnfs=("dnf_category", lambda x: (x == "Other DNF").sum()),
        total_points=("points", "sum"),
        total_wins=("is_win", "sum"),
        pts_lost_to_dnf=("potential_points_lost", "sum"),
    ).reset_index()

    season_rel["dnf_rate"] = season_rel["total_dnfs"] / season_rel["entries"]
    season_rel["mechanical_dnf_rate"] = season_rel["mechanical_dnfs"] / season_rel["entries"]
    season_rel["reliability_index"] = 1 - season_rel["dnf_rate"]

    season_rel.sort_values(["constructorId", "year"], inplace=True)
    season_rel["rolling3_reliability"] = (
        season_rel.groupby("constructorId")["reliability_index"]
        .transform(lambda x: x.rolling(3, min_periods=1).mean())
    )

    era_rel = J7.groupby(["constructorId", "era"]).agg(
        era_entries=("resultId", "count"),
        era_dnfs=("is_dnf", "sum"),
        era_mech_dnfs=("dnf_category", lambda x: (x == "Mechanical DNF").sum()),
    ).reset_index()
    era_rel["era_reliability"] = 1 - (era_rel["era_dnfs"] / era_rel["era_entries"])
    era_rel["era_mech_dnf_rate"] = era_rel["era_mech_dnfs"] / era_rel["era_entries"]

    J8 = season_rel.merge(
        era_rel[["constructorId", "era", "era_reliability", "era_mech_dnf_rate"]],
        on=["constructorId", "era"], how="left",
    )
    save_csv(J8, output_dir, "J8_constructor_reliability.csv")
    joins["J8"] = J8

    log.info(f"  Stage 2 complete: 8 joined tables built ({time.time() - t_stage:.1f}s)")
    return joins


# ═══════════════════════════════════════════════════════════════════
# 5. STAGE 3 — BUILD PRODUCTION FILES
# ═══════════════════════════════════════════════════════════════════

def validate_columns(df: pd.DataFrame, name: str, required: list) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        log.warning(f"  {name} — missing columns: {missing}")
    else:
        log.info(f"  {name} — all required columns present")


def build_production(joins: dict, output_dir: Path) -> None:
    log.info("Stage 3: Building production files")
    t_stage = time.time()

    # ── DB1 — Driver Alpha Season ─────────────────────────────────
    db1 = joins["J2"].rename(columns={
        "full_name": "Driver", "constructor_name": "Constructor",
        "year": "Season", "era": "Era",
        "season_points": "SeasonPoints", "races": "RacesThisSeason",
        "wins": "SeasonWins", "podiums": "SeasonPodiums", "dnfs": "SeasonDNFs",
        "ppr": "PointsPerRace", "constructor_avg_ppr": "ConstructorAvgPPR",
        "driver_alpha": "DriverAlpha", "career_alpha": "CareerAlpha",
        "avg_finish_pos": "AvgFinishPos", "avg_grid_pos": "AvgGridPos",
        "avg_grid_delta": "AvgGridDelta",
        "win_rate": "WinRate", "dnf_rate": "DNFRate",
        "total_races": "CareerTotalRaces",
    }).copy()
    validate_columns(db1, "DB1_driver_alpha_season",
                     ["Driver", "Season", "Constructor", "Era", "DriverAlpha", "PointsPerRace"])
    save_csv(db1, output_dir, "DB1_driver_alpha_season.csv")

    # ── DB2 — Pit Strategy ────────────────────────────────────────
    db2 = joins["J5"].rename(columns={
        "full_name": "Driver", "constructor_name": "Constructor",
        "race_name": "RaceName", "year": "Season", "era": "Era",
        "country": "Country", "circuit_name": "Circuit",
        "total_stops": "TotalStops", "strategy": "Strategy",
        "median_pit_sec": "MedianPitSec", "total_pit_sec": "TotalPitSec",
        "min_pit_ms": "MinPitMs",
        "first_pit_lap": "FirstPitLap", "last_pit_lap": "LastPitLap",
        "pit_time_per_stop_sec": "AvgSecPerStop",
        "positionOrder": "FinishPosition", "points": "Points",
        "grid": "GridPosition", "laps": "TotalLaps",
        "is_dnf": "DNF", "grid_vs_finish": "GridDelta",
        "status": "Status", "dnf_category": "DNFCategory",
    }).copy()
    db2["FirstStopPct"] = np.where(
        db2["TotalLaps"] > 0,
        db2["FirstPitLap"] / db2["TotalLaps"] * 100,
        np.nan,
    )
    validate_columns(db2, "DB2_pit_strategy",
                     ["Driver", "Season", "TotalStops", "Strategy", "FinishPosition", "MedianPitSec"])
    save_csv(db2, output_dir, "DB2_pit_strategy.csv")

    # ── DB3 — Reliability DNF ─────────────────────────────────────
    db3 = joins["J7"].rename(columns={
        "full_name": "Driver", "constructor_name": "Constructor",
        "nationality_driver": "DriverNationality",
        "race_name": "RaceName", "year": "Season", "era": "Era",
        "country": "Country", "circuit_name": "Circuit",
        "grid": "GridPosition", "positionOrder": "FinishPosition",
        "laps": "LapsCompleted", "total_race_laps": "TotalRaceLaps",
        "laps_pct_completed": "LapsPctCompleted",
        "status": "Status", "dnf_category": "DNFCategory",
        "is_dnf": "IsDNF", "is_win": "IsWin", "is_podium": "IsPodium",
        "potential_points_lost": "PotentialPointsLost",
    }).copy()
    validate_columns(db3, "DB3_reliability_dnf",
                     ["Driver", "Season", "Era", "DNFCategory", "IsDNF"])
    save_csv(db3, output_dir, "DB3_reliability_dnf.csv")

    # ── DB4 — Championship Story ──────────────────────────────────
    db4 = joins["J4"].rename(columns={
        "full_name": "Driver", "constructor_name": "Constructor",
        "race_name": "RaceName", "year": "Season", "era": "Era",
        "country": "Country", "round": "Round",
        "points": "Points", "is_win": "IsWin", "is_podium": "IsPodium",
        "is_dnf": "IsDNF", "positionOrder": "FinishPosition",
        "grid": "GridPosition",
        "cumulative_points": "CumulativePoints",
        "cumulative_wins": "CumulativeWins",
        "championship_pos": "ChampionshipPosition",
        "gap_to_leader": "GapToLeader",
    }).copy()
    validate_columns(db4, "DB4_championship_story",
                     ["Driver", "Season", "Round", "CumulativePoints", "ChampionshipPosition", "GapToLeader"])
    save_csv(db4, output_dir, "DB4_championship_story.csv")

    # ── MASTER — Tableau Ready ────────────────────────────────────
    log.info("  Building MASTER_tableau_ready ...")
    master = joins["J1"].copy()
    expected = len(master)

    q_cols = ["raceId", "driverId", "q1_ms", "q2_ms", "q3_ms",
              "best_qual_ms", "q1_vs_team_avg_ms", "reached_q2", "reached_q3"]
    master = master.merge(joins["J3"][q_cols], on=["raceId", "driverId"], how="left")

    c_sub = joins["J4"][["raceId", "driverId", "cumulative_points", "championship_pos", "gap_to_leader"]] \
        .drop_duplicates(subset=["raceId", "driverId"], keep="first")
    master = master.merge(c_sub, on=["raceId", "driverId"], how="left")

    a_cols = joins["J2"][["driverId", "year", "constructorId", "driver_alpha", "constructor_avg_ppr", "ppr"]]
    master = master.merge(a_cols, on=["driverId", "year", "constructorId"], how="left")

    assert len(master) == expected, f"MASTER row count changed: expected {expected}, got {len(master)}"
    validate_columns(master, "MASTER_tableau_ready",
                     ["full_name", "year", "era", "points", "is_win", "is_dnf",
                      "dnf_category", "driver_alpha", "championship_pos", "q1_ms"])
    save_csv(master, output_dir, "MASTER_tableau_ready.csv")

    log.info(f"  Stage 3 complete: 5 production files built ({time.time() - t_stage:.1f}s)")


# ═══════════════════════════════════════════════════════════════════
# 6. MAIN — ARGUMENT PARSING & PIPELINE ORCHESTRATION
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="F1 ETL Pipeline — cleaned CSVs → joined tables → Tableau production files"
    )
    parser.add_argument("--input", default="data/processed",
                        help="Directory containing cleaned CSV files (default: data/processed)")
    parser.add_argument("--joins", default="data/joined",
                        help="Directory to write joined tables (default: data/joined)")
    parser.add_argument("--prod", default="data/production",
                        help="Directory to write production files (default: data/production)")
    parser.add_argument("--stage", choices=["all", "joins", "production"], default="all",
                        help="Pipeline stage to run (default: all)")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable DEBUG-level logging")
    args = parser.parse_args()

    setup_logging(args.verbose)

    input_dir = Path(args.input)
    joins_dir = Path(args.joins)
    prod_dir = Path(args.prod)

    for d in [joins_dir, prod_dir, Path("logs")]:
        d.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    log.info(f"F1 ETL Pipeline starting — stage: {args.stage}")
    log.info(f"  Input  : {input_dir}")
    log.info(f"  Joins  : {joins_dir}")
    log.info(f"  Prod   : {prod_dir}")

    try:
        joins = {}

        if args.stage in ("all", "joins"):
            tables = load_and_enrich(input_dir)
            joins = build_joins(tables, joins_dir)

        if args.stage == "production":
            log.info("  Loading existing join files ...")
            join_files = [
                ("J1", "J1_master_race_results.csv"),
                ("J2", "J2_driver_alpha.csv"),
                ("J3", "J3_qualifying_analysis.csv"),
                ("J4", "J4_championship_progression.csv"),
                ("J5", "J5_pit_strategy.csv"),
                ("J6", "J6_lap_by_lap.csv"),
                ("J7", "J7_reliability_dnf.csv"),
                ("J8", "J8_constructor_reliability.csv"),
            ]
            for name, fname in join_files:
                lm = name in ("J1", "J6")
                joins[name] = pd.read_csv(joins_dir / fname, low_memory=not lm)
                log.info(f"    Loaded {name}: {len(joins[name]):,} rows")

        if args.stage in ("all", "production"):
            build_production(joins, prod_dir)

    except Exception as e:
        log.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)

    elapsed = time.time() - t0
    log.info(f"\n{'=' * 70}")
    log.info("  OUTPUT FILE SUMMARY")
    log.info(f"{'=' * 70}")

    for d in [joins_dir, prod_dir]:
        for f in sorted(d.glob("*.csv")):
            size_kb = f.stat().st_size / 1024
            # Count lines without loading into pandas (fast)
            with open(f) as fh:
                row_count = sum(1 for _ in fh) - 1
            log.info(f"  {f.name:<45}  {row_count:>8,} rows  {size_kb:>8,.0f} KB")

    log.info(f"\nPipeline complete in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
