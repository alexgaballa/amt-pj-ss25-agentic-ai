# amt-pj-ss25-agentic-ai
## Orchestrated Multi-Agent AI System with LangGraph

A sophisticated multi-agent architecture that intelligently coordinates between specialized AI agents to handle complex, multi-faceted queries through task decomposition and sequential execution.

## Architecture Overview

This system implements an **orchestrated multi-agent architecture** consisting of:

- **Orchestrator Agent**: Central coordinator that analyzes queries, decomposes tasks, and routes to appropriate sub-agents
- **Search Agent**: Specialized in Wikipedia information retrieval and research tasks
- **Reasoning Agent**: Handles mathematical calculations, unit conversions, and analytical tasks

The agents communicate through a **LangGraph StateGraph** workflow with persistent memory and intelligent routing.

## ✨ Key Features

- **Multi-Agent Coordination**: Intelligent task routing and result synthesis
- **Token-Aware Context**: Adapted to the token window of Gemini 2.0 Flash to maximize message context
- **Long-Term-Memory**: Persona preserved across message interactions and across sessions
- **ReAct Pattern**: Reasoning + Acting cycles for complex problem solving
- **Efficient API Usage**: Rate limiting and batch operations
- **Multiple Interfaces**: Command-line and web-based UI options
- **Dual Implementation**: Standard tools and MCP (Model Context Protocol) support
- **Cutting-Edge Tool-Provisioning**: via Model Context Protocol

## Getting Started

### Installation

```bash
git clone https://github.com/alexgaballa/amt-pj-ss25-agentic-ai.git
cd amt-pj-ss25-agentic-ai
```

### Environment Setup

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

```bash
# ⚠️ Use Python 3.10, 3.11 or 3.12 – Python 3.13 is not yet supported
pip install -r requirements.txt
```

## Usage
### Web Interface (Recommended)

Launch the interactive web interface using Chainlit:

```bash
chainlit run chainlit_mcp_main.py
```

This provides:
- Interactive chat interface which opens automatically on a localhost
- Real-time conversation flow visualization
- Session-based short term memory
- User-based long term memory
- Token-aware context management

### Command Line Interface MCP Implementation

Start the MCP tools server:

```bash
python -m mcp_server_setup.mcp_tools_server
```

Run MCP-enabled agents:

```bash
python -m agents.mcp_sub_agent_search
python -m agents.mcp_sub_agent_reason
```

## Example Queries

The system handles various query types:

### Multi-Agent Orchestration
```
"What is the population of Germany's capital and what is 15% of that number?"
"Find Berlin's area and convert it from square kilometers to square miles"
"What happened on June 18, 1994 in Berlin according to Wikipedia?"
```

### Complex Multi-Step Reasoning
```
"Compare the GDP of Germany and UK according to Wikipedia and calculate the percentage difference"
"Find the exact first part of the Economy section on the Berlin Wikipedia page"
```

## Evaluation System

### LLM-as-a-Judge Framework

The system includes a comprehensive evaluation framework using:

- **PollMultihopCorrectness**: Factual accuracy and logical consistency assessment
- **MTBenchChatBotResponseQuality**: Overall response quality evaluation

### Running Evaluations

# Run LLM-as-a-Judge evaluation
python evaluate_system.py
```

Evaluation data format:
```json
{
  "prompt": "Your test query",
  "system_response": "Agent's response", 
  "reference": "Ground truth answer"
}
```


## Configuration Options

### Memory Settings
- **Thread-based Sessions**: Each conversation retains its own context for consistent reasoning and task execution.
- **User-based Persona**: Persistent profiles capture key user attributes (e.g. name, studies, interests) across sessions, enabling personalized interactions and memory continuity.

### Rate Limiting
- **API Quota Management**: 2-second delays between node transitions
- **Batch Operations**: Efficient multi-section Wikipedia retrieval
- **Error Recovery**: Graceful handling of API failures

### Agent Customization
- **Temperature Settings**: Control response creativity
- **Tool Selection**: Customize available tools per agent
- **Prompt Engineering**: Modify agent behavior and instructions

## Workflow Architecture

The system uses **LangGraph StateGraph** for workflow management:

```
START → Orchestrator → [Decision Point]
                     ↓
        [Search Agent] OR [Reasoning Agent]
                     ↓
              Delay Node (Rate Limiting)
                     ↓
              Result Synthesis
                     ↓
                    END
```

### State Management
```python
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
```

## Memory System

### Chainlit Implementation
- **Session-based Storage**: Persistent across browser sessions
- **Token-aware Context**: Intelligent context selection within limits
- **Graceful Degradation**: Fallback strategies for memory management

### Context Selection Algorithm
```python
def select_messages_by_tokens(
    conversation_memory: List[dict], 
    current_query: str, 
    max_tokens: int = 64000
) -> List[BaseMessage]:
    # Backward selection from recent messages
    # Official Gemini tokenizer for accuracy
    # Token limit enforcement
```

## Use Cases

- **Educational Research**: Multi-step information gathering and analysis
- **Data Analysis**: Combining search with mathematical calculations  
- **Content Creation**: Research-backed content with quantitative analysis
- **Decision Support**: Fact-gathering with analytical reasoning
- **Knowledge Management**: Enterprise information synthesis

## Troubleshooting

### Common Issues

**API Rate Limits:**
- Increase delay between node transitions
- Reduce batch sizes for tool calls

**Memory Errors:**
- Check token limits in context selection
- Verify conversation history cleanup
- Check "long_term_memory.json" for persistet user attributes

**Tool Loading Failures:**
- Ensure MCP server is running for MCP implementation
- Verify all dependencies are installed

## Dependencies

Key libraries:
- **LangChain**: Agent framework and tool integration
- **LangGraph**: Workflow orchestration and state management
- **Google Generative AI**: Gemini model integration
- **MCP**: Model Context Protocol Library
- **Chainlit**: Web interface framework
- **Requests**: HTTP API interactions

## Performance Metrics

The system tracks:
- **Response Accuracy**: Through LLM-as-a-Judge evaluation
- **Query Processing Time**: End-to-end latency measurement
- **Tool Usage Efficiency**: API call optimization metrics
- **Memory Utilization**: Context size and management efficiency
