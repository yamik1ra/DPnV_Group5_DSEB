# 📘 Hate Crime Data Preparation & Storytelling (2021–2024)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

*A complete ETL, data cleaning, enrichment, visualization, and machine learning workflow built using the FBI Hate Crime Master Files.*

---

## 🔗 Table of Contents

* [Project Overview](#project-overview)
* [Dataset Description](#dataset-description)
* [Feature Description](#feature-description)
* [Project Structure](#project-structure)
* [Pipeline Overview](#pipeline-overview)

  * [Load Raw Data](#1️⃣-load-raw-data--srcload_datapy)
  * [Decode Fields](#2️⃣-decode-fields--srcdecodepy)
  * [Clean and Transform](#3️⃣-clean--transform--srcclean_transformpy)
  * [Enrich Population Data](#4️⃣-enrich-population-data--srcenrichpy)
  * [Visualization Module](#5️⃣-visualizations--srcvisualizepy)
  * [Run Pipeline](#6️⃣-run-full-pipeline--srcmainpy)
* [Storytelling & Visualizations](#storytelling--visualizations)
* [Machine Learning Component](#machine-learning-component)
* [How to Run](#how-to-run-the-project)
* [Requirements](#requirements)
* [Authors](#authors)

---

# 📌 Project Overview

This project demonstrates the **importance of Data Preparation** by transforming raw FBI Hate Crime Master Files into a clean, enriched, offense-level dataset used for visualization and machine learning storytelling.

It fulfills the course requirement:

> ✔ “Use data storytelling to show how data preparation affects insights and model performance.”

---

# 📂 Dataset Description

### Raw Data (FBI Hate Crime Master Files)

* Format: **fixed-width text**
* Two hierarchical data structures:

  * **BH – Batch Header** (state, agency, reporting metadata)
  * **IR – Incident Report** (victims, offenders, bias motivations, offenses)
* Up to **10 offenses per incident**

### External Data

Stored under `data/external_data/`:

* `state_population_21-24.xlsx`
* `territories_population_21-24.csv`

### Processed Outputs

Located in `data/processed/`:

* `bh_decoded.parquet`
* `ir_decoded.parquet`
* `hatecrimes_clean.parquet`
* `hatecrimes_enriched.parquet`

---

# 📑 Feature Description

### **Core Incident Features**

| Feature                     | Description                               |
| --------------------------- | ----------------------------------------- |
| `ori`                       | ORI code identifying the reporting agency |
| `incident_number`           | Unique incident ID                        |
| `incident_date`             | Date of the incident                      |
| `year`, `quarter`, `month`  | Extracted temporal dimensions             |
| `day_of_week`, `is_weekend` | Derived time-based features               |

### **Victim & Offender Features**

| Feature                                         | Description                             |
| ----------------------------------------------- | --------------------------------------- |
| `total_victims`                                 | Total number of victims in the incident |
| `num_adult_victims`, `num_juvenile_victims`     | Age-based victim counts                 |
| `total_offenders`                               | Total number of offenders               |
| `num_adult_offenders`, `num_juvenile_offenders` | Age-based offender counts               |
| `victim_offender_ratio`                         | Victims divided by offenders            |

### **Offense-Level Features** *(after unpivot)*

Each offense becomes its own row.

| Feature                            | Description                                    |
| ---------------------------------- | ---------------------------------------------- |
| `offense_type`                     | FBI NIBRS offense description                  |
| `offense_severity`                 | Derived categorical severity (low/medium/high) |
| `location`                         | Crime location category                        |
| `num_victims`                      | Victims related to this specific offense       |
| `bias_motivation`, `bias_category` | Bias motivation applied to this offense        |

### **Demographic & Geography**

| Feature              | Description                           |
| -------------------- | ------------------------------------- |
| `offender_race`      | Race of offender                      |
| `offender_ethnicity` | Ethnicity of offender                 |
| `state_name`         | Full state name                       |
| `state_population`   | Population of that state in that year |
| `city_name`          | City of reporting agency              |

### **Agency & Metadata**

| Feature                              | Description                          |
| ------------------------------------ | ------------------------------------ |
| `agency_name`                        | Reporting agency                     |
| `agency_type`                        | Municipal / State / Tribal / Federal |
| `population_group`                   | FBI population grouping              |
| `country_division`, `country_region` | U.S. Census region                   |
| `bh_index`                           | Batch header index used for merging  |

---

# 🗂️ Project Structure

```
DPNV_GROUP5_DSEB/
│
├── data/
│   ├── raw/                        # Raw FBI Hate Crime Master Files (2021–2024)
│   ├── interim/                    # Decoded (BH/IR) parquet files
│   ├── processed/                  # Cleaned + enriched final datasets
│   └── external_data/              # Population datasets
│
├── docs/
│   └── data_documentation/         # Codebooks & reference files
│
├── images/
│   ├── images_before/              # Dirty-data visual diagnostics
│   └── story_telling/              # Final figures used in presentation
│
├── notebooks/
│   ├── raw_data_diagnosis.ipynb    # Pre-cleaning exploration
│   └── storytelling.ipynb          # Storytelling & visualization
│
├── src/
│   ├── load_data.py                # Load fixed-width text master files
│   ├── decode.py                   # Decode categorical fields using NIBRS code tables
│   ├── clean_transform.py          # Main cleaning, validation, unpivot transformation
│   ├── enrich.py                   # Add state/territory population
│   ├── visualize.py                # Chart helper functions
│   └── main.py                     # Full ETL pipeline orchestrator
│
├── requirements.txt
└── README.md

```

---

# 🔧 Pipeline Overview

## **1️⃣ Load Raw Data** — [`src/load_data.py`](src/load_data.py)

Reads fixed-width text files and extracts BH / IR blocks.

---

## **2️⃣ Decode Fields** — [`src/decode.py`](src/decode.py)

Applies FBI code tables to convert codes into human-readable values.

---

## **3️⃣ Clean & Transform** — [`src/clean_transform.py`](src/clean_transform.py)

Key steps include:

* Standardize dates & numeric types
* Clean missing values
* Check data consistency
* Add engineered features
* Remove unused offense slots
* Merge incidents with batch headers
* **Unpivot incidents → offense-level rows**

Output: `hatecrimes_clean.parquet`

---

## **4️⃣ Enrich Population Data** — [`src/enrich.py`](src/enrich.py)

Adds:

* State population (2021–2024)
* Territory population (AS, GU, MP, PR, VI) (2021-2024)

Output: `hatecrimes_enriched.parquet`

---

## **5️⃣ Visualizations** — [`src/visualize.py`](src/visualize.py)

Helper functions for:

* Timeline analysis
* Offense analysis 
* Bias motivation and categories analysis 
* Geography analysis 
* Offender demographics
---

## **6️⃣ Run Full Pipeline** — [`src/main.py`](src/main.py)

```bash
python src/main.py
```

---

# 📊 Storytelling & Visualizations

**Notebook:** <br>
👉 `notebooks/storytelling.ipynb`

**Includes:** <br>
👉 A comprehensive, narrative-driven analysis of FBI Hate Crime Statistics (2021-2024), structured around a **"What? So What? Now What?"** framework to transform over 40,000 raw records into actionable intelligence:

- **Part I: Data Quality Assessment:** Visualizes the critical transformation from raw to clean data, demonstrating how completeness was improved from ~60% to >95% through standardization and validation.

- **Part II: Contextual Analysis ("WHAT"):** Establishes the factual landscape using year-over-year trends and geographic patterns, highlighting the crucial difference between raw incident counts and population-adjusted rates (per 100k).

- **Part III: Impact Assessment ("SO WHAT"):** Analyzes the complexity of hate crimes, including offense severity, the rise of specific bias motivations (e.g., Anti-Asian trends), and location risk assessments.

- **Part IV: Strategic Action ("NOW WHAT"):** Translates insights into concrete strategies, such as optimizing resource deployment based on temporal patterns (seasonal/weekday) and targeting interventions based on offender demographics.

- **Technical Implementation:** Utilizes Pandas for data manipulation and a mix of Matplotlib, Seaborn, and Plotly to create interactive maps, heatmaps, and trend lines.

---

# 🤖 Machine Learning Component

**Notebook:** <br>
👉 `notebooks/model_comparison.ipynb`

**Objective:** <br>
👉 Predict whether an offense is motivated by **Race/Ethnicity Bias (1)** versus **Non-Race Bias (0)**.

**The Experiment:** <br>
👉 We conducted a head-to-head comparison to quantify the impact of our data cleaning pipeline:

1. **Baseline (Dirty Model):** Trained on raw, incident-level data with missing values and no feature engineering using Logistic Regression.
2. **Final (Clean Model):** Trained on processed, offense-level data enriched with population metrics using a Random Forest Classifier.


**Key Results:** Data cleaning did not just improve accuracy; it prevented total model failure.

| **Metric**          | **Dirty Model** | **Clean Model** | **Impact** |
|---------------------|-----------------|------------------|------------|
| Accuracy            | 0.56            | 0.65             | +9% improvement in overall correctness |
| Macro F1-Score      | 0.36            | 0.62             | +26 points indicating more balanced learning |
| Class 0 Precision   | 0.00            | 0.67             | Fixed “model collapse” — dirty model failed to identify any Class 0 instances |
| ROC AU   | 0.45  | 0.69  | Clean model can actually rank classes correctly |
| PR AU    | 0.53  | 0.72  | Big improvement in precision-recall tradeoff |


**Critical Insight:** The "Dirty" model suffered from **model collapse**, predicting the majority class (Class 1) for every single instance. The data cleaning and unpivoting process recovered the signal necessary for the model to distinguish between bias types effectively.

---

# ▶️ How to Run the Project

### 1. Clone

```bash
git clone <your_repo_url>
cd project
```

### 2. Install requirements

```bash
pip install -r requirements.txt
```

### 3. Run ETL Pipeline

```bash
python src/main.py
```

### 4. View Processed Outputs

Located in: `data/processed/`

---

# 🧪 Requirements

```
pandas
numpy
matplotlib
seaborn
plotly
pyarrow
scikit-learn
```
---

## 📁 **Data Sources**

- FBI Hate Crime Master Files (2021–2024) — NIBRS dataset  
- State population (2021–2024) - U.S. Census Bureau, Population Division
- U.S. Territories population (2021-2024)

---

# 👥 Authors

**Group 5 – Data Preparation & Visualization**
| ID  | Name                | Contribution (%) |
|-----|---------------------|------------------|
| 11230527  | Đỗ Tuấn Đạt          | 22%       |
| 11230531  | Trần Minh Đức        | 18%       |
| 11230552  | Đỗ Hữu Kiên          | 20%       |
| 11230577  | Tô Bích Ngọc         | 22%       |
| 11230580  | Nguyễn Tuấn Phong    | 18%       |

---
