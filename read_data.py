#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
read_data.py
------------
Parse the 4 yearly Hate-Crime master files (2021-2024) that live in ./data/
and write **four** CSVs:

    hate_crime_batch_header_raw.csv
    hate_crime_incident_raw.csv
    hate_crime_batch_header_decoded.csv
    hate_crime_incident_decoded.csv

All field positions & lookup tables follow the FBI PDF
“Hate Crime Yearly Master Record Descriptions v4.0 (11/12/2021)”.
"""

import csv
from pathlib import Path

# ----------------------------------------------------------------------
# 1. Paths – script lives next to a folder called data/
# ----------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent          # folder that contains this script
DATA_DIR = BASE_DIR / "data"                        # <-- your 4 txt files live here

YEARS = [2021, 2022, 2023, 2024]
INPUT_FILES = [DATA_DIR / f"{y}_HC_NATIONAL_MASTER_FILE.txt" for y in YEARS]

# output files (also written inside the data/ folder)
BH_RAW_OUT = DATA_DIR / "hate_crime_batch_header.csv"
IR_RAW_OUT = DATA_DIR / "hate_crime_incident.csv"
BH_DEC_OUT = DATA_DIR / "hate_crime_batch_header_decoded.csv"
IR_DEC_OUT = DATA_DIR / "hate_crime_incident_decoded.csv"

# ----------------------------------------------------------------------
# 2. Lookup dictionaries (exact from the PDF)
# ----------------------------------------------------------------------
AGENCY_TYPE = {
    "0": "City", "1": "County", "2": "State", "3": "University/College",
    "4": "Federal", "5": "Tribal", "6": "Other", "7": "Unknown"
}
POP_GROUP = {
    "1": "Cities 250,000+", "2": "Cities 100,000-249,999",
    "3": "Cities 50,000-99,999", "4": "Cities 25,000-49,999",
    "5": "Cities 10,000-24,999", "6": "Cities 2,500-9,999",
    "7": "Cities <2,500", "8": "Non-MSA Counties", "9": "MSA Counties"
}
BIAS = {
    "11": "Anti-White", "12": "Anti-Black or African American",
    "13": "Anti-American Indian or Alaska Native", "14": "Anti-Asian",
    "15": "Anti-Native Hawaiian or Other Pacific Islander",
    "16": "Anti-Multiple Races, Group", "21": "Anti-Jewish",
    "22": "Anti-Catholic", "23": "Anti-Protestant", "24": "Anti-Islamic (Muslim)",
    "25": "Anti-Other Religion", "26": "Anti-Multiple Religions, Group",
    "27": "Anti-Atheism/Agnosticism/etc.", "31": "Anti-Arab",
    "32": "Anti-Hispanic or Latino", "33": "Anti-Other Race/Ethnicity/Ancestry",
    "41": "Anti-Male", "42": "Anti-Female", "43": "Anti-Transgender",
    "44": "Anti-Gender Non-Conforming", "51": "Anti-Lesbian",
    "52": "Anti-Gay (Male)", "53": "Anti-Lesbian, Gay, Bisexual, or Transgender (Mixed Group)",
    "54": "Anti-Heterosexual", "55": "Anti-Bisexual",
    "61": "Anti-Physical Disability", "62": "Anti-Mental Disability",
    "71": "Anti-Male Homosexual (Gay)", "72": "Anti-Female Homosexual (Lesbian)",
    "81": "Anti-Eastern Orthodox (Russian, Greek, Other)",
    "82": "Anti-Other Christian", "83": "Anti-Buddhist", "84": "Anti-Hindu",
    "85": "Anti-Sikh", "88": "Unknown"
}
LOCATION = {
    "01": "Air/Bus/Train Terminal", "02": "Bank/Savings and Loan",
    "03": "Bar/Nightclub", "04": "Church/Synagogue/Temple/Mosque",
    "05": "Commercial/Office Building", "06": "Construction Site",
    "07": "Convenience Store", "08": "Department/Discount Store",
    "09": "Drug Store/Doctor’s Office/Hospital", "10": "Field/Woods",
    "11": "Government/Public Building", "12": "Grocery/Supermarket",
    "13": "Highway/Road/Alley/Street/Sidewalk", "14": "Hotel/Motel/Etc.",
    "15": "Jail/Prison/Penitentiary/Corrections Facility",
    "16": "Lake/Waterway/Beach", "17": "Liquor Store",
    "18": "Parking/Drop Lot/Garage", "19": "Rental Storage Facility",
    "20": "Residence/Home", "21": "Restaurant", "22": "School/College",
    "23": "Service/Gas Station", "24": "Specialty Store",
    "25": "Other/Unknown", "26": "Community Center", "27": "Cyberspace",
    "88": "Unknown"
}
OFFENSE = {
    "01": "Murder and Nonnegligent Manslaughter",
    "02": "Rape", "03": "Robbery", "04": "Aggravated Assault",
    "05": "Burglary/Breaking & Entering", "06": "Larceny-Theft",
    "07": "Motor Vehicle Theft", "08": "Arson",
    "09": "Simple Assault", "10": "Intimidation",
    "11": "Destruction/Damage/Vandalism of Property",
    "12": "Human Trafficking, Commercial Sex Acts",
    "13": "Human Trafficking, Involuntary Servitude",
    "88": "Unknown"
}
VICTIM_TYPE = {
    "I": "Individual", "B": "Business/Financial Institution",
    "G": "Government", "R": "Religious Organization",
    "S": "Society/Public", "O": "Other", "U": "Unknown"
}
OFFENDER_RACE = {
    "W": "White", "B": "Black or African American",
    "I": "American Indian or Alaska Native", "A": "Asian",
    "P": "Native Hawaiian or Other Pacific Islander",
    "M": "Multiple", "U": "Unknown"
}

# ----------------------------------------------------------------------
# 3. Safe decode helper
# ----------------------------------------------------------------------
def decode(dct, code, blank="Unknown"):
    s = code.strip()
    return dct.get(s, blank) if s else blank

# ----------------------------------------------------------------------
# 4. Open the 4 output files
# ----------------------------------------------------------------------
with (
    BH_RAW_OUT.open("w", newline="", encoding="utf-8") as bh_raw_f,
    IR_RAW_OUT.open("w", newline="", encoding="utf-8") as ir_raw_f,
    BH_DEC_OUT.open("w", newline="", encoding="utf-8") as bh_dec_f,
    IR_DEC_OUT.open("w", newline="", encoding="utf-8") as ir_dec_f
):

    bh_raw = csv.writer(bh_raw_f)
    ir_raw = csv.writer(ir_raw_f)
    bh_dec = csv.writer(bh_dec_f)
    ir_dec = csv.writer(ir_dec_f)

    # ----- headers (raw) -----
    bh_raw.writerow([
        "year","record_type","state","ori","agency_name",
        "agency_type","population_group","country_division",
        "population","agency_status","covered_by_ori",
        "fbi_field_office","judicial_district"
    ])
    ir_raw.writerow([
        "year","record_type","incident_id","ori","incident_date",
        "total_victims","total_offenses",
        "bias_1","bias_2","bias_3","bias_4","bias_5",
        "location","offense","victim_type","offender_race","offender_ethnicity"
    ])

    # ----- headers (decoded) -----
    bh_dec.writerow([
        "year","record_type","state","ori","agency_name",
        "agency_type","population_group","country_division",
        "population","agency_status","covered_by_ori",
        "fbi_field_office","judicial_district"
    ])
    ir_dec.writerow([
        "year","record_type","incident_id","ori","incident_date",
        "total_victims","total_offenses",
        "bias_1","bias_2","bias_3","bias_4","bias_5",
        "location","offense","victim_type","offender_race","offender_ethnicity"
    ])

    # ------------------------------------------------------------------
    # 5. Process each yearly file
    # ------------------------------------------------------------------
    processed = 0
    for fp, yr in zip(INPUT_FILES, YEARS):
        if not fp.exists():
            print(f"[WARN] {fp.name} not found – skipping")
            continue

        print(f"[INFO] Reading {fp.name}")
        with fp.open("r", encoding="utf-8", errors="ignore") as src:
            for raw in src:
                line = raw.rstrip("\n")
                if len(line) < 200:          # malformed line guard
                    continue

                rtype = line[0:2]

                # ------------------- BH -------------------
                if rtype == "BH":
                    # raw
                    bh_raw.writerow([
                        yr, rtype,
                        line[2:4].strip(), line[4:13].strip(), line[13:38].strip(),
                        line[38:39].strip(), line[39:41].strip(), line[41:43].strip(),
                        line[43:52].strip(), line[52:53].strip(),
                        line[53:62].strip(), line[62:64].strip(), line[64:67].strip()
                    ])
                    # decoded
                    bh_dec.writerow([
                        yr, rtype,
                        line[2:4].strip() or "Unknown",
                        line[4:13].strip() or "Unknown",
                        line[13:38].strip() or "Unknown",
                        decode(AGENCY_TYPE, line[38:39]),
                        decode(POP_GROUP, line[39:41]),
                        line[41:43].strip() or "Unknown",
                        line[43:52].strip() or "0",
                        line[52:53].strip() or "Unknown",
                        line[53:62].strip() or "None",
                        line[62:64].strip() or "Unknown",
                        line[64:67].strip() or "Unknown"
                    ])

                # ------------------- IR -------------------
                elif rtype == "IR":
                    # raw
                    ir_raw.writerow([
                        yr, rtype,
                        line[2:14].strip(), line[14:23].strip(), line[23:31].strip(),
                        line[31:33].strip(), line[33:35].strip(),
                        line[35:37].strip(), line[37:39].strip(), line[39:41].strip(),
                        line[41:43].strip(), line[43:45].strip(),
                        line[45:47].strip(), line[47:49].strip(),
                        line[49:50].strip(), line[50:51].strip(), line[51:52].strip()
                    ])
                    # decoded
                    ir_dec.writerow([
                        yr, rtype,
                        line[2:14].strip() or "Unknown",
                        line[14:23].strip() or "Unknown",
                        line[23:31].strip() or "Unknown",
                        line[31:33].strip() or "0",
                        line[33:35].strip() or "0",
                        decode(BIAS, line[35:37]),
                        decode(BIAS, line[37:39]),
                        decode(BIAS, line[39:41]),
                        decode(BIAS, line[41:43]),
                        decode(BIAS, line[43:45]),
                        decode(LOCATION, line[45:47]),
                        decode(OFFENSE, line[47:49]),
                        decode(VICTIM_TYPE, line[49:50]),
                        decode(OFFENDER_RACE, line[50:51]),
                        line[51:52].strip() or "Unknown"
                    ])

        processed += 1

    print(f"\nFinished! Processed {processed} file(s).")
    print(f"   → {BH_RAW_OUT.name}")
    print(f"   → {IR_RAW_OUT.name}")
    print(f"   → {BH_DEC_OUT.name}")
    print(f"   → {IR_DEC_OUT.name}")