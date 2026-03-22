# Engineering Learnings — DataChat

A personal knowledge base built while developing DataChat.
These are lessons learned through building, breaking, and fixing —
not from tutorials.

---

## How Large Language Models Work

**Tokenization**
Words are converted to numbers before the model processes them.
Every token costs money and consumes context window space.

**Attention Mechanism**
The model maps relationships between all tokens simultaneously.
"Show me customers from Germany" — the model understands
"Germany" modifies "customers" through attention, not keyword matching.

**Pattern Completion**
LLMs are trained on billions of examples. They predict the most
probable next token based on patterns seen in training data.
They do not "think" — they complete patterns.

**Key Insight**
Schema quality = output quality.
Better context given to the model = better SQL generated.
Garbage in, garbage out applies to AI systems too.

---

## Prompt Engineering

**System prompt is for rules and schema only.**
Never inject runtime or user-specific data into the system prompt.
Runtime data belongs in conversation history or the user message.

**Prompt instructions compete with training data.**
Strong training patterns can override weak prompt rules.
Example: "return France instead" instruction lost to the
"customers from Germany" training pattern.

**Security must never rely on prompt instructions alone.**
Always use hard-coded checks for safety-critical logic.

> *"Prompts control behavior. Code enforces safety."*

**Temperature controls randomness.**
- `0.0` — deterministic, same output every time
- `1.0` — maximum creativity, different output every time
- SQL generation uses `0.0` — consistency is a feature
- Plain English answers use `0.1` — slight variation feels natural
- Never set `TEMPERATURE_SQL` above `0.2` — causes silent failures

---

## Architecture Principles

**Single Responsibility Principle**
One module = one responsibility.
`claude.py` talks to AI. `db.py` talks to database. `safety.py` validates.
When something breaks, you know exactly where to look.

**Lazy Loading**
Load only when needed. Fail only when needed.
Schema is fetched on the first question, not on app startup.
If the database is down at startup — the app still launches.

**Externalized Configuration**
All magic numbers and settings live in `config.py`.
Change model name, temperature, or timeout in one place.
Config values need comments explaining valid ranges.

**Signal Protocol**
AI responses are treated as signals first, SQL second.
- Clean SQL → valid question, execute it
- `NOT_A_DB_QUESTION` → invalid input, tell the user
- `EXTRACTED:` → partial input recovery, warn and proceed

---

## Testing & Quality

**Evals over manual testing**
Evals are coded once and run after every change.
Manual testing is time-consuming, inconsistent, and forgettable.
Evals catch regressions automatically.

**Three types of evals**
- Safety evals — does it block dangerous input?
- Correctness evals — does it return the right data?
- Functional evals — does it return data at all?

**Robust assertions**
Never assert exact column names from AI-generated SQL.
Assert values not structure.
`list(rows[0].values())[0]` is more resilient than `rows[0]['count']`
Brittle evals break on improvements, not just regressions.

**Always verify your verification**
Wrong manual calculation = false bug report.
Before blaming AI — check your test data.
In production: use known test data with pre-calculated expected results.

**Test data strategy**
Never run evals against production database.
Use dedicated test DB with seed data covering:
happy path, edge cases, and false positive scenarios.
Northwind is perfect seed data — static, diverse, realistic.

---

## Python Lessons

**Mutable default arguments — silent trap**
```python
# DANGEROUS
def function(history=[]):

# CORRECT  
def function(history=None):
    if history is None:
        history = []
```
Mutable defaults are shared across all function calls.
One of the hardest bugs to find in production.

**Docstrings are contracts**
A docstring tells you: what goes in, what comes out, what can fail.
An inline comment tells you: why this decision was made.
Never use `"""` for inline comments — use `#`.

**Why comments over what comments**
```python
# BAD — describes what code does (redundant)
# Loop through rows

# GOOD — explains why decision was made
# Cap at 20 rows to prevent token overflow in Gemini context
```

---

## AI System Design

**Grounding prevents hallucination**
Restrict AI to provided data only.
Tell the model: use ONLY this data, never invent facts.
The more freedom given to AI, the more hallucination risk introduced.

**Conversation memory is an illusion**
LLMs have no memory between API calls.
Your app sends the full conversation history on every request.
This creates the illusion of memory — it is engineering, not magic.

**Sliding window memory**
Keep last N exchanges. Drop oldest when limit reached.
Every message added = more tokens = more cost.
Balance context quality against API cost.

**Silent wrong answers are the most dangerous failures**
A query that crashes is safe — you know it failed.
A query that returns wrong data confidently is dangerous —
the user makes decisions based on incorrect information.

---

## Personal Lessons

**Building beats watching.**
Every tutorial watched is time not building.
Real learning happens when something breaks at 11pm
and you have to figure out why.

**Your engineering instincts transfer.**
10 years of Java instincts transferred instantly to Python and AI.
Pattern recognition, systems thinking, debugging instinct —
these are language-agnostic skills.

**Fear of visibility held me back.**
For years I did great work invisibly.
Building in public is uncomfortable.
It is also how opportunities find you.

**Consistency compounds.**
2 hours every day beats 12 hours on weekends.
The engineers winning in AI right now are not the smartest.
They are the most consistent.