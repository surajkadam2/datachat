## 2026-03-20
- Learned: Lazy loading pattern — load only when needed
- Learned: Signal protocol between AI and app
- Bug fixed: EXTRACTED signal wrong SQL passed to run_query
- Question I still have: How to handle conversation memory?
- Next: Day 7 — final break-it session

## 2026-03-21
- Lesson: Always verify your verification.
- When checking AI output manually, wrong manual 
  calculation = false bug report.
- Silent wrong answers are hard to catch because 
  the verifier can also make mistakes.
- In production: use known test data with 
  pre-calculated expected results.

## How Gemini works
- Tokenization: words become numbers
- Attention: model maps relationships between all tokens
- Context window: schema + rules + question processed together
- Pattern completion: trained on millions of SQL examples
- Probability: generates most likely next token
- Key insight: schema quality = output quality

- Sliding window — keep last N messages, drop oldest when limit reached

## Python trap: Mutable default arguments
- Never use [] or {} as default parameter values
- Use None instead and initialize inside function
- Mutable defaults are shared across all function calls
- Silent bug — very hard to find in production


## Architecture Principle learned
System prompt = rules + schema only.
Never inject runtime/user-specific data into system prompt.
Runtime data belongs in conversation history or user message.