# Scripts Directory

This directory contains testing and utility scripts for the TradingAgents project.

## Test Scripts

### Core System Tests
- **`quick_test.py`** - Basic system validation script
  - Tests environment variables
  - Validates imports
  - Checks LLM connections

- **`test_system.py`** - Comprehensive health check system
  - Tests all components
  - Validates API connections
  - Checks dependencies

### Embedding Model Tests
- **`test_embedding_models.py`** - Tests custom endpoint embedding models
  - Tests which embedding models are available at your endpoint
  - Provides configuration recommendations

- **`test_ollama_embeddings.py`** - Tests Ollama embedding models
  - Discovers available Ollama embedding models
  - Tests model functionality and vector dimensions
  - Provides setup recommendations

- **`test_ollama_memory.py`** - Tests TradingAgents memory system with Ollama
  - Validates embedding integration
  - Tests memory storage and retrieval
  - Confirms system configuration

## Usage

All scripts should be run from the project root directory:

```bash
# Run from project root
python scripts/quick_test.py
python scripts/test_system.py
python scripts/test_ollama_embeddings.py
# etc.
```

Make sure your conda environment is activated before running:

```bash
conda activate tradingagents
python scripts/quick_test.py
```