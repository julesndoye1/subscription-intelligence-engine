# Subscription Intelligence Agent

## Overview

Subscription Intelligence Agent is an AI-powered analytics platform that helps fintechs automatically identify recurring subscription payments from Visa transaction history.

The application detects recurring merchants, predicts the next renewal date, estimates recurring spend, and prepares the platform for real-time webhook integration with Onafriq Visa.

The current version analyzes uploaded Visa transaction reports in Excel format.

---

# Features

## Current Version

- Upload Visa transaction report
- Merchant normalization
- Recurring subscription detection
- Renewal prediction
- Executive dashboard
- Customer subscription listing
- CSV export

---

# Future Versions

- NSF Risk Prediction
- Subscription Health Score
- Renewal Notifications
- Push Notifications
- Onafriq Webhook Integration
- AI Merchant Classification
- AI Renewal Forecasting

---

# Technology Stack

| Component | Technology |
|------------|------------|
| Language | Python 3.12+ |
| Framework | Streamlit |
| Data Processing | Pandas |
| Excel Support | OpenPyXL |
| Merchant Database | CSV |
| Charts | Streamlit Native |
| Testing | Pytest |

---

# Project Structure

```text
subscription-agent/

README.md
requirements.txt
app.py

core/
    __init__.py
    loader.py
    merchant.py
    detector.py
    predictor.py
    dashboard.py

data/
    merchant_database.csv

assets/
    logo.png

tests/
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/your-company/subscription-agent.git

cd subscription-agent
```

---

## Create Virtual Environment

Mac/Linux

```bash
python3 -m venv venv

source venv/bin/activate
```

Windows

```cmd
python -m venv venv

venv\Scripts\activate
```

---

## Install Packages

```bash
pip install -r requirements.txt
```

---

# Run

```bash
streamlit run app.py
```

---

# Workflow

```text
Visa Transaction Report
            │
            ▼
      Load Transactions
            │
            ▼
    Merchant Normalization
            │
            ▼
 Subscription Detection
            │
            ▼
  Renewal Prediction
            │
            ▼
 Executive Dashboard
            │
            ▼
 Export Results
```

---

# Merchant Intelligence

The application automatically recognizes recurring merchants such as:

- Netflix
- Spotify
- Apple
- Google
- Amazon Prime
- Adobe
- Microsoft
- OpenAI
- Canva
- Zoom
- LinkedIn

Merchant information is stored in

```text
data/merchant_database.csv
```

---

# Subscription Detection

The detection engine evaluates:

- Merchant
- Billing interval
- Amount consistency
- Number of occurrences
- Billing frequency

Each subscription receives a confidence score from **0–100**.

---

# Renewal Prediction

For every detected subscription the application predicts:

- Next charge date
- Days until renewal
- Monthly spend
- Annual spend
- Renewal status

Possible statuses

- Upcoming
- Due Soon
- Overdue

---

# Dashboard

The dashboard displays

- Total subscriptions
- Monthly spend
- Annual spend
- Spend by merchant
- Spend by category
- Upcoming renewals
- Customer subscriptions

---

# Roadmap

## Version 1.0

- Excel Upload
- Merchant Intelligence
- Subscription Detection
- Renewal Prediction
- Dashboard

## Version 2.0

- NSF Detection
- Subscription Health Score
- Balance Forecast
- Notifications

## Version 3.0

- Onafriq Integration
- Visa Webhooks
- Event Processing

## Version 4.0

- AI Merchant Recognition
- AI Prediction
- AI Customer Insights

---

# License

Copyright © 2026

Subscription Intelligence Agent

All rights reserved