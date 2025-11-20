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
from datetime import datetime
from typing import List
import warnings
warnings.filterwarnings('ignore')
import pathlib as Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]

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
def convert_date(df: pd.DataFrame, date_cols: List[str]) -> pd.DataFrame:
    '''
    Convert specified columns to datetime.
    '''
    for col in date_cols:
        if 'date' in df.columns:
            df[col] = pd.to_datetime(df[col], format='%Y%m%d', errors='coerce')
    return df

def convert_numeric(df:pd.DataFrame, numeric_cols: List[str]) -> pd.DataFrame:
    '''
    Convert specified columns to numeric.
    '''
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
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
    
    # 
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
    df_bh = df_bh.validation()
        
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
    df_ir = df_ir.add_features_ir()
    df_ir = df_ir.validation()

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