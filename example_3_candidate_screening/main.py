"""
AI Candidate Screening Team - MVP
===================================

A multi-agent system that automatically screens candidates against job requirements.

4-Agent Team:
1. Resume Parser - Extracts structured data from resumes
2. Skills Matcher - Matches candidate skills to job requirements
3. Experience Evaluator - Analyzes work experience relevance
4. Scorer & Ranker - Ranks candidates with detailed reports

Author: Built for TalentPerformer
Date: October 2025
Version: 1.0 MVP
"""

import os
import json
import asyncio
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Agno imports
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat


# ============================================================================
# SAMPLE DATA (For MVP Testing)
# ============================================================================

SAMPLE_JOB_DESCRIPTION = """
Senior Python Developer

Requirements:
- 5+ years of Python development experience
- Strong knowledge of Django or Flask frameworks
- Experience with AWS (EC2, S3, Lambda)
- React.js for frontend development
- SQL and NoSQL databases (PostgreSQL, MongoDB)
- Docker and Kubernetes
- Git version control
- Bachelor's degree in Computer Science or related field

Nice to have:
- Machine Learning experience
- CI/CD pipeline setup
- Agile/Scrum methodologies
"""

SAMPLE_RESUMES = {
    "candidate_1.txt": """
John Smith
Email: john.smith@email.com
Phone: +1-555-0100

EXPERIENCE:
Senior Software Engineer at TechCorp (2019-2024, 5 years)
- Led development of Python-based microservices using Django
- Implemented AWS infrastructure (EC2, S3, Lambda, RDS)
- Built React.js dashboards for data visualization
- Managed PostgreSQL and MongoDB databases
- Containerized applications using Docker
- Mentored junior developers

Software Developer at StartupXYZ (2017-2019, 2 years)
- Developed Flask APIs for mobile applications
- Set up CI/CD pipelines using Jenkins
- Worked in Agile teams

EDUCATION:
Bachelor of Science in Computer Science, MIT (2017)

SKILLS:
Python, Django, Flask, AWS, React, PostgreSQL, MongoDB, Docker, Kubernetes, Git, Machine Learning basics, Jenkins, Agile
""",

    "candidate_2.txt": """
Sarah Johnson
Email: sarah.j@email.com
Phone: +1-555-0200

EXPERIENCE:
Python Developer at DataCo (2021-2024, 3 years)
- Built data pipelines using Python and pandas
- Created Flask APIs for internal tools
- Worked with MySQL databases
- Used Git for version control

Junior Developer at WebAgency (2019-2021, 2 years)
- Developed WordPress sites
- Some JavaScript and jQuery
- Basic SQL queries

EDUCATION:
Bachelor of Arts in Information Systems, State University (2019)

SKILLS:
Python, Flask, pandas, MySQL, Git, JavaScript, HTML, CSS, WordPress
""",

    "candidate_3.txt": """
Michael Chen
Email: m.chen@email.com
Phone: +1-555-0300

EXPERIENCE:
Lead Full Stack Developer at FinTech Inc (2018-2024, 6 years)
- Architected Python microservices with Django REST Framework
- Built React.js SPAs with Redux
- Managed AWS infrastructure (EC2, S3, RDS, Lambda, CloudFormation)
- Implemented Docker containerization and Kubernetes orchestration
- Database design with PostgreSQL and Redis
- Designed and deployed CI/CD pipelines
- Led Scrum teams as technical lead

Software Engineer at eCommerce Corp (2015-2018, 3 years)
- Developed Django applications
- Integrated payment gateways
- MongoDB for product catalogs

EDUCATION:
Master of Science in Computer Science, Stanford (2015)
Bachelor of Science in Computer Engineering, UC Berkeley (2013)

SKILLS:
Python, Django, Django REST Framework, Flask, React.js, Redux, AWS (EC2, S3, RDS, Lambda, CloudFormation), 
Docker, Kubernetes, PostgreSQL, MongoDB, Redis, Git, CI/CD, Jenkins, GitHub Actions, Agile, Scrum, 
Machine Learning (TensorFlow, scikit-learn), System Design
"""
}


# ============================================================================
# AGENT 1: Resume Parser
# ============================================================================

resume_parser = Agent(
    name="Resume Parser",
    role="Extract structured data from resumes",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=[
        "You are an expert at extracting structured information from resumes.",
        "",
        "Extract the following information and output as JSON:",
        "1. name - candidate's full name",
        "2. email - email address",
        "3. phone - phone number",
        "4. skills - list of technical skills (as array)",
        "5. total_years_experience - total years of professional experience (number)",
        "6. experience - array of jobs with: title, company, years (number), key_responsibilities (array)",
        "7. education - array with: degree, field, school, year",
        "",
        "Output ONLY valid JSON, no other text.",
        "",
        "Example output:",
        "{",
        '  "name": "John Doe",',
        '  "email": "john@email.com",',
        '  "phone": "+1-555-0123",',
        '  "skills": ["Python", "Django", "AWS"],',
        '  "total_years_experience": 5,',
        '  "experience": [',
        '    {',
        '      "title": "Senior Developer",',
        '      "company": "TechCorp",',
        '      "years": 3,',
        '      "key_responsibilities": ["Led team", "Built APIs"]',
        '    }',
        '  ],',
        '  "education": [',
        '    {',
        '      "degree": "Bachelor of Science",',
        '      "field": "Computer Science",',
        '      "school": "MIT",',
        '      "year": 2020',
        '    }',
        '  ]',
        '}',
    ],
    markdown=False,
)


# ============================================================================
# AGENT 2: Skills Matcher
# ============================================================================

skills_matcher = Agent(
    name="Skills Matcher",
    role="Match candidate skills against job requirements",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=[
        "You are an expert at matching candidate skills to job requirements.",
        "",
        "Given:",
        "1. Job description with required skills",
        "2. Candidate's parsed resume data (JSON)",
        "",
        "Analyze and output JSON with:",
        "1. required_skills - array of skills required by the job",
        "2. candidate_skills - array of candidate's skills",
        "3. matched_skills - skills the candidate has that match requirements",
        "4. missing_skills - required skills the candidate lacks",
        "5. bonus_skills - candidate skills that are nice-to-have or extra",
        "6. skills_match_score - percentage match (0-100)",
        "",
        "Consider semantic similarity (e.g., 'React.js' matches 'React', 'PostgreSQL' matches 'Postgres').",
        "",
        "Output ONLY valid JSON.",
    ],
    markdown=False,
)


# ============================================================================
# AGENT 3: Experience Evaluator
# ============================================================================

experience_evaluator = Agent(
    name="Experience Evaluator",
    role="Evaluate work experience relevance and seniority",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=[
        "You are an expert at evaluating candidate work experience.",
        "",
        "Given:",
        "1. Job description with experience requirements",
        "2. Candidate's parsed resume data (JSON)",
        "",
        "Analyze and output JSON with:",
        "1. required_years - years required by job",
        "2. candidate_years - candidate's total years",
        "3. meets_experience_requirement - true/false",
        "4. relevant_experience - array of relevant jobs with brief explanation",
        "5. seniority_level - Junior/Mid/Senior/Lead based on roles",
        "6. progression - description of career progression",
        "7. experience_score - score 0-100 based on:",
        "   - Years of experience (40 points)",
        "   - Relevance of roles (30 points)",
        "   - Seniority/leadership (20 points)",
        "   - Career progression (10 points)",
        "",
        "Output ONLY valid JSON.",
    ],
    markdown=False,
)


# ============================================================================
# AGENT 4: Scorer & Ranker
# ============================================================================

scorer_ranker = Agent(
    name="Scorer & Ranker",
    role="Calculate final scores and generate candidate reports",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=[
        "You are an expert at scoring and ranking candidates.",
        "",
        "Given:",
        "1. Job description",
        "2. Parsed resume data",
        "3. Skills match analysis",
        "4. Experience evaluation",
        "",
        "Calculate final score using weighted formula:",
        "- Skills Match: 40%",
        "- Experience: 35%",
        "- Education: 15%",
        "- Bonus factors: 10% (leadership, certifications, etc.)",
        "",
        "Output JSON with:",
        "1. candidate_name",
        "2. final_score - 0-100",
        "3. skills_score - from skills matcher",
        "4. experience_score - from experience evaluator",
        "5. education_score - 0-100 based on degree relevance",
        "6. recommendation - STRONG_YES/YES/MAYBE/NO",
        "7. strengths - array of top 3-5 strengths",
        "8. concerns - array of any concerns or gaps",
        "9. summary - 2-3 sentence hiring recommendation",
        "",
        "Recommendation thresholds:",
        "- STRONG_YES: score >= 85",
        "- YES: score >= 70",
        "- MAYBE: score >= 55",
        "- NO: score < 55",
        "",
        "Output ONLY valid JSON.",
    ],
    markdown=False,
)


# ============================================================================
# SCREENING TEAM
# ============================================================================

screening_team = Team(
    name="AI Candidate Screening Team",
    members=[
        resume_parser,
        skills_matcher,
        experience_evaluator,
        scorer_ranker,
    ],
    num_history_runs=3,
    markdown=False,
)


# ============================================================================
# SCREENING FUNCTIONS
# ============================================================================

async def screen_candidate(resume_text: str, job_description: str, candidate_name: str) -> Dict[str, Any]:
    """
    Screen a single candidate through the 4-agent pipeline.
    
    Args:
        resume_text: Raw resume text
        job_description: Job description text
        candidate_name: Name/ID for logging
        
    Returns:
        Screening results as dictionary
    """
    print(f"\n{'='*70}")
    print(f"🔍 SCREENING: {candidate_name}")
    print(f"{'='*70}\n")
    
    # Combine inputs for the team
    screening_request = f"""
Job Description:
{job_description}

---

Candidate Resume:
{resume_text}

---

Please screen this candidate through all 4 stages:
1. Parse the resume
2. Match skills to requirements
3. Evaluate experience
4. Calculate final score and recommendation
"""
    
    # Run the screening team
    print("⏳ Running 4-agent screening pipeline...\n")
    response = await screening_team.arun(screening_request)
    
    # Extract the final result
    content = response.content if hasattr(response, 'content') else str(response)
    
    print(f"✅ Screening complete for {candidate_name}\n")
    
    return {
        "candidate": candidate_name,
        "screening_result": content,
        "timestamp": datetime.now().isoformat()
    }


async def screen_all_candidates(job_description: str, resumes: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Screen multiple candidates and rank them.
    
    Args:
        job_description: Job description text
        resumes: Dictionary of {filename: resume_text}
        
    Returns:
        List of screening results
    """
    print(f"\n{'='*70}")
    print(f"🎯 AI CANDIDATE SCREENING SYSTEM")
    print(f"{'='*70}")
    print(f"\n📋 Job: Senior Python Developer")
    print(f"📊 Candidates to screen: {len(resumes)}\n")
    
    results = []
    
    # Screen each candidate
    for filename, resume_text in resumes.items():
        result = await screen_candidate(resume_text, job_description, filename)
        results.append(result)
        
        # Brief pause between candidates (API rate limits)
        await asyncio.sleep(1)
    
    return results


def save_screening_results(results: List[Dict[str, Any]]) -> Path:
    """Save screening results to file."""
    output_dir = Path("outputs/screening_results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"screening_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    return output_file


def print_summary(results: List[Dict[str, Any]]):
    """Print a summary of screening results."""
    print(f"\n{'='*70}")
    print(f"📊 SCREENING SUMMARY")
    print(f"{'='*70}\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['candidate']}")
        
        # Try to extract key info from the result
        content = result['screening_result']
        if 'final_score' in content.lower():
            print(f"   Preview: {content[:200]}...")
        else:
            print(f"   (See full results in output file)")
        print()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main function to run the screening system."""
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found")
        print("Please create a .env file with your OpenAI API key")
        return
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║       🎯 AI CANDIDATE SCREENING TEAM - MVP                   ║
    ║                                                              ║
    ║  Built for TalentPerformer - Agentic Solutions              ║
    ║                                                              ║
    ║  4-Agent Pipeline:                                          ║
    ║  1. Resume Parser                                           ║
    ║  2. Skills Matcher                                          ║
    ║  3. Experience Evaluator                                    ║
    ║  4. Scorer & Ranker                                         ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Run screening
    results = await screen_all_candidates(SAMPLE_JOB_DESCRIPTION, SAMPLE_RESUMES)
    
    # Save results
    save_screening_results(results)
    
    # Print summary
    print_summary(results)
    
    print(f"\n{'='*70}")
    print("✅ SCREENING COMPLETE")
    print(f"{'='*70}")
    print("\n📝 Next steps:")
    print("1. Review detailed results in outputs/screening_results/")
    print("2. Each candidate has full analysis and recommendation")
    print("3. Scores are weighted: Skills 40%, Experience 35%, Education 15%, Bonus 10%")


if __name__ == "__main__":
    asyncio.run(main())