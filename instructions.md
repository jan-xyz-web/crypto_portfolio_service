# 💼 Crypto Portfolio & Price Alerts Service (CoinGecko, EUR)

## 🎯 Project Purpose
Build a FastAPI backend that fetches cryptocurrency prices from **CoinGecko**, stores data in **SQLite**, manages portfolio holdings, evaluates alerts, and exposes clean API endpoints with exports.

This is a **learning-focused** project — Cursor acts as a **mentor**, not a coder.  
You implement everything yourself; Cursor provides structure, validation, and conceptual guidance.

---

## ⚙️ Tech Stack

- **Language:** Python 3.12+
- **Framework:** FastAPI + Uvicorn
- **Database:** SQLite + SQLAlchemy Core
- **Config:** Pydantic Settings (`.env`)
- **HTTP:** requests / httpx
- **Testing:** pytest
- **Deployment:** Hetzner VPS

---

## 🧠 Cursor’s Role

Cursor must:
- Provide **architectural guidance** (folders, modules, function outlines)
- Explain **concepts** when unclear, not write code
- Review structure and reasoning
- Ask diagnostic questions when issues appear
- Suggest test structure and validation ideas (no full implementations)

---

## 🗂️ Directory Structure (to start)

app/
├── db/
│ ├── schema.py
│ ├── operations.py
├── api/
│ ├── routes/
│ └── init.py
├── core/
│ ├── settings.py
│ ├── logging.py
├── main.py
├── ingest.py
tests/
.env.example
requirements.txt
README.md
PROJECT_GUIDE.md

---

## 🧩 Database Schema

| Table | Columns |
|-------|----------|
| **assets** | id, symbol, name |
| **prices** | asset_id, ts, price, mcap, vol |
| **holdings** | id, asset_id, amount, avg_buy_price, created_at |
| **alerts** | id, asset_id, type, op, threshold, active, last_fired_ts |

**Indexes**
- `prices(asset_id, ts)`
- `holdings(asset_id)`

**Constraints**
- Foreign key links
- Unique `(asset_id, ts)` in `prices`

---

## 🌍 Endpoints Overview

| Method | Endpoint | Description |
|--------|-----------|--------------|
| GET | `/assets` | List all assets |
| GET | `/prices/{asset_id}?limit=100` | Latest prices |
| GET | `/portfolio` | Portfolio snapshot |
| POST | `/holdings` | Add new holding |
| GET | `/alerts` | List alerts |
| POST | `/alerts` | Create alert |
| PATCH | `/alerts/{id}` | Toggle active |
| GET | `/export/prices/{asset_id}.csv` | CSV export |
| GET | `/export/portfolio.json` | JSON export |
| POST | `/ingest` | Trigger ingestion manually |

---

## 🧮 CLI Commands

```bash
python ingest.py --ids bitcoin,ethereum --once
python ingest.py --interval 300
⚙️ Example .env
bash
Code kopieren
ASSET_IDS=bitcoin,ethereum,solana
DB_PATH=app/db/data.db
INGEST_INTERVAL=300
✅ Acceptance Criteria
Works with ≥ 50 assets

No duplicate (asset_id, ts)

Portfolio and P/L calculations correct

Alerts fire + de-dupe correctly

Clean linting + tests pass

FastAPI endpoints respond under 200 ms (p95)

🪜 Development Roadmap (19 Steps)
🏗️ Create project structure, .env.example, requirements.txt, and README.md

🧱 Define SQLAlchemy Core tables in app/db/schema.py

⚙️ Implement upsert_assets, insert_prices, query helpers in operations.py

🧪 Write pytest tests for DB layer (PK constraints, idempotency)

🌐 Build CoinGecko API client (retry, normalization)

🧪 Write pytest tests for API client (mock, validation)

🚀 Create ingest.py CLI with --once / --interval, graceful shutdown

🔘 Add POST /ingest trigger endpoint

📊 Implement compute_portfolio_snapshot (P/L calc, rounding)

🧪 Write pytest tests for portfolio calculations

🚨 Implement alert evaluation, de-duplication, stdout logging

🧪 Write pytest tests for alerts (fire conditions, de-dupe)

🌍 Implement all FastAPI endpoints (assets, prices, portfolio, holdings, alerts)

🧪 Write pytest tests for all API endpoints

💾 Implement CSV + JSON exports with streaming

⚙️ Finalize Pydantic Settings + logging setup

🔍 Run manual test checklist

🧾 Complete README with setup, API examples, deployment guide

🧠 Run final acceptance checklist (≥ 50 assets, load test, lint check)

🧰 Additional Guidance for Cursor
You are a mentor guiding through each milestone, not a generator.
The user writes every implementation manually.
Cursor must:

Suggest file and function names

Explain design choices

Ensure logical structure and consistency

Avoid providing complete code

Support reasoning and debugging steps

🏁 Outcome
A functioning, tested, and deployed FastAPI backend service demonstrating mastery of:

Python backend design

SQLAlchemy Core and persistence logic

API and async I/O

Testing workflows

Real deployment on a VPS

After completion, the user will be capable of independently designing, implementing, and deploying production-style Python backends.

yaml
Code kopieren

---

✅ **Save as:** `PROJECT_GUIDE.md`  
✅ **Put in:** Workspace root (next to `README.md`)  
✅ **Use it as:** Your master reference file inside Cursor.