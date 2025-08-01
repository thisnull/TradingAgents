# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Installation and Setup
```bash
# Create virtual environment
conda create -n tradingagents python=3.13
conda activate tradingagents

# Install dependencies
pip install -r requirements.txt
```

### Required Environment Variables
```bash
export FINNHUB_API_KEY=$YOUR_FINNHUB_API_KEY  # Required for financial data
export OPENAI_API_KEY=$YOUR_OPENAI_API_KEY    # Required for LLM agents

# For Ollama embedding setup (recommended)
ollama serve --host 0.0.0.0:10000  # Start Ollama server
ollama pull nomic-embed-text        # Download embedding model
```

### Running the Application
```bash
# CLI interface
python -m cli.main

# Direct Python usage
python main.py
```

## Architecture Overview

TradingAgents is a multi-agent LLM framework built with LangGraph that simulates a real trading firm with specialized agents:

### Core Components

**Main Entry Point**: `tradingagents/graph/trading_graph.py` - The `TradingAgentsGraph` class orchestrates the entire framework

**Agent Teams**:
- **Analysts** (`tradingagents/agents/analysts/`): Market, news, fundamentals, and social media analysts
- **Researchers** (`tradingagents/agents/researchers/`): Bull and bear researchers who debate analyst findings
- **Risk Management** (`tradingagents/agents/risk_mgmt/`): Conservative, neutral, and aggressive debators
- **Trader** (`tradingagents/agents/trader/`): Makes final trading decisions

**Data Flows** (`tradingagents/dataflows/`): Handles data fetching from various financial APIs (FinnHub, Yahoo Finance, Reddit, Google News)

**Graph Structure** (`tradingagents/graph/`):
- `setup.py`: Graph initialization and node/edge configuration
- `propagation.py`: Forward propagation through the agent workflow
- `conditional_logic.py`: Decision routing between agents
- `reflection.py`: Learning from past trading decisions
- `signal_processing.py`: Processing agent outputs and signals

### Key Configuration

Default configuration is in `tradingagents/default_config.py`. Key settings:
- `deep_think_llm`: Primary reasoning model (default: "o4-mini")  
- `quick_think_llm`: Fast response model (default: "gpt-4o-mini")
- `max_debate_rounds`: Number of research team debate rounds
- `online_tools`: Whether to use real-time data vs cached data

### Python API Usage

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Basic usage
ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())
_, decision = ta.propagate("NVDA", "2024-05-10")

# Custom configuration
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4o-mini"
config["max_debate_rounds"] = 2
ta = TradingAgentsGraph(debug=True, config=config)
```

### Agent State Management

The framework uses structured state objects:
- `AgentState`: Overall system state passed between agents
- `InvestDebateState`: State for investment research debates
- `RiskDebateState`: State for risk management discussions

### Memory and Reflection

The system includes a financial memory component (`tradingagents/agents/utils/memory.py`) that allows agents to learn from past decisions using the `reflect_and_remember()` method.

## File Structure Notes

- No formal test suite exists - testing is done through CLI and direct execution
- No build process - pure Python package
- Dependencies managed through `requirements.txt` and `pyproject.toml`
- CLI uses Typer framework with Rich for formatting
- The codebase supports multiple LLM providers (OpenAI, Anthropic, Google)