import streamlit as st
import requests

# This is the internal URL where the Streamlit container talks to the API container
API_BASE_URL = "http://api:8000/api"

st.set_page_config(page_title="AI Compliance Auditor", layout="wide")
st.title("🤖 AI Audit Agent")

# --- SIDEBAR: POLICY UPLOAD ---
st.sidebar.header("1. Upload Policy")
uploaded_policy = st.sidebar.file_uploader("Upload Policy PDF", type="pdf")

if st.sidebar.button("Process Policy"):
    if uploaded_policy is not None:
        with st.spinner("Reading rules and building knowledge base..."):
            
            # Package the PDF and send it to FastAPI Endpoint 1
            files = {"file": (uploaded_policy.name, uploaded_policy.getvalue(), "application/pdf")}
            try:
                response = requests.post(f"{API_BASE_URL}/upload-policy", files=files)
                if response.status_code == 200:
                    st.sidebar.success("Knowledge Base Ready! ✅")
                else:
                    st.sidebar.error(f"Error: {response.text}")
            except Exception as e:
                st.sidebar.error(f"Backend connection failed: {e}")
    else:
        st.sidebar.warning("Please upload a PDF first.")

# --- MAIN CONTENT: INVOICE AUDIT ---
st.header("2. Provide Invoice")

# Your tabs for Upload vs Camera are back!
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
    
    if st.button("Run Compliance Check"):
        with st.spinner("Agent is working..."):
            
            # Package the image (from upload OR camera) and send it to FastAPI Endpoint 2
            files = {"invoice_image": (input_image.name, input_image.getvalue(), "image/jpeg")}
            try:
                response = requests.post(f"{API_BASE_URL}/run-audit", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("Audit Complete!")
                    st.write("### Findings:")
                    st.write(result["findings"])
                elif response.status_code == 400:
                    st.error("Please process the Policy PDF in the sidebar first!")
                else:
                    st.error(f"Backend Error: {response.text}")
            except Exception as e:
                st.error(f"Backend connection failed: {e}")