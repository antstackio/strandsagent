# Serverless Agents: Real-World Tooling with Strands SDK, MCP, and AWS

## Talk Duration: 30-40 minutes

---

## Opening (2 minutes)

### Hook
"How many of you have built an AI agent that can *actually* do something? Not just chat, not just reason - but actually interact with real systems, query databases, call APIs, and deliver production value?"

### The Problem
- We're great at building chatbots
- We're great at building serverless applications
- But combining AI agents with real-world capabilities? That's where it gets tricky
- Today: Bridge that gap with production-ready patterns

### What You'll Learn
- Build agents that don't just think - they act
- Deploy them serverlessly for scale and cost efficiency
- Connect them to any system using open standards

---

## Part 1: Setting the Stage (5 minutes)

### The Agent Evolution
```
Gen 1: Chatbots → "How's the weather?"
Gen 2: RAG Systems → "What does our documentation say?"
Gen 3: Tool-Calling Agents → "Let me check that database for you"
Gen 4: Production Agents → "I've analyzed your business metrics and here's what I found..."
```

### Why Serverless for Agents?
1. **Stateless by Design**: Agents should be ephemeral
2. **Cost Efficient**: Pay only when agents work
3. **Auto-scaling**: Handle 1 or 10,000 requests
4. **Focus on Logic**: Not infrastructure

### The Stack We're Building
```
┌─────────────────┐
│   Claude/GPT    │  <-- LLM Brain
├─────────────────┤
│  Strands SDK    │  <-- Agent Framework
├─────────────────┤
│      MCP        │  <-- Tool Protocol
├─────────────────┤
│  AWS Lambda     │  <-- Serverless Runtime
├─────────────────┤
│   Real World    │  <-- Databases, APIs, Services
└─────────────────┘
```

---

## Part 2: Understanding the Components (8 minutes)

### Strands SDK: The Agent Framework

**What it is**: Python framework for building production agents

**Key Features**:
- Clean abstraction over LLMs
- Built-in tool support
- Structured outputs
- Production-ready patterns

**Show Code Snippet**:
```python
from strands import Agent
from strands.models.openai import OpenAIModel

agent = Agent(
    system_prompt="You are a helpful assistant",
    tools=[my_tool],
    model=OpenAIModel(model_id="gpt-4o")
)

response = Agent("What's the weather?")
```

### Model Context Protocol (MCP): The Universal Tool Language

**The Problem MCP Solves**:
- Every LLM provider has different tool formats
- Tools aren't portable between systems
- No standard for tool discovery

**MCP's Solution**:
- JSON-RPC based protocol
- Language agnostic
- Tool discovery and invocation
- Works with any LLM

**Architecture**:
```
Client (Claude, etc.) <--MCP--> Server (Your Tools)
                         │
                    ┌────┴────┐
                    │ Tools:  │
                    │ • Query │
                    │ • Search│
                    │ • Action│
                    └─────────┘
```

### AWS Lambda: The Serverless Platform

**Why Lambda for Agents**:
1. **Cold Start Acceptable**: Users expect AI latency
2. **Memory Efficient**: Most agent work is I/O bound
3. **Cost Model Aligns**: Sporadic, burst usage patterns
4. **Integration Rich**: Connect to any AWS service

---

## Part 3: Demo - Building a Weather Agent (7 minutes)

### The Simple Case: Weather Tool

**Show the Code Structure**:
```
lambda/weather/
├── weather_agent_handler.py  # Main handler
└── (deployed with dependencies layer)
```

**Walk Through weather_agent_handler.py**:
1. System prompt defines agent capabilities
2. HTTP tool for API calls
3. National Weather Service integration
4. Human-readable formatting

**Live Demo**:
```bash
# Test locally
{
  "prompt": "What's the weather in San Francisco?"
}

# Agent:
# 1. Gets coordinates for San Francisco
# 2. Calls NWS API with coordinates
# 3. Formats forecast in readable way
```

**Key Takeaways**:
- Agent handles multi-step workflows
- No hardcoded API logic
- Adapts to different location formats

---

## Part 4: Demo - Production Database Agent with MCP (10 minutes)

### The Real-World Case: Business Intelligence Agent

**Show the Architecture**:
```
┌──────────────┐     MCP      ┌─────────────┐
│   Client     │──────────────>│   Lambda    │
│ (Claude/App) │               │  MCP Server │
└──────────────┘               └──────┬──────┘
                                      │
                               ┌──────▼──────┐
                               │  PostgreSQL │
                               │   Database  │
                               └─────────────┘
```

**Walk Through the Code**:

1. **query_agent_handler.py** - Core business logic
   - Database connection management
   - Query execution functions
   - AI-powered analysis

2. **mcp_handler.py** - MCP Protocol implementation
   - Tool definitions
   - JSON-RPC handling
   - Request routing

**Show MCP Tool Definitions**:
```python
tools = [
    {
        "name": "query_business_data",
        "description": "Query business data and get AI-powered insights",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language query"
                }
            }
        }
    },
    # Additional tools...
]
```

**Live Demo Sequence**:

1. **Simple Query**:
   ```
   "Show me revenue for the last 30 days"
   ```
   - Agent analyzes request
   - Executes SQL query
   - Returns formatted data

2. **Complex Analysis**:
   ```
   "What are my top performing products and what trends do you see?"
   ```
   - Multiple queries executed
   - Data aggregation
   - AI-powered insights

3. **MCP in Action**:
   - Show how Claude desktop can connect
   - Same tool works in different contexts
   - Protocol handles discovery

**Production Considerations**:
- Connection pooling
- Query timeouts
- Error handling
- Security (parameter binding)

---

## Part 5: Deployment with AWS CDK (5 minutes)

### Infrastructure as Code

**Show AgentLambdaStack.ts**:
```typescript
// Key components
const dependenciesLayer = new lambda.LayerVersion(...);
const queryFunction = new lambda.Function(this, "QueryLambda", {
    runtime: lambda.Runtime.PYTHON_3_12,
    handler: "mcp_handler.handler",
    layers: [dependenciesLayer],
    environment: {
        DB_HOST: process.env.DB_HOST,
        // ... other env vars
    }
});
```

**Deployment Strategy**:
1. Dependencies in Lambda Layer (keep code readable)
2. Environment variables for configuration
3. Appropriate timeouts and memory
4. ARM architecture for cost savings

**Show Deployment**:
```bash
# Deploy the stack
npm run cdk deploy

# Output shows Lambda function URLs
# Ready for production use
```

---

## Part 6: Patterns and Best Practices (5 minutes)

### Pattern 1: Stateless Design
```python

def handler(event, context):
    # Each invocation is independent
    # No shared state between calls
    # Database/API for persistence

```

### Pattern 2: Tool Composition
```python

# Small, focused tools
execute_revenue_query()
execute_product_query()
execute_customer_query()

# Agent combines them intelligently
```

### Pattern 3: Error Handling
```python

@contextmanager
def get_db_connection():
    try:
        # Connect
        yield conn
    except Exception as e:
        # Graceful degradation
        return fallback_response()

```

### Pattern 4: Observability
- CloudWatch for logs
- X-Ray for tracing
- Metrics for usage patterns
- Cost tracking per invocation

### Security Considerations
1. **Never trust agent input**: Parameterized queries
2. **Principle of least privilege**: IAM roles
3. **Secrets management**: AWS Secrets Manager
4. **Network isolation**: VPC for databases

---

## Part 7: Scaling and Evolution (3 minutes)

### Scaling Patterns

**Horizontal Scaling**:
```
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Lambda 1│     │ Lambda 2│     │ Lambda 3│
└────┬────┘     └────┬────┘     └────┬────┘
     └───────────────┼───────────────┘
                     ▼
              [Shared Database]
```

**Tool Marketplace**:
- Deploy tools as separate functions
- Discovery through MCP
- Mix and match capabilities
- Language agnostic

### Future Evolution

**What's Next**:
1. **Stateful Workflows**: Step Functions + Agents
2. **Real-time Processing**: Lambda + Kinesis
3. **Edge Deployment**: Lambda@Edge for global agents
4. **Multi-Agent Systems**: Agents calling agents

---

## Closing (2 minutes)

### Key Takeaways

1. **Agents Need Tools**: Not just reasoning, but action
2. **Serverless Fits Perfectly**: Stateless, scalable, cost-effective
3. **Standards Matter**: MCP enables portability
4. **Production Ready**: These patterns work at scale

### Your Next Steps

1. **Start Simple**: Build a basic tool-calling agent
2. **Add MCP**: Make your tools portable
3. **Deploy Serverless**: Get to production quickly
4. **Iterate**: Add capabilities incrementally

### Resources

- **Code**: [GitHub repository link]
- **Strands SDK**: https://github.com/strands-ai/strands
- **MCP Specification**: https://modelcontextprotocol.io
- **AWS Lambda**: https://aws.amazon.com/lambda

### Q&A Prep Topics
- Cost optimization strategies
- Cold start mitigation
- Multi-region deployment
- Debugging serverless agents
- Integration with existing systems
- Comparison with container-based approaches

---

## Demo Backup Plans

**If Live Demo Fails**:
1. Have screenshots ready
2. Pre-recorded video backup
3. Local environment fallback

**Demo Data**:
- Use synthetic data
- Avoid real customer information
- Have multiple example queries ready

---

## Speaker Notes

### Timing Markers
- [ ] 5 min: Should be explaining MCP
- [ ] 15 min: Starting database agent demo
- [ ] 25 min: Wrapping up patterns
- [ ] 30 min: Q&A begins

### Energy Points
- Hook them with the opening question
- Build excitement during first demo
- Peak energy during MCP reveal
- Practical tone for patterns
- Inspiring close

### Audience Engagement
- "Raise hands: Who's built serverless?"
- "Anyone used LLM tools before?"
- "What systems would you connect?"

### Technical Depth Adjustments
- If audience is more AWS-focused: Emphasize Lambda patterns
- If audience is more AI-focused: Dive deeper into agent reasoning
- Have both paths ready

---

## Additional Materials

### Code Snippets for Quick Reference

**Basic Agent**:
```python
agent = Agent(
    system_prompt="You are a data analyst",
    tools=[database_tool],
    model=model
)
```

**MCP Tool Registration**:
```python
{
    "method": "tools/list",
    "result": {
        "tools": [...]
    }
}
```

**Lambda Handler Pattern**:
```python
def handler(event, context):
    # Parse input
    # Execute logic  
    # Return response
```

### Common Questions & Answers

**Q: Why not use containers?**
A: Lambda is simpler for stateless workloads, automatically scales, and you only pay for actual usage.

**Q: How do you handle long-running agent tasks?**
A: Break them into steps with Step Functions, or use SQS for async processing.

**Q: What about vendor lock-in?**
A: MCP makes tools portable. Core logic is in Python. Only the deployment is AWS-specific.

**Q: Cost comparison?**
A: For sporadic use (most agents), Lambda is 70-90% cheaper than always-on containers.

**Q: How do you test agents?**
A: Unit test tools separately, integration test with local Lambda runtime, use CloudWatch for production monitoring.