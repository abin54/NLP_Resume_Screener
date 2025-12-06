"""
Streamlit Web App for Resume Screening
HR-facing interface for uploading JDs and ranking candidates
"""

import streamlit as st
import pandas as pd
import sys
sys.path.append('../src')

st.set_page_config(page_title="Resume Screener", page_icon="📄", layout="wide")

st.title("📄 Indian Resume Screening System")
st.markdown("ATS-style resume matching with English + Hindi language support")

# Initialize session state
if 'candidates' not in st.session_state:
    st.session_state.candidates = []

# Skill database (simplified for demo)
SKILLS = {
    'programming': ['python', 'java', 'javascript', 'c++', 'sql', 'r'],
    'ml_ai': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'nlp'],
    'data': ['pandas', 'numpy', 'tableau', 'power bi', 'excel'],
    'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes'],
    'database': ['mysql', 'postgresql', 'mongodb', 'redis']
}

def extract_skills_simple(text):
    """Simple skill extraction"""
    text_lower = text.lower()
    found = []
    for category, skills in SKILLS.items():
        for skill in skills:
            if skill in text_lower:
                found.append(skill)
    return found

def calculate_match(resume_text, jd_text):
    """Calculate match score"""
    jd_skills = set(extract_skills_simple(jd_text))
    resume_skills = set(extract_skills_simple(resume_text))

    if not jd_skills:
        return 0, [], []

    matched = jd_skills.intersection(resume_skills)
    missing = jd_skills - resume_skills
    score = len(matched) / len(jd_skills) * 100

    return round(score, 1), list(matched), list(missing)

# Tabs
tab1, tab2, tab3 = st.tabs(["📝 Job Description", "📁 Upload Resumes", "📊 Results"])

with tab1:
    st.header("Enter Job Description")

    jd_text = st.text_area(
        "Paste job description here",
        height=300,
        placeholder="""Example:
Data Scientist - 3+ years experience

Requirements:
- Strong Python programming skills
- Experience with Machine Learning and TensorFlow
- SQL database knowledge
- AWS cloud experience

Nice to have:
- NLP experience
- Docker/Kubernetes"""
    )

    if jd_text:
        st.subheader("Extracted Requirements")
        jd_skills = extract_skills_simple(jd_text)
        if jd_skills:
            st.success(f"Skills identified: {', '.join(jd_skills)}")
        else:
            st.warning("No skills identified. Try adding more technical terms.")

with tab2:
    st.header("Add Candidates")

    col1, col2 = st.columns(2)

    with col1:
        candidate_name = st.text_input("Candidate Name")
        candidate_email = st.text_input("Email")

    with col2:
        resume_text = st.text_area(
            "Resume Content",
            height=200,
            placeholder="Paste resume text here..."
        )

    if st.button("Add Candidate", type="primary"):
        if candidate_name and resume_text:
            st.session_state.candidates.append({
                'name': candidate_name,
                'email': candidate_email,
                'text': resume_text
            })
            st.success(f"Added {candidate_name}")
        else:
            st.error("Please enter name and resume text")

    # Show added candidates
    if st.session_state.candidates:
        st.subheader(f"Candidates Added: {len(st.session_state.candidates)}")
        for i, c in enumerate(st.session_state.candidates):
            st.write(f"{i+1}. {c['name']} ({c['email']})")

        if st.button("Clear All Candidates"):
            st.session_state.candidates = []
            st.rerun()

    # Sample candidates button
    st.markdown("---")
    if st.button("Load Sample Candidates"):
        st.session_state.candidates = [
            {
                'name': 'Rahul Kumar',
                'email': 'rahul@email.com',
                'text': 'Python developer with 4 years experience. Skills: Python, Machine Learning, TensorFlow, SQL, AWS, Docker. Worked on NLP projects.'
            },
            {
                'name': 'Priya Sharma',
                'email': 'priya@email.com',
                'text': 'Data Analyst with 2 years experience. Skills: Python, SQL, Tableau, Power BI, Excel. Basic knowledge of machine learning.'
            },
            {
                'name': 'Amit Singh',
                'email': 'amit@email.com',
                'text': 'Software Engineer with 5 years experience. Skills: Java, JavaScript, MySQL, PostgreSQL, AWS, Kubernetes.'
            },
            {
                'name': 'Sneha Reddy',
                'email': 'sneha@email.com',
                'text': 'ML Engineer with 3 years experience. Skills: Python, Deep Learning, PyTorch, TensorFlow, NLP, AWS, GCP, Docker.'
            }
        ]
        st.success("Loaded 4 sample candidates")
        st.rerun()

with tab3:
    st.header("Screening Results")

    if not jd_text:
        st.warning("Please enter a job description in the first tab")
    elif not st.session_state.candidates:
        st.warning("Please add candidates in the second tab")
    else:
        if st.button("🔍 Screen Candidates", type="primary"):
            results = []

            for candidate in st.session_state.candidates:
                score, matched, missing = calculate_match(candidate['text'], jd_text)
                results.append({
                    'Rank': 0,
                    'Name': candidate['name'],
                    'Email': candidate['email'],
                    'Match Score': f"{score}%",
                    'Matched Skills': ', '.join(matched) if matched else 'None',
                    'Missing Skills': ', '.join(missing) if missing else 'None',
                    'score_num': score
                })

            # Sort and rank
            results.sort(key=lambda x: x['score_num'], reverse=True)
            for i, r in enumerate(results):
                r['Rank'] = i + 1

            # Display results
            st.subheader("Candidate Rankings")

            # Top candidate highlight
            if results:
                top = results[0]
                st.success(f"🏆 Top Candidate: **{top['Name']}** with {top['Match Score']} match")

            # Results table
            df = pd.DataFrame(results)
            display_cols = ['Rank', 'Name', 'Email', 'Match Score', 'Matched Skills', 'Missing Skills']
            st.dataframe(df[display_cols], use_container_width=True, hide_index=True)

            # Detailed view
            st.subheader("Detailed Analysis")
            for r in results:
                with st.expander(f"{r['Rank']}. {r['Name']} - {r['Match Score']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Matched Skills:**")
                        if r['Matched Skills'] != 'None':
                            for skill in r['Matched Skills'].split(', '):
                                st.write(f"✅ {skill}")
                        else:
                            st.write("No matching skills")
                    with col2:
                        st.write("**Missing Skills:**")
                        if r['Missing Skills'] != 'None':
                            for skill in r['Missing Skills'].split(', '):
                                st.write(f"❌ {skill}")
                        else:
                            st.write("All required skills present!")

            # Download results
            csv = df[display_cols].to_csv(index=False)
            st.download_button(
                "Download Results (CSV)",
                csv,
                "screening_results.csv",
                "text/csv"
            )

st.markdown("---")
st.markdown("**Resume Screening System** | Built for Indian Job Market | © 2024")
