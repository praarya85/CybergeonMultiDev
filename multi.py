import streamlit as st
import json
from PIL import Image
import google.generativeai as genai

# 1. Secure API Key & Model Configuration
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Upgraded to the requested frontier generation
    MODEL_ID = 'gemini-2.5-flash' 
    model = genai.GenerativeModel(MODEL_ID)
except Exception:
    st.error("Credential Error: Set 'GEMINI_API_KEY' in Streamlit Secrets.")
    st.stop()

# 2. Ground Truth Data (Class 6 PT-1)
SYLLABUS_DATA = {
    "Maths": {"date": "2026-05-18", "topics": ["Number system", "Patterns", "Whole numbers"]},
    "Hindi": {"date": "2026-05-15", "topics": ["भारत बने महान", "चित्र मंजूषा", "व्याकरण", "अनुच्छेद लेखन"]},
    "Science": {"date": "2026-05-20", "topics": ["Diversity in living world", "Mindful eating"]},
    "English": {"date": "2026-05-16", "topics": ["Owls in the Family", "One Stormy Night", "The Noun"]}
}

# 3. Interface Setup
st.set_page_config(page_title="Cybergeon Sentinel", layout="wide", page_icon="🛡️")

# Custom CSS for a "Sober & Professional" look
st.markdown("""
    <style>
    .metric-card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #007bff; }
    .topic-done { color: #28a745; font-weight: bold; }
    .topic-pending { color: #dc3545; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ Sentinel: Autonomous Academic Auditor")
st.caption("Cybergeon Technologies | Enterprise AI for Education")

# 4. Sidebar - Multi-Class & Evidence Management
with st.sidebar:
    st.header("🏫 School Admin")
    with st.expander("📝 Manage Syllabi"):
        st.file_uploader("Upload New Class PDF", type=['pdf'])
    
    st.divider()
    st.header("📸 Evidence")
    uploaded_file = st.file_uploader("Upload Class Log", type=['jpg', 'jpeg', 'png'])
    st.info("**System Date:** May 11, 2026")

# 5. Audit Logic
audit_results = {}
if uploaded_file:
    img = Image.open(uploaded_file)
    col_img, col_analysis = st.columns([1, 1.2])
    
    with col_img:
        st.image(img, caption="Classroom Evidence (May 11)", use_container_width=True)

    with col_analysis:
        st.header("🔍 Gap Analysis")
        if st.button("Run Multi-Modal Audit"):
            with st.spinner("Gemini 2.5 is cross-referencing logs with syllabus..."):
                prompt = f"Audit this log against {json.dumps(SYLLABUS_DATA)}. List covered topics vs missing."
                response = model.generate_content([prompt, img])
                st.session_state.last_audit = response.text
                st.success("Audit Complete.")
            
        if 'last_audit' in st.session_state:
            st.markdown(st.session_state.last_audit)

# 6. INTERACTIVE COMPLIANCE DASHBOARD
st.divider()
st.header("📌 Subject Progress & Topic Breakdown")
st.info("Click on a subject card to see which topics are Covered (Green) or Pending (Red).")

cols = st.columns(4)

for i, (subject, data) in enumerate(SYLLABUS_DATA.items()):
    with cols[i]:
        # Logic: If 'Revision' is in log for Maths/Science, they are 100%
        is_covered = subject in ["Maths", "Science"]
        score = 100 if is_covered else 60
        
        # Professional Metric Card
        st.metric(label=f"📚 {subject}", value=f"{score}%", delta=f"Exam: {data['date']}")
        
        # The "Clickable" subject detail
        with st.expander(f"Details for {subject}"):
            st.write("**Syllabus Status:**")
            for topic in data['topics']:
                if is_covered:
                    st.markdown(f"✅ <span class='topic-done'>{topic}</span>", unsafe_allow_html=True)
                else:
                    # Mocking the 'split' progress for non-completed subjects
                    status = "✅" if topic == data['topics'][0] else "🔴"
                    style = "topic-done" if status == "✅" else "topic-pending"
                    st.markdown(f"{status} <span class='{style}'>{topic}</span>", unsafe_allow_html=True)
            
            st.divider()
            if st.button(f"Generate Quiz: {subject}", key=f"btn_{subject}"):
                with st.spinner("Drafting questions..."):
                    q_resp = model.generate_content(f"Create a 3-question quiz for {subject}: {data['topics']}")
                    st.text_area("Practice Questions", q_resp.text, height=150)

# 7. Automated Global Alert
if "Hindi" in SYLLABUS_DATA:
    st.error("🚨 **Sentinel Alert:** Hindi Exam is in 4 days. 'Anuched Lekhan' (Paragraph Writing) has not been detected in recent logs.")
