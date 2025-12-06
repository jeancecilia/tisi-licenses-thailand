# Thai Industrial Standards Licenses (TISI) – 2024–2025

## Summary
Monthly disclosures from the Thai Industrial Standards Institute (TISI) detail how many licenses exist for each Thai Industrial Standard (TIS) across manufacturing, import, and display activities. This repository merges all official CSV snapshots (February 2024 onwards), standardizes the schema, and produces multiple value-added datasets suitable for Kaggle, HuggingFace, or other open-data hubs.

## Long description
The TISI licensing registry tracks the number of certified entrepreneurs and licenses for each industrial standard. Because TISI publishes new CSVs every month, analysts must merge files, align column names, and engineer features by hand. This project automates that pipeline, providing:

- A clean panel dataset with every standard × month record
- Trend tables capturing month-over-month deltas
- Import dependency views highlighting foreign exposure
- A lightweight risk index combining entrepreneur concentration and import reliance
- A latest-month snapshot for quick reporting

Each dataset is generated from public TISI CSVs and is licensed under CC BY 4.0, enabling reuse with attribution.

## Data source
- **Organization:** Thai Industrial Standards Institute (TISI)
- **URL:** <https://www.tisi.go.th/>
- **License:** Creative Commons Attribution 4.0 (CC BY 4.0)

## Files
| File | Key columns |
| --- | --- |
| `tisi_licenses_clean_2024_2025.csv` | `tis_number`, `tis_name_th`, `snapshot_date`, license counts, entrepreneur totals, ratio features |
| `tisi_trends_by_standard.csv` | clean columns + `_diff`, `_pct_change` fields for each license metric |
| `tisi_import_dependency.csv` | `tis_number`, `snapshot_date`, manufacturing/import counts, `import_dependency_ratio`, `domestic_share_ratio` |
| `tisi_risk_index.csv` | `tis_number`, `snapshot_date`, `num_total_entrepreneurs`, `import_dependency_ratio`, `risk_score`, `risk_label` |
| `tisi_latest_snapshot_summary.csv` | Latest month with all license counts, ratios, and risk scores |

## Example use cases
1. **Supply-chain monitoring:** Flag standards that are becoming import-heavy relative to domestic capacity.
2. **Market research:** Track licensing growth for sectors tied to specific TIS codes.
3. **Policy analysis:** Evaluate how regulatory changes affect entrepreneur counts month to month.
4. **Risk dashboards:** Combine the risk index with other macro indicators to monitor vulnerabilities.

## Research questions
1. Which standards exhibit the fastest growth in import dependency?
2. Are entrepreneur counts consolidating among a few actors or diversifying?
3. Does domestic licensing keep pace with total license issuance for strategic sectors?
4. How do month-over-month deltas correlate with macroeconomic indicators such as PMI or export volumes?

## Maintainer
Prepared by **Jean** — <https://example.com>. Feel free to update the backlink before publishing on Kaggle.
