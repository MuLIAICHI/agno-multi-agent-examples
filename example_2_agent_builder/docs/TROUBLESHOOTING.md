# 🔧 Troubleshooting Guide

Common issues and solutions for the Agno Agent Builder Team.

---

## Quick Diagnosis

Run this checklist first:

```bash
# 1. Check Python version
python --version  # Should be 3.8+

# 2. Check if .env exists
cat .env  # Should show OPENAI_API_KEY=sk-...

# 3. Check dependencies
pip list | grep agno  # Should show agno>=1.1.0

# 4. Check directories exist
ls -la outputs/  # Should exist
ls -la tmp/      # May not exist yet (created on first run)
```

---

## Common Issues

### 🔴 Issue #1: "OPENAI_API_KEY not found"

**Error Message**:
```
❌ Error: OPENAI_API_KEY not found in environment variables
Please create a .env file with your OpenAI API key
```

**Cause**: Missing or incorrectly configured `.env` file

**Solution**:
```bash
# 1. Copy the example file
cp .env.example .env

# 2. Edit .env and add your real API key
nano .env  # or use your preferred editor

# Should look like:
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx

# 3. Verify it's loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

**Common Mistakes**:
- ❌ `.env` file in wrong directory (must be in project root)
- ❌ Key has extra spaces: `OPENAI_API_KEY= sk-...` (remove space after `=`)
- ❌ Key is wrapped in quotes: `OPENAI_API_KEY="sk-..."` (remove quotes)
- ❌ Using `.env.example` instead of `.env`

---

### 🔴 Issue #2: No Files Generated

**Symptoms**:
```
❌ No file markers found in response!
⚠️  Skipped main.py: No content extracted
```

**Cause**: Code Generator is being too conversational instead of generating files

**Solution 1** - Check the output:
```bash
# Look for this in the output:
📄 FULL TEAM RESPONSE
# If you see "Would you like me to..." or "Shall I generate..." 
# instead of "=== FILE: main.py ===", the generator is asking instead of doing
```

**Solution 2** - The system should auto-retry, but if it doesn't:
```python
# In main.py, the retry logic should trigger automatically
# If it doesn't, try running again - sometimes LLMs need a second attempt
```

**Solution 3** - Verify instructions:
```python
# Make sure Code Generator has these instructions:
"DO NOT ask for permission or confirmation"
"DO NOT suggest modifications"
"START GENERATING NOW. DO NOT WAIT. DO NOT ASK."
```

**Prevention**: The current version has forceful instructions and retry logic. If this still happens, it's an LLM behavior issue - just run again.

---

### 🔴 Issue #3: Knowledge Base Loading Fails

**Error Message**:
```
Error loading Agno documentation
Failed to connect to https://docs.agno.com/llms-full.txt
```

**Cause**: Network connectivity issue or URL change

**Solution 1** - Check your internet connection:
```bash
# Test connectivity
curl https://docs.agno.com/llms-full.txt
```

**Solution 2** - Try again:
```bash
# Sometimes it's a temporary issue
# Just run the script again
python main.py
```

**Solution 3** - Clear and reload:
```bash
# Remove the existing knowledge base
rm -rf tmp/lancedb

# Run again to download fresh
python main.py
```

**Solution 4** - Use local documentation:
```python
# In main.py, change this:
await knowledge.add_content_async(
    name="Agno Docs", 
    url="https://docs.agno.com/llms-full.txt"
)

# To use a local file:
await knowledge.add_content_async(
    name="Agno Docs",
    path="./docs/agno_docs_local.txt"  # Download the file first
)
```

---

### 🔴 Issue #4: "Module 'agno' has no attribute..."

**Error Message**:
```
AttributeError: module 'agno' has no attribute 'agent'
# or
ImportError: cannot import name 'Agent' from 'agno.agent'
```

**Cause**: Wrong Agno version or installation issue

**Solution**:
```bash
# 1. Check installed version
pip show agno

# 2. Should be version 1.1.0 or higher
# If not, upgrade:
pip install --upgrade agno

# 3. If still failing, reinstall:
pip uninstall agno
pip install agno>=1.1.0

# 4. Verify installation:
python -c "from agno.agent import Agent; print('✅ Import successful')"
```

---

### 🔴 Issue #5: Slow First Run

**Symptoms**:
- First run takes 60-120 seconds
- Stuck at "Loading Agno documentation..."

**Cause**: This is **NORMAL** - downloading and embedding documentation

**Not a Bug**: First run timeline:
```
📚 Loading Agno documentation... (5-10 seconds - download)
   Processing chunks...           (20-30 seconds - splitting)
   Generating embeddings...       (30-60 seconds - OpenAI API)
✅ Agno documentation loaded      (Total: ~60-120 seconds)
```

**Subsequent runs are much faster** (~5 seconds) because the knowledge base is cached.

**To Speed Up**:
- Use faster internet connection (downloads ~5MB)
- Use OpenAI's faster embedding model (but costs more)
- Once loaded, it's cached - future runs are quick

---

### 🔴 Issue #6: Generated Code Has Errors

**Symptoms**:
- Generated `main.py` has syntax errors
- Imports are incorrect
- Code doesn't run

**Cause**: Code Generator used outdated patterns or hallucinated

**Solution 1** - Check the generated code:
```bash
# Validate syntax
python -m py_compile outputs/*/main.py

# Look for common issues:
# - Wrong imports (should be: from agno.agent import Agent)
# - Missing dependencies in requirements.txt
# - Hardcoded values instead of env variables
```

**Solution 2** - Use the Code Validator (if you built it):
```python
from tools.code_validator import CodeValidator

validator = CodeValidator()
with open('outputs/agent_name/main.py', 'r') as f:
    code = f.read()

result = validator.validate_python_code(code)
print(validator.format_validation_report(result))
```

**Solution 3** - Regenerate with more specific request:
```python
# Instead of:
"Build a GitHub agent"

# Try:
"Build a GitHub search agent using the GithubTools from Agno's built-in tools, 
following the exact patterns from Agno documentation for agent creation"
```

**Prevention**: The Agno Docs Expert should prevent this by providing current documentation, but LLMs can still make mistakes.

---

### 🔴 Issue #7: Out of Memory

**Error Message**:
```
MemoryError: Unable to allocate array
# or
Killed (process ran out of memory)
```

**Cause**: Knowledge base embedding or large documentation

**Solution 1** - Reduce batch size:
```python
# This is an internal Agno setting, but if it's an issue:
# Close other applications
# Or use a machine with more RAM (minimum 8GB recommended)
```

**Solution 2** - Use smaller knowledge source:
```python
# Instead of full docs, use a subset
# Manually curate relevant documentation sections
```

**Solution 3** - Use pagination:
```python
# Process documentation in chunks
# This would require modifying the knowledge loading code
```

---

### 🔴 Issue #8: Empty `outputs/` Directory

**Symptoms**:
- Script runs successfully
- But `outputs/` folder is empty
- No error messages

**Cause**: Files generated but not saved (parsing issue)

**Debug Steps**:
```python
# 1. Check if the script reached file saving
# Look for this in output:
"📦 Attempting to save generated files..."

# 2. Check if file markers were found
# Look for:
"✅ Found 4 file markers:"

# 3. If markers not found, check the full response
# The script should print the full response for debugging
```

**Solution**:
```bash
# 1. Check permissions
ls -la outputs/
# Should be writable (drwxr-xr-x)

# 2. Create directory manually if needed
mkdir -p outputs

# 3. Run again with verbose output
python main.py 2>&1 | tee debug.log
# Check debug.log for details
```

---

### 🔴 Issue #9: API Rate Limits

**Error Message**:
```
RateLimitError: Rate limit exceeded
# or
APIError: Too many requests
```

**Cause**: Too many requests to OpenAI API

**Solution 1** - Wait and retry:
```bash
# OpenAI has rate limits based on your tier
# Free tier: very limited
# Paid tier: higher limits

# Wait 60 seconds and try again
sleep 60
python main.py
```

**Solution 2** - Upgrade OpenAI account:
- Free tier: ~3 requests/minute
- Tier 1: ~60 requests/minute
- Tier 2+: Higher limits

**Solution 3** - Add delays between requests:
```python
# In main.py, add delays:
import time

requirements = await requirements_analyst.arun(request)
time.sleep(5)  # Wait 5 seconds

docs = await agno_docs_expert.arun(requirements)
time.sleep(5)

code = await code_generator.arun(docs)
```

---

### 🔴 Issue #10: Invalid JSON from Requirements Analyst

**Symptoms**:
```
JSONDecodeError: Expecting value: line 1 column 1
```

**Cause**: Requirements Analyst outputted text before/after JSON

**Solution**:
```python
# The system should handle this, but if it doesn't:
# Look at the Requirements output in the logs

# Should be pure JSON:
{"type": "single_agent", ...}

# If you see extra text:
Here is the analysis:
{"type": "single_agent", ...}
Hope this helps!

# The parsing will fail
```

**Fix**: The Requirements Analyst instructions explicitly say "Output ONLY JSON" but LLMs can be chatty. If this persists, we can add JSON extraction logic.

---

## Performance Issues

### Slow Generation

**If generation takes > 2 minutes**:

```bash
# 1. Check OpenAI API status
# Visit: https://status.openai.com

# 2. Try a different model (in main.py):
# Instead of gpt-4o, try:
model=OpenAIChat(id="gpt-4o-mini")  # Faster, cheaper

# 3. Check network speed
ping api.openai.com
```

### High Costs

**If OpenAI costs are too high**:

```python
# 1. Use cheaper model for non-critical agents
requirements_analyst = Agent(
    model=OpenAIChat(id="gpt-4o-mini")  # Much cheaper
)

# 2. Cache requirements for similar requests
# (Would require code changes to implement)

# 3. Use local LLMs (advanced)
# Replace OpenAIChat with Ollama or similar
```

---

## Debugging Tips

### Enable Verbose Logging

```python
# In main.py, add detailed logging:
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Each Step Individually

```python
# Run each agent separately to isolate issues:

# Test Requirements Analyst
requirements = await requirements_analyst.arun("Build a GitHub agent")
print(f"Requirements: {requirements}")

# Test Docs Expert (if requirements worked)
docs = await agno_docs_expert.arun(f"Given: {requirements}")
print(f"Docs: {docs}")

# Test Code Generator (if both above worked)
code = await code_generator.arun(f"Requirements: {requirements}, Docs: {docs}")
print(f"Code: {code}")
```

### Inspect Generated Files Manually

```bash
# Even if parsing fails, the response contains the code
# Look for the full response in terminal output
# Copy/paste files manually if needed
```

---

## FAQ

### Q: Do I need Node.js?

**A**: No, the current version uses Knowledge base instead of MCP. Node.js is NOT required.

---

### Q: Can I use other LLM providers?

**A**: Yes, replace `OpenAIChat` with other Agno-supported models:
```python
# Anthropic Claude
from agno.models.anthropic import Claude
model = Claude(id="claude-sonnet-4-0")

# Groq
from agno.models.groq import Groq
model = Groq(id="llama-3.3-70b-versatile")
```

---

### Q: Can I customize generated code style?

**A**: Yes, modify the Code Generator's instructions:
```python
code_generator = Agent(
    instructions=[
        # Add your custom requirements:
        "Use double quotes for strings",
        "Maximum line length: 100 characters",
        "Include docstrings for all functions",
        # ... existing instructions ...
    ]
)
```

---

### Q: How do I generate a team instead of single agent?

**A**: Just ask for a team in your request:
```python
request = "Build a team with a researcher and a writer"
# Requirements Analyst will detect this and set type="agent_team"
```

---

### Q: Why does it keep downloading documentation?

**A**: It shouldn't! Check:
```bash
# Knowledge base should be cached here:
ls -la tmp/lancedb/

# If this directory exists, docs won't re-download
# If it doesn't exist, check permissions:
mkdir -p tmp/lancedb
```

---

### Q: Can I add custom tools to generated agents?

**A**: Yes, in two ways:

1. **Request it**: "Build an agent with a custom weather API tool"
2. **Modify after**: Edit the generated `main.py` to add your tool

---

## Still Having Issues?

If none of these solutions work:

1. **Check Agno documentation**: https://docs.agno.com
2. **Review generated code**: Look for obvious errors
3. **Check dependencies**: `pip list | grep -E "agno|openai|lancedb"`
4. **Try a simpler request**: "Build a simple agent with no tools"
5. **Check API key validity**: Test with OpenAI's playground

---

## Error Message Reference

| Error | Typical Cause | Quick Fix |
|-------|--------------|-----------|
| `OPENAI_API_KEY not found` | No .env file | `cp .env.example .env` and add key |
| `No file markers found` | Generator being conversational | Run again (has retry logic) |
| `Knowledge base loading failed` | Network issue | Check internet, try again |
| `Module 'agno' has no attribute` | Wrong version | `pip install --upgrade agno` |
| `RateLimitError` | Too many API calls | Wait 60s, reduce requests |
| `MemoryError` | Insufficient RAM | Use smaller docs, close apps |
| `JSONDecodeError` | Invalid requirements output | Check Requirements Analyst output |
| `Empty outputs/` | Parsing or permissions | Check logs, verify directory permissions |

---

**💡 Pro Tip**: Most issues are resolved by simply running the script again. LLMs can be non-deterministic!