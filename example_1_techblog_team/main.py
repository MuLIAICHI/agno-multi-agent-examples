"""
TechBlog AI Writer Team - Advanced Multi-Agent System
======================================================

This example demonstrates an advanced multi-agent team that researches technical topics
and produces comprehensive, well-structured blog posts.

Advanced Features:
- Coordinate mode with sequential task delegation
- Custom GitHub search tool integration
- Memory for tracking research findings
- Structured blog post output with multiple sections
- Streaming for real-time progress updates
- Success criteria validation

Run: pip install agno openai duckduckgo-search requests
"""

from textwrap import dedent
from typing import Optional
import os

from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.db.sqlite import SqliteDb


# ============================================================================
# CUSTOM GITHUB SEARCH TOOL
# ============================================================================

class GitHubSearchTool:
    """Custom tool for searching GitHub repositories and code examples."""
    
    def __init__(self):
        self.name = "github_search"
        self.description = "Search GitHub repositories and code examples"
    
    def search_repositories(self, query: str, language: Optional[str] = None) -> str:
        """
        Search GitHub repositories by query and optional language filter.
        
        Args:
            query: Search query for repositories
            language: Programming language filter (e.g., "python", "javascript")
        
        Returns:
            Formatted string with top repository results
        """
        try:
            import requests
            
            # Build search query
            search_query = query
            if language:
                search_query += f" language:{language}"
            
            # GitHub API search (public, no auth needed for basic search)
            url = "https://api.github.com/search/repositories"
            params = {
                "q": search_query,
                "sort": "stars",
                "order": "desc",
                "per_page": 5
            }
            
            headers = {"Accept": "application/vnd.github.v3+json"}
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for repo in data.get("items", [])[:5]:
                    results.append(f"""
Repository: {repo['full_name']}
Stars: {repo['stargazers_count']} | Forks: {repo['forks_count']}
Description: {repo['description']}
URL: {repo['html_url']}
Language: {repo.get('language', 'N/A')}
Topics: {', '.join(repo.get('topics', [])[:5])}
---""")
                
                return "\n".join(results) if results else "No repositories found."
            else:
                return f"GitHub API error: {response.status_code}"
                
        except Exception as e:
            return f"Error searching GitHub: {str(e)}"
    
    def search_code(self, query: str, language: Optional[str] = None) -> str:
        """
        Search for code examples on GitHub.
        
        Args:
            query: Code search query
            language: Programming language filter
        
        Returns:
            Formatted string with code search results
        """
        try:
            import requests
            
            search_query = query
            if language:
                search_query += f" language:{language}"
            
            url = "https://api.github.com/search/code"
            params = {
                "q": search_query,
                "sort": "indexed",
                "order": "desc",
                "per_page": 3
            }
            
            headers = {"Accept": "application/vnd.github.v3+json"}
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get("items", [])[:3]:
                    results.append(f"""
File: {item['name']}
Repository: {item['repository']['full_name']}
Path: {item['path']}
URL: {item['html_url']}
---""")
                
                return "\n".join(results) if results else "No code examples found."
            else:
                return f"GitHub code search error: {response.status_code}"
                
        except Exception as e:
            return f"Error searching code: {str(e)}"


# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

# Agent 1: Technical Researcher
technical_researcher = Agent(
    name="Technical Researcher",
    role="Expert at finding technical documentation, GitHub repositories, and code examples",
    model=OpenAIChat(id="gpt-4o"),
    tools=[GitHubSearchTool()],
    instructions=dedent("""\
        You are a technical research specialist! 🔍
        
        Your mission:
        1. Search GitHub for relevant repositories and projects related to the topic
        2. Identify popular libraries, frameworks, and tools
        3. Find real-world code examples and implementations
        4. Note important GitHub repos with high stars/activity
        5. Identify key technical concepts and patterns
        
        Research Guidelines:
        - Focus on actively maintained projects (recent commits)
        - Prioritize repositories with good documentation
        - Look for official/popular implementations
        - Note specific versions and compatibility
        - Identify best practices from top repos
        
        Output Format:
        - List top 3-5 most relevant repositories
        - Highlight key features and use cases
        - Note any important technical requirements
        - Include GitHub URLs for reference
        
        Be thorough but concise. Quality over quantity!
    """),

    markdown=True,
    
)

# Agent 2: News & Trends Agent
news_trends_agent = Agent(
    name="News & Trends Agent",
    role="Expert at finding latest articles, tutorials, and trends in technology",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools(enable_news=False)],
    instructions=dedent("""\
        You are a tech news and trends analyst! 📰
        
        Your mission:
        1. Search for recent articles, blog posts, and tutorials
        2. Identify current trends and best practices
        3. Find expert opinions and community discussions
        4. Discover common pitfalls and solutions
        5. Note any recent updates or changes
        
        Search Strategy:
        - Look for articles from the last 6-12 months
        - Prioritize reputable tech blogs and official docs
        - Find real-world case studies and experiences
        - Check community sentiment (Reddit, Dev.to, Medium)
        - Identify emerging patterns and practices
        
        Output Format:
        - List 4-6 most valuable articles/resources
        - Summarize key insights from each
        - Highlight current best practices
        - Note any controversies or debates
        - Include URLs for all sources
        
        Focus on practical, actionable information!
    """),

    markdown=True,
    
)

# Agent 3: Code Example Generator
code_example_generator = Agent(
    name="Code Example Generator",
    role="Expert at creating clear, practical code examples and demonstrations",
    model=OpenAIChat(id="gpt-4o"),
    instructions=dedent("""\
        You are a coding expert who creates excellent examples! 💻
        
        Your mission:
        1. Create 2-3 practical, working code examples
        2. Demonstrate key concepts and best practices
        3. Add helpful comments explaining the code
        4. Include realistic use cases
        5. Show both basic and advanced patterns
        
        Code Quality Guidelines:
        - Write production-ready code (not pseudocode)
        - Follow language-specific best practices
        - Include proper error handling
        - Add type hints where applicable
        - Keep examples focused and clear
        - Avoid overly complex scenarios
        
        Example Structure:
        - Start with a basic example (10-20 lines)
        - Show a practical use case (20-40 lines)
        - Optionally include an advanced pattern
        - Add comments explaining WHY, not just WHAT
        - Include example output or usage
        
        Output Format:
        ```language
        # Example 1: [Description]
        [code with comments]
        
        # Example 2: [Description]
        [code with comments]
        ```
        
        Make it easy to understand and immediately useful!
    """),

    markdown=True,
    
)

# Agent 4: Technical Writer
technical_writer = Agent(
    name="Technical Writer",
    role="Expert at synthesizing research into polished, engaging technical blog posts",
    model=OpenAIChat(id="gpt-4o"),
    instructions=dedent("""\
        You are a senior technical writer for a top tech blog! ✍️
        
        Your mission:
        1. Synthesize all research into a cohesive narrative
        2. Create a well-structured, engaging blog post
        3. Balance technical depth with readability
        4. Include all code examples and resources
        5. Maintain a professional yet approachable tone
        
        Blog Post Structure:
        
        # [Compelling Title]
        
        ## Introduction (2-3 paragraphs)
        - Hook the reader with why this matters
        - Brief overview of what they'll learn
        - Set expectations for skill level
        
        ## What is [Topic]? (2-3 paragraphs)
        - Clear explanation of core concepts
        - Key features and capabilities
        - When and why to use it
        
        ## Popular Tools & Libraries (with GitHub links)
        - List top 3-5 repos from research
        - Brief description of each
        - Stars/activity indicators
        
        ## Best Practices (4-6 points)
        - Based on research findings
        - Practical, actionable advice
        - Include "why" not just "what"
        
        ## Code Examples
        - Include 2-3 complete examples
        - Progressive complexity
        - Well-commented
        
        ## Common Pitfalls & Solutions (3-4 items)
        - Real issues developers face
        - Clear solutions
        
        ## Current Trends & Future Outlook
        - What's happening now
        - Where things are heading
        
        ## Conclusion (2 paragraphs)
        - Summarize key takeaways
        - Encourage readers to try it
        
        ## Resources
        - All GitHub repos
        - Articles and tutorials
        - Official documentation
        
        Writing Style:
        - Clear and conversational
        - Use "you" to address reader
        - Short paragraphs (3-4 sentences)
        - Include emojis sparingly for personality
        - Bold key terms
        - Use code blocks properly
        
        Quality Standards:
        - Minimum 1500 words
        - All sources cited with URLs
        - No made-up information
        - Technical accuracy is paramount
        - Proofread for grammar/spelling
    """),

    markdown=True,

    
)


# ============================================================================
# TEAM DEFINITION
# ============================================================================

techblog_team = Team(
    name="TechBlog AI Writer Team",
    model=OpenAIChat(id="gpt-4o"),
    members=[
        technical_researcher,
        news_trends_agent,
        code_example_generator,
        technical_writer
    ],
    description=dedent("""\
        An elite team of AI agents that collaborates to produce high-quality 
        technical blog posts. The team researches GitHub repos, finds latest trends, 
        generates code examples, and synthesizes everything into polished articles.
    """),
    instructions=[
        "Step 1: Delegate to Technical Researcher to find GitHub repos and technical resources",
        "Step 2: Delegate to News & Trends Agent to find articles and best practices",
        "Step 3: Delegate to Code Example Generator to create practical examples",
        "Step 4: Delegate to Technical Writer to synthesize everything into a complete blog post",
        "Ensure all research is passed to subsequent agents",
        "Validate that the final blog post includes all research and examples",
        "The blog post should be comprehensive, accurate, and publication-ready"
    ],
    num_history_runs=3,  # Remember last 3 interactions
    markdown=True,
    db=SqliteDb(db_file="tmp/team.db"),  # Changed from 'storage' to 'db'
    session_id="blog_writer_session",
)

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def main():
    """Run example blog generation scenarios."""
    
    print("=" * 80)
    print("TechBlog AI Writer Team - Advanced Multi-Agent Example")
    print("=" * 80)
    print()
    
    # Example 1: Write about FastAPI
    print("📝 Example 1: Writing about FastAPI best practices\n")
    
response = techblog_team.run(
    "Write a comprehensive blog post about FastAPI best practices for building production APIs",
    stream=True
)

print("\n" + "=" * 80)
print("FINAL BLOG POST:")
print("=" * 80)

# Iterate through the streaming response
for event in response:
    if hasattr(event, 'content') and event.content:
        print(event.content, end='', flush=True)
    
    # # Example 2: Follow-up question (tests memory)
    # print("\n\n" + "=" * 80)
    # print("📝 Example 2: Follow-up question (testing memory)\n")
    
    # techblog_team.print_response(
    #     "Can you add a section about testing FastAPI applications?",
    #     stream=True
    # )


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
        print("Please set it before running:")
        print("export OPENAI_API_KEY='your-key-here'")
    else:
        main()