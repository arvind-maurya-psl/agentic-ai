# Agentic AI Project Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    User/Application Layer                       │
│  - Web UI (future), CLI, API, Lambda, Scripts                   │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│        Agentic AI Application (Main Orchestrator)               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  AgentCoordinator                                        │   │
│  │  - Task routing and delegation                          │   │
│  │  - Multiple agent management                            │   │
│  │  - Workflow orchestration                               │   │
│  └────┬────────────────────┬─────────────────┬────────────┘   │
│       │                    │                 │                 │
│  ┌────▼──┐  ┌────────────▼┐  ┌──────────────▼┐  ┌──────────┐ │
│  │Analytics Asset   Customer  │Content   │ │
│  │Agent   │  Service Agent    │Generation│ │
│  │        │  │                │Agent     │ │
│  └────────┘  └────────────┘  └──────────┘  └──────────┘ │
│                   ▲              ▲             ▲         │
│  ┌────────────────┴──────────────┴─────────────┘         │
│  │                                                        │
│  │  All Agents Share:                                    │
│  │  - MemoryManager (Conversation history)              │
│  │  - Plugins (Calculator, WebSearch, DataAnalysis)     │
│  │  - System prompts and context                        │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│  Semantic Kernel Framework                                      │
│  - Function orchestration                                       │
│  - Plugin management                                            │
│  - Prompt execution                                             │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│  Bedrock Service                                                │
│  - Model invocation                                             │
│  - Streaming support                                            │
│  - Error handling & retries                                     │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│  AWS Bedrock API                                                │
│  - Claude 3.5 Sonnet, Other models                             │
│  - Foundation models across regions                             │
└───────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Supporting Systems                           │
├─────────────────────────────────────────────────────────────────┤
│  Memory          Configuration      Logging        Plugins      │
│  ├─ In-Memory    ├─ AWS Config     ├─ File       ├─ Calculator │
│  ├─ Redis*       ├─ SK Config      ├─ Console    ├─ WebSearch  │
│  └─ Database*    ├─ Agent Config   └─ CloudWatch └─ DataAnalysis
│  (*planned)      └─ App Config                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
Input (Task/Prompt)
       │
       ▼
AgentCoordinator
  │ Routes to appropriate agent based on keywords
  │
  ├─→ AnalyticsAgent
  ├─→ CustomerServiceAgent  
  └─→ ContentGenerationAgent
       │
       ├─→ Add context to MemoryManager
       ├─→ Call agent.plan() for action steps
       ├─→ Generate system prompt
       │
       ▼
BedrockService
  │
  ├─→ Prepare messages with context
  ├─→ Invoke AWS Bedrock API
  ├─→ Handle streaming responses
  │
  ▼
Agent Response
  │
  ├─→ Store in conversation history
  ├─→ Log execution metrics
  │
  ▼
Output (Result)
```

## Component Interaction

```
┌─────────────────────────────────────────────────────────┐
│  External User System                                   │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ execute_task/execute_workflow
                  ▼
         ┌────────────────────┐
         │ AgenticAIApp       │
         └────────┬───────────┘
                  │
         ┌────────▼─────────────────┐
         │ AgentCoordinator         │
         │ Routing (route_task)     │
         │ Delegation (delegate)    │
         └────────┬─────────────────┘
                  │
    ┌─────────────┼──────────────┐
    │             │              │
    ▼             ▼              ▼
 Agent1        Agent2         Agent3
    │             │              │
    └─────────────┼──────────────┘
                  │
         ┌────────▼──────────┐
         │ MemoryManager     │
         │ add_message()     │
         │ get_recent()      │
         │ search_memory()   │
         └────────┬──────────┘
                  │
         ┌────────▼──────────────┐
         │ BedrockService        │
         │ invoke_model()        │
         │ invoke_streaming()    │
         └────────┬──────────────┘
                  │
         ┌────────▼──────────────┐
         │ AWS Bedrock API       │
         │ (/foundation-model)   │
         └───────────────────────┘
```

## Agent Lifecycle

```
Agent Creation
    │
    ├─→ Initialize with Bedrock service
    ├─→ Set role and name
    ├─→ Initialize MemoryManager (if enabled)
    │
    ▼
Agent Ready
    │
    ├─→ receive task via execute_task(task)
    │
    ▼
Plan Generation
    │
    ├─→ plan(objective, context) - returns action steps
    │
    ▼
Message Processing
    │
    ├─→ add_message("user", task description)
    ├─→ get_conversation_context()
    ├─→ get_system_prompt()
    │
    ▼
Bedrock Invocation
    │
    ├─→ bedrock_service.invoke_model(
        messages=[...],
        temperature=0.7,
        system_prompt=...
    )
    │
    ▼
Response Processing
    │
    ├─→ add_message("assistant", response)
    ├─→ Log execution metrics
    ├─→ Store in memory
    │
    ▼
Task Complete / Error Handling
    │
    ├─→ Return result dictionary
    └─→ Log errors if failed
```

## Plugin Architecture

```
BasePlugin (Abstract)
    │
    ├─→ CalculatorPlugin
    │   ├─→ add(a, b)
    │   ├─→ subtract(a, b)
    │   ├─→ multiply(a, b)
    │   ├─→ divide(a, b)
    │   ├─→ power(base, exp)
    │   └─→ square_root(a)
    │
    ├─→ WebSearchPlugin
    │   ├─→ search(query, max_results)
    │   ├─→ get_page_content(url)
    │   └─→ get_current_weather(location)
    │
    └─→ DataAnalysisPlugin
        ├─→ analyze_sentiment(text)
        ├─→ extract_entities(text)
        ├─→ summarize_text(text, num_sentences)
        └─→ statistical_summary(data)
```

## Configuration Hierarchy

```
AppConfig (Top-level)
    │
    ├─→ AWSConfig
    │   ├─→ region
    │   ├─→ bedrock_model_id
    │   ├─→ max_retries
    │   └─→ timeout_seconds
    │
    ├─→ SemanticKernelConfig
    │   ├─→ log_enabled
    │   ├─→ log_level
    │   ├─→ function_call_retry_max_attempts
    │   └─→ timeout_seconds
    │
    └─→ AgentConfig
        ├─→ max_iterations
        ├─→ temperature
        ├─→ timeout_seconds
        ├─→ enable_memory
        └─→ memory_type (in_memory/redis)
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   GitHub Actions CI/CD                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │PR Validation│  │Build    │  │Deploy   │  │Release  │  │
│  │  (lint,     │  │Docker   │  │to AWS   │  │Manage   │  │
│  │  test,      │  │Image    │  │        │  │Package │  │
│  │  security)  │  │        │  │        │  │        │  │
│  └────────────┘  └──────────┘  └──────────┘  └──────────┘  │
│         │              │             │            │        │
│         └──────────────┴─────────────┴────────────┘        │
│                        │                                    │
└────────────────────────┼────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
   ┌────▼─────┐                   ┌──────▼──────┐
   │  ECR      │                   │  S3        │
   │(Container │                   │(Source)   │
   │Registry) │                   └──────┬──────┘
   └────┬─────┘                          │
        │                                 │
   ┌────▼──────────────────────────────────▼──┐
   │         AWS Lambda/ECS/EC2                │
   │    (Application Runtime Environments)     │
   └────┬───────────────────────────────┬────┘
        │                               │
   ┌────▼──────┐             ┌──────────▼────┐
   │Bedrock API│             │CloudWatch     │
   │(LLM)      │             │(Monitoring)   │
   └───────────┘             └───────────────┘
```

## Security Model

```
┌─────────────────────────────────────────────────────────────┐
│                  GitHub OIDC Token                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Exchanged for
                     ▼
         ┌───────────────────────┐
         │ AWS STS AssumeRole    │
         │ (No long-lived creds) │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │ Temporary AWS Creds   │
         │ (15 min-1 hour TTL)   │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │  agentic-ai-role IAM  │
         │  (Least privilege)    │
         ├───────────────────────┤
         │ ✓ Bedrock invoke      │
         │ ✓ S3 artifacts        │
         │ ✓ CloudWatch logs     │
         │ ✗ Other AWS services  │
         └───────────────────────┘
```

## Memory Architecture

```
┌─────────────────────────────────────────┐
│      MemoryManager                      │
├─────────────────────────────────────────┤
│                                         │
│  Conversation History Storage           │
│  ┌─────────────────────────────────┐   │
│  │ [Message1] → [Message2] → [...] │   │
│  │ timestamp   timestamp            │   │
│  │ role        role                 │   │
│  │ content     content              │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Operations:                            │
│  • add_message(msg)                     │
│  • get_recent_messages(limit)           │
│  • search_memory(query)                 │
│  • get_context_window(hours)            │
│  • clear()                              │
│                                         │
│  Storage Options:                       │
│  • In-Memory (fast, ephemeral)          │
│  • Redis (persistent, shared)           │
│  • Database (audit trail, long-term)*   │
│                                         │
│  (*planned for future versions)         │
└─────────────────────────────────────────┘
```

## Error Handling Flow

```
    Agent Task Execution
            │
            ▼
    Try to Execute
            │
     │──────┴──────│
     │             │
   Success       Error
     │             │
     ▼             ▼
Return Result   Handle Exception
              │
         ┌────┴────────────────────┐
         │                         │
    Known Error          Unknown Error
         │                    │
         ├─ Task Error       ├─ Log & Report
         ├─ Model Error      ├─ Return error
         ├─ Timeout          └─ Notify (optional)
         └─ etc.
              │
              ▼
        Return Error Response
         {
           "status": "failed",
           "task_id": "...",
           "error": "Error message"
         }
```

## Performance Characteristics

```
Single Task Execution:
  - Parse input: 10ms
  - Route to agent: 5ms
  - Generate prompt: 20ms
  - Bedrock invocation: 1000-5000ms (depends on model)
  - Process response: 50ms
  ─────────────────────────────
  Total: ~1-6 seconds per task

Workflow (5 tasks):
  - Sequential: ~5-30 seconds
  - Parallel (if implemented): ~5-6 seconds

Memory Impact:
  - Base application: ~50MB
  - Per agent: ~5-10MB
  - Per 1000 messages: ~1-2MB
  - With Redis: ~100MB (Redis remote storage)
```

## Scalability Considerations

```
Vertical Scaling:
  • Increase EC2/Lambda memory
  • Increase CPU allocation
  • Optimize Bedrock model selection

Horizontal Scaling:
  • Multiple Lambda functions (concurrent)
  • ECS cluster with auto-scaling
  • Load balancer in front
  • Redis for shared memory

Database:
  • PostgreSQL for conversation archival
  • Read replicas for analytics
  • Connection pooling

Model:
  • Bedrock provisioned throughput
  • Model caching (if available)
```

## Monitoring & Observability

```
Application Metrics:
  • Task execution time
  • Success/failure rate
  • Model invocation count
  • Error types and frequency

System Metrics:
  • Memory usage
  • CPU utilization
  • I/O operations
  • Network traffic

Business Metrics:
  • Agents active
  • Tasks processed
  • Average resolution time
  • Agent performance comparison

Logging:
  • Application logs → CloudWatch Logs
  • Structured JSON format
  • Severity levels
  • Request tracing
```

This architecture document provides a comprehensive view of how all components interact and integrate together to form the complete Agentic AI system.
