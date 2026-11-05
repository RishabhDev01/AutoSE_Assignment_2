# AutoSE Assignment 2

## Research Title
The Code Is There. Does the Agent Understand It?

## Repository
- Repository URL: To be added after GitHub setup
- Submission commit: To be added after final commit

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
1. Prepare a fresh copy of the TinyDB experiment snapshot.
2. Use the task specification from `experiment/tasks/`.
3. For Condition A, provide the agent with the source code only.
4. For Condition B, provide the same source code and `ARCHITECTURE.md`.
5. Use the agent, model, settings in `experiment/config.md`.
6. Run the task in a fresh agent session.
7. Record the session log, final code diff, test output, execution time, and tool-call count.

