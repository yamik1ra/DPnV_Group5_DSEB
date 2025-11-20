'''
clean_transform.py
---------------------------------
Module to clean and transform decoded BH and IR data,
then merge them into a single clean DataFrame.

Steps:
- Datatype standardization
- Missing & placeholder cleanup
- Categorical normalization
- Logical integrity checks
- Feature engineering
'''

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List
import warnings
warnings.filterwarnings('ignore')
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# ------------------------------------------
# OFFENSE SEVERITY CLASSIFICATION
# ------------------------------------------
VIOLENT_OFFENSES = {
    'Aggravated Assault', 'Murder/Non-negligent Manslaughter',
    'Negligent Manslaughter', 'Kidnapping/Abduction', 'Robbery',
    'Rape', 'Sodomy', 'Sexual Assault With An Object', 'Fondling (Indecent Liberties/Child Molestation)'
}

NON_VIOLENT_EXCEPTIONS = {
    'Statutory Rape', 'Incest'
}

def compute_offense_severity(row):
    """Return violent / non-violent based on decoded offense names."""
    offenses = [row.get(f"offense_{i}") for i in range(1, 11)]
    offenses = [o for o in offenses if isinstance(o, str)]

    if any(o in VIOLENT_OFFENSES for o in offenses):
        return "Violent"

    if any(o in NON_VIOLENT_EXCEPTIONS for o in offenses):
        return "Non-Violent"

    return "Non-Violent"


# ------------------------------------------
# 1. PLACEHOLDER REPLACEMENT
# ------------------------------------------

def replace_placeholders(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Replace placeholder values with NaN.
    '''
    placeholders = ['', ' ']
    return df.replace(placeholders, pd.NA)

# ------------------------------------------
# 2. DATATYPE CONVERSIONS 
# ------------------------------------------
def convert_date(df: pd.DataFrame, date_cols: List[str] = None) -> pd.DataFrame:
    """
    Convert specified columns to datetime.
    """
    if date_cols is None:
        date_cols = [col for col in df.columns if "date" in col.lower()]

    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


def convert_numeric(df: pd.DataFrame, numeric_cols: List[str] = None) -> pd.DataFrame:
    """
    Convert specified columns to numeric.
    """
    if numeric_cols is None:
        numeric_cols = [
            col for col in df.columns 
            if col.lower().startswith(("num_", "current_", "last_", "population"))
            or col.lower().endswith(("_count", "_num"))
            or col in [
                "total_victims", "adult_victims", "juvenile_victims",
                "total_offenders", "adult_offenders", "juvenile_offenders"
            ]
        ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    placeholders = ['', ' ']
    string_cols = df.select_dtypes(include=['object']).columns

    for col in string_cols:
        df[col] = df[col].replace(placeholders, pd.NA)

    # victim/offender negative → NaN
    victim_offender_cols = [
        'total_victims','adult_victims','juvenile_victims',
        'total_offenders','adult_offenders','juvenile_offenders'
    ]
    for col in victim_offender_cols:
        if col in df.columns:
            df.loc[df[col] < 0, col] = pd.NA

    # offender race/eth → Unknown → NaN
    for col in ['offender_race','offender_ethnicity']:
        if col in df.columns:
            df[col] = df[col].replace(['Unknown','UNKNOWN','U'], pd.NA)

    # population 0 → NaN
    if "population" in df.columns:
        df.loc[df["population"] == 0, "population"] = pd.NA

    return df

def validation(df: pd.DataFrame) -> pd.DataFrame:
    issues = []

    # ------------------------------------------------------
    # Victim totals consistency check
    # ------------------------------------------------------
    if all(c in df.columns for c in ['adult_victims', 'juvenile_victims', 'total_victims']):
        df['computed_victims'] = df['adult_victims'].fillna(0) + df['juvenile_victims'].fillna(0)
        mismatch = abs(df['computed_victims'] - df['total_victims'].fillna(0)) > 1
        if mismatch.sum() > 0:
            df.loc[mismatch, 'total_victims'] = df.loc[mismatch, 'computed_victims']
            issues.append(f"Fixed {mismatch.sum()} victim count mismatches")
        df = df.drop(columns=['computed_victims'])

    # ------------------------------------------------------
    # Offender totals consistency check
    # ------------------------------------------------------
    if all(c in df.columns for c in ['adult_offenders', 'juvenile_offenders', 'total_offenders']):
        df['computed_offenders'] = df['adult_offenders'].fillna(0) + df['juvenile_offenders'].fillna(0)
        mismatch = abs(df['computed_offenders'] - df['total_offenders'].fillna(0)) > 1
        if mismatch.sum() > 0:
            df.loc[mismatch, 'total_offenders'] = df.loc[mismatch, 'computed_offenders']
            issues.append(f"Fixed {mismatch.sum()} offender count mismatches")
        df = df.drop(columns=['computed_offenders'])

    # ------------------------------------------------------
    # Remove future dates
    # ------------------------------------------------------
    if 'incident_date' in df.columns:
        future_mask = df['incident_date'] > pd.Timestamp.now()
        if future_mask.sum() > 0:
            df.loc[future_mask, 'incident_date'] = pd.NaT
            issues.append(f"Removed {future_mask.sum()} future dates")

    # ------------------------------------------------------
    # Detect dates older than 2000
    # ------------------------------------------------------
    if 'incident_date' in df.columns:
        old_mask = df['incident_date'] < pd.Timestamp('2000-01-01')
        if old_mask.sum() > 0:
            issues.append(f"Found {old_mask.sum()} incidents before year 2000 (verify manually)")

    # ------------------------------------------------------
    # Year-Month alignment check
    # ------------------------------------------------------
    if all(c in df.columns for c in ['incident_date', 'year', 'month']):
        df['year_check'] = df['incident_date'].dt.year
        df['month_check'] = df['incident_date'].dt.month

        year_mismatch = (df['year'] != df['year_check'])
        month_mismatch = (df['month'] != df['month_check'])

        if year_mismatch.sum() > 0 or month_mismatch.sum() > 0:
            df['year'] = df['year_check']
            df['month'] = df['month_check']
            issues.append(
                f"Fixed {year_mismatch.sum()} year mismatches and {month_mismatch.sum()} month mismatches"
            )

        df = df.drop(columns=['year_check', 'month_check'])

    # ------------------------------------------------------
    # Critical missing fields
    # ------------------------------------------------------
    critical_fields = ['incident_date', 'bias_category', 'offense_severity']
    for field in critical_fields:
        if field in df.columns:
            missing_count = df[field].isna().sum()
            if missing_count > 0:
                issues.append(f"{missing_count} records missing {field}")

    # ------------------------------------------------------
    # Print summary (optional)
    # ------------------------------------------------------
    if len(issues) > 0:
        print("Issues Found & Fixed:")
        for issue in issues:
            print("   -", issue)

    return df



# ------------------------------------------
# 3. FEATURES ENGINEERING
# ------------------------------------------

def add_features_ir(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Add 
    '''
    # TEMPORAL FEATURES
    # ---------------------------------
    if 'incident_date' in df.columns:
        date = df['incident_date']

        df['year'] = date.dt.year
        df['month'] = date.dt.month
        df["quarter"] = "Q" + date.dt.quarter.astype(str)
        df["day_of_week"] = date.dt.day_name()
        df["is_weekend"] = date.dt.dayofweek.isin([5, 6])
        df["day_of_year"] = date.dt.dayofyear
    else:
        raise KeyError("⚠️ Column 'incident_date' is missing from the dataframe.")

    # VICTIM / OFFENDER FEATURES
    # ---------------------------------
    required_cols = [
        "num_adult_victims", "num_juvenile_victims",
        "num_adult_offenders", "num_juvenile_offenders"
    ]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns for ratio computation: {missing}")

    df['total_victims'] = df['num_adult_victims'].fillna(0) + df['num_juvenile_victims'].fillna(0)
    df['total_offenders'] = df['num_adult_offenders'].fillna(0) + df['num_juvenile_offenders'].fillna(0)
    
    df['victim_offender_ratio'] = df['total_victims'] / df['total_offenders']
    # Replace divide-by-zero or invalid values with NaN
    df['victim_offender_ratio'] = df['victim_offender_ratio'].replace([np.inf, -np.inf], np.nan)
    
    # ---------------------------------
    # OFFENSE SEVERITY SCORE
    # ---------------------------------
    df["offense_severity"] = df.apply(compute_offense_severity, axis=1)
    df["severity_score"] = df["offense_severity"].map({"Violent": 1, "Non-Violent": 0})

    return df

def drop_unnecessary_cols(df: pd.DataFrame, df_type: str) -> pd.DataFrame:
    bh_cols_to_keep = ['ori', 'state_code', 'state_abbr', 'state_name', 
                        'agency_name', 'agency_type', 'date_ori_went_nibrs', 'master_file_year',
                        'city_name', 'is_core_city', 'population_group',
                        'country_division', 'country_region',
                        'current_population_1', 'last_population_1', 
                        'current_population_2', 'last_population_2',
                        'current_population_3', 'last_population_3',
                        'current_population_4', 'last_population_4',
                        'current_population_5', 'last_population_5',
                        'state_q1_activity', 'state_q2_activity', 'state_q3_activity', 'state_q4_activity', 
                        'federal_q1_activity', 'federal_q2_activity', 'federal_q3_activity', 'federal_q4_activity', 
                        'fips_counties_1', 'fips_counties_2', 'fips_counties_3', 'fips_counties_4', 'fips_counties_5',
                        '_bh_index' ]
    ir_cols_to_keep = ['bh_index','ori', 'incident_number', 'incident_date',
                        'data_source', 'year', 'quarter', 'month', 'day_of_week', 'is_weekend', 
                        'total_victims', 'num_adult_victims', 'num_juvenile_victims',
                        'total_offenders', 'num_adult_offenders', 'num_juvenile_offenders',
                        'offender_race', 'offender_ethnicity',
                        ]
    # Expand offense fields automatically
    for i in range(1, 11):
        ir_cols_to_keep.extend([
            f"offense_{i}", f"num_victims_{i}", f"victim_types_{i}", f"location_{i}"
        ])
        for suffix in ['a', 'b', 'c', 'd', 'e']:
            ir_cols_to_keep.extend([
                f"bias_motivation_{i}{suffix}", f"bias_{i}{suffix}_category"
            ])
    
    if df_type == 'bh':
        keep = bh_cols_to_keep
    elif df_type == "ir":
        keep = ir_cols_to_keep
    else:
        raise ValueError("df_type must be either 'bh' or 'ir'")
    
    keep = [col for col in keep if col in df.columns]

    return df[keep]

# ------------------------------------------
# 4. BH & IR SPECIFIC CLEANING FUNCTIONS
# ------------------------------------------

def clean_bh(df_bh: pd.DataFrame) -> pd.DataFrame:
    '''
    Clean the BH dataframe.
    '''
    df_bh = replace_placeholders(df_bh)
    df_bh = convert_date(df_bh)
    df_bh = convert_numeric(df_bh)
    df_bh = handle_missing(df_bh)
    df_bh = drop_unnecessary_cols(df_bh, df_type='bh')
    df_bh = df_bh.drop_duplicates()
    df_bh = validation(df_bh)
        
    return df_bh

def clean_ir(df_ir: pd.DataFrame) -> pd.DataFrame:
    '''
    Clean and transform the IR dataframe.
    '''
    df_ir = replace_placeholders(df_ir)
    df_ir = convert_date(df_ir)
    df_ir = convert_numeric(df_ir)
    df_ir = handle_missing(df_ir)
    df_ir = drop_unnecessary_cols(df_ir, df_type='ir')
    df_ir = df_ir.drop_duplicates()
    df_ir = add_features_ir(df_ir)
    df_ir = validation(df_ir)

    df_ir = df_ir.sort_values(['incident_date', 'ori', 'incident_number'])

    return df_ir

# ------------------------------------------
# 5. MERGE BH + IR
# ------------------------------------------

def merge_bh_ir(df_bh: pd.DataFrame, df_ir: pd.DataFrame) -> pd.DataFrame:
    clean_df = df_ir.merge(
        df_bh, left_on='bh_index',
        right_index=True,
        how='left',
        suffixes=('', '_agency')
    )
    return clean_df

# ------------------------------------------
# 6. MAIN PIPELINE FUNCTION
# ------------------------------------------

def clean_and_merge(df_bh: pd.DataFrame, df_ir: pd.DataFrame) -> pd.DataFrame:
    '''
    Run the entire cleaning + merging pipeline.
    Produces: clean_df (ready for EDA / visualization / modeling)
    '''
    print("🧼 Cleaning BH dataframe...")
    df_bh_clean = clean_bh(df_bh)

    print("🧼 Cleaning IR dataframe...")
    df_ir_clean = clean_ir(df_ir)

    print("🔗 Merging BH + IR dataframes...")
    clean_df = merge_bh_ir(df_bh_clean, df_ir_clean)

    return clean_df

if __name__ == '__main__':
    print("This module is intended to be imported by main.py, not run directly.")