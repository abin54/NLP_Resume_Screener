"""
Text Processing for Indian Language Resume Screening
Handles mixed English + Hindi/Regional language content
"""

import re
import string
from typing import List, Dict
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)

class IndianResumeProcessor:
    """Process mixed-language Indian resumes"""

    # Common Hindi words in tech resumes (transliterated)
    HINDI_STOPWORDS = {
        'aur', 'hai', 'hain', 'ke', 'ka', 'ki', 'ko', 'se', 'me', 'mein',
        'par', 'tha', 'thi', 'the', 'ho', 'bhi', 'kiya', 'karna', 'karke',
        'saath', 'liye', 'wala', 'wali', 'diya', 'dena', 'lena', 'kuch'
    }

    # Indian education terms
    EDUCATION_TERMS = {
        'btech': 'B.Tech', 'b.tech': 'B.Tech', 'mtech': 'M.Tech', 'm.tech': 'M.Tech',
        'bca': 'BCA', 'mca': 'MCA', 'bsc': 'B.Sc', 'msc': 'M.Sc',
        'be': 'B.E', 'me': 'M.E', 'mba': 'MBA', 'bba': 'BBA',
        'cbse': 'CBSE', 'icse': 'ICSE', 'iit': 'IIT', 'nit': 'NIT',
        'iiit': 'IIIT', 'bits': 'BITS', 'vit': 'VIT', 'srm': 'SRM',
        '10th': '10th', '12th': '12th', 'intermediate': 'Intermediate',
        'diploma': 'Diploma', 'phd': 'Ph.D', 'pgdm': 'PGDM'
    }

    # Indian exam/certification terms
    CERTIFICATION_TERMS = {
        'gate': 'GATE', 'cat': 'CAT', 'gre': 'GRE', 'toefl': 'TOEFL',
        'ielts': 'IELTS', 'upsc': 'UPSC', 'ssc': 'SSC', 'ibps': 'IBPS',
        'neet': 'NEET', 'jee': 'JEE', 'clat': 'CLAT'
    }

    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.english_stopwords = set(stopwords.words('english'))

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)

        # Remove email addresses (but keep for extraction)
        text = re.sub(r'\S+@\S+', '', text)

        # Remove phone numbers
        text = re.sub(r'[\+]?[0-9]{10,13}', '', text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep periods and commas
        text = re.sub(r'[^\w\s.,]', ' ', text)

        return text.strip()

    def normalize_education(self, text: str) -> str:
        """Normalize Indian education terms"""
        words = text.split()
        normalized = []
        for word in words:
            word_lower = word.lower().strip('.,')
            if word_lower in self.EDUCATION_TERMS:
                normalized.append(self.EDUCATION_TERMS[word_lower])
            elif word_lower in self.CERTIFICATION_TERMS:
                normalized.append(self.CERTIFICATION_TERMS[word_lower])
            else:
                normalized.append(word)
        return ' '.join(normalized)

    def remove_stopwords(self, text: str) -> str:
        """Remove English and Hindi stopwords"""
        words = word_tokenize(text.lower())
        filtered = [
            word for word in words
            if word not in self.english_stopwords
            and word not in self.HINDI_STOPWORDS
            and word not in string.punctuation
            and len(word) > 2
        ]
        return ' '.join(filtered)

    def extract_contact_info(self, text: str) -> Dict:
        """Extract contact information from resume"""
        contact = {}

        # Email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            contact['email'] = email_match.group()

        # Phone (Indian format)
        phone_match = re.search(r'[\+]?[91]?[-\s]?[6-9]\d{9}', text)
        if phone_match:
            contact['phone'] = phone_match.group()

        # LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text)
        if linkedin_match:
            contact['linkedin'] = linkedin_match.group()

        # GitHub
        github_match = re.search(r'github\.com/[\w-]+', text)
        if github_match:
            contact['github'] = github_match.group()

        return contact

    def extract_sections(self, text: str) -> Dict:
        """Extract common resume sections"""
        sections = {}
        section_patterns = {
            'education': r'(?:education|academic|qualification)s?\s*[:\n](.+?)(?=experience|skill|project|work|$)',
            'experience': r'(?:experience|employment|work\s*history)\s*[:\n](.+?)(?=education|skill|project|$)',
            'skills': r'(?:skills?|technical\s*skills?|competencies)\s*[:\n](.+?)(?=experience|education|project|$)',
            'projects': r'(?:projects?|portfolio)\s*[:\n](.+?)(?=experience|education|skill|$)'
        }

        text_lower = text.lower()
        for section, pattern in section_patterns.items():
            match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            if match:
                sections[section] = match.group(1).strip()

        return sections

    def preprocess_resume(self, text: str) -> Dict:
        """Complete preprocessing pipeline"""
        result = {
            'original': text,
            'cleaned': self.clean_text(text),
            'contact': self.extract_contact_info(text),
            'sections': self.extract_sections(text)
        }

        result['normalized'] = self.normalize_education(result['cleaned'])
        result['tokens'] = self.remove_stopwords(result['normalized'])

        return result


# Sample resume texts for testing
SAMPLE_RESUMES = [
    """
    Rahul Kumar
    Email: rahul.kumar@gmail.com | Phone: +91-9876543210
    LinkedIn: linkedin.com/in/rahulkumar | GitHub: github.com/rahulk

    EDUCATION
    B.Tech in Computer Science, IIT Delhi (2020-2024) - CGPA: 8.5
    12th CBSE, DPS Delhi (2020) - 95%
    10th CBSE, DPS Delhi (2018) - 94%

    SKILLS
    Programming: Python, Java, C++, JavaScript
    ML/AI: TensorFlow, PyTorch, Scikit-learn
    Web: React, Node.js, Django
    Database: MySQL, MongoDB, PostgreSQL
    Cloud: AWS, GCP, Docker

    EXPERIENCE
    Data Science Intern, TCS (May 2023 - July 2023)
    - Developed ML models for customer churn prediction
    - Worked on NLP projects for sentiment analysis

    PROJECTS
    - E-commerce Recommendation System using collaborative filtering
    - Stock Price Prediction using LSTM neural networks
    """,

    """
    Priya Sharma
    priya.sharma@outlook.com | 8765432109
    Bangalore, Karnataka

    QUALIFICATIONS
    MCA from Christ University (2022) - 85%
    BCA from Bangalore University (2020) - 82%
    Intermediate from State Board - 88%

    TECHNICAL SKILLS
    Languages: Python, R, SQL
    Tools: Tableau, Power BI, Excel
    ML: Regression, Classification, Clustering
    Big Data: Hadoop, Spark basics

    PROJECT WORK
    Sales Analytics Dashboard for retail client
    Customer Segmentation using K-Means clustering
    Predictive maintenance model for manufacturing
    """
]

if __name__ == "__main__":
    processor = IndianResumeProcessor()

    for i, resume in enumerate(SAMPLE_RESUMES):
        print(f"\n{'='*60}")
        print(f"RESUME {i+1}")
        print('='*60)

        result = processor.preprocess_resume(resume)

        print(f"\nContact Info: {result['contact']}")
        print(f"\nSections Found: {list(result['sections'].keys())}")
        print(f"\nCleaned Text Preview: {result['cleaned'][:200]}...")
