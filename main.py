from fastapi import FastAPI, UploadFile, File, HTTPException
import tempfile
import os
from rag_utils import build_vector_store
from agent import AuditAgent
from dotenv import load_dotenv


load_dotenv()


app = FastAPI(
    title="AI Compliance Auditor API",
    description="API for processing policies and auditing invoices."
)


app_state = {}

@app.post("/api/upload-policy")
async def upload_policy(file: UploadFile = File(...)):
    """Upload a policy PDF and build the vector database."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        temp_policy_path = tmp_file.name
        
    try:
        
        db = build_vector_store(temp_policy_path)
        
        
        app_state['vector_store'] = db
        
        
        
        return {"status": "success", "message": "Knowledge Base Ready! ✅"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building knowledge base: {str(e)}")

@app.post("/api/run-audit")
async def run_audit(invoice_image: UploadFile = File(...)):
    """Upload an invoice image and run the compliance check against the policy."""
    
    
    if 'vector_store' not in app_state:
        raise HTTPException(status_code=400, detail="Please process the Policy PDF first!")
        
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img:
        content = await invoice_image.read()
        tmp_img.write(content)
        temp_img_path = tmp_img.name
        
    try:
        
        agent = AuditAgent()
        result = agent.analyze_invoice(temp_img_path, app_state['vector_store'])
        
        return {
            "status": "success",
            "findings": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing invoice: {str(e)}")