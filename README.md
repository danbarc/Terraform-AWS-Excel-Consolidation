# Therm Tech - Excel Shipment Consolidation Tool

Internal tool developed for **Therm Tech** to consolidate multiple Excel files (.xlsx / .xltm) containing shipment and logistics data.

## Purpose

This application automates the consolidation of item shipment spreadsheets used by the **Logistics Department**, extracting key information such as:
- Customer / Work (Obra)
- Date
- Item codes and descriptions
- Quantities and units

The tool processes 100–200 files per run and generates a single unified Excel report (`rastreamento_codigos.xlsx`).

---

## Architecture

- **Frontend**: Static website hosted on Amazon S3
- **Backend**: 
  - API Gateway (HTTP)
  - Two AWS Lambda functions (Upload + Processing)
- **Storage**: Amazon S3 with automatic cleanup policies
- **Processing Engine**: Pandas + OpenPyXL via official AWS SDK for Pandas Layer

---

## Features

- Drag & drop or select multiple Excel files
- Automatic detection of "CLIENTE", "QTD.", "VOLUME", and dates
- Centralized modern and responsive interface
- Presigned download link for the consolidated file
- Automatic cleanup of old jobs (7 days for uploads, 30 days for outputs)

---

## How to Use

1. Access the internal tool:  
   **→ [Frontend URL]** (provided after deployment)

2. Upload your Excel shipment files
3. Click **"Process All"**
4. Download the consolidated report

---

## How to Deploy

# 1. Initialize
terraform init

# 2. Review changes
terraform plan

# 3. Deploy
terraform apply

## Main Outputs

- **frontend_url** → Public URL of the web interface
- **api_endpoint** → API Gateway endpoint
- **s3_bucket_data** → Bucket for uploaded files and results

## Project Structure

```bash
Terraform-AWS-Excel-Consolidation/
├── frontend/              # Static HTML + Tailwind UI
├── lambda/
│   ├── upload/            # File upload Lambda
│   └── process/           # Main consolidation logic
├── *.tf                   # Terraform configuration files
└── README.md

```
## Technologies

- Terraform (IaC)
- AWS Lambda + API Gateway
- Amazon S3
- Python 3.11 + Pandas
- Tailwind CSS

## Developed for
**Therm Tech**
Logistics Department
Shipment and Item Tracking Consolidation