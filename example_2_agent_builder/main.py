"""
Agno Agent Builder Team - FIXED VERSION
========================================

A meta-agent system that generates complete Agno agents from natural language descriptions.
This version FORCES code generation without asking for permission.

Author: Agno Agent Builder Team
Date: October 2025
Version: 1.2 - FIXED
"""

import os
import json
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Agno imports
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.db.sqlite import SqliteDb


# ============================================================================
# UTILITY FUNCTIONS (moved to top)
# ============================================================================

def save_generated_agent(response: str, agent_name: str) -> Optional[Path]:
    """Save the generated agent package to the outputs directory."""
    try:
        print("\n📦 Attempting to save generated files...")
        print(f"Response length: {len(response)} characters")
        
        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = agent_name.lower().replace(" ", "_").replace("-", "_")
        output_dir = Path("outputs") / f"{safe_name}_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Parse the response and extract files
        files = {
            "main.py": None,
            "README.md": None,
            "requirements.txt": None,
            ".env.example": None,
        }
        
        # Debug: Show what we're looking for
        print("\n🔍 Searching for file markers in response...")
        file_markers_found = []
        for line in response.split("\n"):
            if "=== FILE:" in line:
                file_markers_found.append(line.strip())
        
        if file_markers_found:
            print(f"✅ Found {len(file_markers_found)} file markers:")
            for marker in file_markers_found:
                print(f"   - {marker}")
        else:
            print("❌ No file markers found in response!")
            print("\n📄 First 500 characters of response:")
            print(response[:500])
            return None
        
        # Simple parsing - look for file markers
        current_file = None
        current_content = []
        in_code_block = False
        
        for line in response.split("\n"):
            if "=== FILE:" in line:
                # Save previous file if any
                if current_file and current_content:
                    content = "\n".join(current_content).strip()
                    files[current_file] = content
                    print(f"   📝 Extracted {current_file}: {len(content)} characters")
                    current_content = []
                    in_code_block = False
                
                # Extract new filename
                current_file = line.split("FILE:")[1].split("===")[0].strip()
                continue
            
            if current_file:
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block or (current_file == "requirements.txt" or current_file == ".env.example"):
                    current_content.append(line)
        
        # Save last file
        if current_file and current_content:
            content = "\n".join(current_content).strip()
            files[current_file] = content
            print(f"   📝 Extracted {current_file}: {len(content)} characters")
        
        # Write files to disk
        files_saved = 0
        for filename, content in files.items():
            if content:
                file_path = output_dir / filename
                file_path.write_text(content)
                print(f"✅ Saved: {file_path}")
                files_saved += 1
            else:
                print(f"⚠️  Skipped {filename}: No content extracted")
        
        if files_saved > 0:
            print(f"\n🎉 Generated agent package saved to: {output_dir}")
            print(f"   {files_saved}/4 files saved successfully")
            return output_dir
        else:
            print(f"\n❌ No files were saved! Check the response format.")
            return None
        
    except Exception as e:
        print(f"❌ Error saving generated agent: {e}")
        import traceback
        traceback.print_exc()
        return None


async def build_agent(user_request: str, save_output: bool = True) -> str:
    """
    Build a complete Agno agent package from a natural language request.
    Uses a sequential approach to ensure all agents run and files are generated.
    """
    print("\n" + "="*70)
    print("🤖 AGNO AGENT BUILDER TEAM - STARTING")
    print("="*70)
    print(f"\n📝 User Request: {user_request}\n")
    
    # ========================================================================
    # STEP 1: Setup Knowledge Base
    # ========================================================================
    print("🔧 Setting up Agno Docs Knowledge base...")
    knowledge = Knowledge(
        vector_db=LanceDb(
            uri="./tmp/lancedb",
            table_name="agno_docs_knowledge",
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(id="text-embedding-3-small"),
        ),
    )
    
    if not os.path.exists("./tmp/lancedb"):
        print("📚 Loading Agno documentation (this may take a minute)...")
        await knowledge.add_content_async(
            name="Agno Docs", 
            url="https://docs.agno.com/llms-full.txt"
        )
        print("✅ Agno documentation loaded\n")
    else:
        print("✅ Using existing knowledge base\n")
    
    # ========================================================================
    # STEP 2: Requirements Analyst - Parse the request
    # ========================================================================
    print("="*70)
    print("🔹 STEP 1/3: Requirements Analyst")
    print("="*70)
    
    requirements_analyst = Agent(
        name="Requirements Analyst",
        model=OpenAIChat(id="gpt-4o"),
        instructions=[
            "You are an expert at analyzing user requests for agent development.",
            "Parse the user's request and extract structured requirements.",
            "",
            "Output ONLY a JSON object with this EXACT format:",
            "{",
            '  "type": "single_agent" or "agent_team",',
            '  "name": "Agent Name",',
            '  "purpose": "Clear description",',
            '  "features": {',
            '    "tools": ["GitHub", "DuckDuckGo", etc.],',
            '    "memory": true/false,',
            '    "knowledge": true/false,',
            '    "reasoning": true/false',
            "  },",
            '  "model": "gpt-4o",',
            '  "instructions": "Detailed instructions"',
            "}",
            "",
            "DO NOT add any text before or after the JSON.",
            "Output ONLY the JSON object.",
        ],
        markdown=False,
    )
    
    print("⏳ Analyzing requirements...")
    requirements_response = await requirements_analyst.arun(user_request)
    requirements = requirements_response.content if hasattr(requirements_response, 'content') else str(requirements_response)
    print(f"✅ Requirements extracted ({len(requirements)} chars)")
    print(f"\n📋 Requirements:\n{requirements[:300]}...\n")
    
    # ========================================================================
    # STEP 2: Agno Docs Expert - Fetch documentation
    # ========================================================================
    print("="*70)
    print("🔹 STEP 2/3: Agno Docs Expert")
    print("="*70)
    
    agno_docs_expert = Agent(
        name="Agno Docs Expert",
        model=OpenAIChat(id="gpt-4o"),
        db=SqliteDb(db_file="./tmp/agents.db"),
        knowledge=knowledge,
        instructions=[
            "You are an expert on the Agno framework.",
            "Search your knowledge base for relevant Agno documentation and examples.",
            "",
            "Based on the requirements, find:",
            "- Correct import patterns for Agno",
            "- Code examples for the requested tools",
            "- Agent/Team configuration examples",
            "- Best practices",
            "",
            "Provide comprehensive code examples and documentation.",
            "Focus on CURRENT Agno patterns (not outdated ones).",
        ],
        markdown=True,
        add_history_to_context=True,
    )
    
    print("⏳ Fetching Agno documentation...")
    docs_query = f"Given these requirements:\n{requirements}\n\nProvide Agno code examples and documentation for building this agent."
    docs_response = await agno_docs_expert.arun(docs_query)
    docs = docs_response.content if hasattr(docs_response, 'content') else str(docs_response)
    print(f"✅ Documentation fetched ({len(docs)} chars)")
    print(f"\n📚 Docs preview:\n{docs[:300]}...\n")
    
    # ========================================================================
    # STEP 3: Code Generator - GENERATE FILES (NO ASKING!)
    # ========================================================================
    print("="*70)
    print("🔹 STEP 3/3: Code Generator")
    print("="*70)
    
    code_generator = Agent(
        name="Code Generator",
        model=OpenAIChat(id="gpt-4o"),
        instructions=[
            "You are an expert Python developer specializing in the Agno framework.",
            "",
            "⚠️ CRITICAL INSTRUCTIONS:",
            "1. You MUST generate ALL FOUR files immediately",
            "2. DO NOT ask for permission or confirmation",
            "3. DO NOT suggest modifications",
            "4. DO NOT provide summaries - GENERATE THE ACTUAL CODE",
            "",
            "Generate EXACTLY FOUR files with these EXACT markers:",
            "",
            "=== FILE: main.py ===",
            "```python",
            "# Complete, working Agno agent code here",
            "```",
            "",
            "=== FILE: README.md ===",
            "```markdown",
            "# Complete README here",
            "```",
            "",
            "=== FILE: requirements.txt ===",
            "```",
            "agno>=1.1.0",
            "openai>=1.0.0",
            "# ... other dependencies",
            "```",
            "",
            "=== FILE: .env.example ===",
            "```",
            "OPENAI_API_KEY=sk-your-key-here",
            "# ... other keys",
            "```",
            "",
            "REQUIREMENTS FOR main.py:",
            "- Use CORRECT imports: from agno.agent import Agent",
            "- Include complete, runnable code (no placeholders)",
            "- Add error handling and type hints",
            "- Include usage example in if __name__ == '__main__'",
            "",
            "REQUIREMENTS FOR README.md:",
            "- Project title and description",
            "- Features list",
            "- Installation instructions",
            "- Usage examples",
            "",
            "START GENERATING NOW. DO NOT WAIT. DO NOT ASK.",
        ],
        markdown=True,
    )
    
    print("⏳ Generating complete agent package...")
    generation_query = f"""Given these requirements:
{requirements}

And this Agno documentation:
{docs}

Generate a COMPLETE agent package with ALL FOUR files NOW.
Use the === FILE: === markers as shown in your instructions.
DO NOT ask for confirmation - GENERATE THE FILES IMMEDIATELY."""
    
    code_response = await code_generator.arun(generation_query)
    generated_code = code_response.content if hasattr(code_response, 'content') else str(code_response)
    
    print(f"✅ Code generated ({len(generated_code)} chars)")
    
    # Check if files were actually generated
    if "=== FILE:" not in generated_code:
        print("\n❌ WARNING: Code Generator did not output file markers!")
        print("Trying again with more forceful instructions...")
        
        force_generate = await code_generator.arun(
            "STOP ASKING AND GENERATE THE FOUR FILES NOW WITH === FILE: === MARKERS. "
            "I DO NOT WANT A SUMMARY. I WANT THE ACTUAL CODE FILES. "
            "START WITH '=== FILE: main.py ===' RIGHT NOW."
        )
        generated_code = force_generate.content if hasattr(force_generate, 'content') else str(force_generate)
    
    print("\n" + "="*70)
    print("📄 GENERATED CODE PREVIEW")
    print("="*70)
    print(generated_code[:500])
    print("...")
    print("="*70)
    
    # Save if requested
    if save_output:
        agent_name = "generated_agent"
        # Try to extract name from requirements JSON
        try:
            req_json = json.loads(requirements)
            if "name" in req_json:
                agent_name = req_json["name"]
        except:
            pass
        
        saved_path = save_generated_agent(generated_code, agent_name)
        if not saved_path:
            print("\n⚠️  Files were not saved. Showing full generated code:")
            print(generated_code)
    
    return generated_code


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main async function to run the agent builder."""
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please create a .env file with your OpenAI API key")
        return
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║           🤖 AGNO AGENT BUILDER - FIXED 🤖                   ║
    ║                                                              ║
    ║  Sequential execution: Analyst → Docs → Generator           ║
    ║  FORCES code generation without asking permission           ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Example request
    example_1 = "Build an agent that searches GitHub repositories for Python projects"
    
    # Run the builder
    result = await build_agent(example_1, save_output=True)
    
    print("\n" + "="*70)
    print("✅ AGENT GENERATION COMPLETE")
    print("="*70)
    print("\nCheck the 'outputs' directory for your generated agent package!")


if __name__ == "__main__":
    asyncio.run(main())