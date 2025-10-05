# 🏗️ Architecture Documentation

## System Overview

The Agno Agent Builder Team is a **meta-agent system** that uses AI to generate other AI agents. It employs a sequential, three-stage architecture with knowledge-based reasoning to produce production-ready Agno code packages.

---

## Core Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│                   User Request                           │
│  "Build an agent that searches GitHub repositories"      │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│              Sequential Execution Engine                 │
│  (Async/Await Pattern for Agno Agents)                  │
└────────────────────┬────────────────────────────────────┘
                     ↓
        ┌────────────┴────────────┐
        ↓                          ↓
┌──────────────┐          ┌──────────────────┐
│  Knowledge   │          │  Agent State     │
│  Base        │          │  Management      │
│  (LanceDB)   │          │  (SQLite)        │
└──────┬───────┘          └────────┬─────────┘
       │                           │
       ↓                           ↓
┌─────────────────────────────────────────────────────────┐
│              Three-Agent Pipeline                        │
│                                                          │
│  Agent 1: Requirements Analyst                          │
│           ↓                                             │
│  Agent 2: Agno Docs Expert                             │
│           ↓                                             │
│  Agent 3: Code Generator                               │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│              File Generation & Validation                │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│         Complete Agent Package (4 files)                 │
│  • main.py  • README.md  • requirements.txt  • .env     │
└─────────────────────────────────────────────────────────┘
```

---

## Agent Specifications

### Agent 1: Requirements Analyst

**Purpose**: Parse natural language requests into structured specifications

**Model**: GPT-4o

**Input**: User's natural language request

**Output**: JSON specification
```json
{
  "type": "single_agent" | "agent_team",
  "name": "Agent Name",
  "purpose": "Description",
  "features": {
    "tools": ["GitHub", "DuckDuckGo"],
    "memory": true,
    "knowledge": false,
    "reasoning": false
  },
  "model": "gpt-4o",
  "instructions": "Agent behavior description"
}
```

**Key Behaviors**:
- Extracts explicit requirements from request
- Infers missing requirements based on context
- Normalizes tool names to Agno conventions
- Determines single agent vs. team structure

**Why It's Needed**: 
Converts ambiguous human requests into precise technical specifications that downstream agents can act on.

---

### Agent 2: Agno Docs Expert

**Purpose**: Fetch relevant Agno documentation and code examples

**Model**: GPT-4o

**Tools**: 
- Knowledge base (LanceDB + OpenAI embeddings)
- SQLite database for conversation history

**Input**: Requirements specification (JSON)

**Output**: Comprehensive documentation including:
- Relevant code examples
- Import patterns
- Configuration examples
- Best practices
- Tool integration guides

**Knowledge Base Details**:
```python
Knowledge(
    vector_db=LanceDb(
        uri="./tmp/lancedb",
        table_name="agno_docs_knowledge",
        search_type=SearchType.hybrid,  # Keyword + semantic
        embedder=OpenAIEmbedder(id="text-embedding-3-small")
    )
)
```

**Data Source**: `https://docs.agno.com/llms-full.txt`

**Key Behaviors**:
- Semantic search through Agno documentation
- Filters examples by relevance to requirements
- Prioritizes current API patterns over deprecated ones
- Provides multiple examples for complex requests

**Why It's Needed**:
Ensures generated code uses current, correct Agno patterns. Static templates would become outdated.

---

### Agent 3: Code Generator

**Purpose**: Generate complete, production-ready code packages

**Model**: GPT-4o

**Input**: 
- Requirements specification
- Agno documentation and examples

**Output**: Four files with specific markers
```
=== FILE: main.py ===
=== FILE: README.md ===
=== FILE: requirements.txt ===
=== FILE: .env.example ===
```

**Key Behaviors**:
- Generates complete, working code (no placeholders)
- Follows Agno best practices from documentation
- Includes error handling and type hints
- Creates comprehensive documentation
- Validates output format with markers

**Critical Instructions**:
- MUST generate files immediately (no asking permission)
- MUST use exact file markers for parsing
- MUST include complete, runnable code
- NO summaries or suggestions - only actual code

**Why It's Needed**:
Synthesizes requirements and documentation into working code. The forceful instructions prevent conversational behavior.

---

## Data Flow

### Sequential Execution Pattern

```python
# Step 1: Parse requirements
requirements = await requirements_analyst.arun(user_request)
# Output: JSON specification

# Step 2: Fetch documentation
docs = await agno_docs_expert.arun(
    f"Given requirements: {requirements}, provide Agno examples"
)
# Output: Documentation and code examples

# Step 3: Generate code
code = await code_generator.arun(
    f"Requirements: {requirements}\nDocs: {docs}\nGENERATE NOW"
)
# Output: Four complete files
```

**Why Sequential vs. Team?**

Initially used `Team(mode="coordinate")` but found issues:
- ❌ Teams can be too conversational
- ❌ Agents might ask for confirmation
- ❌ Less control over execution order
- ❌ Harder to debug individual steps

Sequential execution provides:
- ✅ Full control over each step
- ✅ Clear progress visibility
- ✅ Better error handling
- ✅ Guaranteed execution order

---

## Knowledge Base System

### Architecture

```
User Request → Agno Docs Expert
                      ↓
            Search Knowledge Base
                      ↓
        ┌─────────────┴─────────────┐
        ↓                           ↓
   Keyword Search            Vector Search
   (Exact matches)         (Semantic similarity)
        ↓                           ↓
        └─────────────┬─────────────┘
                      ↓
              Hybrid Results
              (Ranked by relevance)
                      ↓
              Return Documentation
```

### Storage Details

**Location**: `./tmp/lancedb/`

**Table**: `agno_docs_knowledge`

**Search Type**: Hybrid (keyword + semantic)

**Embeddings**: OpenAI `text-embedding-3-small`

**Initialization**: First run only (persists after)

### Performance Characteristics

- **First run**: ~30-60 seconds (downloads + embeds docs)
- **Subsequent runs**: ~2-5 seconds (uses cached embeddings)
- **Storage size**: ~50-100MB
- **Query latency**: ~500ms per search

---

## File Generation Process

### Parsing Algorithm

```python
def parse_generated_files(response: str) -> Dict[str, str]:
    files = {}
    current_file = None
    current_content = []
    in_code_block = False
    
    for line in response.split("\n"):
        if "=== FILE:" in line:
            # Save previous file
            if current_file and current_content:
                files[current_file] = "\n".join(current_content)
            
            # Start new file
            current_file = extract_filename(line)
            current_content = []
            in_code_block = False
            
        elif current_file:
            if line.startswith("```"):
                in_code_block = not in_code_block
            elif in_code_block:
                current_content.append(line)
    
    return files
```

### File Structure

Each generated package follows this structure:
```
outputs/agent_name_timestamp/
├── main.py           # 100-300 lines typically
├── README.md         # 50-150 lines
├── requirements.txt  # 5-15 lines
└── .env.example      # 3-10 lines
```

---

## Design Decisions

### Why No Templates?

**Decision**: Use live documentation instead of hardcoded templates

**Rationale**:
- ✅ Always uses current Agno patterns
- ✅ Adapts to framework updates automatically
- ✅ More flexible for diverse requests
- ❌ Templates would become outdated
- ❌ Templates limit creativity

**Trade-off**: Slightly slower (documentation lookup) but more accurate and flexible.

---

### Why Knowledge Base Instead of MCP?

**Initial Approach**: Context7 MCP for live documentation

**Changed To**: LanceDB knowledge base with embedded docs

**Rationale**:
- ✅ No Node.js dependency
- ✅ Works offline after first run
- ✅ Faster for repeated queries
- ✅ Full control over documentation source
- ✅ No rate limits
- ❌ MCP requires Node.js
- ❌ MCP has potential network issues
- ❌ MCP might have rate limits

**Trade-off**: Initial setup time for documentation loading, but better reliability.

---

### Why Async/Await Throughout?

**Decision**: Use async/await pattern for all agent calls

**Rationale**:
- ✅ Required for Knowledge base operations
- ✅ Better for future MCP integration
- ✅ Allows parallel operations (future enhancement)
- ✅ Standard pattern in modern Python
- ✅ Required by Agno's async methods

---

### Why Force Code Generation?

**Problem**: Initial version asked for confirmation before generating

**Solution**: Aggressive instructions + retry logic

```python
instructions=[
    "DO NOT ask for permission",
    "DO NOT suggest modifications", 
    "START GENERATING NOW",
]

# Plus retry if needed
if "=== FILE:" not in response:
    response = await code_generator.arun(
        "GENERATE FILES NOW - NO ASKING"
    )
```

**Rationale**: 
- LLMs default to being helpful and polite
- Politeness means asking before doing
- We need action, not conversation
- Forceful instructions override default behavior

---

## Performance Characteristics

### Execution Time

**First Run** (with knowledge base loading):
- Requirements Analyst: ~5-10 seconds
- Load Agno Docs: ~30-60 seconds
- Agno Docs Expert: ~10-15 seconds
- Code Generator: ~20-30 seconds
- **Total**: ~65-115 seconds

**Subsequent Runs** (knowledge base cached):
- Requirements Analyst: ~5-10 seconds
- Agno Docs Expert: ~5-10 seconds
- Code Generator: ~20-30 seconds
- **Total**: ~30-50 seconds

### Cost Estimates (OpenAI API)

Per agent generation (approximate):
- Requirements Analyst: ~$0.01
- Agno Docs Expert: ~$0.02 (includes embeddings)
- Code Generator: ~$0.05
- **Total per generation**: ~$0.08

First run adds embedding cost: +~$0.10

---

## Error Handling

### Validation Points

1. **Environment Check**: OPENAI_API_KEY exists
2. **Knowledge Base**: Loads successfully
3. **Requirements**: Valid JSON output
4. **Documentation**: Non-empty response
5. **Code Generation**: File markers present
6. **File Saving**: All 4 files extracted

### Retry Logic

```python
# If code generation fails to produce files
if "=== FILE:" not in generated_code:
    print("Retrying with forceful instructions...")
    generated_code = await code_generator.arun(
        "GENERATE FILES NOW WITH === FILE: === MARKERS"
    )
```

### Failure Modes

| Failure | Cause | Recovery |
|---------|-------|----------|
| No API key | Missing .env | User prompted to create .env |
| Knowledge load fails | Network issue | Error shown, suggests retry |
| Invalid requirements JSON | Analyst error | Show raw output for debugging |
| No file markers | Generator being conversational | Automatic retry with stronger instructions |
| File parse error | Unexpected format | Show full response for debugging |

---

## Future Enhancements

### Planned Features

1. **Parallel Agent Execution**: Run docs fetching while analyzing requirements
2. **Caching Layer**: Cache common requests (e.g., "GitHub agent")
3. **Validation Agent**: Fourth agent to validate generated code
4. **Multiple Output Formats**: Support for different project structures
5. **Interactive Mode**: CLI with prompts for refinement
6. **Batch Generation**: Generate multiple agents from a list

### Architecture Changes Needed

```
Current: Sequential (A → B → C)

Future: Parallel + Cache
        ┌─→ B (Docs) ─┐
    A →─┤             ├→ D (Validation) → Output
        └─→ Cache ────┘
                ↓
           C (Generator)
```

---

## Security Considerations

### API Key Handling

- ✅ Stored in `.env` (gitignored)
- ✅ Never hardcoded
- ✅ Loaded via `python-dotenv`
- ✅ Not included in generated files

### Generated Code Safety

- ✅ Validator checks for hardcoded keys
- ✅ All agents use environment variables
- ✅ `.env.example` provided (never actual keys)

### Knowledge Base

- ✅ Local storage only
- ✅ No external data sent except to OpenAI API
- ✅ Documentation from official Agno source

---

## Monitoring & Debugging

### Logging Levels

```python
print("🔧 Setting up...")     # Setup
print("⏳ Running...")         # In progress
print("✅ Complete")           # Success
print("❌ Error")              # Failure
print("⚠️  Warning")          # Warning
```

### Debug Information

Each step logs:
- Input size (characters)
- Output size (characters)
- Execution time (seconds)
- Success/failure status

### Troubleshooting Hooks

- Full response preview on failure
- File marker detection debug output
- Knowledge base load status
- Individual agent outputs shown

---

**This architecture enables reliable, production-ready agent generation through a combination of intelligent parsing, knowledge-based reasoning, and forceful code generation.**