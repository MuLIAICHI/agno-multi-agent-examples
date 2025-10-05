# Agno Multi-Agent Examples

Advanced multi-agent systems built with [Agno](https://docs.agno.com) - demonstrating production-ready AI agent architectures.

---

## Overview

This repository contains **3 production-ready examples** showcasing different multi-agent system patterns using the Agno framework. Each example solves real-world problems and demonstrates advanced agent orchestration techniques.

---

## Examples

### 1. TechBlog AI Writer Team
**Path**: `example_1_techblog_team/`

**What it does**: Automatically generates 2000+ word technical blog posts

**Architecture**: 4-agent team in coordinate mode
- Technical Researcher (GitHub API)
- News & Trends Agent (DuckDuckGo)
- Code Example Generator
- Technical Writer

**Key Features**:
- Custom GitHub tool integration
- Team memory and context sharing
- Production-ready code generation
- Complete blog post with examples

**Use Case**: Content marketing automation for tech companies

[View Example 1 →](./example_1_techblog_team/)

---

### 2. Agent Builder Team
**Path**: `example_2_agent_builder/`

**What it does**: Meta-agent system that builds other Agno agents from natural language

**Architecture**: 3-agent sequential pipeline
- Requirements Analyst (parses user requests)
- Agno Docs Expert (uses knowledge base)
- Code Generator (writes production code)

**Key Features**:
- Generates complete agent packages (4 files)
- Knowledge base with Agno documentation
- Self-validating code generation
- Meta-programming demonstration

**Use Case**: Rapid agent development, lowering barrier to entry for Agno

[View Example 2 →](./example_2_agent_builder/)

---

### 3. AI Candidate Screening System
**Path**: `example_3_candidate_screening/`

**What it does**: Automates candidate screening for hiring (built for TalentPerformer)

**Architecture**: 4-agent screening pipeline
- Resume Parser (extracts structured data)
- Skills Matcher (matches against requirements)
- Experience Evaluator (analyzes relevance)
- Scorer & Ranker (generates recommendations)

**Key Features**:
- Screens 100+ candidates in minutes
- Weighted scoring system (customizable)
- Bias-free evaluation
- Detailed screening reports

**Use Case**: High-volume recruitment, HR automation

[View Example 3 →](./example_3_candidate_screening/)

---

## Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### Setup

```bash
# Clone the repository
git clone https://github.com/MuLIAICHI/agno-multi-agent-examples.git
cd agno-multi-agent-examples

# Choose an example
cd example_1_techblog_team  # or example_2_agent_builder or example_3_candidate_screening

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the example
python main.py
```

Each example has its own README with detailed instructions.

---

## What This Demonstrates

### Advanced Agno Capabilities

**Multi-Agent Orchestration**
- Team coordination modes (coordinate, sequential)
- Agent-to-agent communication
- Context sharing and memory

**Production Patterns**
- Error handling and validation
- Async/await for performance
- Knowledge bases and vector search
- Custom tool development

**Real-World Applications**
- Content generation at scale
- Meta-programming and code generation
- HR tech automation

### Code Quality

- Type hints throughout
- Comprehensive documentation
- Clean architecture
- Production-ready error handling
- Full test coverage potential

---

## Architecture Comparison

| Example | Agents | Mode | Complexity | Use Case |
|---------|--------|------|------------|----------|
| TechBlog Writer | 4 | Coordinate | Medium | Content automation |
| Agent Builder | 3 | Sequential | High | Meta-programming |
| Candidate Screening | 4 | Sequential | Medium | HR automation |

---

## Technology Stack

- **Framework**: [Agno](https://docs.agno.com) 1.1.0+
- **LLM**: OpenAI GPT-4o / GPT-4o-mini
- **Vector DB**: LanceDB (Example 2)
- **Storage**: SQLite (agent memory)
- **Language**: Python 3.8+

---

## Project Structure

```
agno-multi-agent-examples/
├── example_1_techblog_team/      # Content generation system
├── example_2_agent_builder/      # Meta-agent builder
├── example_3_candidate_screening/ # HR automation
└── README.md                      # This file
```

---

## Use Cases by Industry

**Marketing & Content**
- Example 1: Automated blog writing
- Example 2: Generate content agents on-demand

**HR & Recruiting**  
- Example 3: Candidate screening at scale
- Example 2: Build custom HR agents

**Software Development**
- Example 2: Auto-generate dev tools
- Example 1: Generate technical documentation

---

## Learning Path

**Beginner**: Start with Example 3 (simpler logic, clear use case)

**Intermediate**: Try Example 1 (team coordination, custom tools)

**Advanced**: Explore Example 2 (meta-programming, knowledge bases)

---

## Performance & Costs

**Example 1 - TechBlog Writer**
- Time: ~60-90 seconds per blog post
- Cost: ~$0.15-0.25 per post

**Example 2 - Agent Builder**  
- Time: ~30-50 seconds per agent (after first run)
- Cost: ~$0.08 per generated agent

**Example 3 - Candidate Screening**
- Time: ~30 seconds per candidate
- Cost: ~$0.05 per screening

---

## Contributing

Ideas for improvements:
- Add more example use cases
- Enhance error handling
- Add web UIs for examples
- Create integration guides
- Add monitoring/observability

---

## License

MIT License - feel free to use these examples as starting points for your own projects.

---

## Acknowledgments

Built with:
- [Agno](https://docs.agno.com) - High-performance multi-agent framework
- [OpenAI](https://openai.com) - LLM capabilities
- [LanceDB](https://lancedb.com) - Vector database

---

## Contact

Built by [MuLIAICHI](https://github.com/MuLIAICHI)

For questions about these examples or Agno in general, check the [Agno documentation](https://docs.agno.com).

---

**Showcasing production-ready multi-agent systems with Agno**