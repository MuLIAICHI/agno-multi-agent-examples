"""
Code Validator for Agno Agent Builder
======================================

Validates generated Agno agent code for:
- Python syntax correctness
- Correct Agno import patterns
- Agent/Team configuration best practices
- Common pitfalls and errors

Author: Agno Agent Builder Team
Date: October 2025
Version: 1.0
"""

import ast
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of code validation."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    score: int  # 0-100


class CodeValidator:
    """
    Validates generated Agno agent code for correctness and best practices.
    """
    
    # Correct Agno import patterns
    CORRECT_IMPORTS = {
        "Agent": "from agno.agent import Agent",
        "Team": "from agno.team import Team",
        "OpenAIChat": "from agno.models.openai import OpenAIChat",
        "Claude": "from agno.models.anthropic import Claude",
        "Groq": "from agno.models.groq import Groq",
        "SqliteStorage": "from agno.storage.sqlite import SqliteStorage",
        "MCPTools": "from agno.tools.mcp import MCPTools",
        "DuckDuckGoTools": "from agno.tools.duckduckgo import DuckDuckGoTools",
        "YFinanceTools": "from agno.tools.yfinance import YFinanceTools",
    }
    
    # Common incorrect import patterns
    INCORRECT_IMPORTS = [
        "from agno.agents import Agent",  # Wrong: should be agno.agent
        "from agno.team.team import Team",  # Wrong: should be agno.team
        "from agno.storage import AgentStorage",  # Wrong: should be SqliteStorage
        "from agno import Agent",  # Wrong: not at top level
    ]
    
    # Required Agno patterns
    REQUIRED_PATTERNS = {
        "agent_definition": r"(\w+)\s*=\s*Agent\s*\(",
        "team_definition": r"(\w+)\s*=\s*Team\s*\(",
        "model_specification": r"model\s*=\s*(\w+)\s*\(",
    }
    
    def __init__(self):
        """Initialize the code validator."""
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.suggestions: List[str] = []
    
    def validate_python_code(self, code: str) -> ValidationResult:
        """
        Validate Python code for syntax and structure.
        
        Args:
            code: Python code as a string
            
        Returns:
            ValidationResult with validation details
        """
        self.errors = []
        self.warnings = []
        self.suggestions = []
        
        # 1. Check syntax with AST
        syntax_valid = self._check_syntax(code)
        
        # 2. Check imports
        self._check_imports(code)
        
        # 3. Check Agno patterns
        self._check_agno_patterns(code)
        
        # 4. Check best practices
        self._check_best_practices(code)
        
        # 5. Check for common mistakes
        self._check_common_mistakes(code)
        
        # Calculate score
        score = self._calculate_score()
        
        # Determine if valid
        valid = syntax_valid and len(self.errors) == 0
        
        return ValidationResult(
            valid=valid,
            errors=self.errors.copy(),
            warnings=self.warnings.copy(),
            suggestions=self.suggestions.copy(),
            score=score
        )
    
    def _check_syntax(self, code: str) -> bool:
        """
        Check if Python code has valid syntax using AST.
        
        Args:
            code: Python code to check
            
        Returns:
            True if syntax is valid, False otherwise
        """
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            self.errors.append(
                f"Syntax Error at line {e.lineno}: {e.msg}"
            )
            return False
        except Exception as e:
            self.errors.append(f"Parse Error: {str(e)}")
            return False
    
    def _check_imports(self, code: str) -> None:
        """
        Check for correct and incorrect import patterns.
        
        Args:
            code: Python code to check
        """
        lines = code.split('\n')
        
        # Check for incorrect imports
        for line_num, line in enumerate(lines, 1):
            for incorrect in self.INCORRECT_IMPORTS:
                if incorrect in line:
                    self.errors.append(
                        f"Line {line_num}: Incorrect import pattern '{incorrect}'"
                    )
        
        # Check for missing essential imports
        has_agent = "from agno.agent import Agent" in code
        has_model = any(
            model_import in code 
            for model_import in [
                "from agno.models.openai import",
                "from agno.models.anthropic import",
                "from agno.models.groq import"
            ]
        )
        
        if "Agent(" in code and not has_agent:
            self.errors.append("Missing import: from agno.agent import Agent")
        
        if ("Agent(" in code or "Team(" in code) and not has_model:
            self.warnings.append(
                "No model import found. You may need to import a model provider."
            )
        
        # Check for Team import if Team is used
        if "Team(" in code and "from agno.team import Team" not in code:
            self.errors.append("Missing import: from agno.team import Team")
    
    def _check_agno_patterns(self, code: str) -> None:
        """
        Check for correct Agno agent/team patterns.
        
        Args:
            code: Python code to check
        """
        # Check if Agent is properly defined
        agent_pattern = re.search(self.REQUIRED_PATTERNS["agent_definition"], code)
        if "Agent(" in code and not agent_pattern:
            self.warnings.append(
                "Agent definition found but pattern unclear. "
                "Ensure: agent_name = Agent(...)"
            )
        
        # Check if model is specified
        if "Agent(" in code:
            model_pattern = re.search(self.REQUIRED_PATTERNS["model_specification"], code)
            if not model_pattern:
                self.errors.append(
                    "Agent must have a 'model' parameter specified"
                )
        
        # Check Team patterns
        if "Team(" in code:
            if "members=" not in code and "team=" not in code:
                self.errors.append(
                    "Team must have 'members' parameter with list of agents"
                )
            
            if "mode=" not in code:
                self.suggestions.append(
                    "Consider specifying 'mode' parameter for Team "
                    "(e.g., mode='coordinate')"
                )
    
    def _check_best_practices(self, code: str) -> None:
        """
        Check for Agno best practices.
        
        Args:
            code: Python code to check
        """
        # Check for docstrings
        if '"""' not in code and "'''" not in code:
            self.suggestions.append(
                "Add a module docstring to document the agent's purpose"
            )
        
        # Check for environment variables
        if "OPENAI_API_KEY" in code or "API_KEY" in code:
            if "os.getenv" not in code and "os.environ" not in code:
                self.warnings.append(
                    "API keys should be loaded from environment variables"
                )
        
        # Check for instructions
        if "Agent(" in code and "instructions=" not in code and "role=" not in code:
            self.suggestions.append(
                "Consider adding 'instructions' or 'role' parameter to guide the agent"
            )
        
        # Check for proper error handling
        if "__name__" in code and "__main__" in code:
            if "try:" not in code and "except:" not in code:
                self.suggestions.append(
                    "Consider adding try-except blocks for error handling"
                )
        
        # Check for type hints (Python best practice)
        if "def " in code and "->" not in code:
            self.suggestions.append(
                "Consider adding type hints to function signatures"
            )
    
    def _check_common_mistakes(self, code: str) -> None:
        """
        Check for common mistakes in Agno code.
        
        Args:
            code: Python code to check
        """
        # Check for using strings instead of tool objects
        if "tools=[" in code and '"' in code.split("tools=[")[1].split("]")[0]:
            self.warnings.append(
                "Tools should be tool objects, not strings. "
                "Use DuckDuckGoTools(), not 'duckduckgo'"
            )
        
        # Check for missing load_dotenv
        if "os.getenv" in code and "load_dotenv" not in code:
            self.warnings.append(
                "Using os.getenv without load_dotenv(). "
                "Import: from dotenv import load_dotenv"
            )
        
        # Check for hardcoded API keys
        if re.search(r'sk-[a-zA-Z0-9]{32,}', code):
            self.errors.append(
                "SECURITY: Hardcoded API key detected! Use environment variables."
            )
        
        # Check for missing if __name__ == "__main__"
        if "agent.run" in code or "agent.print_response" in code:
            if '__name__' not in code or '__main__' not in code:
                self.suggestions.append(
                    "Wrap execution code in: if __name__ == '__main__':"
                )
        
        # Check for Team without add_history_to_messages
        if "Team(" in code and "add_history_to_messages" not in code:
            self.suggestions.append(
                "Consider adding 'add_history_to_messages=True' to Team "
                "for conversation context"
            )
    
    def _calculate_score(self) -> int:
        """
        Calculate a code quality score (0-100).
        
        Returns:
            Integer score from 0 to 100
        """
        score = 100
        
        # Deduct points for errors (major issues)
        score -= len(self.errors) * 20
        
        # Deduct points for warnings (moderate issues)
        score -= len(self.warnings) * 10
        
        # Deduct points for suggestions (minor improvements)
        score -= len(self.suggestions) * 5
        
        # Ensure score is in valid range
        return max(0, min(100, score))
    
    def validate_file(self, filepath: str) -> ValidationResult:
        """
        Validate a Python file.
        
        Args:
            filepath: Path to the Python file
            
        Returns:
            ValidationResult with validation details
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            return self.validate_python_code(code)
        except FileNotFoundError:
            return ValidationResult(
                valid=False,
                errors=[f"File not found: {filepath}"],
                warnings=[],
                suggestions=[],
                score=0
            )
        except Exception as e:
            return ValidationResult(
                valid=False,
                errors=[f"Error reading file: {str(e)}"],
                warnings=[],
                suggestions=[],
                score=0
            )
    
    def format_validation_report(self, result: ValidationResult) -> str:
        """
        Format validation results as a readable report.
        
        Args:
            result: ValidationResult to format
            
        Returns:
            Formatted string report
        """
        report = []
        report.append("=" * 70)
        report.append("CODE VALIDATION REPORT")
        report.append("=" * 70)
        report.append(f"\nStatus: {'✅ VALID' if result.valid else '❌ INVALID'}")
        report.append(f"Score: {result.score}/100")
        
        if result.errors:
            report.append(f"\n❌ Errors ({len(result.errors)}):")
            for i, error in enumerate(result.errors, 1):
                report.append(f"  {i}. {error}")
        
        if result.warnings:
            report.append(f"\n⚠️  Warnings ({len(result.warnings)}):")
            for i, warning in enumerate(result.warnings, 1):
                report.append(f"  {i}. {warning}")
        
        if result.suggestions:
            report.append(f"\n💡 Suggestions ({len(result.suggestions)}):")
            for i, suggestion in enumerate(result.suggestions, 1):
                report.append(f"  {i}. {suggestion}")
        
        if result.valid and not result.warnings and not result.suggestions:
            report.append("\n🎉 Perfect! No issues found.")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of the CodeValidator.
    """
    
    # Example 1: Valid code
    valid_code = """
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from dotenv import load_dotenv
import os

load_dotenv()

agent = Agent(
    name="Search Agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
    instructions="Search the web for information",
)

if __name__ == "__main__":
    agent.print_response("Tell me about AI")
"""
    
    # Example 2: Invalid code with errors
    invalid_code = """
from agno.agents import Agent  # Wrong import
from agno.team.team import Team  # Wrong import

agent = Agent(
    name="Test Agent",
    # Missing model parameter
    tools=["duckduckgo"],  # Wrong: should be tool object
)

agent.run("test"  # Syntax error: missing closing paren
"""
    
    # Create validator
    validator = CodeValidator()
    
    # Test valid code
    print("Testing VALID code:")
    print("-" * 70)
    result1 = validator.validate_python_code(valid_code)
    print(validator.format_validation_report(result1))
    
    print("\n\n")
    
    # Test invalid code
    print("Testing INVALID code:")
    print("-" * 70)
    result2 = validator.validate_python_code(invalid_code)
    print(validator.format_validation_report(result2))