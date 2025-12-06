# Thai Industrial Standards Licenses (TISI) – 2025 Dataset  
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17836099.svg)](https://doi.org/10.5281/zenodo.17836099)

🔗 **Official Dataset Landing Page (Canonical URL):**  
https://appdevbangkok.com/tisi-thai-industrial-licenses-dataset-2025-free-open-data-download

This repository provides a fully reproducible data pipeline and enriched dataset based on publicly available licensing information from the **Thai Industrial Standards Institute (TISI)**.  
It includes **cleaned monthly snapshots**, **derived analytics**, and **Kaggle-ready datasets**, along with the complete Python ETL workflow.

This dataset is valuable for analysts, researchers, policymakers, and data scientists studying:

- Industrial regulation & compliance in Thailand  
- Import dependency and market structure  
- Domestic vs. imported production dynamics  
- Supply chain and industrial risk assessment  
- Sector-level industrial trends over time  

---

## 📊 Dataset Overview

The dataset contains key counts, trends, and computed ratios for each TIS (Thai Industrial Standard), including:

- **Manufacturing licenses**  
- **Import licenses**  
- **Standard mark display licenses**  
- **Entrepreneurs per license type**  
- **Total licenses**  
- **Import dependency ratio**  
- **Domestic production share**  
- **Industrial risk index (0–100)**  
- **Snapshot date (monthly)**  

Raw data originates from the official TISI open-data portal and is licensed under **CC BY**.

---

## 📁 Repository Structure

```
tisi-licenses-thailand/
│
├── data/
│   ├── raw/              # Raw monthly CSVs (user-provided)
│   └── processed/        # Output of merge_raw.py
│
├── datasets/             # Final enriched datasets (Kaggle-ready)
│   ├── tisi_licenses_clean_2024_2025.csv
│   ├── tisi_import_dependency.csv
│   ├── tisi_risk_index.csv
│   ├── tisi_latest_snapshot_summary.csv
│   └── tisi_trends_by_standard.csv
│
├── scripts/
│   ├── merge_raw.py      # Standardizes and merges raw CSVs
│   └── build_features.py # Computes derived features and exports datasets
│
└── docs/
    ├── README.md
    ├── COLUMN_DICTIONARY.md
    └── KAGGLE_DESCRIPTION.md
```

---

## ⚙️ ETL Pipeline

### **1️⃣ merge_raw.py**
- Reads all CSVs from `data/raw/`  
- Detects Thai encoding (`cp874` / `tis-620`)  
- Maps Thai → English column names  
- Extracts `snapshot_date` from filenames (`tis_YYYY_MM.csv`)  
- Normalizes, deduplicates, and sorts records  
- Outputs: `data/processed/tisi_licenses_merged.csv`

Run:

```bash
python scripts/merge_raw.py
```

### **2️⃣ build_features.py**
Computes:

- Total entrepreneurs  
- Import/manufacturing ratios  
- Domestic vs. import share  
- Risk index (0–100)  
- Month-over-month trends  
- Latest snapshot summary  

Run:

```bash
python scripts/build_features.py
```

Outputs saved in `datasets/`.

---

## 🔗 Important Links

- **📌 Canonical Dataset Page (Backlink Target):**  
  https://appdevbangkok.com/tisi-thai-industrial-licenses-dataset-2025-free-open-data-download
- **📚 Zenodo (Citable DOI):**  
  https://doi.org/10.5281/zenodo.17836099
- **🧑‍💻 GitHub Repository:**  
  https://github.com/jeancecilia/tisi-licenses-thailand
- **🏛 Official Source (TISI):**  
  https://appdb.tisi.go.th/tis_dev/p4_license_report/p4license_report.php

---

## 📚 Citation

If you use this dataset, please cite:

```
@dataset{cecilia-menzel_2025_tisi,
  author       = {Jean-Maurice Cecilia-Menzel},
  title        = {Thai Industrial Standards Licenses (TISI) – 2025 Dataset},
  year         = {2025},
  publisher    = {Zenodo},
  version      = {1.0.0},
  doi          = {10.5281/zenodo.17836099},
  url          = {https://doi.org/10.5281/zenodo.17836099}
}
```

---

## 👤 Maintainer

**Jean-Maurice Cecilia-Menzel**  
Data Engineering • AI • Mobile & Cloud Systems  
🔗 Website: https://appdevbangkok.com  
🔗 Dataset Page: https://appdevbangkok.com/tisi-thai-industrial-licenses-dataset-2025-free-open-data-download  
For inquiries or collaboration, open an issue or reach out via the website.

---

## 📝 License

- **Repository code:** MIT License  
- **Underlying TISI data:** Creative Commons Attribution (CC BY)
