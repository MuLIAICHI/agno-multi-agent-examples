# 🔧 Troubleshooting Guide

Common issues and solutions for the TechBlog AI Writer Team.

---

## 🚨 Installation Issues

### ❌ Problem: `ModuleNotFoundError: No module named 'agno'`

**Symptoms:**
```bash
ModuleNotFoundError: No module named 'agno'
```

**Solutions:**

1. **Check virtual environment is activated:**
```bash
# Should show (venv) in your prompt
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Verify installation:**
```bash
pip list | grep agno
# Should show: agno 1.1.0 (or higher)
```

---

### ❌ Problem: `ImportError: cannot import name 'Team'`

**Symptoms:**
```python
ImportError: cannot import name 'Team' from 'agno.team'
```

**Solution:**

Correct import (both work):
```python
# Option 1 (simpler)
from agno.team import Team

# Option 2 (more explicit)
from agno.team.team import Team
```

---

### ❌ Problem: `requests` module not found

**Symptoms:**
```bash
ModuleNotFoundError: No module named 'requests'
```

**Solution:**
```bash
pip install requests
# Or
pip install -r requirements.txt
```

---

## 🔑 API Key Issues

### ❌ Problem: Missing OpenAI API Key

**Symptoms:**
```bash
⚠️  Warning: OPENAI_API_KEY not found in environment variables
```

**Solutions:**

1. **Set environment variable:**
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

2. **Or create `.env` file:**
```bash
# Copy example
cp .env.example .env

# Edit .env and add your key
OPENAI_API_KEY=sk-your-actual-key-here
```

3. **Load in Python:**
```python
from dotenv import load_dotenv
load_dotenv()  # Loads from .env file
```

---

### ❌ Problem: Invalid API Key

**Symptoms:**
```bash
openai.AuthenticationError: Incorrect API key provided
```

**Solutions:**

1. **Check key format:**
   - Should start with `sk-`
   - Should be ~51 characters long
   - No extra spaces or quotes

2. **Verify key is active:**
   - Go to https://platform.openai.com/api-keys
   - Check if key still exists and is not revoked

3. **Check quotas:**
   - Go to https://platform.openai.com/usage
   - Verify you have credits available

---

### ❌ Problem: Rate Limit Exceeded

**Symptoms:**
```bash
openai.RateLimitError: Rate limit exceeded
```

**Solutions:**

1. **Wait a bit:**
```bash
# Free tier: Wait 60 seconds
# Pay-as-you-go: Wait 20 seconds
```

2. **Check your limits:**
   - https://platform.openai.com/account/rate-limits

3. **Use exponential backoff:**
```python
import time
from openai import RateLimitError

try:
    response = team.run(query)
except RateLimitError:
    print("Rate limited, waiting 60s...")
    time.sleep(60)
    response = team.run(query)
```

---

## 🐛 GitHub Tool Issues

### ❌ Problem: GitHub API Rate Limit

**Symptoms:**
```bash
GitHub API error: 403 (Rate limit exceeded)
```

**Solutions:**

1. **Without token limit:** 60 requests/hour
   - Wait for reset (check response headers)

2. **Add GitHub token** (recommended):
```bash
# Create token at: https://github.com/settings/tokens
export GITHUB_TOKEN="ghp_your_token_here"
```

3. **With token limit:** 5,000 requests/hour
   - Much better for development

---

### ❌ Problem: GitHub API Returns Empty Results

**Symptoms:**
```
No repositories found for this query.
```

**Solutions:**

1. **Check query spelling:**
```python
# ❌ Wrong
tool.search_repositories("fastpi")  # Typo

# ✅ Correct
tool.search_repositories("fastapi")
```

2. **Try broader query:**
```python
# Too specific
tool.search_repositories("fastapi async validation best practices")

# Better
tool.search_repositories("fastapi")
```

3. **Check language filter:**
```python
# No results with wrong language
tool.search_repositories("fastapi", language="rust")

# Correct
tool.search_repositories("fastapi", language="python")
```

---

## 💬 Team Execution Issues

### ❌ Problem: Team Not Coordinating

**Symptoms:**
- Final output missing research from earlier agents
- Agents seem to work in isolation

**Solutions:**

1. **Ensure coordinate mode:**
```python
techblog_team = Team(
    mode="coordinate",  # ✅ Not "route" or "collaborate"
)
```

2. **Add explicit instructions:**
```python
techblog_team = Team(
    instructions=[
        "IMPORTANT: Pass ALL research to next agent",
        "Technical Writer MUST include ALL repos and examples",
    ],
)
```

3. **Enable context sharing:**
```python
techblog_team = Team(
    show_members_responses=True,  # ✅ See what each agent does
)
```

---

### ❌ Problem: Output Too Short

**Symptoms:**
- Blog post only 300-500 words
- Missing sections

**Solutions:**

1. **Strengthen success criteria:**
```python
success_criteria="""
    MUST include:
    - Minimum 2000 words (not 1500)
    - ALL sections required
    - Reject if incomplete
"""
```

2. **Add explicit length requirements:**
```python
technical_writer = Agent(
    instructions=dedent("""\
        CRITICAL: Blog post MUST be at least 1500 words.
        
        If generated post is shorter:
        1. Expand each section
        2. Add more examples
        3. Include more details
    """),
)
```

3. **Check model settings:**
```python
# Some models have token limits
model=OpenAIChat(id="gpt-4o")  # ✅ Higher limits
# Not
model=OpenAIChat(id="gpt-3.5-turbo")  # ❌ Lower quality
```

---

### ❌ Problem: Slow Execution

**Symptoms:**
- Takes >5 minutes per blog post
- Seems stuck

**Solutions:**

1. **Use faster models:**
```python
# Faster for research
technical_researcher = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),  # ✅ 2x faster
)
```

2. **Reduce research depth:**
```python
# Less thorough but faster
news_trends_agent = Agent(
    instructions="Find top 3 articles only (not 6)",
)
```

3. **Check streaming:**
```python
# Enable to see progress
response = team.run(query, stream=True)  # ✅ See real-time updates
```

4. **Check network:**
```bash
# Test API connectivity
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

---

## 📝 Output Quality Issues

### ❌ Problem: Generic/Low-Quality Content

**Symptoms:**
- Content feels vague
- No specific examples
- Repeated phrases

**Solutions:**

1. **Add more specific instructions:**
```python
technical_writer = Agent(
    instructions=dedent("""\
        BE SPECIFIC:
        - Use exact version numbers
        - Include real star counts from GitHub
        - Cite specific articles with dates
        - NO generic statements like "popular framework"
        - USE "FastAPI 0.104.1" not "latest version"
    """),
)
```

2. **Increase research quality:**
```python
technical_researcher = Agent(
    instructions=dedent("""\
        QUALITY OVER QUANTITY:
        - Only repos with 1000+ stars
        - Only updated in last 6 months
        - Must have good documentation
    """),
)
```

---

### ❌ Problem: Code Examples Don't Work

**Symptoms:**
- Syntax errors in generated code
- Missing imports
- Outdated patterns

**Solutions:**

1. **Add validation instructions:**
```python
code_example_generator = Agent(
    instructions=dedent("""\
        EVERY code example MUST:
        1. Include ALL imports at top
        2. Be syntactically correct
        3. Use modern Python (3.11+)
        4. Include example output
        5. Be tested mentally for errors
    """),
)
```

2. **Test generated code:**
```python
import ast

def validate_python_code(code):
    """Check if Python code is syntactically valid."""
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False

# Use after generation
if not validate_python_code(code_example):
    print("⚠️ Warning: Code has syntax errors!")
```

---

## 🔧 Memory & Storage Issues

### ❌ Problem: Team Doesn't Remember Previous Conversation

**Symptoms:**
- Follow-up questions don't work
- Team asks same questions again

**Solutions:**

1. **Check memory settings:**
```python
techblog_team = Team(
    add_history_to_messages=True,  # ✅ Must be True
    num_history_runs=3,            # ✅ Remember last 3
)
```

2. **Use same team instance:**
```python
# ❌ Wrong - Creates new team each time
def get_team():
    return Team(...)

team1 = get_team()
team1.run("Write about FastAPI")
team2 = get_team()  # ❌ New team, no memory
team2.run("Add security section")

# ✅ Correct - Reuse same instance
team = Team(...)
team.run("Write about FastAPI")
team.run("Add security section")  # ✅ Remembers!
```

3. **Add persistent storage (if needed):**
```python
from agno.storage.sqlite import SqliteStorage
import os

os.makedirs("tmp", exist_ok=True)

techblog_team = Team(
    storage=SqliteStorage(
        table_name="team_sessions",
        db_file="tmp/team.db"
    ),
    session_id="main_session",  # ✅ Fixed ID
)
```

---

## 🌐 Network Issues

### ❌ Problem: Connection Timeout

**Symptoms:**
```bash
requests.exceptions.Timeout: HTTPSConnectionPool
```

**Solutions:**

1. **Check internet connection:**
```bash
ping api.openai.com
ping api.github.com
```

2. **Increase timeout:**
```python
# In github_tool.py
response = requests.get(url, timeout=30)  # Increased from 10
```

3. **Add retry logic:**
```python
import time
from requests.exceptions import Timeout

def search_with_retry(query, max_retries=3):
    for i in range(max_retries):
        try:
            return tool.search_repositories(query)
        except Timeout:
            if i < max_retries - 1:
                wait = 2 ** i  # Exponential backoff
                print(f"Timeout, retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise
```

---

## 📦 Import Issues

### ❌ Problem: Can't Import Custom Tool

**Symptoms:**
```python
ModuleNotFoundError: No module named 'tools.github_tool'
```

**Solutions:**

1. **Check folder structure:**
```bash
example_1_techblog_team/
├── main.py
├── tools/
│   ├── __init__.py     # ✅ Must exist!
│   └── github_tool.py
```

2. **Create `__init__.py`:**
```bash
touch tools/__init__.py
```

3. **Use correct import:**
```python
# If running from project root
from tools.github_tool import GitHubSearchTool  # ✅ Correct

# Not
from github_tool import GitHubSearchTool  # ❌ Wrong
```

---

## 🎨 Output Format Issues

### ❌ Problem: No Markdown Formatting

**Symptoms:**
- Plain text output
- No headers, bold, code blocks

**Solutions:**

```python
# Ensure markdown is enabled
techblog_team = Team(
    markdown=True,  # ✅ Must be True
)

technical_writer = Agent(
    markdown=True,  # ✅ For each agent too
)
```

---

### ❌ Problem: Streaming Not Working

**Symptoms:**
- No output until complete
- Can't see progress

**Solutions:**

1. **Enable streaming:**
```python
response = team.run(query, stream=True)  # ✅ Not False
```

2. **Or use print_response:**
```python
team.print_response(query, stream=True)  # ✅ Prints as it goes
```

3. **Check Python buffering:**
```bash
# Run with unbuffered output
python -u main.py
```

---

## 🐞 Debugging Tips

### Enable Debug Mode

```python
# See everything that's happening
import logging
logging.basicConfig(level=logging.DEBUG)

techblog_team = Team(
    show_tool_calls=True,        # ✅ See all tool calls
    show_members_responses=True, # ✅ See agent outputs
)
```

---

### Test Individual Components

```python
# Test GitHub tool alone
from tools.github_tool import GitHubSearchTool
tool = GitHubSearchTool()
print(tool.search_repositories("fastapi"))

# Test single agent
technical_researcher.print_response("Find Python web frameworks")

# Test team with simple query
team.print_response("Write a 100-word intro about Python")
```

---

### Check Token Usage

```python
# Monitor API costs
import tiktoken

def count_tokens(text):
    enc = tiktoken.encoding_for_model("gpt-4o")
    return len(enc.encode(text))

# After generation
tokens = count_tokens(response.content)
cost = (tokens / 1000) * 0.005  # GPT-4o pricing
print(f"Used {tokens} tokens ≈ ${cost:.4f}")
```

---

## 📞 Getting Help

### Still Stuck?

1. **Check Agno Docs:**
   - https://docs.agno.com/

2. **Agno Community:**
   - https://community.agno.com/

3. **GitHub Issues:**
   - https://github.com/agno-agi/agno/issues

4. **Enable verbose logging and share:**
```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    filename='debug.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## ✅ Prevention Checklist

Before running:

- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip list`)
- [ ] API keys set (check with `echo $OPENAI_API_KEY`)
- [ ] `.env` file created (if using)
- [ ] Internet connection working
- [ ] Sufficient API credits
- [ ] Project structure correct (check folders exist)

---

## 🔄 Quick Fixes

```bash
# Nuclear option: Fresh start
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."
python main.py
```

---

*Last Updated: October 2025*