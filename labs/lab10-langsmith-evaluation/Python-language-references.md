# Python Language References - Lab 10: LangSmith Evaluation and Testing

## Overview
This document explains the Python methods, classes, and concepts used in this lab for creating datasets, building evaluators, running evaluations, and comparing model performance with LangSmith.

## Environment Setup

### Loading Environment Variables
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Set LangSmith environment variables
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "lab10-evaluation"
```

**`os.environ`:** Dictionary-like object for setting/reading environment variables at runtime.
**`os.getenv(key)`:** Reads an environment variable, returning `None` if not set.
**`load_dotenv()`:** Loads variables from a `.env` file into the environment.

## LangSmith Client

### Creating a Client
```python
from langsmith import Client

client = Client()
```

**Purpose:** Entry point for all LangSmith API operations.
**Authentication:** Reads `LANGCHAIN_API_KEY` from environment automatically.

### Creating a Dataset
```python
dataset = client.create_dataset(
    dataset_name="qa-evaluation-dataset",
    description="Question-answer pairs for evaluating the QA chain"
)
```

**Parameters:**
- `dataset_name` (str): Unique name for the dataset
- `description` (str, optional): Human-readable description

**Returns:** `Dataset` object with an `id` field

### Adding Examples to a Dataset
```python
client.create_examples(
    inputs=[
        {"question": "What is the capital of France?"},
        {"question": "Who wrote Hamlet?"},
    ],
    outputs=[
        {"answer": "Paris"},
        {"answer": "William Shakespeare"},
    ],
    dataset_id=dataset.id,
)
```

**Parameters:**
- `inputs` (list[dict]): Input dictionaries matching your chain's expected input keys
- `outputs` (list[dict]): Expected output dictionaries (ground truth)
- `dataset_id` (str): ID of the target dataset

## Running Evaluations

### evaluate() Function
```python
from langsmith.evaluation import evaluate

results = evaluate(
    target=my_chain.invoke,
    data="qa-evaluation-dataset",
    evaluators=[correctness_evaluator],
    experiment_prefix="gpt-3.5-baseline",
)
```

**Parameters:**
- `target` (callable): The function or chain to evaluate; receives each input example
- `data` (str | Dataset): Dataset name or object to evaluate against
- `evaluators` (list): List of evaluator functions to score each result
- `experiment_prefix` (str, optional): Label for this evaluation run in the LangSmith UI

**Returns:** `ExperimentResults` object with per-example scores and summary statistics

## Building Evaluators

### Custom Evaluator Function
```python
from langsmith.schemas import Run, Example

def correctness_evaluator(run: Run, example: Example) -> dict:
    """Score whether the predicted answer matches the reference answer."""
    predicted = run.outputs.get("answer", "").strip().lower()
    reference = example.outputs.get("answer", "").strip().lower()
    score = 1 if predicted == reference else 0
    return {"key": "correctness", "score": score}
```

**Parameters:**
- `run` (Run): Contains `run.outputs` – the chain's actual output for this example
- `example` (Example): Contains `example.inputs` and `example.outputs` – the ground-truth data

**Returns:** `dict` with keys:
- `"key"` (str): Metric name shown in LangSmith UI
- `"score"` (float | int): Numeric score (typically 0–1)
- `"comment"` (str, optional): Explanation text

### LLM-as-Judge Evaluator
```python
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

judge_llm = ChatOpenAI(model="gpt-4", temperature=0)

judge_prompt = PromptTemplate(
    input_variables=["question", "answer", "reference"],
    template=(
        "Question: {question}\n"
        "Reference Answer: {reference}\n"
        "Predicted Answer: {answer}\n\n"
        "Is the predicted answer correct? Reply with 1 for yes, 0 for no."
    ),
)

def llm_judge_evaluator(run: Run, example: Example) -> dict:
    """Use an LLM to judge answer correctness."""
    prompt_value = judge_prompt.format(
        question=example.inputs["question"],
        answer=run.outputs.get("answer", ""),
        reference=example.outputs.get("answer", ""),
    )
    response = judge_llm.invoke(prompt_value)
    score = int(response.content.strip())
    return {"key": "llm_correctness", "score": score}
```

## Traceable Functions

### @traceable Decorator
```python
from langsmith import traceable

@traceable(name="qa_chain_run")
def run_qa_chain(question: str) -> dict:
    """Run the QA chain and return a structured output."""
    result = qa_chain.invoke({"question": question})
    return {"answer": result}
```

**Purpose:** Automatically captures inputs, outputs, and execution time as a LangSmith trace.
**`name`:** Label for this trace in the LangSmith UI (defaults to the function name).
**Usage:** Can decorate any regular Python function; works with both sync and async functions.

## Comparing Models

### Running Multiple Experiments
```python
models = {
    "gpt-3.5": ChatOpenAI(model="gpt-3.5-turbo", temperature=0),
    "gpt-4":   ChatOpenAI(model="gpt-4", temperature=0),
}

for model_name, llm in models.items():
    chain = build_qa_chain(llm)

    evaluate(
        target=chain.invoke,
        data="qa-evaluation-dataset",
        evaluators=[correctness_evaluator],
        experiment_prefix=model_name,
    )
    print(f"Finished evaluation for {model_name}")
```

**Pattern:** Run `evaluate()` once per model and use `experiment_prefix` to label each run. Compare results side-by-side in the LangSmith UI.

## Reading Evaluation Results

### Listing Experiments
```python
experiments = list(client.list_projects(reference_dataset_name="qa-evaluation-dataset"))

for exp in experiments:
    print(f"Experiment: {exp.name}")
    print(f"  Feedback summary: {exp.feedback_stats}")
```

**`client.list_projects()`:** Returns all LangSmith projects; filter by `reference_dataset_name` to see only experiments on one dataset.

### Fetching Per-Example Scores
```python
runs = list(client.list_runs(project_name="gpt-3.5-baseline"))

scores = [
    run.feedback_stats.get("correctness", {}).get("avg", 0)
    for run in runs
    if run.feedback_stats
]
average_score = sum(scores) / len(scores) if scores else 0
print(f"Average correctness: {average_score:.2f}")
```

## Type Hints

### Common Type Annotations Used
```python
from typing import List, Dict, Any, Optional, Callable

def build_evaluator(threshold: float = 0.8) -> Callable[[Run, Example], dict]:
    """Factory that returns a threshold-based evaluator."""
    def evaluator(run: Run, example: Example) -> dict:
        score = compute_similarity(run.outputs, example.outputs)
        return {"key": "similarity", "score": float(score >= threshold)}
    return evaluator
```

**`Callable[[ArgTypes], ReturnType]`:** Type hint for functions/callables; useful when passing evaluators as arguments.
**`Optional[T]`:** Equivalent to `T | None`; indicates the value may be absent.

## String Formatting

### f-strings
```python
experiment_name = f"experiment_{model_name}_{timestamp}"
print(f"Running {len(examples)} examples against model: {model_name!r}")
```

**`{value!r}`:** Calls `repr()` on the value – useful for showing exact string contents including quotes.
**`{value:.2f}`:** Formats a float to 2 decimal places.

### String Methods
```python
predicted = run.outputs.get("answer", "").strip().lower()
```

**`.strip()`:** Removes leading/trailing whitespace.
**`.lower()`:** Converts string to lowercase for case-insensitive comparison.

## Dictionary Operations

### `.get()` with Default
```python
answer = run.outputs.get("answer", "")
score = feedback.get("correctness", {}).get("avg", 0.0)
```

**Purpose:** Safe access to nested or potentially missing keys without raising `KeyError`.

## List Comprehensions
```python
scores = [run.feedback_stats["correctness"]["avg"] for run in runs if run.feedback_stats]
inputs = [{"question": q} for q in question_list]
```

**Syntax:** `[expression for item in iterable if condition]`
**Purpose:** Concise way to build new lists by transforming or filtering an existing sequence.

## Best Practices

1. **Version your datasets** – once a dataset is created, add new examples rather than recreating it so historical comparisons remain valid.
2. **Use `experiment_prefix`** – always label evaluation runs so you can compare them in the LangSmith UI without ambiguity.
3. **Return numeric scores** – evaluators should return `float` or `int` scores (0–1 range is conventional) to enable aggregation.
4. **Combine automated and LLM-judge evaluators** – exact-match evaluators are fast; LLM-judge evaluators handle open-ended outputs.
5. **Use `@traceable`** – wrapping your chain functions makes debugging failures much easier by capturing the full I/O trace.

## Summary

| Concept | Key API / Syntax |
|---------|-----------------|
| Create dataset | `client.create_dataset(dataset_name=...)` |
| Add examples | `client.create_examples(inputs=..., outputs=..., dataset_id=...)` |
| Run evaluation | `evaluate(target=..., data=..., evaluators=...)` |
| Custom evaluator | `def fn(run: Run, example: Example) -> dict` |
| Trace a function | `@traceable(name="...")` |
| List experiments | `client.list_projects(reference_dataset_name=...)` |
| Compare models | Multiple `evaluate()` calls with different `experiment_prefix` values |
