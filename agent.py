import os
import json
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

import base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


class AuditAgent():
    def __init__(self):
        self.vision_model = ChatGroq(model_name="meta-llama/llama-4-scout-17b-16e-instruct",
                                api_key=os.getenv("GROQ_API_KEY"),
                                temperature=0)
        self.audit_model = ChatGroq(model_name="llama-3.3-70b-versatile",
                                api_key=os.getenv("GROQ_API_KEY"),
                                temperature=0)
    
    def analyze_invoice(self,image_path,vectorstore):
        encoded_image = encode_image(image_path)
        
        messages = [
            HumanMessage(
                content=[
                    {
                        "type":"text",
                        "text":"Extract the Vendor Name, Date, Total Amount, and list of items from this invoice image. Return JSON only."
                    },
                    {
                        "type":"image_url",
                        "image_url":{
                            "url":f"data:image/jpeg;base64,{encoded_image}"
                        }
                    }
                ]
            )
        ]

        print("👀 Scanning Invoice...")
        ocr_response = self.vision_model.invoke(messages)
        invoice_data = ocr_response.content

        print("🧠 Checking Policy Rules...")
        relevant_rules = vectorstore.similarity_search(invoice_data,k=3)
        rules_text = "\n".join([doc.page_content for doc in relevant_rules])
        
        audit_prompt = f"""
        Role: You are a strict Finance Auditor.
        
        Context:
        User is submitting this invoice:
        {invoice_data}
        
        Company Policy Rules:
        {rules_text}
        
        Task:
        Check if the invoice violates any policy.
        Return a decision (Approved/Rejected) and a short reason.
        """

        final_response = self.audit_model.invoke(audit_prompt)
        return final_response.content
        
