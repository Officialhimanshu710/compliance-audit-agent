import streamlit as st
import os
import tempfile
from rag_utils import build_vector_store
from agent import AuditAgent
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="AI Compliance Auditor", layout="wide")
st.title("🤖 AI Audit Agent")

st.sidebar.header("1. Upload Policy")
uploaded_policy = st.sidebar.file_uploader("Upload Policy PDF", type="pdf")

if uploaded_policy is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_policy.read())
        temp_policy_path = tmp_file.name
    
    st.sidebar.success("PDF Uploaded!")
    
    if st.sidebar.button("Process Policy"):
        with st.spinner("Reading rules..."):
            db = build_vector_store(temp_policy_path)
            st.session_state['vector_store'] = db
            
            st.sidebar.success("Knowledge Base Ready! ✅")

st.header("2. Provide Invoice")
tab1, tab2 = st.tabs(["📁 Upload Image", "📸 Take Photo"])

input_image = None
with tab1:
    uploaded_file = st.file_uploader("Upload Invoice Image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        input_image = uploaded_file

with tab2:
    camera_photo = st.camera_input("Take a picture of the invoice")
    if camera_photo:
        input_image = camera_photo

if input_image is not None:
    st.image(input_image, caption="Invoice to Audit", use_column_width=True)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img:
        tmp_img.write(input_image.read())
        temp_img_path = tmp_img.name

    if st.button("Run Compliance Check"):
        if 'vector_store' not in st.session_state:
            st.error("Please process the Policy PDF first!")
        else:
            with st.spinner("Agent is working..."):
                agent = AuditAgent()
                result = agent.analyze_invoice(temp_img_path, st.session_state['vector_store'])
                st.write(result)