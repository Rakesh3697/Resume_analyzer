import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to generate cold email using Gemini AI
def get_cold_email(job_description, linkedin, tone):
    prompt = f"""
    You are a professional job application assistant. Write a well-structured cold email for a job opportunity based on the given job description.

    **Email Requirements:**
    - **Subject Line**: Attention-grabbing but professional
    - **Introduction**: Briefly introduce the candidate (assume they are skilled)
    - **Why This Job?**: Explain why the candidate is a great fit
    - **Relevant Skills**: Highlight 2-3 key skills from the job description
    - **Call to Action**: Ask for an opportunity to discuss further
    - **Signature**: Professional closing

    **Additional Details:**
    - LinkedIn Profile (if provided): {linkedin}
    - Email Tone: {tone} (Choose between Formal or Casual)

    Job Description:
    {job_description}

    Generate a complete email with proper formatting.
    """

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

# Streamlit UI Configuration
st.set_page_config(page_title="AI-Powered Cold Email Generator")

# UI Header
st.markdown("<h1 style='text-align: center;'>📧 AI Cold Email Generator</h1>", unsafe_allow_html=True)

# User Inputs
job_description = st.text_area("Enter Job Description:", height=200)
linkedin = st.text_input("Enter Your LinkedIn Profile (Optional):")
tone = st.radio("Select Email Tone:", ["Formal", "Casual"], index=0)

# Generate Button
if st.button("Generate Cold Email"):
    if job_description.strip():
        cold_email = get_cold_email(job_description, linkedin, tone)
        st.subheader("Generated Cold Email:")
        st.write(cold_email)
    else:
        st.warning("Please enter a job description!")
