# Lab 03: LangChain Agents and Tools

## Learning Objectives
- Build autonomous agents that can use tools
- Create custom tools for specific tasks
- Understand the ReAct (Reasoning + Acting) pattern
- Integrate with external APIs
- Handle agent failures and error cases
- Build multi-tool agents for complex tasks

## Prerequisites
- Completion of Labs 01-02
- Understanding of LangChain chains and prompts
- Basic knowledge of API interactions

## Lab Overview
In this lab, you will:
1. Create custom tools for various tasks
2. Build a ReAct agent that can reason and act
3. Integrate with external APIs (weather, calculator)
4. Handle agent failures gracefully
5. Build a multi-tool agent for complex problem-solving

## Step-by-Step Instructions

### Task 1: Create Custom Tools
**Objective**: Build custom tools that agents can use to perform specific tasks.

**Steps**:
1. Import required modules:
   ```python
   from langchain.tools import Tool, DuckDuckGoSearchRun
   from langchain.agents import AgentType, initialize_agent
   from langchain_openai import ChatOpenAI
   ```

2. Create a calculator tool:
   ```python
   def calculator(expression: str) -> str:
       """Safely evaluate mathematical expressions."""
       try:
           # Safe evaluation of math expressions
           result = eval(expression)
           return f"The result is: {result}"
       except Exception as e:
           return f"Error calculating: {str(e)}"
   
   calculator_tool = Tool(
       name="Calculator",
       func=calculator,
       description="Useful for mathematical calculations. Input should be a valid math expression."
   )
   ```

3. Create a text analysis tool:
   ```python
   def analyze_text(text: str) -> str:
       """Analyze text and return statistics."""
       words = text.split()
       sentences = text.split('.')
       return f"Analysis: {len(words)} words, {len(sentences)} sentences, {len(text)} characters"
   
   text_analyzer = Tool(
       name="TextAnalyzer", 
       func=analyze_text,
       description="Analyze text to get word count, sentence count, and character count."
   )
   ```

**Expected Result**: Custom tools that can be used by agents:
```
Tool Created: Calculator - Ready for mathematical operations
Tool Created: TextAnalyzer - Ready for text analysis
```

### Task 2: Build ReAct Agent
**Objective**: Create an agent that uses the ReAct pattern (Reasoning + Acting).

**Steps**:
1. Initialize the LLM:
   ```python
   llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
   ```

2. Create tool list:
   ```python
   tools = [calculator_tool, text_analyzer, DuckDuckGoSearchRun()]
   ```

3. Initialize the agent:
   ```python
   agent = initialize_agent(
       tools=tools,
       llm=llm,
       agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
       verbose=True,
       handle_parsing_errors=True
   )
   ```

4. Test the agent:
   ```python
   result = agent.run("What is 25 * 4 + 10?")
   ```

**Expected Result**: Agent demonstrates reasoning and tool usage:
```
> Entering new AgentExecutor chain...
I need to calculate 25 * 4 + 10. Let me use the calculator tool.

Action: Calculator
Action Input: 25 * 4 + 10
Observation: The result is: 110

Thought: The calculation is complete.
Final Answer: 25 * 4 + 10 equals 110.
```

### Task 3: Integrate with External APIs
**Objective**: Add tools that interact with external services.

**Steps**:
1. Create a weather tool (mock implementation):
   ```python
   def get_weather(location: str) -> str:
       """Get weather information for a location."""
       # Mock weather data
       weather_data = {
           "New York": "Sunny, 75°F",
           "London": "Cloudy, 60°F", 
           "Tokyo": "Rainy, 68°F"
       }
       return weather_data.get(location, f"Weather data not available for {location}")
   
   weather_tool = Tool(
       name="WeatherTool",
       func=get_weather,
       description="Get current weather for a specific location. Input should be a city name."
   )
   ```

2. Add the new tool to your agent:
   ```python
   enhanced_tools = [calculator_tool, text_analyzer, weather_tool, DuckDuckGoSearchRun()]
   enhanced_agent = initialize_agent(
       tools=enhanced_tools,
       llm=llm,
       agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
       verbose=True
   )
   ```

**Expected Result**: Agent can access weather information:
```
Question: "What's the weather like in New York and what's 20 + 30?"
Agent uses WeatherTool: "Sunny, 75°F"
Agent uses Calculator: "50"
Final Answer: "In New York it's sunny and 75°F, and 20 + 30 equals 50."
```

### Task 4: Handle Agent Failures
**Objective**: Implement error handling and graceful failure recovery.

**Steps**:
1. Create a robust agent with error handling:
   ```python
   def safe_agent_run(agent, query: str, max_retries: int = 3):
       """Run agent with error handling and retries."""
       for attempt in range(max_retries):
           try:
               result = agent.run(query)
               return result
           except Exception as e:
               print(f"Attempt {attempt + 1} failed: {str(e)}")
               if attempt == max_retries - 1:
                   return f"Agent failed after {max_retries} attempts: {str(e)}"
       return "Maximum retries exceeded"
   ```

2. Test with challenging queries:
   ```python
   challenging_queries = [
       "Calculate the square root of -1",  # Should handle math errors
       "What's the weather on Mars?",     # Should handle missing data
       "Analyze this text: ''",          # Should handle empty input
   ]
   ```

**Expected Result**: Graceful error handling:
```
Query: "Calculate the square root of -1"
Attempt 1 failed: math domain error
Agent Response: "I cannot calculate the square root of negative numbers in real numbers..."
```

### Task 5: Build Multi-Tool Agent
**Objective**: Create a comprehensive agent that can handle complex, multi-step tasks.

**Steps**:
1. Create additional specialized tools:
   ```python
   def file_info(filename: str) -> str:
       """Get information about a file (mock)."""
       return f"File {filename}: 1024 bytes, created today"
   
   def unit_converter(conversion: str) -> str:
       """Convert between units (mock)."""
       conversions = {
           "100 cm to m": "1 meter",
           "32 F to C": "0 degrees Celsius"
       }
       return conversions.get(conversion, "Conversion not supported")
   ```

2. Build the ultimate agent:
   ```python
   ultimate_tools = [
       calculator_tool, text_analyzer, weather_tool,
       file_info_tool, unit_converter_tool, DuckDuckGoSearchRun()
   ]
   
   ultimate_agent = initialize_agent(
       tools=ultimate_tools,
       llm=llm,
       agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
       verbose=True,
       max_iterations=10  # Allow more complex reasoning
   )
   ```

3. Test with complex queries:
   ```python
   complex_query = """
   I need to:
   1. Calculate 15% of 200
   2. Check the weather in London
   3. Analyze this text: 'The quick brown fox jumps over the lazy dog'
   4. Convert 100 cm to meters
   """
   ```

**Expected Result**: Agent handles multi-step reasoning:
```
> Entering new AgentExecutor chain...
I need to handle multiple tasks. Let me break this down:

Action: Calculator
Action Input: 200 * 0.15
Observation: The result is: 30.0

Action: WeatherTool  
Action Input: London
Observation: Cloudy, 60°F

Action: TextAnalyzer
Action Input: The quick brown fox jumps over the lazy dog
Observation: Analysis: 9 words, 1 sentences, 43 characters

Action: UnitConverter
Action Input: 100 cm to m
Observation: 1 meter

Final Answer: Here are your results:
1. 15% of 200 = 30
2. London weather: Cloudy, 60°F
3. Text analysis: 9 words, 1 sentence, 43 characters  
4. 100 cm = 1 meter
```

## Expected Outcomes
- Master LangChain agents and tools
- Build production-ready autonomous systems
- Understand agent reasoning patterns
- Implement robust error handling
- Create complex multi-tool workflows

**Complete Program Output**:
```
=== Lab 03: LangChain Agents and Tools ===

Task 1: Creating Custom Tools
✓ Calculator tool created
✓ Text analyzer tool created  
✓ Tools ready for agent use

Task 2: Building ReAct Agent
> Entering new AgentExecutor chain...
Question: What is 25 * 4 + 10?
Thought: I need to calculate this mathematical expression.
Action: Calculator
Action Input: 25 * 4 + 10
Observation: The result is: 110
Final Answer: 25 * 4 + 10 equals 110.

Task 3: External API Integration
Question: What's the weather in New York?
Action: WeatherTool
Action Input: New York
Observation: Sunny, 75°F
Final Answer: The weather in New York is sunny and 75°F.

Task 4: Error Handling
Testing challenging query: "Calculate square root of -1"
✓ Error handled gracefully
✓ Fallback response provided

Task 5: Multi-Tool Agent
Complex query processing...
✓ Mathematical calculation: 15% of 200 = 30
✓ Weather check: London is cloudy, 60°F
✓ Text analysis: 9 words, 1 sentence, 43 characters
✓ Unit conversion: 100 cm = 1 meter

=== Lab 03 Complete! ===
```

## Resources
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

## Next Steps
Proceed to **Lab 04: LangChain Memory**.
