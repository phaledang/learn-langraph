# LangSmith Monitoring

## Introduction to LangSmith

### What is LangSmith?
- **Platform for debugging, testing, and monitoring LLM applications**
- Built by LangChain team
- Provides observability for production systems
- Enables evaluation and testing

### Why LangSmith?

#### Challenges with LLM Apps
- Non-deterministic outputs
- Difficult to debug
- Hard to measure performance
- Complex chains and agents

#### LangSmith Solutions
- **Tracing**: Full execution visibility
- **Debugging**: Identify issues quickly
- **Testing**: Automated evaluations
- **Monitoring**: Production observability
- **Datasets**: Manage test cases

### Core Features

#### 1. Tracing

**Automatic Instrumentation**
```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key"
```

**What You See**
- All LLM calls
- Prompt templates
- Actual prompts sent
- Responses received
- Latency for each step
- Token usage
- Error messages

#### 2. Datasets

**Create Test Sets**
```python
from langsmith import Client

client = Client()
dataset = client.create_dataset("qa-dataset")
client.create_example(
    dataset_id=dataset.id,
    inputs={"question": "What is LangChain?"},
    outputs={"answer": "LangChain is a framework..."}
)
```

#### 3. Evaluations

**Run Tests**
```python
from langsmith import evaluate

results = evaluate(
    my_chain,
    data=dataset,
    evaluators=[correctness, helpfulness]
)
```

### Setting Up LangSmith

#### Step 1: Get API Key
1. Sign up at smith.langchain.com
2. Generate API key
3. Set environment variables

#### Step 2: Configure Project
```python
os.environ["LANGCHAIN_PROJECT"] = "my-project"
```

#### Step 3: Run Your Code
- Traces automatically captured
- View in LangSmith dashboard

### Tracing Deep Dive

#### Trace Components
- **Runs**: Individual executions
- **Spans**: Steps within a run
- **Metadata**: Custom tags and information
- **Feedback**: Human annotations

#### Custom Metadata
```python
from langchain.callbacks import LangChainTracer

tracer = LangChainTracer(
    project_name="my-project",
    tags=["production", "v1.0"]
)
```

### Debugging Workflows

#### 1. Identify Issues
- High latency steps
- Failed calls
- Unexpected outputs
- Token usage spikes

#### 2. Drill Down
- View exact prompts
- See intermediate results
- Check error messages
- Analyze token counts

#### 3. Iterate
- Modify prompts
- Adjust parameters
- Test changes
- Compare versions

### Evaluation Framework

#### Built-in Evaluators
```python
from langchain.evaluation import (
    QAEvalChain,
    CriteriaEvalChain
)

# Correctness evaluation
qa_eval = QAEvalChain.from_llm(llm)

# Criteria-based evaluation
criteria_eval = CriteriaEvalChain.from_llm(
    llm,
    criteria="helpfulness"
)
```

#### Custom Evaluators
```python
def custom_evaluator(run, example):
    prediction = run.outputs["output"]
    reference = example.outputs["answer"]
    
    # Your evaluation logic
    score = calculate_score(prediction, reference)
    
    return {"score": score}
```

### Testing Best Practices

#### 1. Create Representative Datasets
- Cover edge cases
- Include variety
- Update regularly

#### 2. Define Clear Metrics
- Accuracy
- Relevance
- Helpfulness
- Factuality

#### 3. Automate Testing
- CI/CD integration
- Regression detection
- Performance benchmarks

### Production Monitoring

#### Key Metrics
- **Success Rate**: % of successful runs
- **Latency**: Response times
- **Token Usage**: Cost tracking
- **Error Rate**: Failure frequency

#### Alerts and Notifications
- Set up alerts for anomalies
- Monitor critical paths
- Track degradation

#### Dashboard Views
- Real-time metrics
- Historical trends
- Comparison views
- Custom filters

### Human Feedback

#### Collect Annotations
```python
from langsmith import Client

client = Client()
client.create_feedback(
    run_id=run.id,
    key="quality",
    score=0.9,
    comment="Great response!"
)
```

#### Use Feedback
- Improve prompts
- Create training data
- Identify patterns
- Guide optimization

### Integration Patterns

#### CI/CD Pipeline
```bash
# Run evaluations in CI
python -m langsmith evaluate \
    --dataset qa-test-set \
    --output results.json
```

#### A/B Testing
- Compare prompt versions
- Test different models
- Evaluate strategies

### Cost Optimization

#### Track Expenses
- Token usage per run
- Cost per user
- Model comparisons
- Optimization opportunities

#### Identify Waste
- Redundant calls
- Inefficient prompts
- Unnecessary complexity

### Security and Privacy

- Data encryption
- Access controls
- Compliance features
- Data retention policies

### Best Practices

1. **Start Early**: Instrument from day one
2. **Tag Consistently**: Use meaningful tags
3. **Create Datasets**: Build test suites
4. **Monitor Actively**: Review traces regularly
5. **Iterate**: Use insights for improvement

## Resources
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [LangSmith Platform](https://smith.langchain.com/)
- [Evaluation Guide](https://docs.smith.langchain.com/evaluation)
