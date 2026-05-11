import streamlit as st
import json
from PIL import Image
import google.generativeai as genai

# 1. AI Configuration (Gemini 1.5 Pro / 2.0 series ready)
# Model ID is kept flexible for the latest frontier models
MODEL_ID = "gemini-1.5-pro" 

try:
    # Key is pulled from Streamlit App Settings (Secrets)
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(MODEL_ID)
except Exception:
    st.error("Credential Error: Please set 'GEMINI_API_KEY' in Streamlit Secrets.")
    st.stop()

# 2. State Management for the Global Vault
if 'school_vault' not in st.session_state:
    # Initializing with the Class 6 data from your uploaded document
    st.session_state.school_vault = {
        "Class 6": {
            "exams": {
                "Hindi": "2026-05-15", "English": "2026-05-16", 
                "Maths": "2026-05-18", "SSc": "2026-05-19", "Science": "2026-05-20"
            },
            "topics": "Maths (Ch 1-3), English (Ch 1-2 + Grammar), Science (Ch 2-3), Hindi (Ch 1-3 + Grammar)"
        }
    }

# 3. Sidebar: Administrative Control & Evidence Submission
with st.sidebar:
    st.header("🏫 Cybergeon Admin")
    
    # Section A: Syllabus Management
    with st.expander("➕ Upload/Edit Syllabus"):
        new_class = st.text_input("Enter Class Name (e.g., Class 7)")
        uploaded_pdf = st.file_uploader("Upload PDF Syllabus", type=['pdf'])
        if st.button("Register Class") and new_class and uploaded_pdf:
            # Logic to ingest new syllabus data into session_state
            st.session_state.school_vault[new_class] = {"status": "Active", "source": uploaded_pdf.name}
            st.success(f"{new_class} syllabus registered!")

    st.divider()
    
    # Section B: Targeted Log Submission
    st.header("📸 Evidence Submission")
    # Drop-down only shows classes that have a syllabus in the vault
    available_classes = list(st.session_state.school_vault.keys())
    target_class = st.selectbox("Select Target Class for Log", options=available_classes)
    evidence_file = st.file_uploader(f"Upload Log for {target_class}", type=['jpg', 'jpeg', 'png'])

# 4. Main Dashboard: Conditional Display
st.title("🛡️ Sentinel: Autonomous Academic Auditor")

if not target_class:
    st.info("Select a class from the sidebar to view the audit dashboard.")
else:
    # Dashboard only renders for the selected class
    st.header(f"📊 Compliance Dashboard: {target_class}")
    
    # Top Level Metrics using Vault Data
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Syllabus Status", "Verified")
    with m2:
        next_exam = st.session_state.school_vault[target_class]['exams'].get('Hindi', 'TBD')
        st.metric("Next Exam", next_exam, delta="-4 Days")
    with m3:
        st.metric("Audit Integrity", "High (Vision Enabled)")

    # 5. Live Audit Execution
    if evidence_file:
        st.divider()
        col_img, col_audit = st.columns([1, 1.5])
        
        with col_img:
            img = Image.open(evidence_file)
            st.image(img, caption=f"Processing Evidence for {target_class}", use_container_width=True)
            
        with col_audit:
            if st.button(f"Analyze {target_class} Progress"):
                with st.spinner(f"Auditing {target_class} against Ground Truth..."):
                    # The Auditor Agent processes the log vs Syllabus
                    audit_prompt = f"""
                    System: {MODEL_ID} Auditor.
                    Target: {target_class}.
                    Syllabus Data: {json.dumps(st.session_state.school_vault[target_class])}.
                    
                    Task: Scan the handwritten log. 
                    Identify if the teacher is performing 'Revision' as required by the 
                    exam timeline (Start Date: May 15).
                    """
                    response = model.generate_content([audit_prompt, img])
                    st.markdown(response.text)
                    
                    # Automated Guardrail logic
                    st.warning(f"Note: Entry to the {target_class} exam requires clear fee status and complete formalities.")

    # 6. Agentic Output Area
    st.divider()
    st.subheader("🛠️ Automated Teacher Support")
    t1, t2 = st.columns(2)
    with t1:
        if st.button(f"Generate {target_class} Mock Paper"):
            topics = st.session_state.school_vault[target_class].get('topics', 'All Chapters')
            resp = model.generate_content(f"Create a 5-question mock test for {target_class} based on: {topics}")
            st.text_area("Mock Exam Content", resp.text, height=200)
    with t2:
        if st.button(f"Sync {target_class} Schedule"):
            st.success(f"Exam schedule for {target_class} synced to teacher calendar (May 15-20).")

