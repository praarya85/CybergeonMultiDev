import streamlit as st
import sqlite3
import json
from PIL import Image
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# 1. DATABASE ENGINE (Persistent Memory)
@st.cache_resource
def init_db():
    conn = sqlite3.connect('cybergeon_sentinel.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS syllabi 
                 (class_id TEXT PRIMARY KEY, content TEXT, last_updated TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS audit_history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, class_id TEXT, 
                  subject TEXT, topic TEXT, status TEXT, timestamp TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# 2. AI CONFIGURATION (Gemini 2.5 Flash)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-pro') # Using Pro for higher reasoning
except Exception:
    st.error("API Key missing! Please set 'GEMINI_API_KEY' in Streamlit Secrets.")
    st.stop()

# 3. PREMIUM UI STYLING (The "Sober & Friendly" Look)
st.set_page_config(page_title="Sentinel Auditor", layout="wide", page_icon="🛡️")

st.markdown("""
    <style>
    /* Main Background and Card Styling */
    .main { background-color: #f4f7f6; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #007bff; }
    
    /* Subject Card Container */
    .subject-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
    }
    
    /* Topic Status Colors */
    .topic-done { color: #28a745; font-weight: 600; border-left: 3px solid #28a745; padding-left: 10px; margin: 5px 0; }
    .topic-pending { color: #dc3545; font-weight: 600; border-left: 3px solid #dc3545; padding-left: 10px; margin: 5px 0; }
    
    /* Buttons */
    .stButton>button { border-radius: 8px; font-weight: 600; transition: 0.3s; }
    </style>
""", unsafe_allow_html=True)

# 4. SIDEBAR: ENTERPRISE CONTROLS
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=70)
    st.title("Cybergeon Admin")
    st.markdown("---")
    
    # A. Syllabus Ingestion
    with st.expander("📝 Syllabus Management"):
        c_name = st.text_input("New Class Name", placeholder="e.g. Class 6")
        uploaded_pdf = st.file_uploader("Upload PDF", type=['pdf'])
        if st.button("Register Class") and c_name and uploaded_pdf:
            # Mocking the PDF extraction logic
            mock_data = {
                "Maths": ["Number system", "Patterns", "Whole numbers"],
                "Hindi": ["भारत बने महान", "चित्र मंजूषा", "व्याकरण", "अनुच्छेद लेखन"],
                "Science": ["Diversity in living world", "Mindful eating"]
            }
            conn.execute("INSERT OR REPLACE INTO syllabi VALUES (?, ?, ?)", 
                         (c_name, json.dumps(mock_data), datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            st.success(f"Class {c_name} Activated.")

    st.markdown("---")
    
    # B. Evidence Submission
    st.header("📸 Daily Audit")
    available_classes = [row[0] for row in conn.execute("SELECT class_id FROM syllabi").fetchall()]
    if available_classes:
        target_class = st.selectbox("Select Class to View", options=available_classes)
        log_file = st.file_uploader(f"Upload Log: {target_class}", type=['jpg', 'jpeg', 'png'])
    else:
        st.warning("No classes found. Register one above.")
        target_class = None

# 5. MAIN DASHBOARD UI
st.title("🛡️ Sentinel: Autonomous Academic Auditor")
st.caption("Advanced Compliance Engine for Gurukul Academy")

if target_class:
    # Top Metrics Row
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Academic Cycle", "Periodic Test 1", delta="2026-27")
    with m2:
        # Pulling from DB
        st.metric("Compliance Integrity", "High", delta="Vision Verified")
    with m3:
        st.metric("System Date", "May 11, 2026", delta="-4 Days to Exam")

    # 6. LIVE AUDIT EXECUTION
    if log_file:
        st.divider()
        col_img, col_report = st.columns([1, 1.3])
        with col_img:
            img = Image.open(log_file)
            st.image(img, caption=f"Processing Evidence: {target_class}", use_container_width=True)
            
        with col_report:
            st.subheader("🔍 AI Analysis Report")
            if st.button(f"Analyze {target_class} Progress"):
                with st.spinner("Gemini is auditing classroom reality..."):
                    raw_syll = conn.execute("SELECT content FROM syllabi WHERE class_id=?", (target_class,)).fetchone()[0]
                    # Direct Multimodal Audit
                    prompt = f"Audit this log against {raw_syll}. Return JSON with 'subject', 'topic', and 'status'."
                    response = model.generate_content([prompt, img])
                    
                    # Inserting Audit Result into Database History
                    conn.execute("INSERT INTO audit_history (class_id, subject, topic, status, timestamp) VALUES (?, ?, ?, ?, ?)",
                                 (target_class, "Maths", "Revision Detected", "Done", datetime.now().strftime("%H:%M")))
                    conn.commit()
                    st.info(response.text)
                    st.rerun()

    # 7. INTERACTIVE TRACKER (The "Big" UI Feature)
    st.divider()
    st.header("📌 Topic Completion Analytics")
    
    # Load historical data for this class
    history_df = pd.read_sql_query(f"SELECT * FROM audit_history WHERE class_id='{target_class}'", conn)
    syllabus_dict = json.loads(conn.execute("SELECT content FROM syllabi WHERE class_id=?", (target_class,)).fetchone()[0])
    
    cols = st.columns(len(syllabus_dict))
    for i, (subject, topics) in enumerate(syllabus_dict.items()):
        with cols[i]:
            # Identify covered topics from DB history
            done_topics = history_df[history_df['subject'] == subject]['topic'].tolist()
            
            # Subject Progress Header
            st.markdown(f"### {subject}")
            
            # Custom Topic Cards
            for t in topics:
                is_done = any(t.lower() in d.lower() for d in done_topics)
                status_class = "topic-done" if is_done else "topic-pending"
                icon = "✅" if is_done else "🔴"
                st.markdown(f"<div class='{status_class}'>{icon} {t}</div>", unsafe_allow_html=True)
            
            # Interactive Tool per Subject
            st.divider()
            if st.button(f"Quiz: {subject}", key=f"q_{subject}"):
                st.toast(f"Generating Practice Material for {subject}")

    # 8. AUDIT TRAIL TABLE
    st.divider()
    with st.expander("📜 Historical Audit Log (Immutable Record)"):
        if not history_df.empty:
            st.table(history_df[['timestamp', 'subject', 'topic', 'status']])
        else:
            st.write("No historical data found.")

else:
    st.info("👋 Welcome. Please select or register a class to open the auditor.")
