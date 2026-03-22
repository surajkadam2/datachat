# 💬 DataChat

> Ask your SQL Server database questions in plain English. Get answers instantly.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Gemini](https://img.shields.io/badge/Google-Gemini%202.5%20Flash-orange)
![SQL Server](https://img.shields.io/badge/SQL%20Server-2019-red)
![Tests](https://img.shields.io/badge/Tests-15%20passing-brightgreen)

## What is DataChat?

DataChat is a CLI tool that converts natural language questions into SQL queries 
and returns human-readable answers — powered by Google Gemini AI.

**You type:**
```
How many customers are from Germany?
```

**DataChat answers:**
```
💬 There are 11 customers from Germany.
```

No SQL knowledge required.

---

## Demo
```
You: Which employee handled the most orders?

┌────────────┬───────────┬──────────┬────────────────┐
│ EmployeeID │ FirstName │ LastName │ NumberOfOrders │
├────────────┼───────────┼──────────┼────────────────┤
│ 4          │ Margaret  │ Peacock  │ 156            │
└────────────┴───────────┴──────────┴────────────────┘
Rows: 1 │ AI: 2.1s │ DB: 0.02s

💬 Margaret Peacock (EmployeeID 4) handled the most 
   orders with a total of 156 orders.
```

---

## Features

| Feature | Description |
|---------|-------------|
| 🧠 Natural Language to SQL | Converts plain English to accurate SQL queries |
| 💬 Plain English Answers | Summarizes results in human-readable format |
| 🔄 Conversation Memory | Follow-up questions maintain context |
| 🛡️ Two Layer Safety | Blocks dangerous inputs before and after AI processing |
| ⚡ Schema Caching | Lazy-loaded schema avoids DB hit on every request |
| 🔗 Foreign Key Awareness | Improves JOIN accuracy using relationship context |
| 📊 Rich CLI Output | Beautiful tables with timing metrics |
| 🧪 15 Automated Tests | Safety, correctness, and functional evals |

---

## Installation

### Prerequisites
- Python 3.10+
- SQL Server with Northwind database
- Google Gemini API key — free at [aistudio.google.com](https://aistudio.google.com)

### Setup

**1. Clone the repository**
```bash
git clone https://github.com/surajkadam2/datachat
cd datachat
```

**2. Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment**
```bash
cp .env.example .env
# Edit .env with your API key and DB connection string
```

**5. Set up Northwind database**
- Download `instnwnd.sql` from [Microsoft SQL Server Samples](https://github.com/microsoft/sql-server-samples)
- Run in SQL Server Management Studio

**6. Run DataChat**
```bash
python main.py
```

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |
| `DB_SERVER` | SQL Server instance | `DESKTOP-XXX\SQLEXPRESS` |
| `DB_NAME` | Database name | `Northwind` |

---

## Architecture
```
datachat/
├── config.py       → Centralized configuration
├── claude.py       → Gemini AI interface
├── db.py           → SQL Server connection + schema extraction
├── safety.py       → Two layer input + SQL validation
├── prompt.py       → Schema caching + prompt engineering
├── explainer.py    → Grounded plain English answers
├── logger.py       → Dual logging (console + file)
├── main.py         → Rich CLI loop + command handling
└── tests/
    └── eval.py     → 15 automated evals
```

---

## How It Works
```
User Question
      ↓
Safety Check (Layer 1) — block dangerous input
      ↓
Schema + History + Question → Gemini
      ↓
Extract SQL from response
      ↓
Safety Check (Layer 2) — block dangerous SQL
      ↓
Execute against SQL Server
      ↓
Results + Question → Gemini (explainer)
      ↓
Plain English Answer + Rich Table
```

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `help` | Show available commands and example questions |
| `explain` | Show SQL that ran + timing for last query |
| `retry` | Retry with feedback if answer was wrong |
| `edit` | Edit last question without retyping |
| `cls` | Clear terminal |
| `exit` | Quit DataChat |

---

## Testing

Run all 15 automated tests:
```bash
python tests/eval.py
```
```
=== Safety Evaluations ===    6/6  ✅
=== Correctness Evaluations === 5/5  ✅  
=== Functional Evaluations === 4/4  ✅
─────────────────────────────────────
Total: 15 passed, 0 failed
```

---

## Architecture Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Schema context | Full schema | Acceptable for small DBs, revisit at 50+ tables |
| Foreign keys | Included | Significantly improves JOIN accuracy |
| Two API calls | SQL + Explain | Separation of concerns, reduces hallucination |
| Schema loading | Lazy | Avoids DB hit on startup, fails gracefully |
| Temperature | 0.0 for SQL | Deterministic queries, consistent results |

---

## Known Limitations

- Follow-up questions maintain filters but may not restrict to exact previous result set
- Domain context not implemented — business terms like "VIP" use default interpretation
- Schema pruning not implemented — full schema sent for all queries

---

## Built With

- [Google Gemini AI](https://aistudio.google.com) — AI model
- [SQLAlchemy](https://www.sqlalchemy.org) — Database ORM
- [Rich](https://rich.readthedocs.io) — Terminal formatting
- [python-dotenv](https://github.com/theskumar/python-dotenv) — Environment management

---

## License

MIT License — feel free to use, modify, and distribute.