# 🤖 Agno Agent Builder Team

A **meta-agent system** that automatically generates complete, production-ready Agno agents from natural language descriptions.

> **Built with Agno** | **Uses Knowledge Base** | **Sequential Execution** | **Production-Ready Output**

---

## 🎯 What It Does

Give it a request like:
```
"Build an agent that searches GitHub repositories for Python projects"
```

Get back a **complete agent package**:
```
outputs/github_search_agent_20251004/
├── main.py              # Working Agno agent code
├── README.md            # Full documentation
├── requirements.txt     # All dependencies
└── .env.example         # Environment setup
```

**Ready to run immediately!**

---

## ✨ Features

### 🚀 **Full Agent Generation**
- **Complete code packages** - Not just snippets, full working agents
- **4 files per agent** - Code, docs, dependencies, and config
- **Production-ready** - Error handling, type hints, best practices
- **Customizable** - Memory, tools, knowledge, reasoning

### 🧠 **Intelligent System**
- **3-step process** - Requirements → Documentation → Code
- **Live Agno docs** - Uses knowledge base with current Agno patterns
- **Smart analysis** - Understands vague requests and fills gaps
- **Auto-validation** - Checks for correct imports and patterns

### 📦 **Generated Agents Support**
- **Multiple tools** - GitHub, DuckDuckGo, YFinance, and more
- **Team coordination** - Single agents or multi-agent teams
- **Memory & storage** - Conversation history and persistence
- **Knowledge bases** - RAG integration for domain knowledge

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **OpenAI API Key** (required)

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd example_2_agent_builder

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### First Run

```bash
# Run the agent builder
python main.py
```

**That's it!** Check the `outputs/` directory for your generated agent.

---

## 📖 Usage

### Basic Usage

Edit `main.py` and change the example request:

```python
# In main.py, modify this line:
example_1 = "Build an agent that searches GitHub repositories for Python projects"

# Try these examples:
example_2 = "Build an agent that analyzes CSV data and remembers previous analyses"
example_3 = "Build a content writing team with a researcher and a writer"
example_4 = "Build a financial analyst agent with stock data and news"
```

### Programmatic Usage

```python
import asyncio
from main import build_agent

async def create_my_agent():
    result = await build_agent(
        user_request="Build an agent that summarizes research papers",
        save_output=True
    )
    print(f"Agent generated: {result}")

asyncio.run(create_my_agent())
```

### Using Generated Agents

```bash
# 1. Navigate to generated agent
cd outputs/github_search_agent_20251004/

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up API keys
cp .env.example .env
# Edit .env with your keys

# 4. Run the agent
python main.py
```

---

## 🏗️ How It Works

### Sequential 3-Step Process

```
User Request
     ↓
┌─────────────────────────┐
│ 1. Requirements Analyst │
│    Parse request        │
│    Extract features     │
│    Output JSON spec     │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ 2. Agno Docs Expert     │
│    Query knowledge base │
│    Fetch examples       │
│    Get best practices   │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ 3. Code Generator       │
│    Generate main.py     │
│    Generate README.md   │
│    Generate config files│
└───────────┬─────────────┘
            ↓
    Complete Package
```

### Knowledge Base System

The system uses **Agno's Knowledge** feature with:
- **LanceDB** vector database
- **OpenAI embeddings** for semantic search
- **Hybrid search** for accuracy
- **Persistent storage** (loads once, reuses)

---

## 📁 Project Structure

```
example_2_agent_builder/
│
├── main.py                    # Main agent builder (3-step execution)
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore patterns
│
├── tools/                     # Custom validation tools
│   ├── __init__.py
│   └── code_validator.py     # Code quality checker
│
├── outputs/                   # Generated agent packages
│   └── .gitkeep
│
├── tmp/                       # Temporary files (gitignored)
│   ├── lancedb/              # Knowledge base vector DB
│   └── agents.db             # Agent conversation history
│
└── docs/                      # Documentation
    ├── ARCHITECTURE.md        # System design
    └── TROUBLESHOOTING.md    # Common issues
```

---

## 🎨 Example Outputs

### Example 1: GitHub Search Agent

**Request**: "Build an agent that searches GitHub repositories"

**Generated**:
- Single agent with GitHub tools
- Repository search and filtering
- README parsing capabilities
- ~200 lines of production code

### Example 2: Data Analyst with Memory

**Request**: "Build an agent that analyzes CSV data and remembers analyses"

**Generated**:
- Agent with file processing tools
- SQLite memory for conversation history
- Pandas integration for data analysis
- Session persistence across runs

### Example 3: Content Writing Team

**Request**: "Build a team with a researcher and writer"

**Generated**:
- Multi-agent team (coordinate mode)
- Web search researcher
- Content writer with synthesis
- Team coordination and handoffs

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-your-openai-key-here

# Optional (for generated agents)
GITHUB_TOKEN=ghp-your-github-token
ANTHROPIC_API_KEY=your-anthropic-key
```

### Customization

Edit agent instructions in `main.py`:

```python
# Modify Code Generator behavior
code_generator = Agent(
    name="Code Generator",
    model=OpenAIChat(id="gpt-4o"),  # Change model
    instructions=[
        # Add custom instructions here
    ]
)
```

---

## 🎯 Success Criteria

A generated agent package is successful when it includes:

✅ **Complete main.py** - Working Agno agent code  
✅ **Comprehensive README** - Setup and usage docs  
✅ **All dependencies** - requirements.txt with versions  
✅ **Environment template** - .env.example with required keys  
✅ **Best practices** - Type hints, error handling, docstrings  
✅ **Immediately runnable** - After basic setup  

---

## 🤝 Contributing

We welcome contributions! Areas for improvement:

- **More tool templates** - Support for additional Agno tools
- **Better validation** - Enhanced code quality checks
- **UI/CLI** - Interactive interface for agent building
- **Examples gallery** - More generated agent examples
- **Testing** - Unit and integration tests

---

## 📚 Learn More

### Agno Framework
- [Agno Documentation](https://docs.agno.com)
- [Agno GitHub](https://github.com/agno-agi/agno)
- [Agno Examples](https://docs.agno.com/examples)

### Related Projects
- [Example #1: TechBlog AI Writer Team](../example_1_techblog_team/)

---

## 📄 License

This project is part of the Agno hiring process examples.

---

## 🙏 Acknowledgments

- Built with [Agno](https://docs.agno.com) - High-performance agent framework
- Uses [OpenAI](https://openai.com) for LLM capabilities
- Knowledge base powered by [LanceDB](https://lancedb.com)

---

## 💬 Support

Having issues? Check:
1. [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
2. [Architecture Documentation](docs/ARCHITECTURE.md)
3. [Agno Documentation](https://docs.agno.com)

---

**Happy Agent Building! 🚀**

*Generated by Agno Agent Builder Team - A meta-agent system that builds agents*