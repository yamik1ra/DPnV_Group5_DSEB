'''
load_data.py

Responsible for:
- Loading 4 fixed-width raw data files (2021-2024)
- Returning a unified pandas DataFrame

Usage:
    from src.load_data import load_all_raw
    df_bh_raw, df_ir_raw = load_all_raw(data_folder='data/raw')
'''

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# ----------------------------------------------------
# FIELD SPECIFICATIONS
# ----------------------------------------------------

bh_specs = [
    (1, 2, 'record_type'),
    (3, 4, 'state_code'), (5, 13, 'ori'),
    # (14, 25, 'incident_number') present for sequencing purposes only
    (26, 33, 'date_ori_added'), (34, 41, 'date_ori_went_nibrs'),
    (42, 71, 'city_name'), (72, 73, 'state_abbr'),
    (74, 75, 'population_group'), (76, 76, 'country_division'),
    (77, 77, 'country_region'), (78, 78, 'agency_indicator'),
    (79, 79, 'core_city'), (80, 88, 'covered_by_ori'),
    (89, 92, 'fbi_field_office'), (93, 96, 'judicial_district'),
    (97, 97, 'nibrs_flag'), (98, 105, 'inactive_date'),

    # five-county population coverage (some agencies cover up to 5 counties)
    (106, 114, 'current_population_1'), (115, 117, 'ucr_county_code_1'), 
    (118, 120, 'msa_code_1'), (121, 129, 'last_population_1'), 
    (130, 138, 'current_population_2'), (139, 141, 'ucr_county_code_2'), 
    (142, 144, 'msa_code_2'), (145, 153, 'last_population_2'),
    (154, 162, 'current_population_3'), (163, 165, 'ucr_county_code_3'), 
    (166, 168, 'msa_code_3'), (169, 177, 'last_population_3'), 
    (178, 186, 'current_population_4'), (187, 189, 'ucr_county_code_4'),
    (190, 192, 'msa_code_4'), (193, 201, 'last_population_4'),
    (202, 210, 'current_population_5'), (211, 213, 'ucr_county_code_5'), 
    (214, 216, 'msa_code_5'), (217, 225, 'last_population_5'),

    (226, 229, 'master_file_year'),
    (230, 230, 'state_q1_activity'), (231, 231, 'state_q2_activity'),
    (232, 232, 'state_q3_activity'), (233, 233, 'state_q4_activity'),
    (234, 234, 'federal_q1_activity'), (235, 235, 'federal_q2_activity'),
    (236, 236, 'federal_q3_activity'), (237, 237, 'federal_q4_activity'),
    (238, 267, 'agency_name'), 
    (268, 270, 'fips_counties_1'), (271, 273, 'fips_counties_2'),
    (274, 276, 'fips_counties_3'), (277, 279, 'fips_counties_4'),
    (280, 282, 'fips_counties_5'),
]
ir_specs = [
    (1, 2, 'record_type'),
    (3, 4, 'state_code'),
    (5, 13, 'ori'),               # ORI read from the IR line itself
    (14, 25, 'incident_number'), (26, 33, 'incident_date'),
    (34, 34, 'data_source'), (35, 35, 'quarter'),
    (36, 38, 'num_victims'), (39, 40, 'num_offenders'),
    (41, 41, 'offender_race'),
    # Offense 1
    (42, 44, 'ucr_offense_code_1'), (45, 47, 'num_victims_1'), (48, 49, 'location_code_1'),
    (50, 51, 'bias_motivation_1a'), (52, 59, 'victim_types_1'),
    # Offense 2
    (60, 62, 'ucr_offense_code_2'), (63, 65, 'num_victims_2'), (66, 67, 'location_code_2'),
    (68, 69, 'bias_motivation_2a'), (70, 77, 'victim_types_2'),
    # Offense 3
    (78, 80, 'ucr_offense_code_3'), (81, 83, 'num_victims_3'), (84, 85, 'location_code_3'),
    (86, 87, 'bias_motivation_3a'), (88, 95, 'victim_types_3'),
    # Offense 4
    (96, 98, 'ucr_offense_code_4'), (99, 101, 'num_victims_4'), (102, 103, 'location_code_4'),
    (104, 105, 'bias_motivation_4a'), (106, 113, 'victim_types_4'),
    # Offense 5
    (114, 116, 'ucr_offense_code_5'), (117, 119, 'num_victims_5'), (120, 121, 'location_code_5'),
    (122, 123, 'bias_motivation_5a'), (124, 131, 'victim_types_5'),
    # Offense 6
    (132, 134, 'ucr_offense_code_6'), (135, 137, 'num_victims_6'), (138, 139, 'location_code_6'),
    (140, 141, 'bias_motivation_6a'), (142, 149, 'victim_types_6'),
    # Offense 7
    (150, 152, 'ucr_offense_code_7'), (153, 155, 'num_victims_7'), (156, 157, 'location_code_7'),
    (158, 159, 'bias_motivation_7a'), (160, 167, 'victim_types_7'),
    # Offense 8
    (168, 170, 'ucr_offense_code_8'), (171, 173, 'num_victims_8'), (174, 175, 'location_code_8'),
    (176, 177, 'bias_motivation_8a'), (178, 185, 'victim_types_8'),
    # Offense 9
    (186, 188, 'ucr_offense_code_9'), (189, 191, 'num_victims_9'), (192, 193, 'location_code_9'),
    (194, 195, 'bias_motivation_9a'), (196, 203, 'victim_types_9'),
    # Offense 10
    (204, 206, 'ucr_offense_code_10'), (207, 209, 'num_victims_10'), (210, 211, 'location_code_10'),
    (212, 213, 'bias_motivation_10a'), (214, 221, 'victim_types_10'),
    # Other bias motivations for each offense
    (222, 223, 'bias_motivation_1b'), (224, 225, 'bias_motivation_1c'), 
    (226, 227, 'bias_motivation_1d'), (228, 229, 'bias_motivation_1e'),
    (230, 231, 'bias_motivation_2b'), (232, 233, 'bias_motivation_2c'), 
    (234, 235, 'bias_motivation_2d'), (236, 237, 'bias_motivation_2e'),
    (238, 239, 'bias_motivation_3b'), (240, 241, 'bias_motivation_3c'), 
    (242, 243, 'bias_motivation_3d'), (244, 245, 'bias_motivation_3e'),
    (246, 247, 'bias_motivation_4b'), (248, 249, 'bias_motivation_4c'), 
    (250, 251, 'bias_motivation_4d'), (252, 253, 'bias_motivation_4e'),
    (254, 255, 'bias_motivation_5b'), (256, 257, 'bias_motivation_5c'),
    (258, 259, 'bias_motivation_5d'), (260, 261, 'bias_motivation_5e'),
    (262, 263, 'bias_motivation_6b'), (264, 265, 'bias_motivation_6c'), 
    (266, 267, 'bias_motivation_6d'), (268, 269, 'bias_motivation_6e'),
    (270, 271, 'bias_motivation_7b'), (272, 273, 'bias_motivation_7c'), 
    (274, 275, 'bias_motivation_7d'), (276, 277, 'bias_motivation_7e'),
    (278, 279, 'bias_motivation_8b'), (280, 281, 'bias_motivation_8c'), 
    (282, 283, 'bias_motivation_8d'), (284, 285, 'bias_motivation_8e'),
    (286, 287, 'bias_motivation_9b'), (288, 289, 'bias_motivation_9c'), 
    (290, 291, 'bias_motivation_9d'), (292, 293, 'bias_motivation_9e'),
    (294, 295, 'bias_motivation_10b'), (296, 297, 'bias_motivation_10c'), 
    (298, 299, 'bias_motivation_10d'), (300, 301, 'bias_motivation_10e'),
    # Victim/offender age breakdowns
    (302, 304, 'num_adult_victims'), (305, 307, 'num_juvenile_victims'), 
    (308, 309, 'num_adult_offenders'), (310, 311, 'num_juvenile_offenders'), 
    (312, 312, 'offender_ethnicity'),
]

# ----------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------
def get_field(line: str, start: int, end: int) -> str:
    """Extract field from fixed-width line (1-based indexing)."""
    if len(line) < end:
        return line[start-1:].rstrip('\n').strip()
    return line[start-1:end].strip()

def load_single_file(file_path, file_id):
    """
    Parse a single FBI fixed-width file.
    Returns (list_of_bh_records, list_of_ir_records).
    """
    file_path = Path(file_path)
    print(f"\n📁 Reading file: {file_path}")

    if not file_path.exists():
        print(f"⚠️ File not found: {file_path} — skipping")
        return [], []
    
    bh_records = []
    ir_records = []
    current_bh_index = None
    file_bh_count = 0
    file_ir_count = 0

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for lineno, raw_line in enumerate(f, start=1):
            line = raw_line.rstrip('\n')

            if not line: continue

            record_type = line[:2]
            # ---- BH Record ----
            if record_type == "BH":
                bh_data = {
                    name: get_field(line, start, end)
                    for start, end, name in bh_specs
                }
                bh_data["bh_index"] = len(bh_records)
                bh_data['file_id'] = file_id
                bh_records.append(bh_data)

                current_bh_index = bh_data["bh_index"]
                file_bh_count += 1
            
            # ---- IR Record ----
            elif record_type == "IR":
                ir_data = {
                    name: get_field(line, start, end)
                    for start, end, name in ir_specs
                }
                ir_data["bh_index"] = current_bh_index  # link to BH
                ir_data['file_id'] = file_id
                ir_data["_ir_line_no"] = lineno
                ir_records.append(ir_data)

                file_ir_count += 1

    print(f"  ✅ Parsed {file_bh_count:,} BH records, {file_ir_count:,} IR records.")
    return bh_records, ir_records

def load_all_raw(data_folder=PROJECT_ROOT / 'data' / 'raw'):
    """
    Load BH + IR records from all 4 year files (2021-2024).
    Returns df_bh, df_ir as DataFrames.
    """
    file_patterns = {
        '2021': "2021_HC_NATIONAL_MASTER_FILE.txt",
        '2022': "2022_HC_NATIONAL_MASTER_FILE.txt",
        '2023': "2023_HC_NATIONAL_MASTER_FILE.txt",
        '2024': "2024_HC_NATIONAL_MASTER_FILE.txt",
    }

    all_bh = []
    all_ir = []

    for year, file_name in file_patterns.items():
        fp = Path(data_folder) / file_name
        bh_records, ir_records = load_single_file(fp, file_id=year)
        all_bh.extend(bh_records)
        all_ir.extend(ir_records)

    if not all_bh:
        raise ValueError("No BH records were loaded. Double-check file paths.")
    if not all_ir:
        print("⚠️ Warning: No IR records found.")
    
    df_bh = pd.DataFrame(all_bh)
    df_ir = pd.DataFrame(all_ir)

    print(f"{'='*50}")
    print(" TOTAL RECORDS LOADED:")
    print(f"   BH (Agency) records: {len(df_bh):,}")
    print(f"   IR (Incident) records: {len(df_ir):,}")
    print(f"{'='*50}")

    return df_bh, df_ir

# ----------------------------------------------------
# CLI
# ----------------------------------------------------
if __name__ == "__main__":
    bh, ir = load_all_raw()