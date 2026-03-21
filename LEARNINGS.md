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

## Architecture Principle
Separate concerns into dedicated modules.
One module = one responsibility.
Makes testing, debugging, and changing easier.
This is Single Responsibility Principle in practice.

## Testing Principle
Always verify test data before assuming AI hallucination.
Bad test data = false bug report.
Garbage in, garbage out applies to tests too.

## Temperature
- Controls randomness of AI output (0.0 to 1.0)
- 0.0 = deterministic, same output every time
- 1.0 = creative, different output every time
- SQL generation = 0.0 (deterministic, reliable)
- Plain English = 0.1 (slight variation, natural feel)
- DataChat is data system not creative system → low temperature

## Temperature danger
Setting TEMPERATURE_SQL too high = inconsistent SQL generation
= silent failures that are hard to reproduce and debug.
Config values need comments explaining valid ranges.