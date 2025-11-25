"""
enrich.py
---------
Add external demographic data (state + territory population) to the cleaned
hate crime dataset for visualization and per-capita normalization.

This script:
1. Loads cleaned hate crime dataset (passed from main.py)
2. Loads state population Excel file (wide format)
3. Loads territories population CSV (already tidy)
4. Reshapes the state population into tidy long format
5. Combines state + territory population
6. Merges into cleaned dataset using ['state_name', 'year']
7. Returns enriched DataFrame to be saved by main.py

Expected population table format (after reshaping):
    state_name | year | population
"""

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def enrich_with_population(df_clean: pd.DataFrame) -> pd.DataFrame:
    '''
    Enrich the cleaned hate crime dataset with population data.
    '''
    STATE_POP_FILE = PROJECT_ROOT / "data" / "external_data" / "state_population_21-24.xlsx"
    TERR_FILE = PROJECT_ROOT / "data" / "external_data" / "territories_population_21-24.csv"

    df_states = pd.read_excel(STATE_POP_FILE, skiprows=3, nrows=57)

    # Drop total and regions rows
    exclude = ["United States", "Northeast", "Midwest", "South", "West"]
    df_states = df_states[~df_states["Geographic Area"].isin(exclude)]

    df_states = df_states.rename(columns={"Geographic Area": "state_name"})

    # Reshape df_state
    df_states_long = df_states.melt(
        id_vars="state_name",
        value_vars=[2021, 2022, 2023, 2024],
        var_name="year",
        value_name="population"
    )

    df_territories = pd.read_csv(TERR_FILE)

    df_population = pd.concat([df_states_long, df_territories], ignore_index=True)
    df_population['state_population'] = df_population['state_population'].astype("Int64")

    # Ensure no duplicate keys
    if df_population.duplicated(subset=["state_name", "year"]).any():
        dups = df_population[df_population.duplicated(subset=["state_name", "year"], keep=False)]
        raise ValueError(f"❌ Duplicate entries found in population data:\n{dups}")

    # Merge into clean dataset
    df_enriched = df_clean.merge(
        df_population,
        on=["state_name", "year"],
        how="left",
        validate="many_to_one"
    )

    missing = df_enriched["population"].isna().sum()
    if missing > 0:
        print(f"⚠️ WARNING: {missing} rows have missing population data (check state_name or year).")

    print(f"   Final enriched dataset size: {df_enriched.shape}")

    return df_enriched

if __name__ == "__main__":
    print("This module enrichs the cleaned hate crime dataset. \nImport and use the enrich_with_population function.")