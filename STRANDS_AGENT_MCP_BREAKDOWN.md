# Building MCP Tools with Strands Agent: A Real-World Example
## Query Agent Handler - Breaking Down an AI-Powered Business Intelligence System

---

## 🎯 The Big Picture: What We're Building

This Lambda function demonstrates how Strands Agent enables you to build sophisticated MCP (Model Context Protocol) tools that:
- **Connect to real databases** and execute complex SQL queries
- **Analyze business data** intelligently based on natural language requests
- **Generate insights** using AI agents with structured data
- **Provide observability** through comprehensive logging

---

## 🏗️ Architecture Overview

```
User Request (Natural Language)
        ↓
Lambda Handler (Entry Point)
        ↓
Request Analysis & Query Router
        ↓
Database Query Execution Layer
        ↓
Strands Agent (GPT-4 Analysis)
        ↓
Business Insights Response
```

---

## 📦 Key Components Breakdown

### 1. **Environment & Configuration (Lines 1-24)**
```python
from strands import Agent
from strands.models.openai import OpenAIModel
import logging

# Strands-specific logging setup
logging.getLogger("strands").setLevel(logging.DEBUG)
```

**Why This Matters for MCP:**
- Strands provides first-class integration with OpenAI models
- Built-in observability through the Strands logging framework
- Clean separation between infrastructure and business logic

---

### 2. **Secure Credential Management (Lines 26-54)**

```python
def get_database_credentials():
    """Environment-based credential management"""
    logger.debug("Retrieving database credentials")
    # Validates all required env vars exist
    # Returns structured credential dict
```

**MCP Best Practice:**
- Never hardcode credentials
- Fail fast with clear error messages
- Log credential retrieval (without exposing secrets!)

---

### 3. **Database Connection Layer (Lines 56-81)**

```python
@contextmanager
def get_db_connection():
    """Context manager for safe DB connections"""
    logger.debug("Establishing database connection")
    # Auto-cleanup on exit
    # SSL required for security
```

**Key Features:**
- Context manager ensures connections always close
- RealDictCursor for easy JSON serialization
- Comprehensive error handling with logging

---

### 4. **Domain-Specific Query Functions (Lines 83-256)**

Three specialized query functions that demonstrate modularity:

#### Revenue Query (Lines 83-130)
```python
def execute_revenue_query(start_date: str = None):
    """30-day revenue trends with daily breakdowns"""
    # Smart defaults (30 days if not specified)
    # Aggregates: total, average, trends
    # Returns structured data ready for AI analysis
```

#### Product Performance (Lines 132-193)
```python
def execute_product_query(start_date: str = None, category: str = None):
    """Top performing products with sales metrics"""
    # 90-day window for product analysis
    # Category filtering capability
    # Top 15 products by revenue
```

#### Customer Analysis (Lines 195-256)
```python
def execute_customer_query(start_date: str = None, min_amount: float = None):
    """High-value customer identification"""
    # Flexible filtering by order amount
    # Customer segmentation data
    # Order pattern analysis
```

**Why This Architecture Works:**
- Each function is independent and testable
- Clear input/output contracts
- Reusable across different MCP tools

---

### 5. **Natural Language Request Router (Lines 258-307)**

```python
def analyze_business_request(user_prompt: str):
    """Smart routing based on keyword detection"""
    
    # Keyword-based intent detection
    if any(word in prompt_lower for word in ['revenue', 'sales']):
        execute_revenue_query()
    
    # Can execute multiple queries for comprehensive analysis
    # Fallback to general overview if no specific match
```

**The Magic Here:**
- Simple yet effective NLP without external dependencies
- Multi-query execution for holistic insights
- Graceful fallbacks ensure always useful output

---

### 6. **Strands Agent Integration (Lines 309-401)**

```python
def generate_business_insights(query_results, user_prompt):
    """This is where Strands Agent shines!"""
    
    # Initialize OpenAI model through Strands
    model = OpenAIModel(
        client_args={"api_key": openai_api_key},
        model_id="gpt-4o",
        params={"max_tokens": 2000, "temperature": 0.3}
    )
    
    # Create specialized business analyst agent
    analyst = Agent(
        system_prompt="""You are a senior business analyst...""",
        model=model
    )
    
    # Transform raw data into formatted context
    # Agent analyzes and generates insights
    analysis = analyst(data_summary)
```

**Why Strands Agent is Perfect for MCP Tools:**

1. **Abstraction Without Complexity**
   - Simple Agent creation with system prompts
   - Handles all OpenAI API complexity internally
   - Clean, readable code

2. **Flexibility**
   - Easy to swap models (GPT-4, GPT-3.5, etc.)
   - Adjustable parameters per use case
   - Could easily add tools to the agent for enhanced capabilities

3. **Production-Ready**
   - Built-in error handling
   - Automatic retries and rate limiting
   - Comprehensive logging integration

---

### 7. **Lambda Handler - The Orchestrator (Lines 403-455)**

```python
def handler(event: Dict[str, Any], _context):
    """AWS Lambda entry point - coordinates everything"""
    
    # Step 1: Analyze request & execute queries
    query_results = analyze_business_request(user_prompt)
    
    # Step 2: Generate AI insights
    insights = generate_business_insights(query_results, user_prompt)
    
    # Step 3: Return structured response
    return {
        'statusCode': 200,
        'body': json.dumps({
            'response': insights,
            'queries_executed': query_results['queries_executed'],
            'timestamp': datetime.utcnow().isoformat()
        })
    }
```

**Production Considerations:**
- Full request/response logging
- Structured error responses
- CORS headers for web integration
- Execution metadata for debugging

---

## 🚀 What Makes This a Great MCP Tool Example

### 1. **Real-World Complexity**
- Handles actual database connections
- Processes meaningful business data
- Provides actionable insights

### 2. **Clean Architecture**
- Separation of concerns (data, logic, presentation)
- Modular, testable functions
- Clear data flow

### 3. **Strands Agent Advantages**
- Minimal boilerplate for AI integration
- Production-ready with built-in best practices
- Seamless logging and observability

### 4. **Extensibility**
- Easy to add new query types
- Simple to integrate additional data sources
- Can enhance with Strands tools (web search, calculations, etc.)

---

## 💡 Key Takeaways for Building MCP Tools with Strands

1. **Start with Clear Domain Logic**
   - Define your data access patterns
   - Create modular query functions
   - Think in terms of reusable components

2. **Leverage Strands Agent for AI Heavy-Lifting**
   - Don't reinvent the wheel for LLM integration
   - Use system prompts to create specialized agents
   - Let Strands handle the complexity

3. **Implement Comprehensive Logging**
   - Use Strands' built-in logging framework
   - Log at appropriate levels (DEBUG, ERROR)
   - Include context without exposing sensitive data

4. **Design for Natural Language**
   - Simple keyword matching goes a long way
   - Combine multiple data sources for comprehensive responses
   - Always provide fallback behavior

5. **Think in Patterns**
   - Request → Analysis → Execution → Synthesis → Response
   - This pattern works for most MCP tools
   - Keep it simple and maintainable

---

## 🔮 Future Enhancements Possible with Strands

1. **Add Tool Usage to Agents**
   ```python
   analyst = Agent(
       system_prompt="...",
       model=model,
       tools=[calculator_tool, web_search_tool]
   )
   ```

2. **Streaming Responses**
   - Strands supports streaming for real-time updates
   - Perfect for long-running analyses

3. **Multi-Agent Orchestration**
   - Create specialized agents for different domains
   - Coordinate between agents for complex tasks

4. **Enhanced Observability**
   - Integrate with APM tools
   - Custom metrics and tracing
   - A/B testing different prompts

---

## 📊 Metrics That Matter

When presenting this at a meetup, emphasize:

- **Development Speed**: Built in hours, not weeks
- **Line Count**: ~450 lines for a complete business intelligence system
- **Maintainability**: Clear structure, self-documenting code
- **Scalability**: Lambda auto-scales, Strands handles rate limiting
- **Cost Efficiency**: Pay only for actual usage

---

## 🎬 Demo Flow for Meetup

1. **Show a simple request**: "Show me revenue for last 30 days"
2. **Demonstrate multi-query**: "Analyze our business performance"
3. **Highlight the insights**: Show how the AI provides context
4. **Open the code**: Walk through the key sections
5. **Modify on the fly**: Add a new query type live
6. **Show the logs**: Demonstrate observability

---

## 🏁 Conclusion

This example demonstrates that with Strands Agent, you can build sophisticated MCP tools that:
- Connect to real data sources
- Process complex business logic
- Leverage AI for intelligent analysis
- Maintain production-grade quality
- Stay maintainable and extensible

The combination of Strands Agent's simplicity and power makes it an ideal choice for building MCP tools that need to bridge the gap between traditional data systems and modern AI capabilities.

**The Bottom Line**: Strands Agent lets you focus on your domain logic while it handles the AI complexity - exactly what you want when building MCP tools!