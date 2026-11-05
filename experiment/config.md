# Experiment Configuration

## 1. Agent and Environment

| Parameter | Configuration |
|---|---|
| Agent | Claude Code (Claude Desktop – Code tab) |
| Model | Claude Opus 5.5 |
| Thinking effort | Medium |
| Permission mode | Auto |
| Environment | This computer (local Windows machine) |
| Operating system | Windows |
| Project | TinyDB |
| Python version | 3.14.7 |
| Test framework | pytest 9.1.0 |
| Machine | Same physical Windows machine for all runs |
| Temperature | Not exposed in the interface |

## 2. Experimental Design

- Tasks: T1, T2, T3.
- Conditions: A (code only), B (code + ARCHITECTURE.md).
- Trials per condition: 2.
- Total runs: 12.
- Time limit per run: 30 minutes.
- Every run starts from a fresh repository copy.
- Every run uses a fresh Claude Code session.
- The same task specification and completion instruction are used in both conditions.
- Condition B additionally receives: `Read ARCHITECTURE.md before you start.`
- If the agent asks a question, respond: `Use your best judgement.`

## 3. Baseline

- Existing repository tests: 228 passed, 0 failed, 0 skipped.
- Code coverage: 93%.
- T1 hidden acceptance tests: 1 passed, 3 failed.
- T2 hidden acceptance tests: 0 passed, 4 failed.
- T3 hidden acceptance tests: 0 passed, 4 failed.

## 4. Evaluation

- Hidden acceptance tests are executed separately by the researcher.
- Regressions are measured against the original passing test baseline.
- Design fit is scored using three predefined binary checks per task.
- Time and tool calls are recorded for every run.
- Tokens or cost are recorded only when reported by the agent.