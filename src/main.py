'''
main.py - Pipeline Orchestrator
---------------------------------
Runs full ETL pipeline:
1. Load raw fixed-width text files
2. Decode coded values
3. Clean + transform dataset
4. Enrich with external population data
5. Save final processed data
'''

from load_data import load_all_raw
from decode import decode_all
from clean_transform import clean_and_merge
from enrich import enrich_with_population

import warnings
import pandas as pd
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]

def main():
    print("\n=== 📥 STEP 1: Loading raw fixed-width text files ===")
    df_bh_raw, df_ir_raw = load_all_raw()

    print("\n=== 🔓 STEP 2: Decoding ===")
    df_bh_dec, df_ir_dec = decode_all(df_bh_raw, df_ir_raw)

    # Save to .parquet for schema preservation
    df_bh_dec.to_parquet(PROJECT_ROOT / "data/interim/bh_decoded.parquet", index=False,engine="pyarrow")
    df_ir_dec.to_parquet(PROJECT_ROOT / "data/interim/ir_decoded.parquet", index=False,engine="pyarrow")
    print("🗃️ Decoded files saved!")

    print("\n=== 🧼 STEP 3: Cleaning & transforming data ===")
    df_clean = clean_and_merge(df_bh_dec, df_ir_dec)

    df_clean.to_parquet(PROJECT_ROOT / "data/processed/hatecrimes_clean.parquet", index=False, engine='pyarrow')
    print("🗃️ Cleaned files saved!")

    print("\n=== ➕ STEP 4: Enriching with population data ===")
    df_enriched = enrich_with_population(df_clean)

    enriched_path = PROJECT_ROOT / "data/processed/hatecrimes_enriched.parquet"
    df_enriched.to_parquet(enriched_path, index=False)
    print("🗃️ Enriched file saved!")
    
    print("✅ Pipeline completed successfully!")

if __name__ == '__main__':
    main()