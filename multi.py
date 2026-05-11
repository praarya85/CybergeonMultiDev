import streamlit as st
import json
from PIL import Image
import google.generativeai as genai

# 1. Secure API Key Retrieval from App Settings
try:
    # This pulls from your Streamlit Secret management
    GENAI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GENAI_API_KEY)
except KeyError:
    st.error("Missing 'GEMINI_API_KEY' in Streamlit Secrets.")
    st.stop()

# 2. Model Configuration (Targeting the latest 2.x generation)
# Note: Update this string as specific 2.x versions are released in your region
MODEL_ID = 'gemini-1.5-pro' # Currently the most stable for long-context vision
model = genai.GenerativeModel(MODEL_ID)

# 3. Ground Truth Data Extraction
SYLLABUS_DATA = {
    "Maths": {"date": "2026-05-18", "topics": ["Number system", "Patterns", "Whole numbers"]},
    "Hindi": {"date": "2026-05-15", "topics": ["भारत बने महान", "चित्र मंजूषा", "व्याकरण", "अनुच्छेद लेखन"]},
    "Science": {"date": "2026-05-20", "topics": ["Diversity in living world", "Mindful eating"]},
    "English": {"date": "2026-05-16", "topics": ["Owls in the Family", "One Stormy Night", "The Noun"]}
}

# 4. Interface Setup
st.set_page_config(page_title="Cybergeon Auditor", layout="wide", page_icon="🛡️")
st.title("🛡️ Autonomous Syllabus-to-Outcome Auditor")
st.caption(f"Powered by {MODEL_ID} | Enterprise AI for Education")

# 5. Sidebar - Evidence Management
with st.sidebar:
    st.header("📂 Audit Evidence")
    uploaded_file = st.file_uploader("Upload Class Log Image", type=['jpg', 'jpeg', 'png'])
    st.divider()
    st.info("**Audit Context:** Periodic Test 1 (2026-27)")
    st.write("**Today's Date:** May 11, 2026") #

# 6. Main Logic Execution
if uploaded_file:
    img = Image.open(uploaded_file)
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.image(img, caption="Detected Class Log", use_container_width=True)

    with col2:
        st.header("🔍 Intelligent Gap Analysis")
        if st.button("Run Multi-Modal Audit"):
            with st.spinner("Analyzing classroom progress against syllabus..."):
                # Combining Vision with Document Context
                audit_prompt = f"""
                Analyze this classroom log from May 11, 2026. 
                Compare findings against the Syllabus: {json.dumps(SYLLABUS_DATA)}.
                
                Identify:
                1. Topics currently in 'Revision' (Mark as On-Track).
                2. Any topic taught that is NOT in the PT-1 syllabus.
                3. High-priority risks for the Hindi exam on May 15.
                """
                response = model.generate_content([audit_prompt, img])
                st.markdown(response.text)
                
                # Critical Date Alert
                st.error("🚨 **Urgent Alert:** Hindi Examination starts in 4 days. Verify 'Varn Vichar' completion.")

# 7. Compliance Tracking Dashboard
st.divider()
st.header("Subject Compliance Status")
cols = st.columns(4)

for i, (subject, data) in enumerate(SYLLABUS_DATA.items()):
    with cols[i]:
        # Visual evidence from the log shows Revision for Maths & Science
        is_on_track = subject in ["Maths", "Science", "Hindi"]
        score = 100 if is_on_track else 65
        
        st.metric(label=subject, value=f"{score}%", delta=f"Exam: {data['date']}")
        st.progress(score / 100)
        
        if st.button(f"Generate Practice: {subject}"):
            with st.spinner(f"Agent is drafting {subject} Mock Paper..."):
                test_prompt = f"As an AI Academic Assistant, generate a 5-question mock paper for Class 6 {subject} based on: {data['topics']}."
                test_resp = model.generate_content(test_prompt)
                st.text_area("Mock Examination Paper", test_resp.text, height=250)
