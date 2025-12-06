"""
Skill Extraction and Matching Engine
Extracts skills from resumes and matches with job descriptions
"""

import re
from typing import List, Dict, Set, Tuple
from collections import defaultdict

class SkillExtractor:
    """Extract and categorize skills from resumes"""

    # Comprehensive skill database for Indian tech jobs
    SKILL_DATABASE = {
        'programming': {
            'python', 'java', 'javascript', 'c++', 'c', 'c#', 'ruby', 'go', 'golang',
            'rust', 'scala', 'kotlin', 'swift', 'typescript', 'php', 'perl', 'r',
            'matlab', 'julia', 'shell', 'bash', 'powershell', 'vba'
        },
        'web_development': {
            'html', 'css', 'react', 'angular', 'vue', 'vuejs', 'nodejs', 'node.js',
            'express', 'django', 'flask', 'fastapi', 'spring', 'springboot',
            'asp.net', 'ruby on rails', 'laravel', 'bootstrap', 'tailwind',
            'jquery', 'webpack', 'next.js', 'nuxt', 'gatsby'
        },
        'data_science': {
            'machine learning', 'deep learning', 'nlp', 'natural language processing',
            'computer vision', 'tensorflow', 'pytorch', 'keras', 'scikit-learn',
            'sklearn', 'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn',
            'plotly', 'opencv', 'spacy', 'nltk', 'huggingface', 'transformers',
            'xgboost', 'lightgbm', 'catboost', 'feature engineering', 'eda'
        },
        'databases': {
            'sql', 'mysql', 'postgresql', 'postgres', 'mongodb', 'redis',
            'cassandra', 'elasticsearch', 'oracle', 'sqlite', 'dynamodb',
            'neo4j', 'firebase', 'mariadb', 'mssql', 'sql server'
        },
        'cloud': {
            'aws', 'azure', 'gcp', 'google cloud', 'ec2', 's3', 'lambda',
            'cloudformation', 'terraform', 'kubernetes', 'k8s', 'docker',
            'jenkins', 'ci/cd', 'devops', 'ansible', 'chef', 'puppet'
        },
        'data_engineering': {
            'hadoop', 'spark', 'pyspark', 'hive', 'kafka', 'airflow',
            'etl', 'data pipeline', 'data warehouse', 'redshift', 'bigquery',
            'snowflake', 'databricks', 'dbt', 'nifi'
        },
        'bi_tools': {
            'tableau', 'power bi', 'powerbi', 'looker', 'qlik', 'metabase',
            'superset', 'excel', 'google sheets', 'reporting', 'dashboards'
        },
        'soft_skills': {
            'communication', 'leadership', 'teamwork', 'problem solving',
            'analytical', 'critical thinking', 'time management', 'agile',
            'scrum', 'project management', 'presentation'
        },
        'certifications': {
            'aws certified', 'azure certified', 'gcp certified', 'pmp',
            'scrum master', 'cissp', 'ccna', 'ccnp', 'comptia',
            'google analytics', 'hubspot', 'salesforce'
        }
    }

    # Skill aliases/variations
    SKILL_ALIASES = {
        'ml': 'machine learning',
        'dl': 'deep learning',
        'ai': 'artificial intelligence',
        'js': 'javascript',
        'ts': 'typescript',
        'py': 'python',
        'tf': 'tensorflow',
        'k8s': 'kubernetes',
        'postgres': 'postgresql',
        'mongo': 'mongodb',
        'react.js': 'react',
        'vue.js': 'vue',
        'node': 'nodejs'
    }

    def __init__(self):
        # Create flat skill set for quick lookup
        self.all_skills = set()
        self.skill_to_category = {}

        for category, skills in self.SKILL_DATABASE.items():
            for skill in skills:
                self.all_skills.add(skill.lower())
                self.skill_to_category[skill.lower()] = category

    def normalize_skill(self, skill: str) -> str:
        """Normalize skill name using aliases"""
        skill = skill.lower().strip()
        return self.SKILL_ALIASES.get(skill, skill)

    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract skills from text and categorize them"""
        text = text.lower()
        found_skills = defaultdict(list)

        # Check for each skill in database
        for skill in self.all_skills:
            # Create pattern that matches whole word
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text):
                category = self.skill_to_category[skill]
                if skill not in found_skills[category]:
                    found_skills[category].append(skill)

        # Check for aliases
        for alias, full_skill in self.SKILL_ALIASES.items():
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, text):
                if full_skill in self.skill_to_category:
                    category = self.skill_to_category[full_skill]
                    if full_skill not in found_skills[category]:
                        found_skills[category].append(full_skill)

        return dict(found_skills)

    def extract_experience_years(self, text: str) -> int:
        """Extract years of experience from text"""
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
            r'experience\s*(?:of)?\s*(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:in|of|working)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))

        return 0

    def get_skill_summary(self, skills: Dict[str, List[str]]) -> Dict:
        """Generate skill summary statistics"""
        total_skills = sum(len(s) for s in skills.values())

        summary = {
            'total_skills': total_skills,
            'categories': len(skills),
            'by_category': {cat: len(skills_list) for cat, skills_list in skills.items()},
            'top_categories': sorted(skills.items(), key=lambda x: len(x[1]), reverse=True)[:3]
        }

        return summary


class ResumeJobMatcher:
    """Match resumes to job descriptions"""

    def __init__(self):
        self.skill_extractor = SkillExtractor()

    def extract_jd_requirements(self, jd_text: str) -> Dict:
        """Extract requirements from job description"""
        requirements = {
            'skills': self.skill_extractor.extract_skills(jd_text),
            'experience': self.skill_extractor.extract_experience_years(jd_text),
            'must_have': [],
            'nice_to_have': []
        }

        # Look for required/must-have skills
        must_have_pattern = r'(?:required|must have|essential|mandatory)[:\s]+(.+?)(?:\n|$)'
        match = re.search(must_have_pattern, jd_text.lower())
        if match:
            requirements['must_have'] = self.skill_extractor.extract_skills(match.group(1))

        return requirements

    def calculate_match_score(self, resume_skills: Dict, jd_skills: Dict) -> Dict:
        """Calculate match score between resume and JD"""
        resume_flat = set()
        jd_flat = set()

        for skills in resume_skills.values():
            resume_flat.update(skills)
        for skills in jd_skills.values():
            jd_flat.update(skills)

        if not jd_flat:
            return {'score': 0, 'matched': [], 'missing': []}

        matched = resume_flat.intersection(jd_flat)
        missing = jd_flat - resume_flat

        score = len(matched) / len(jd_flat) * 100

        return {
            'score': round(score, 1),
            'matched': list(matched),
            'missing': list(missing),
            'extra': list(resume_flat - jd_flat)
        }

    def rank_candidates(self, resumes: List[Dict], jd_text: str) -> List[Dict]:
        """Rank multiple candidates for a job"""
        jd_requirements = self.extract_jd_requirements(jd_text)

        rankings = []
        for resume in resumes:
            resume_skills = self.skill_extractor.extract_skills(resume.get('text', ''))
            match = self.calculate_match_score(resume_skills, jd_requirements['skills'])

            rankings.append({
                'candidate': resume.get('name', 'Unknown'),
                'email': resume.get('email', ''),
                'score': match['score'],
                'matched_skills': match['matched'],
                'missing_skills': match['missing'],
                'total_skills': len(set().union(*resume_skills.values())) if resume_skills else 0
            })

        # Sort by score descending
        rankings.sort(key=lambda x: x['score'], reverse=True)

        # Add rank
        for i, r in enumerate(rankings):
            r['rank'] = i + 1

        return rankings


# Sample job description
SAMPLE_JD = """
Data Scientist - Bangalore

We are looking for an experienced Data Scientist to join our team.

Requirements:
- 3+ years of experience in data science/machine learning
- Strong programming skills in Python
- Experience with ML frameworks: TensorFlow, PyTorch, or Scikit-learn
- Proficiency in SQL and databases
- Experience with NLP and text analytics
- Knowledge of cloud platforms (AWS/GCP)

Nice to have:
- Experience with deep learning
- Big data tools: Spark, Hadoop
- Docker and Kubernetes experience

Skills: Python, Machine Learning, TensorFlow, SQL, NLP, AWS
"""

if __name__ == "__main__":
    extractor = SkillExtractor()
    matcher = ResumeJobMatcher()

    print("="*60)
    print("JOB DESCRIPTION ANALYSIS")
    print("="*60)

    jd_skills = extractor.extract_skills(SAMPLE_JD)
    print("\nSkills Required:")
    for category, skills in jd_skills.items():
        print(f"  {category}: {', '.join(skills)}")

    print(f"\nExperience Required: {extractor.extract_experience_years(SAMPLE_JD)} years")
