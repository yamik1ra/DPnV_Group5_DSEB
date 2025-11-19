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
import warnings
warnings.filterwarnings('ignore')
import pathlib as Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# ------------------------------------------
# 1. COLUMN NORMALIZATION HELPERS
# ------------------------------------------

def replace_placeholders(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Replace placeholder values with NaN.
    '''
    placeholders = {'': pd.NA, ' ': pd.NA}
    return df.replace(placeholders)

def convert_numeric(df:pd.DataFrame) -> pd.DataFrame:
    return None

# ------------------------------------------
# 2. DATATYPE STANDARDIZATION 
# ------------------------------------------
def convert_date(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if 'date' in col.lower():
            df[col] = pd.to_datetime(df[col], format='%Y%m%d', errors='coerce')
    return df

def convert_numeric(df:pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if df[col].dtype == object:
            if df[col].str.match(r"^\d+$", na=False).any():
                df[col] = pd.to_numeric(df[col], errors='coerce')

# ------------------------------------------
# 3. BH & IR SPECIFIC CLEANING FUNCTIONS
# ------------------------------------------

def clean_bh(df_bh: pd.DataFrame) -> pd.DataFrame:
    '''
    Clean the BH dataframe.
    '''
    cols_to_keep = ['ori', 'state_code', 'state_abbr', 'state_name', 
                    'agency_name', 'agency_type', 'date_ori_went_nibrs', 'master_file_year'
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
                    '_bh_index'
                    ]
    df_bh = df_bh.copy()
    df_bh = df_bh[[col for col in cols_to_keep if col in df_bh.columns]]

    df_bh = replace_placeholders(df_bh)
    df_bh = convert_date(df_bh)
        
    return df_bh

def clean_ir(df_ir: pd.DataFrame) -> pd.DataFrame:
    '''
    Clean and transform the IR dataframe.
    '''
    df_ir = replace_placeholders(df_ir)
    df_ir = convert_date(df_ir)

    # Add computed columns
    df_ir['total_victims'] = df_ir['adult_victims'].fillna(0) + df_ir['juvenile_victims'].fillna(0)
    df_ir['total_offenders'] = df_ir['adult_offenders'].fillna(0) + df_ir['juvenile_offenders'].fillna(0)

    df_ir = df_ir.sort_values(['incident_date', 'ori', 'incident_number'])

    return df_ir

# ------------------------------------------
# 4. MERGE BH + IR
# ------------------------------------------

def merge_bh_ir(df_bh: pd.DataFrame, df_ir: pd.DataFrame) -> pd.DataFrame:
    clean_df = df_ir.merge(
        df_bh, left_on='_bh_index',
        right_index=True,
        how='left',
        suffixes=('', '_agency')
    )
    return clean_df

# ------------------------------------------
# 5. MAIN PIPELINE FUNCTION
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