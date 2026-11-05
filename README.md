# AutoSE Assignment 2

## Research Title
The Code Is There. Does the Agent Understand It?

## Repository
- Repository URL: https://github.com/RishabhDev01/AutoSE_Assignment_2
- Initial Submission Commit: a2736c5
- Branch: main

## Experiment Overview
This experiment evaluates whether providing an architecture document improves an autonomous coding agent's performance when modifying an existing software project.

The experiment uses TinyDB and compares two conditions:

- **Condition A:** Agent receives the source code only.
- **Condition B:** Agent receives the same source code along with `ARCHITECTURE.md`.

Three software tasks were evaluated under both conditions, with two trials per task and condition, resulting in 12 runs.

## Agent and Model
- Agent: Claude Code
- Model: Claude Opus 5.5
- Claude Code version: 2.1.317
- Effort level: Medium
- Permission mode: Auto

## Project Structure
- `ARCHITECTURE.md`: Architecture documentation for TinyDB.
- `experiment/config.md`: Experiment configuration and prompt details.
- `experiment/removed_files.txt`: Record of removed repository files.
- `experiment/tasks/`: Task specifications and design-fit checks.
- `results/results.csv`: Recorded results for all 12 runs.
- `results/baseline_tests.txt`: Baseline test output.
- `results/runs/`: Session logs, code diffs, and run notes for each experiment.

## Reproducing a Run

### 1. Prepare the Repository
- Start from the TinyDB experiment snapshot at commit `eae18d1`.
- Create a fresh repository copy for each run.
- Start a fresh Claude Code session for every run.

### 2. Select the Task and Condition
- Select the task specification from `experiment/tasks/T1.md`, `T2.md`, or `T3.md`.
- **Condition A:** Provide the agent with the source code and task specification only.
- **Condition B:** Provide the same source code and task specification, along with `ARCHITECTURE.md`.

### 3. Configure the Agent
Use the agent, model, and settings documented in `experiment/config.md`.

For Condition B, additionally include this instruction:

`Read ARCHITECTURE.md before you start.`

Use the same task completion instruction in both conditions:

`When you are done, make sure the existing tests still pass.`

If the agent asks a question, respond:

`Use your best judgement.`

Each run has a 30-minute time limit.

### 4. Record the Results
Record the following for each run:
- Session log
- Final code diff
- Test output
- Execution time
- Tool-call count
- Token usage, when reported by the agent

The recorded evidence is stored under `results/runs/`, and the consolidated measurements are in `results/results.csv`.

