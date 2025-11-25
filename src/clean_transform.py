'''
clean_transform.py
---------------------------------
Module to clean and transform decoded BH and IR data,
then merge them into a single clean DataFrame.

Steps:
- Datatype standardization
- Missing & placeholder cleanup
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

OFFENSE_SEVERITY_MAP = {
    # High Severity (Person crimes, immediate threat to life/safety)
    '09A': 'High', '09B': 'High', '11A': 'High', '11B': 'High', '11C': 'High',
    '120': 'High', '13A': 'High', '64A': 'High', '64B': 'High', '100': 'High',
    
    # Medium Severity (Major property, weapons, severe fraud, severe drugs)
    '200': 'Medium', '220': 'Medium', '210': 'Medium', '240': 'Medium', 
    '35A': 'Medium', '520': 'Medium', '26F': 'Medium', '26G': 'Medium', 
    '26E': 'Medium',
    
    # Low Severity (Minor property, public order, simple assault)
    '13B': 'Low', '13C': 'Low', '510': 'Low', '250': 'Low', '290': 'Low', 
    '35B': 'Low', '270': 'Low', '26A': 'Low', '26B': 'Low', '26C': 'Low', 
    '26D': 'Low', '39A': 'Low', '39B': 'Low', '39C': 'Low', '39D': 'Low', 
    '23A': 'Low', '23B': 'Low', '23C': 'Low', '23D': 'Low', '23E': 'Low', 
    '23F': 'Low', '23G': 'Low', '23H': 'Low', '370': 'Low', '40A': 'Low', 
    '40B': 'Low', '40C': 'Low', '11D': 'Low', '36A': 'Low', '36B': 'Low',
    '280': 'Low', '720': 'Low',

    # Non-Criminal/Informational
    '09C': 'Non-Criminal'
}

bh_cols_to_keep = ['ori', 'state_code', 'state_abbr', 'state_name', 
                    'agency_name', 'agency_type', 'date_ori_went_nibrs', 'master_file_year',
                    'city_name', 'is_core_city', 'population_group',
                    'country_division', 'country_region', 'judicial_district',
                    'current_population', 'last_population',
                    'state_q1_activity', 'state_q2_activity', 'state_q3_activity', 'state_q4_activity', 
                    'federal_q1_activity', 'federal_q2_activity', 'federal_q3_activity', 'federal_q4_activity', 
                    'fips_counties_1', 'fips_counties_2', 'fips_counties_3', 'fips_counties_4', 'fips_counties_5',
                    'bh_index', 'file_id']
ir_cols_to_keep = [ 'ori', 'incident_number', 'incident_date',
                    'data_source', 'year', 'quarter', 'month', 'day_of_week', 'is_weekend', 
                    'total_victims', 'num_adult_victims', 'num_juvenile_victims',
                    'total_offenders', 'num_adult_offenders', 'num_juvenile_offenders',
                    'victim_offender_ratio',
                    'offender_race', 'offender_ethnicity',
                    'file_id', 'bh_index']
# Expand offense fields automatically
for i in range(1, 11):
    ir_cols_to_keep.extend([
        f"offense_{i}", f'offense_{i}_severity', f"num_victims_{i}", f"victim_types_{i}", f"location_{i}"
    ])
    for suffix in ['a', 'b', 'c', 'd', 'e']:
        ir_cols_to_keep.extend([
            f"bias_motivation_{i}{suffix}", f"bias_{i}{suffix}_category"
        ])

def replace_placeholders(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Replace placeholder values with NaN.
    '''
    placeholders = ['', ' ']
    return df.replace(placeholders, np.nan)

def convert_date(df: pd.DataFrame, date_cols: List[str] = None) -> pd.DataFrame:
    '''
    Convert specified columns to datetime.
    '''
    if date_cols is None:
        date_cols = [col for col in df.columns if "date" in col.lower()]

    for col in date_cols:
        df[col] = pd.to_datetime(df[col], format='%Y%m%d', errors="coerce")

    return df

def convert_numeric(df:pd.DataFrame, numeric_cols: List[str]=None) -> pd.DataFrame:
    '''
    Convert specified columns to numeric.
    '''
    if numeric_cols is None:
        numeric_cols = [
            col for col in df.columns 
            if col.lower().startswith(("num_", "current_", "last_", "total_"))
            or col.lower().endswith(("_count", "_num"))
        ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype('Int64')
    
    return df

def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    # victim/offender: negative → NA
    victim_offender_cols = [
        'total_victims','num_adult_victims','num_juvenile_victims',
        'total_offenders','num_adult_offenders','num_juvenile_offenders'
    ]
    for col in victim_offender_cols:
        if col in df.columns:
            df.loc[df[col] < 0, col] = np.nan

    # offender race/ethnicity: Unknown → NaN
    for col in ['offender_race','offender_ethnicity']:
        if col in df.columns:
            df[col] = df[col].replace('Unknown', np.nan)

    # population <= 0 should means missing information
    pop_cols = df.filter(regex=r'^(current|last)_population_\d+$').columns.tolist()
    for col in pop_cols:    
        if col in df.columns:
            df.loc[df[col] <= 0, col] = np.nan

    return df

def handle_incident_number_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Checks for duplicate incident numbers. 
    If found, check if they occur within the same agency (ORI). 
    If not so, merge ORI and incident_number to create a new unique identifier.
    """
    if 'incident_number' not in df.columns or 'ori' not in df.columns:
        return df

    # Check: Global duplicate incident numbers
    duplicate_global_mask = df['incident_number'].duplicated(keep=False)
    global_duplicate_count = duplicate_global_mask.sum()

    if global_duplicate_count == 0:
        return df
    else:
        # Check: Duplicate incident numbers within the same agency (ORI)
        # but the rows themselves are not exact duplicates.
        agency_duplicate_mask = (
            df.duplicated(subset=['ori', 'incident_number'], keep=False)
            &
            (~df.duplicated(keep=False)) 
        )
        agency_duplicate_count = agency_duplicate_mask.sum()

        if agency_duplicate_count == 0: 
            # Create a unique incident identifier by combining ORI and incident_number
            df['incident_number'] = df['ori'].astype(str) + '-' + df['incident_number'].astype(str)

        else:
            print('⚠️ Warning: Conflicting records for the same (ori, incident_number). Appending unqiue suffix.')
            
            # Create a deduplicated ID by appending a counter
            df['incident_number'] = (
                df['ori'].astype(str) + '-' +
                df['incident_number'].astype(str) + '-' +
                df.groupby(['ori', 'incident_number']).cumcount().astype(str)
            )
        
        return df

def validate(df: pd.DataFrame) -> pd.DataFrame:
    issues = []

    # ------------------------------------------------------
    # Victim totals consistency check
    # ------------------------------------------------------
    if all(c in df.columns for c in ['num_adult_victims', 'num_juvenile_victims', 'total_victims']):
        calculated_total = (df['num_adult_victims'].fillna(0) + df['num_juvenile_victims'].fillna(0))
        reported_total = df['total_victims'].fillna(0)
        
        mismatch_mask = (calculated_total != reported_total)
        mismatch_count = mismatch_mask.sum()

        if mismatch_count > 0:
            df.loc[mismatch_mask, 'total_victims'] = calculated_total[mismatch_mask]
            issues.append(f"Fixed {mismatch_count} victim count mismatches.")
    
    # ------------------------------------------------------
    # Offender totals consistency check
    # ------------------------------------------------------
    if all(c in df.columns for c in ['num_adult_offenders', 'num_juvenile_offenders', 'total_offenders']):
        calculated_total = (df['num_adult_offenders'].fillna(0) + df['num_juvenile_offenders'].fillna(0))
        reported_total = df['total_offenders'].fillna(0)

        mismatch_mask = (calculated_total != reported_total)
        mismatch_count = mismatch_mask.sum()

        if mismatch_count > 0:
            df.loc[mismatch_mask, 'total_offenders'] = calculated_total[mismatch_mask]
            issues.append(f"Fixed {mismatch_count} offender count mismatches.")
    
    # ------------------------------------------------------
    # Remove future dates
    # ------------------------------------------------------
    if 'incident_date' in df.columns:
        future_mask = df['incident_date'] > pd.Timestamp.now()
        if future_mask.sum() > 0:
            df.loc[future_mask, 'incident_date'] = pd.NaT
            issues.append(f"Removed {future_mask.sum()} future dates.")
    
    # ------------------------------------------------------
    # Detect dates older than 2021
    # ------------------------------------------------------
    if 'incident_date' in df.columns:
        old_mask = df['incident_date'] < pd.Timestamp('2021-01-01')
        if old_mask.sum() > 0:
            issues.append(f"Found {old_mask.sum()} incidents before year 2021.")

    return df

def add_features_bh(df: pd.DataFrame)-> pd.DataFrame:
    # ---------------------------------
    # Total POPULATION the agency is responsible for
    # ---------------------------------
    current_pop_cols = df.filter(regex=r'^current_population_\d+$')
    last_pop_cols = df.filter(regex=r'^last_population_\d+$')
    
    df['current_population'] = current_pop_cols.sum(axis=1, min_count=1)
    df['last_population'] = last_pop_cols.sum(axis=1, min_count=1)

    return df

def add_features_ir(df: pd.DataFrame) -> pd.DataFrame:
    # ---------------------------------
    # TEMPORAL FEATURES
    # ---------------------------------
    if 'incident_date' in df.columns:
        date = df['incident_date']

        df['year'] = date.dt.year
        df['month'] = date.dt.month
        
        quarter_series = date.dt.quarter.astype('Int64')
        df["quarter"] = np.where(quarter_series.notna(), "Q" + quarter_series.astype(str), np.nan)
        
        df["day_of_week"] = date.dt.day_name().astype('category')
        df["is_weekend"] = date.dt.dayofweek.isin([5, 6])
        df["day_of_year"] = date.dt.dayofyear
    else:
        raise KeyError("⚠️ Column 'incident_date' is missing from the dataframe.")

    # ---------------------------------
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
    # OFFENSE SEVERITY
    # ---------------------------------
    for i in range(1, 11):
        offense_col = f'ucr_offense_code_{i}'
        severity_col = f'offense_{i}_severity'

        if offense_col in df.columns:
            df[severity_col] = df[offense_col].map(OFFENSE_SEVERITY_MAP)

    return df

def drop_zero_variance_cat(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Remove categorical columns with zero variance
    '''
    cat_cols = df.select_dtypes(include=['object', 'category']).columns

    zero_var_cols = [col for col in cat_cols if df[col].nunique(dropna=True) <= 1]

    cleaned_df = df.drop(columns=zero_var_cols)

    return cleaned_df

def cleanup_unused_offense_cols(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Identifies and removes offense-related columns (offense_i, num_victims_i, 
    victim_types_i, location_i for i = 1 to 10) that contain only missing data (NaN).
    '''
    all_offense_columns = []
    for i in range(1, 11):
        all_offense_columns.extend([
            f"offense_{i}", f'offense_{i}_severity', f"num_victims_{i}", f"victim_types_{i}", f"location_{i}"
        ])
        for suffix in ['a', 'b', 'c', 'd', 'e']:
            all_offense_columns.extend([
                f"bias_motivation_{i}{suffix}", f"bias_{i}{suffix}_category"
            ])
    
    existing_offense_cols = [col for col in all_offense_columns if col in df.columns]
    
    if not existing_offense_cols:
        return df

    empty_cols = df[existing_offense_cols].columns[df[existing_offense_cols].isna().all()].tolist()

    if empty_cols:
        print(f"Dropping {len(empty_cols)} completely empty offense columns.")
        return df.drop(columns=empty_cols)

    return df

def drop_unnecessary_cols(df: pd.DataFrame, df_type: str) -> pd.DataFrame:
    if df_type == 'bh':
        df = df.dropna(axis=1, how='all')
        df = drop_zero_variance_cat(df)
        keep = bh_cols_to_keep
    elif df_type == "ir":
        df = cleanup_unused_offense_cols(df)
        keep = ir_cols_to_keep
    else:
        raise ValueError("df_type must be either 'bh' or 'ir'")
    
    keep = [col for col in keep if col in df.columns]

    return df[keep]

# ------------------------------------------
#   BH & IR SPECIFIC CLEANING FUNCTIONS
# ------------------------------------------

def clean_bh(df_bh: pd.DataFrame) -> pd.DataFrame:
    '''
    Clean the BH dataframe.
    '''
    
    df_bh = replace_placeholders(df_bh)
    df_bh = convert_date(df_bh)
    df_bh = convert_numeric(df_bh)
    df_bh = handle_missing(df_bh)
    df_bh = validate(df_bh)
    df_bh = add_features_bh(df_bh)
    df_bh = drop_unnecessary_cols(df_bh, df_type='bh')
    df_bh = df_bh.set_index(['file_id', 'bh_index'])
        
    return df_bh

def clean_ir(df_ir: pd.DataFrame) -> pd.DataFrame:
    '''
    Clean and transform the IR dataframe.
    '''
    df_ir = replace_placeholders(df_ir)
    df_ir = convert_date(df_ir)
    df_ir = convert_numeric(df_ir)
    df_ir = handle_missing(df_ir)
    df_ir = handle_incident_number_duplicates(df_ir)
    df_ir = validate(df_ir)
    df_ir = add_features_ir(df_ir)
    df_ir = drop_unnecessary_cols(df_ir, df_type='ir')
    df_ir = df_ir.set_index(['file_id', 'bh_index'])

    df_ir = df_ir.sort_values(['incident_date', 'ori', 'incident_number'])

    return df_ir

# ------------------------------------------
#   MERGE BH + IR
# ------------------------------------------

def merge_bh_ir(df_bh: pd.DataFrame, df_ir: pd.DataFrame) -> pd.DataFrame:
    """
    Merge IR and BH data using MultiIndex (file_id, bh_index)
    """
    clean_df = df_ir.merge(
        df_bh, 
        left_index=True,
        right_index=True,
        how='left',
        suffixes=('', '_agency')
    )
    return clean_df

# ------------------------------------------
#   MAIN PIPELINE FUNCTION
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
    clean_df = clean_df.reset_index()
    clean_df = clean_df.drop_duplicates(ignore_index=True)

    return clean_df

if __name__ == '__main__':
    print("This module is intended to be imported by main.py, not run directly.")