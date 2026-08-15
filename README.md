# Experience OS

> A reusable decision memory system for AI agents.

[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)]()
[![Tests](https://img.shields.io/badge/tests-284%20passed-success)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()
[![Status](https://img.shields.io/badge/status-Gen--1-orange.svg)]()

---

## Overview

Experience OS is an AI memory framework that enables agents to learn from previous successful executions and safely reuse those experiences when solving similar tasks.

Unlike traditional conversational memory, Experience OS stores **validated decision patterns** that can be recalled, ranked, validated, and reused.

The project is designed as a modular architecture where future generations can introduce semantic retrieval, knowledge graphs, reflection, and persistent memory without changing the public API.

---

## Motivation

Most LLM agents repeatedly solve the same problems because they do not retain reusable experience.

Experience OS introduces an execution-driven memory system that answers:

- Have we solved this before?
- Under which conditions?
- Was the solution successful?
- Can we safely reuse it?

Instead of remembering conversations, Experience OS remembers **validated decisions**.

---

# Architecture

```
                ┌────────────┐
                │    Task    │
                └─────┬──────┘
                      │
                      ▼
          ┌────────────────────┐
          │ Experience Planner │
          └─────────┬──────────┘
                    │
                    ▼
              Decision Created
                    │
                    ▼
          ┌───────────────────┐
          │    Executor       │
          └─────────┬─────────┘
                    │
                    ▼
                Outcome
                    │
                    ▼
          ┌───────────────────┐
          │    Validator      │
          └─────────┬─────────┘
                    │
        Successful? │
                    ▼
          ┌───────────────────┐
          │ Experience Learner│
          └─────────┬─────────┘
                    │
                    ▼
             Experience Store
                    │
                    ▼
             Future Executions
```

---

# Features

- Deterministic planning
- Experience recall
- Applicability checking
- Experience ranking
- Rule-based execution
- Outcome validation
- Experience learning
- Experience confidence tracking
- In-memory experience store
- Modular architecture
- Fully tested

---

# Project Structure

```
experience-os/

│
├── src/
│   └── experience_os/
│       ├── planner.py
│       ├── executor.py
│       ├── validator.py
│       ├── learning.py
│       ├── recall.py
│       ├── ranking.py
│       ├── storage.py
│       ├── experience_api.py
│       ├── models.py
│       └── ...
│
├── tests/
│
├── experiments/
│
├── README.md
├── LICENSE
├── pyproject.toml
└── uv.lock
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/<your-username>/experience-os.git
```

Enter the project

```bash
cd experience-os
```

Install dependencies

```bash
uv sync
```

---

# Running Tests

Run the complete test suite

```bash
uv run pytest
```

Current status

```
284 passed
0 failed
```

---

# Quick Example

```python
from experience_os.models import Task
from experience_os.recall import ExperienceRecall, ExperienceStore
from experience_os.experience_api import ExperienceAPI

store = ExperienceStore()

recall = ExperienceRecall(store)

api = ExperienceAPI(recall)

task = Task(
    goal="Book Flight",
    context={
        "traveler_type": "family"
    }
)

result = api.execute(task)

print(result.outcome.status)
```

---

# Core Concepts

## Task

Represents a business objective.

Example

```python
Task(
    goal="Book flight",
    context={
        "traveler_type":"family"
    }
)
```

---

## Decision

Planner output.

Contains

- description
- rationale
- alternatives

---

## Outcome

Execution result.

Possible values

```
SUCCESS
PARTIAL
FAILURE
```

---

## Experience

A reusable decision pattern.

Contains

- applicability conditions
- reusable decisions
- confidence
- execution statistics

Example

```python
Experience(
    conditions={
        "traveler_type":"family"
    },
    decision_pattern=[
        "Compare total trip cost"
    ]
)
```

---

# Experience Lifecycle

```
Task

↓

Planning

↓

Execution

↓

Validation

↓

Learning

↓

Experience

↓

Future Recall
```

---

# Test Coverage

Current test suite

- Planner
- Executor
- Validator
- Experience API
- Learning
- Storage
- Memory
- Trust
- Ranking
- Recall
- Lifecycle
- Models

```
284 tests
100% passing
```

---

# Current Version

Gen-1

Capabilities

- Deterministic planning
- Rule-based execution
- Experience learning
- Experience reuse
- Trust scoring
- Validation pipeline

Storage

```
In-memory
```

---

# Roadmap

## Gen-2

- Vector database
- Semantic search
- Embedding retrieval
- Reflection engine
- Persistent storage
- Knowledge graph

---

## Gen-3

- Multi-agent shared memory
- Continual learning
- Self-improving planners
- Autonomous reflection
- Long-term memory

---

# Why Experience OS?

Traditional Memory

```
Conversation history
```

Experience OS

```
Validated decision memory
```

Traditional Memory

```
Remembers text
```

Experience OS

```
Remembers successful decisions
```

Traditional Memory

```
Retrieves similar conversations
```

Experience OS

```
Retrieves reusable experiences
```

---

# Contributing

Contributions are welcome.

To contribute

1. Fork the repository

2. Create a feature branch

```bash
git checkout -b feature/my-feature
```

3. Commit

```bash
git commit -m "Add feature"
```

4. Push

```bash
git push origin feature/my-feature
```

5. Open a Pull Request

---

# Citation

If you use Experience OS in research or production, please cite:

```
Experience OS

Reusable Decision Memory for AI Agents

Version 1.0
```

---

# License

MIT License

---

# Author

**Vikash Kumar**

AI Product Leader

Enterprise AI • Agentic AI • Decision Intelligence

---

⭐ If you find this project useful, please consider giving it a star.