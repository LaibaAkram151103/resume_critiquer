import streamlit as st
import PyPDF2
import os
import requests
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Resume Critiquer", page_icon="📜", layout="centered")

st.title("AI Resume Critiquer")
st.markdown("Upload your resume to get AI powered feeedback tailored to your needs!")

GEMINI_API_KEY=st.secrets["GEMINI_API_KEY"]

uploaded_file=st.file_uploader("Upload your resume (PDF OF TXT)", type=["pdf", "txt"])
job_role=st.text_input("Enter the job role you're targeting (optional)")

analyze=st.button("Analyze Resume")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        uploaded_file.seek(0)
        return extract_text_from_pdf(uploaded_file)
    return uploaded_file.read().decode("utf-8")

if analyze and uploaded_file:
    try:
        file_content=extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("File does not have any content...")
            st.stop()

        prompt = f"""Please analyze this resume and provide constructive feedback. 
        Focus on the following aspects:
        1. Content clarity and impact
        2. Skills presentation
        3. Experience descriptions
        4. Specific improvements for {job_role if job_role else 'general job applications'}
        
        Resume content:
        {file_content}
        
        Please provide your analysis in a clear, structured format with specific recommendations."""

        response = requests.post(
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",

            headers={"Content-Type": "application/json"},
            json={
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            }
        )

        response_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]

        st.markdown("### Analysis Results")
        st.markdown(response_text)

    except Exception as e:
        st.error(f"An error occured: {str(e)}")