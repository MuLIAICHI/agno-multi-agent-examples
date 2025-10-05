"""
GitHub Search Tool - Custom tool for searching repositories and code.

This tool uses the GitHub API to search for repositories and code examples.
No authentication is required for basic searches, but adding a GITHUB_TOKEN
environment variable will increase rate limits.

Rate Limits:
- Without token: 60 requests per hour
- With token: 5,000 requests per hour
"""

from typing import Optional
import os


class GitHubSearchTool:
    """Custom tool for searching GitHub repositories and code examples."""
    
    def __init__(self):
        self.name = "github_search"
        self.description = "Search GitHub repositories and code examples"
        self.github_token = os.getenv("GITHUB_TOKEN")
    
    def search_repositories(self, query: str, language: Optional[str] = None) -> str:
        """
        Search GitHub repositories by query and optional language filter.
        
        Args:
            query: Search query for repositories (e.g., "fastapi", "docker best practices")
            language: Programming language filter (e.g., "python", "javascript", "go")
        
        Returns:
            Formatted string with top repository results including:
            - Repository name and description
            - Stars and forks count
            - Primary language
            - Topics/tags
            - GitHub URL
        
        Example:
            >>> tool = GitHubSearchTool()
            >>> results = tool.search_repositories("fastapi", language="python")
            >>> print(results)
        """
        try:
            import requests
            
            # Build search query
            search_query = query
            if language:
                search_query += f" language:{language}"
            
            # GitHub API endpoint for repository search
            url = "https://api.github.com/search/repositories"
            params = {
                "q": search_query,
                "sort": "stars",
                "order": "desc",
                "per_page": 5
            }
            
            # Set headers (include token if available)
            headers = {"Accept": "application/vnd.github.v3+json"}
            if self.github_token:
                headers["Authorization"] = f"Bearer {self.github_token}"
            
            # Make API request
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for repo in data.get("items", [])[:5]:
                    results.append(f"""
Repository: {repo['full_name']}
Stars: {repo['stargazers_count']:,} | Forks: {repo['forks_count']:,}
Description: {repo['description'] or 'No description'}
URL: {repo['html_url']}
Language: {repo.get('language', 'N/A')}
Topics: {', '.join(repo.get('topics', [])[:5]) or 'None'}
Last Updated: {repo['updated_at'][:10]}
---""")
                
                if results:
                    return "\n".join(results)
                else:
                    return "No repositories found for this query."
            
            elif response.status_code == 403:
                return "GitHub API rate limit exceeded. Please add a GITHUB_TOKEN environment variable for higher limits."
            
            else:
                return f"GitHub API error: {response.status_code} - {response.text[:100]}"
                
        except ImportError:
            return "Error: 'requests' library not installed. Run: pip install requests"
        
        except Exception as e:
            return f"Error searching GitHub: {str(e)}"
    
    def search_code(self, query: str, language: Optional[str] = None) -> str:
        """
        Search for code examples on GitHub.
        
        Args:
            query: Code search query (e.g., "async def", "docker-compose", "class Component")
            language: Programming language filter (e.g., "python", "javascript")
        
        Returns:
            Formatted string with code search results including:
            - File name and path
            - Repository name
            - GitHub URL to the file
        
        Example:
            >>> tool = GitHubSearchTool()
            >>> results = tool.search_code("async def", language="python")
            >>> print(results)
        """
        try:
            import requests
            
            search_query = query
            if language:
                search_query += f" language:{language}"
            
            # GitHub API endpoint for code search
            url = "https://api.github.com/search/code"
            params = {
                "q": search_query,
                "sort": "indexed",
                "order": "desc",
                "per_page": 3
            }
            
            # Set headers (include token if available)
            headers = {"Accept": "application/vnd.github.v3+json"}
            if self.github_token:
                headers["Authorization"] = f"Bearer {self.github_token}"
            
            # Make API request
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
                
                if results:
                    return "\n".join(results)
                else:
                    return "No code examples found for this query."
            
            elif response.status_code == 403:
                return "GitHub API rate limit exceeded. Please add a GITHUB_TOKEN environment variable."
            
            else:
                return f"GitHub code search error: {response.status_code}"
                
        except ImportError:
            return "Error: 'requests' library not installed. Run: pip install requests"
        
        except Exception as e:
            return f"Error searching code: {str(e)}"


# Example usage and testing
if __name__ == "__main__":
    """Test the GitHub search tool."""
    
    print("Testing GitHub Search Tool")
    print("=" * 80)
    
    tool = GitHubSearchTool()
    
    # Test 1: Search repositories
    print("\n1. Searching for FastAPI repositories...")
    print("-" * 80)
    result = tool.search_repositories("fastapi", language="python")
    print(result)
    
    # Test 2: Search code
    print("\n\n2. Searching for async code examples...")
    print("-" * 80)
    result = tool.search_code("async def", language="python")
    print(result)
    
    print("\n" + "=" * 80)
    print("✓ Tests complete!")