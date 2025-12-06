# Column Dictionary

| column_name | type | description | origin |
| --- | --- | --- | --- |
| `tis_number` | string | Official Thai Industrial Standards (TIS) identifier. | Original |
| `tis_name_th` | string | TIS standard name in Thai. | Original |
| `snapshot_date` | date (YYYY-MM-DD) | Month represented by the snapshot (first day of month). | Derived |
| `num_manufacturing_licenses` | integer | Count of manufacturing licenses granted for the TIS standard. | Original |
| `num_manufacturing_entrepreneurs` | integer | Number of entrepreneurs holding manufacturing licenses. | Original |
| `num_import_licenses` | integer | Count of import licenses granted for the TIS standard. | Original |
| `num_import_entrepreneurs` | integer | Number of entrepreneurs holding import licenses. | Original |
| `num_display_licenses` | integer | Count of display/showroom licenses granted for the TIS standard. | Original |
| `num_display_entrepreneurs` | integer | Number of entrepreneurs holding display/showroom licenses. | Original |
| `total_licenses` | integer | Total licenses for the standard (manufacturing + import + display). | Original / Derived (filled when missing) |
| `num_total_entrepreneurs` | integer | Sum of manufacturing, import, and display entrepreneurs. | Derived |
| `import_to_manufacturing_ratio` | float | Ratio of import licenses to manufacturing licenses (stabilized with 1e-6). | Derived |
| `import_dependency_ratio` | float | Share of import licenses vs. import + manufacturing licenses. | Derived |
| `domestic_share_ratio` | float | Share of manufacturing licenses vs. import + manufacturing licenses. | Derived |
| `display_to_total_ratio` | float | Share of display licenses relative to all licenses. | Derived |
| `num_manufacturing_licenses_diff` | integer | Month-over-month change in manufacturing licenses. | Derived (trends dataset) |
| `num_manufacturing_licenses_pct_change` | float | Percentage change in manufacturing licenses vs. prior month. | Derived (trends dataset) |
| `num_import_licenses_diff` | integer | Month-over-month change in import licenses. | Derived (trends dataset) |
| `num_import_licenses_pct_change` | float | Percentage change in import licenses vs. prior month. | Derived (trends dataset) |
| `num_display_licenses_diff` | integer | Month-over-month change in display licenses. | Derived (trends dataset) |
| `num_display_licenses_pct_change` | float | Percentage change in display licenses vs. prior month. | Derived (trends dataset) |
| `total_licenses_diff` | integer | Month-over-month change in total licenses. | Derived (trends dataset) |
| `total_licenses_pct_change` | float | Percentage change in total licenses vs. prior month. | Derived (trends dataset) |
| `entrepreneur_risk_raw` | float | Raw inverse of total entrepreneurs (1 / (num_total_entrepreneurs + 1)). | Derived (risk dataset) |
| `entrepreneur_risk_norm` | float | Min-max normalized entrepreneur risk indicator. | Derived (risk dataset) |
| `import_dependency_norm` | float | Min-max normalized import dependency ratio. | Derived (risk dataset) |
| `risk_score` | float | Composite risk score (50% entrepreneur + 50% import dependency). | Derived (risk dataset) |
| `risk_label` | string | Categorized risk level: `high`, `medium`, or `low`. | Derived (risk dataset) |

> Columns appear across multiple CSV files in `datasets/`. Refer to `docs/README.md` for file-level descriptions.
