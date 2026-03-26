#  MD-SOAR Monthly Statistics Pipeline

This repository contains a Python-based pipeline for generating **monthly usage statistics** for MD-SOAR. It processes raw analytics reports, enriches them with repository metadata, and produces structured outputs for reporting.

---

##  Overview

The pipeline automates the end-to-end workflow for monthly statistics generation:

1. **Preprocess raw analytics data**
2. **Collect unique repository handles from Solr**
3. **Generate page view statistics**
4. **Generate download statistics**

All steps are orchestrated through a single entry script.

---

##  Project Structure

```
mdsoar_stats_pipeline/
│
├── RunMonthlyStatsPipeline.py   # Main pipeline orchestrator
├── Preprocessing.py             # Cleans raw analytics CSV
├── CollectUniqueHandles.py      # Retrieves handles from Solr
├── PageViewStats.py             # Computes page view statistics
├── DownloadStats.py             # Handles download stats (placeholder/partial)
├── campusuuidlist.csv           # Campus UUID → name mapping
├── requirements.txt             # Python dependencies
└── .gitignore
```

---

##  Requirements

- Python 3.8+
- Access to Solr instance (for handle collection)
- Required Python packages:

```
pip install -r requirements.txt
```

---

##  Usage

Apply the port-forwarding for Solr:

```
kubectl port-forward mdsoar-solr-0 8983:8983
```

In a separate tab run the full monthly pipeline:

```
python3 RunMonthlyStatsPipeline.py <input_csv> <campus_csv> <start_date> <end_date> --label <LABEL>
```

### Example

(report_February_2026.csv is the Google Analytics generated csv file.)

```
python3 RunMonthlyStatsPipeline.py \
  report_February_2026.csv \
  campusuuidlist.csv \
  "2026-02-01T00:00:00Z" \
  "2026-02-28T23:59:59Z" \
  --label "February_2026"
```

---

##  Pipeline Steps

### 1. Preprocessing
- Removes unnecessary header lines from raw analytics reports
- Outputs a clean CSV for downstream processing

### 2. Collect Unique Handles
- Queries Solr to retrieve all repository item handles
- Deduplicates results

### 3. Page View Statistics
- Matches analytics data with repository items
- Aggregates views by campus and item

### 4. Download Statistics
- Placeholder for download metrics (currently minimal implementation)

---

##  Output

The pipeline generates output under:

```
Monthy_Stats_Report/
├── PageView_Statistics/
│   └── <LABEL>_PageView.csv
└── Download_Statistics/
```

---

##  Key Features

- Modular pipeline design
- Handles large datasets (supports chunked processing)
- Integrates analytics data with repository metadata
- Easily extensible for additional metrics

---

##  Notes

- Ensure the input CSV format matches expected analytics export structure
- The script assumes a working Solr endpoint for handle retrieval

---


