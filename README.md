# 📘 **Hate Crime Data Preparation, Enrichment, and Visualization (2021–2024)**
*A complete data engineering + storytelling pipeline for the US Hate Crime Database*

---

## 📌 **Project Overview**

This project transforms raw U.S. hate crime data (2021–2024) into a clean, enriched, analysis-ready dataset, and produces visual storytelling insights.  
It was created as the final project for **Data Preparation & Visualization**, focusing on:

- Large-scale data cleaning  
- Feature extraction & validation  
- Data enrichment with external population data  
- Offense-level unpivoting  
- Exploratory visualization & storytelling  

The final processed outputs are stored as **Parquet** files for efficient loading.

---

## 🗂️ **Project Structure**

```
DPNV_GROUP5_DSEB/
│
├── data/
│   ├── raw/                    # Original FBI NIBRS Hate Crime Master Files
│   ├── interim/                # Decoded intermediate parquet files
│   ├── processed/              # Final cleaned & enriched datasets
│   └── external_data/          # State & territory population datasets for enrichment
│
├── docs/
│   └── data_documentation/     # Definitions, metadata
│
├── images/                 # Final visualizations
│   ├── images_before/      # Pre-cleaning diagnostic visuals
│   └── story_telling/      # Final charts used in storytelling
│
├── notebooks/
│   ├── raw_data_eda.ipynb           # Exploratory data analysis
│   └── storytelling.ipynb           # Final storytelling notebook
│
├── src/
│   ├── load_data.py            # Load raw master files
│   ├── decode.py               # Decode FBI fields
│   ├── clean_transform.py      # Main cleaning framework
│   ├── enrich.py               # Adds state/territory population data
│   ├── main.py                 # Full pipeline execution script
│   └── visualize.py            # Helper functions for plots
│
├── README.md
└── requirements.txt
```

---

## 🔧 **Pipeline Steps**

### **1️⃣ Load Raw Master Files**
`load_data.py` reads the raw hate crime master files (2021–2024) and prepares them for decoding.

---

### **2️⃣ Decode Raw Columns**
`decode.py` translates encoded FBI fields into readable values using the official NIBRS code tables.

Outputs stored in `data/interim/`:

- `bh_decoded.parquet`
- `ir_decoded.parquet`

---

### **3️⃣ Clean & Transform**
`clean_transform.py` performs the heavy lifting:

✔ Convert datetime columns properly <br>
✔ Convert numeric columns properly <br>
✔ Handle missing bias/ethnicity/race <br>
✔ Drop irrelevant columns  <br>
✔ Fix inconsistent values <br>
✔ Derive temporal features  <br>
✔ Create severity for each offense  <br>
✔ Merge Incident Reports (IR) with Batch Headers (BH) 
✔ Unpivot offenses: incident_level → offense-level dataset<br>
✔ Save clean output → `data/processed/hatecrimes_clean.parquet`

---

### **4️⃣ Enrich with Population Data**
`enrich.py` merges:

- **State population** (from 2021–2024 Excel)
- **US Territories population** (from digitized documents)

Adds:

- `state_population`

Final file:  
`data/processed/hatecrimes_enriched.parquet`

---

## 📊 **Storytelling & Visualization**

The storytelling notebook (`notebooks/storytelling.ipynb`) includes:

- Top offenses (count + percentage)  
- State & regional distribution  
- Bias category dominance by region (with special handling for U.S. possessions)  
- Temporal trends  
- Agency reporting patterns  
- Victim/offender ratio distributions  
- Population-adjusted hate crime rates  

All final visualizations are stored in:

```
docs/images/story_telling/
```

---

## ▶️ **How to Run the Pipeline**

Run entire pipeline:

```bash
python src/main.py
```

Or run modules individually:

```bash
python src/load_data.py
python src/decode.py
python src/clean_transform.py
python src/enrich.py
```

---

## 📦 **Dependencies**

```
pandas
numpy
pyarrow
matplotlib
seaborn
plotly
```

Install:

```bash
pip install -r requirements.txt
```

---

## 📁 **Data Sources**

- FBI Hate Crime Master Files (2021–2024) — NIBRS dataset  
- State population Excel (2021–2024)  
- U.S. Territories population (2021-2024)

---

## 🏁 **Status**

✔ Data fully cleaned and validated  
✔ Enriched dataset completed  
✔ Visual storytelling completed 
✔ Ready for presentation & GitHub submission  
