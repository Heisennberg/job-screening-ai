import streamlit as st
import sqlite3
import pdfplumber
from io import BytesIO
from agents import extract_keywords, calculate_ats_score, detect_bias
from database import setup_database
from clean_data import clean_text

# Initialize database
setup_database()

# Custom CSS with your color scheme
st.markdown(f"""
<style>
    .report-title {{ 
        font-size: 28px !important; 
        color: #A7AFD1;
        border-bottom: 2px solid #A7AFD1;
        padding-bottom: 10px;
    }}
    body {{
        background-color: #1C2B68;
        color: #A7AFD1;
    }}
    .stTextArea textarea, .stTextArea label, .stFileUploader label {{
        color: #A7AFD1 !important;
    }}
    .stButton>button {{
        background-color: #A7AFD1;
        color: #1C2B68;
        border: 1px solid #A7AFD1;
    }}
    .stProgress > div > div > div {{
        background-color: #A7AFD1;
    }}
    .stMetric {{
        color: #A7AFD1 !important;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="report-title">AI Job Screening Dashboard</p>', unsafe_allow_html=True)

# Input Section
with st.expander("📥 Input Data", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        jd_text = st.text_area("Job Description", height=250,
                             placeholder="Paste job description here...",
                             help="Paste the text of the job description")
    
    with col2:
        # PDF Upload for CV
        cv_file = st.file_uploader("Upload CV (PDF)", type=["pdf"])
        cv_text = st.text_area("OR Paste CV Text", height=150,
                             placeholder="Alternatively, paste resume text here...",
                             help="Text alternative to PDF upload")

# Process PDF if uploaded
def process_pdf(uploaded_file):
    text = ""
    try:
        with pdfplumber.open(BytesIO(uploaded_file.read())) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None
    return text

# Analysis Section
if st.button("🚀 Run Analysis", type="primary"):
    if not jd_text or (not cv_text and not cv_file):
        st.error("⚠️ Please provide both Job Description and CV!")
    else:
        with st.spinner("🔍 Analyzing documents..."):
            conn = sqlite3.connect('jobs.db')
            cursor = conn.cursor()
            
            try:
                # Process CV input
                final_cv_text = ""
                if cv_file:
                    final_cv_text = process_pdf(cv_file)
                    if not final_cv_text:
                        raise ValueError("Failed to extract text from PDF")
                else:
                    final_cv_text = cv_text

                # Data processing
                jd_keywords = extract_keywords(jd_text, "jd")
                cv_keywords = extract_keywords(final_cv_text, "cv")
                ats_score, matched = calculate_ats_score(jd_keywords, cv_keywords)
                bias_report = detect_bias(jd_text)

                # Database operations
                cursor.execute('INSERT INTO jds (jd_text, keywords) VALUES (?, ?)', 
                             (jd_text, ", ".join(jd_keywords)))
                jd_id = cursor.lastrowid
                cursor.execute('INSERT INTO cvs (cv_text, keywords) VALUES (?, ?)', 
                             (final_cv_text, ", ".join(cv_keywords)))
                cv_id = cursor.lastrowid
                cursor.execute('INSERT INTO matches (jd_id, cv_id, ats_score) VALUES (?, ?, ?)', 
                             (jd_id, cv_id, ats_score))
                conn.commit()

                # Display Results
                st.success("✅ Analysis completed successfully!")
                
                # Results Section
                with st.container():
                    st.markdown("### 📊 Match Analysis")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(label="ATS Compatibility Score", 
                                 value=f"{ats_score}%",
                                 help="Percentage of JD keywords found in CV")
                        st.progress(ats_score/100)
                    
                    with col2:
                        st.metric(label="Keyword Matches", 
                                 value=f"{len(matched)}",
                                 help="Number of technical skills matched")
                        st.write(f"**Matched Keywords:**  \n{', '.join(matched) if matched else 'No matches found'}")

                # Bias Analysis
                with st.container():
                    st.markdown("### 🛡️ Bias Detection")
                    
                    if "error" in bias_report:
                        st.error(f"❌ Error: {bias_report['error']}")
                    else:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"""
                            <div style="background-color:#A7AFD1; padding:15px; border-radius:5px; color:#1C2B68;">
                                <h4>Bias Score: {bias_report.get('bias_score', 0)}/100</h4>
                                <small>{'High bias detected' if bias_report.get('bias_score',0) > 50 else 'Low bias detected'}</small>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            with st.expander("🔍 Detailed Findings"):
                                st.write("**Problematic Phrases:**")
                                for phrase in bias_report.get('biased_phrases', []):
                                    st.markdown(f"- 🚩 {phrase}")
                                
                                st.write("**Suggested Alternatives:**")
                                for alt in bias_report.get('alternatives', []):
                                    st.markdown(f"- ✅ {alt}")

                st.info("💾 Analysis results saved to database")

            except Exception as e:
                conn.rollback()
                st.error(f"❌ Analysis failed: {str(e)}")
            finally:
                conn.close()

# Sidebar
with st.sidebar:
    st.markdown("## 📖 How to Use")
    st.write("""
    1. **Job Description** - Paste text in left panel
    2. **Candidate CV** - Upload PDF or paste text
    3. Click 'Run Analysis'
    4. Review results below
    
    **Features:**
    - PDF resume parsing
    - ATS scoring system
    - Bias detection analysis
    - Historical data tracking
    """)
    
    st.markdown("## 🛠️ System Status")
    try:
        conn = sqlite3.connect('jobs.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM jds")
        jd_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM cvs")
        cv_count = cursor.fetchone()[0]
        st.write(f"📁 Stored Analyses: {jd_count} JDs | {cv_count} CVs")
    except:
        st.warning("Database connection unavailable")
    finally:
        conn.close()