# DataChat v1.0

## What it does
Natural language interface for SQL Server databases.
Type a question in plain English, get data back instantly.

## Tech Stack
- Python 3.13
- Google Gemini 2.5 Flash
- SQL Server + Northwind
- SQLAlchemy + pyodbc
- Rich CLI

## Architecture
claude.py      → Gemini AI interface
db.py          → SQL Server connection + schema extraction
safety.py      → Input validation + SQL validation + extraction
prompt.py      → Schema caching + prompt building + SQL generation
logger.py      → Dual logging (console + file)
explainer.py   → Plain English answers with grounding
main.py        → CLI loop + command handling

## What makes it production-grade
- Two layer safety validation
- Schema cached in memory (lazy loading)
- Foreign key relationships in schema context
- Query timeout protection (10 seconds)
- Row limit protection (100 rows max)
- Structured logging with timestamps
- AI signal protocol (NOT_A_DB_QUESTION, EXTRACTED:)
- Graceful error handling throughout

## Architecture Decisions
1. Full schema sent to Gemini — acceptable for small DBs,
   revisit when schema exceeds 50 tables
2. Foreign keys included — improves JOIN accuracy significantly
3. Two API call approach rejected — too costly
4. Lazy schema loading — avoids DB hit on startup

## Known Limitations
1. CustomerID shows codes not names in some queries
2. Domain context not implemented — VIP/premium undefined
3. Follow-up questions maintain filters but may not restrict
   to exact previous result set
4. Schema pruning not implemented

## Bug Fixes Log
- Day 6: Vague terms default to TOP 10
- Day 6: Empty input handled gracefully
- Day 6: NOT_A_DB_QUESTION signal protocol
- Day 6: EXTRACTED signal for mixed input
- Day 6: CLI commands handled correctly

## What I learned
- Prompt engineering controls AI behavior
- Silent failures are more dangerous than loud errors
- Schema context quality directly affects SQL quality
- AI responses need a signal protocol
- Two layer safety: input layer + SQL layer
- Lazy loading pattern
- Dual logging pattern

## eval
- DataChat passes 15 automated tests including exact correctness checks against known data.
- System prompt rules compete with training data patterns. Strong training patterns can win.

## Testing Strategy
- Evals run against Northwind — a static test database.
- Absolute correctness assertions are safe because test data never changes.
- For production databases: use relative assertions or dedicated test DB with fixed seed data.

## Test Data Strategy
- Never run evals against production DB
- Use dedicated test DB with seed data
- Seed data covers: happy path, edge cases, false positives
- Northwind = perfect seed data (static, diverse, realistic)
- Absolute assertions safe only with static test data
- Production DB = relative assertions or snapshot testing