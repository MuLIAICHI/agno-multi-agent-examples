# 🎨 Customization Guide

This guide shows you how to customize the TechBlog AI Writer Team for your specific needs.

---

## 🎯 Quick Customization Recipes

### Change Output Style

**Make it more casual:**
```python
technical_writer = Agent(
    name="Technical Writer",
    instructions=dedent("""\
        You're a friendly tech blogger! 🎉
        
        Writing Style:
        - Super casual and conversational
        - Use humor and pop culture references
        - Include memes and emoji liberally
        - Keep it fun but informative
        - Use "you" and "we" a lot
    """),
)
```

**Make it more formal/academic:**
```python
technical_writer = Agent(
    name="Technical Writer",
    instructions=dedent("""\
        You are an academic technical writer.
        
        Writing Style:
        - Formal, professional tone
        - Third-person perspective
        - Cite all sources academically
        - Use technical terminology precisely
        - Include references section
        - No emoji or casual language
    """),
)
```

---

## 🤖 Customizing Agents

### 1. Modify Agent Behavior

#### Change Research Depth

```python
technical_researcher = Agent(
    name="Technical Researcher",
    instructions=dedent("""\
        Your mission:
        1. Search for top 10 repositories (not just 5)
        2. Include security analysis
        3. Check for recent activity (last 30 days)
        4. Verify license compatibility
        5. Include contributor stats
    """),
)
```

#### Change Article Focus

```python
news_trends_agent = Agent(
    name="News & Trends Agent",
    instructions=dedent("""\
        Focus specifically on:
        - Reddit discussions from r/programming
        - Hacker News top stories
        - Twitter threads from tech influencers
        - Conference talks from last 6 months
        - Production case studies only
    """),
)
```

---

### 2. Add New Agents

#### Example: SEO Optimizer Agent

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat

seo_optimizer = Agent(
    name="SEO Optimizer",
    role="Optimize content for search engines",
    model=OpenAIChat(id="gpt-4o"),
    instructions=dedent("""\
        Analyze the blog post and add:
        1. SEO-friendly title (60 chars max)
        2. Meta description (155 chars)
        3. Focus keyword analysis
        4. Internal linking suggestions
        5. Header optimization (H1, H2, H3)
        6. Alt text for images
        7. Readability score
    """),
)

# Add to team
techblog_team = Team(
    members=[
        technical_researcher,
        news_trends_agent,
        code_example_generator,
        technical_writer,
        seo_optimizer,  # ← New agent
    ],
)
```

#### Example: Image Generator Agent

```python
from agno.tools.dalle import DalleTools

image_generator = Agent(
    name="Image Generator",
    role="Create featured images and diagrams",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DalleTools()],
    instructions=dedent("""\
        Create:
        1. Featured image for the blog post
        2. Diagram illustrating main concept
        3. Infographic of best practices
        
        Style: Modern, clean, tech-focused
    """),
)
```

#### Example: Fact Checker Agent

```python
fact_checker = Agent(
    name="Fact Checker",
    role="Verify claims and statistics",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
    instructions=dedent("""\
        Review the blog post and:
        1. Verify all statistics mentioned
        2. Check GitHub star counts are current
        3. Validate version numbers
        4. Confirm release dates
        5. Flag any outdated information
        6. Provide corrections if needed
    """),
)
```

---

### 3. Remove Agents

```python
# Minimal 2-agent team
quick_team = Team(
    name="Quick Blog Team",
    mode="coordinate",
    members=[
        news_trends_agent,     # Research only
        technical_writer,      # Writing only
    ],
    # Faster but less comprehensive
)
```

---

## 🔧 Customizing Tools

### 1. Modify GitHub Tool

#### Add More Search Options

```python
# In tools/github_tool.py

def search_repositories(
    self, 
    query: str, 
    language: Optional[str] = None,
    min_stars: int = 100,          # ← New parameter
    sort_by: str = "stars",        # ← New parameter
    max_results: int = 5           # ← New parameter
) -> str:
    params = {
        "q": f"{query} stars:>{min_stars}" + (f" language:{language}" if language else ""),
        "sort": sort_by,
        "order": "desc",
        "per_page": max_results
    }
    # ... rest of implementation
```

#### Add Repository Details

```python
def get_repository_details(self, repo_full_name: str) -> str:
    """
    Get detailed info about a specific repository.
    
    Args:
        repo_full_name: e.g., "tiangolo/fastapi"
    """
    url = f"https://api.github.com/repos/{repo_full_name}"
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        return f"""
Repository: {data['full_name']}
Description: {data['description']}
Stars: {data['stargazers_count']:,}
Forks: {data['forks_count']:,}
Open Issues: {data['open_issues_count']}
License: {data.get('license', {}).get('name', 'N/A')}
Last Updated: {data['updated_at']}
Homepage: {data.get('homepage', 'N/A')}
"""
```

---

### 2. Add New Tools

#### Example: Stack Overflow Search Tool

```python
# tools/stackoverflow_tool.py

import requests
from typing import Optional

class StackOverflowSearchTool:
    """Search Stack Overflow for questions and answers."""
    
    def __init__(self):
        self.name = "stackoverflow_search"
        self.base_url = "https://api.stackexchange.com/2.3"
    
    def search_questions(self, query: str, tag: Optional[str] = None) -> str:
        """Search Stack Overflow questions."""
        params = {
            "order": "desc",
            "sort": "votes",
            "intitle": query,
            "site": "stackoverflow",
            "pagesize": 5
        }
        
        if tag:
            params["tagged"] = tag
        
        response = requests.get(
            f"{self.base_url}/search",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            results = []
            
            for item in data.get("items", []):
                results.append(f"""
Question: {item['title']}
Score: {item['score']} | Answers: {item['answer_count']}
Link: {item['link']}
---""")
            
            return "\n".join(results) if results else "No questions found."
        
        return f"Error: {response.status_code}"
```

**Add to agent:**
```python
from tools.stackoverflow_tool import StackOverflowSearchTool

technical_researcher = Agent(
    name="Technical Researcher",
    tools=[
        GitHubSearchTool(),
        StackOverflowSearchTool(),  # ← New tool
    ],
)
```

---

## 🎛️ Customizing Team Behavior

### 1. Change Team Mode

#### Route Mode (Pick Best Agent)

```python
support_team = Team(
    name="Support Team",
    mode="route",  # ← Changed from "coordinate"
    members=[
        python_expert,
        javascript_expert,
        devops_expert,
    ],
    # User asks "Python async issue" → Routes to python_expert only
)
```

#### Collaborate Mode (All Work Together)

```python
review_team = Team(
    name="Review Team",
    mode="collaborate",  # ← All agents work simultaneously
    members=[
        code_reviewer,
        security_reviewer,
        performance_reviewer,
    ],
    # All agents analyze the same code, team synthesizes feedback
)
```

---

### 2. Adjust Success Criteria

#### Stricter Requirements

```python
techblog_team = Team(
    success_criteria=dedent("""\
        Blog post must include:
        - EXACTLY 3 code examples (no more, no less)
        - Minimum 2500 words (not 1500)
        - At least 8 GitHub repos with 1000+ stars
        - All code must be tested and runnable
        - Include performance benchmarks
        - SEO score of 90+
        - Readability grade of 8-10
    """),
)
```

#### Looser Requirements

```python
quick_team = Team(
    success_criteria=dedent("""\
        Brief blog post with:
        - At least 1 code example
        - Minimum 800 words
        - 2-3 GitHub repos mentioned
        - Clear introduction and conclusion
    """),
)
```

---

### 3. Customize Instructions

#### Add Domain Expertise

```python
techblog_team = Team(
    instructions=[
        # Original instructions...
        "All examples must be compatible with Python 3.11+",
        "Focus on production-ready patterns, not tutorials",
        "Include Docker deployment examples",
        "Mention Kubernetes when relevant",
        "Always discuss testing strategies",
    ],
)
```

#### Add Style Guide

```python
techblog_team = Team(
    instructions=[
        # Original instructions...
        "Follow Google Developer Style Guide",
        "Use British English spelling",
        "Avoid jargon unless explained",
        "Include glossary for technical terms",
        "Target audience: Senior developers",
    ],
)
```

---

## 🎨 Customizing Output Format

### 1. Change Blog Structure

```python
technical_writer = Agent(
    instructions=dedent("""\
        Blog Structure (Custom):
        
        # Title
        
        ## TL;DR (3 bullet points)
        
        ## Why This Matters
        [Compelling introduction]
        
        ## Quick Start (5 minutes)
        [Immediate hands-on example]
        
        ## Deep Dive
        [Technical details]
        
        ## Production Considerations
        [Security, performance, scaling]
        
        ## Alternatives & Comparison
        [Other options]
        
        ## Real-World Examples
        [Case studies]
        
        ## Conclusion & Next Steps
    """),
)
```

---

### 2. Add Different Output Formats

#### JSON Output

```python
from pydantic import BaseModel

class BlogPostOutput(BaseModel):
    title: str
    summary: str
    sections: list[dict]
    code_examples: list[str]
    references: list[str]
    word_count: int

technical_writer = Agent(
    response_model=BlogPostOutput,  # ← Structured output
)
```

#### Markdown + HTML

```python
technical_writer = Agent(
    instructions=dedent("""\
        Generate TWO versions:
        1. Markdown version (for GitHub/dev.to)
        2. HTML version (for WordPress/CMS)
        
        Include appropriate meta tags and formatting
    """),
)
```

---

## 🔄 Customizing Models

### 1. Use Different Models per Agent

```python
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude

# Fast model for research
technical_researcher = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),  # Cheaper, faster
)

# Smart model for writing
technical_writer = Agent(
    model=Claude(id="claude-sonnet-4-0"),  # Better at writing
)

# Reasoning model for code
code_example_generator = Agent(
    model=OpenAIChat(id="o1-preview"),  # Better at code
)
```

---

### 2. Add Model Fallbacks

```python
import openai

def get_model_with_fallback():
    """Try expensive model first, fallback to cheaper."""
    try:
        return OpenAIChat(id="gpt-4o")
    except openai.RateLimitError:
        print("Rate limited, using fallback model")
        return OpenAIChat(id="gpt-4o-mini")

technical_writer = Agent(
    model=get_model_with_fallback(),
)
```

---

## 💾 Adding Persistent Storage

### For Multi-Session Use

```python
import os
from agno.storage.sqlite import SqliteStorage

os.makedirs("tmp", exist_ok=True)

techblog_team = Team(
    # ... other config
    storage=SqliteStorage(
        table_name="blog_sessions",
        db_file="tmp/team_storage.db"
    ),
    session_id="main_writer_session",
)
```

**Now you can continue conversations:**
```python
# Day 1
team.run("Write about FastAPI")

# Day 2 (new script run)
team.run("Update that FastAPI post with security section")
# ✅ Team remembers the previous post!
```

---

## 🌐 Adding Different Languages

```python
# French tech blogger
french_writer = Agent(
    name="French Technical Writer",
    instructions=dedent("""\
        Écrivez en français !
        
        Structure:
        1. Introduction captivante
        2. Outils et bibliothèques
        3. Meilleures pratiques
        4. Exemples de code (commentés en français)
        5. Conclusion
    """),
)

# Create language-specific teams
french_team = Team(
    name="Équipe Française",
    members=[technical_researcher, news_trends_agent, code_example_generator, french_writer],
)
```

---

## 📊 Adding Analytics & Logging

```python
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    filename=f'logs/team_{datetime.now():%Y%m%d}.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Custom wrapper
class AnalyticsTeam(Team):
    def run(self, query, **kwargs):
        start = datetime.now()
        logging.info(f"Query started: {query}")
        
        result = super().run(query, **kwargs)
        
        duration = (datetime.now() - start).total_seconds()
        word_count = len(result.content.split())
        
        logging.info(f"Query completed: {duration}s, {word_count} words")
        
        return result
```

---

## 🎯 Creating Templates

### Save Reusable Configurations

```python
# config/agents.py

def create_researcher(topic_focus: str):
    """Factory for creating specialized researchers."""
    return Agent(
        name=f"{topic_focus} Researcher",
        role=f"Expert at finding {topic_focus} resources",
        model=OpenAIChat(id="gpt-4o"),
        tools=[GitHubSearchTool()],
        instructions=f"Focus specifically on {topic_focus} repositories and resources.",
    )

# Usage
python_researcher = create_researcher("Python")
js_researcher = create_researcher("JavaScript")
rust_researcher = create_researcher("Rust")
```

---

## 🧪 Testing Custom Configurations

```python
# test_custom.py

def test_custom_team():
    """Test your customized team."""
    result = my_custom_team.run(
        "Write about Docker",
        stream=False
    )
    
    assert len(result.content) > 1000
    assert "```" in result.content  # Has code
    assert "github.com" in result.content  # Has repos
    print("✅ Custom team works!")

if __name__ == "__main__":
    test_custom_team()
```

---

## 📚 Example: Complete Custom Team

```python
# custom_team.py - SEO-Optimized Blog Team

from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from tools.github_tool import GitHubSearchTool
from tools.seo_tool import SEOAnalyzerTool

# Custom agents
researcher = Agent(name="Researcher", tools=[GitHubSearchTool()], ...)
writer = Agent(name="Writer", ...)
seo_optimizer = Agent(name="SEO Expert", tools=[SEOAnalyzerTool()], ...)
image_gen = Agent(name="Image Creator", tools=[DalleTools()], ...)

# Custom team
seo_blog_team = Team(
    name="SEO Blog Team",
    mode="coordinate",
    members=[researcher, writer, seo_optimizer, image_gen],
    success_criteria="SEO score 90+, featured image included, 2000+ words",
)

# Run
result = seo_blog_team.run("Write SEO-optimized post about FastAPI")
```

---

## 💡 Tips for Customization

1. **Start Small**: Change one thing at a time
2. **Test Often**: Run after each change
3. **Keep Backups**: Save working versions
4. **Document Changes**: Comment why you changed things
5. **Use Version Control**: Git commit after successful changes

---

## 🎓 Advanced Customization Resources

- **Agno Custom Tools**: https://docs.agno.com/tools/custom
- **Agent Configuration**: https://docs.agno.com/agents/introduction
- **Team Modes**: https://docs.agno.com/teams/introduction
- **Pydantic Models**: https://docs.pydantic.dev/

---

*Need help customizing? Check TROUBLESHOOTING.md or open an issue!*