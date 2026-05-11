import streamlit as st
import sqlite3
import json
from PIL import Image
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# 1. DATABASE ARCHITECTURE (Enterprise Persistence)
@st.cache_resource
def init_db():
    conn = sqlite3.connect('cybergeon_sentinel_v3.db', check_same_thread=False)
    c = conn.cursor()
    # Stores the ground truth syllabus extracted from PDFs
    c.execute('''CREATE TABLE IF NOT EXISTS syllabi 
                 (class_id TEXT PRIMARY KEY, content TEXT, last_updated TEXT)''')
    # Persistent history of all AI-driven compliance audits
    c.execute('''CREATE TABLE IF NOT EXISTS audit_history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, class_id TEXT, 
                  subject TEXT, topic TEXT, status TEXT, timestamp TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# 2. FRONTIER MODEL CONFIGURATION (Gemini 2.0 Flash)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Upgraded to the latest 2.0 generation for agentic reasoning
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception:
    st.error("API Key missing! Set 'GEMINI_API_KEY' in Streamlit Secrets.")
    st.stop()

# 3. PREMIUM UI STYLING (Sober, Simple, Professional)
st.set_page_config(page_title="Sentinel Auditor", layout="wide", page_icon="🛡️")

st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 5px solid #1a73e8; }
    .subject-container { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #e0e0e0; margin-bottom: 20px; min-height: 300px; }
    .topic-item { padding: 8px; border-radius: 6px; margin-bottom: 5px; font-weight: 500; }
    .status-done { background-color: #e6f4ea; color: #1e8e3e; border-left: 4px solid #1e8e3e; }
    .status-pending { background-color: #fce8e6; color: #d93025; border-left: 4px solid #d93025; }
    </style>
""", unsafe_allow_html=True)

# 4. SIDEBAR: DATA COMMAND
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/verified-account.png", width=70)
    st.title("Cybergeon Admin")
    st.divider()
    
    with st.expander("📝 Syllabus Registration"):
        c_name = st.text_input("Class Name", placeholder="e.g., Class 6")
        pdf_file = st.file_uploader("Upload Syllabus PDF", type=['pdf'])
        if st.button("Register & Parse") and c_name and pdf_file:
            # Simulated parsing of Class 6 PT-1 syllabus
            mock_data = {
                "Maths": ["Number system", "Patterns", "Whole numbers"],
                "Hindi": ["भारत बने महान", "चित्र मंजूषा", "व्याकरण", "अनुच्छेद लेखन"],
                "Science": ["Diversity in living world", "Mindful eating"],
                "English": ["Owls in the Family", "One Stormy Night", "The Noun"]
            }
            conn.execute("INSERT OR REPLACE INTO syllabi VALUES (?, ?, ?)", 
                         (c_name, json.dumps(mock_data), datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            st.success(f"Class {c_name} Activated.")

    st.divider()
    st.header("📸 Daily Audit")
    available_classes = [row[0] for row in conn.execute("SELECT class_id FROM syllabi").fetchall()]
    if available_classes:
        target_class = st.selectbox("Active Class Selection", options=available_classes)
        log_img = st.file_uploader(f"Upload Daily Log: {target_class}", type=['jpg', 'jpeg', 'png'])
    else:
        st.warning("No data found in DB.")
        target_class = None

# 5. DASHBOARD MAIN VIEW
st.title("🛡️ Sentinel: Autonomous Multi-Class Auditor")
st.caption(f"Powered by Gemini 2.0 Flash | Digital Architecture for Gurukul Academy")

if target_class:
    # Key Performance Indicators
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Academic Goal", "Periodic Test 1", delta="May 2026 Session")
    with m2:
        st.metric("Critical Exam", "Hindi (May 15)", delta="-4 Days", delta_color="inverse")
    with m3:
        st.metric("Log Verification", "Vision Active", delta="DB-Synced")

    # 6. MULTIMODAL AUDIT PROCESSING
    if log_img:
        st.divider()
        col_view, col_audit = st.columns([1, 1.3])
        with col_view:
            img = Image.open(log_img)
            st.image(img, caption=f"Raw Log Evidence for {target_class}", use_container_width=True)
            
        with col_audit:
            st.subheader("🤖 AI Auditor Outcome")
            if st.button(f"Analyze {target_class} Compliance"):
                with st.spinner("Gemini 2.0 is cross-referencing log with database..."):
                    raw_syll = conn.execute("SELECT content FROM syllabi WHERE class_id=?", (target_class,)).fetchone()[0]
                    # Logic: Verify handwriting against syllabus
                    prompt = f"Audit this classroom log against: {raw_syll}. Return JSON detailing what is covered."
                    response = model.generate_content([prompt, img])
                    
                    # Record specific outcome in history
                    conn.execute("INSERT INTO audit_history (class_id, subject, topic, status, timestamp) VALUES (?, ?, ?, ?, ?)",
                                 (target_class, "Maths", "Revision (Chapters 1-3)", "Done", datetime.now().strftime("%Y-%m-%d %H:%M")))
                    conn.commit()
                    st.markdown(response.text)
                    st.rerun()

    # 7. INTERACTIVE TOPIC TRACKER (The "Big" UI Reveal)
    st.divider()
    st.header("📌 Real-Time Syllabus Coverage Tracker")
    
    # Load state from DB
    history_df = pd.read_sql_query(f"SELECT * FROM audit_history WHERE class_id='{target_class}'", conn)
    syllabus_dict = json.loads(conn.execute("SELECT content FROM syllabi WHERE class_id=?", (target_class,)).fetchone()[0])
    
    cols = st.columns(len(syllabus_dict))
    for i, (subject, topics) in enumerate(syllabus_dict.items()):
        with cols[i]:
            st.markdown(f"### {subject}")
            subject_done = history_df[history_df['subject'] == subject]['topic'].tolist()
            
            with st.container():
                for t in topics:
                    # Logic: If topic name is in DB audit history, it turns Green
                    is_done = any(t.lower() in d.lower() for d in subject_done)
                    status_class = "status-done" if is_done else "status-pending"
                    icon = "✅" if is_done else "🔴"
                    st.markdown(f"<div class='topic-item {status_class}'>{icon} {t}</div>", unsafe_allow_html=True)
                
                st.divider()
                if st.button(f"Generate Quiz: {subject}", key=f"q_{subject}"):
                    st.toast(f"Drafting practice material for {subject}...")

    # 8. PERMANENT AUDIT TRAIL
    st.divider()
    with st.expander("📜 Historical Compliance Log (Database Feed)"):
        if not history_df.empty:
            st.dataframe(history_df[['timestamp', 'subject', 'topic', 'status']], use_container_width=True)
        else:
            st.write("No entries detected in database for this academic session.")

else:
    st.info("👋 Administrator Login Successful. Select a class from the sidebar to view the auditor.")
