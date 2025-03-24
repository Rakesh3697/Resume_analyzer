import streamlit as st
import base64
import os
import io
import re
import fitz  # PyMuPDF
import matplotlib.pyplot as plt
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to Get Gemini Response
def get_gemini_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, pdf_content[0], prompt])
    return response.text

# Extract Resume Image and Encode
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as pdf_doc:
            first_page = pdf_doc[0].get_pixmap()
            img_bytes = first_page.tobytes("png")  # Convert to PNG
            img = Image.open(io.BytesIO(img_bytes))  # Convert to PIL Image
            encoded_img = base64.b64encode(img_bytes).decode()  # Encode image to base64
            return img, encoded_img
    else:
        raise FileNotFoundError("No file uploaded")

# Extract Match Percentage from Gemini Response
def extract_match_percentage(response_text):
    match = re.search(r"Match Percentage:\s*(\d+)%", response_text)
    return int(match.group(1)) if match else 0

# Draw Match Percentage Pie Chart
def draw_pie_chart(match_percentage):
    fig, ax = plt.subplots()
    labels = ['Match', 'Remaining']
    sizes = [match_percentage, 100 - match_percentage]
    colors = ['#4CAF50', '#FF5733']
    explode = (0.1, 0)  # Emphasize match %
    
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
           shadow=True, startangle=90)
    ax.axis('equal')  # Ensures pie chart is circular
    return fig

# Streamlit Configuration
st.set_page_config(page_title="Technical ATS Resume Expert")

# Page Styling
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(to right, #2c3e50, #4ca1af);
        color: white;
    }
    h1 {
        text-align: center;
        font-size: 2.5em;
    }
    </style>
    """, unsafe_allow_html=True
)

st.markdown("<h1 style='text-align: center;'>Technical Resume Expert</h1>", unsafe_allow_html=True)

# Inputs
input_text = st.text_area("Job Description: ")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

if uploaded_file:
    st.success("✅ PDF Uploaded Successfully!")

# Buttons
submit1 = st.button("Analyze Resume")
submit2 = st.button("How Can I Improve My Skills?")
submit3 = st.button("Match Resume with Job Description")

# Prompts
input_prompt1 = """
You are an experienced Technical HR Manager specializing in hiring for technology, finance, and business roles. 
Your task is to analyze the provided resume against the job description.

1. **Alignment with Job Requirements**: Identify matching skills, qualifications, and experience.
2. **Strengths**: Highlight key strengths relevant to the role.
3. **Weaknesses**: Mention gaps in skills, experience, or certifications.
4. **Overall Fit**: Provide a final assessment with a recommendation on suitability for the role.

Ensure your analysis is professional, specific, and actionable.
"""

input_prompt2 = """
You are a Technical Career Advisor specializing in Data Science, Web Development, Big Data, and DevOps. Your task is to provide personalized career improvement suggestions.

1. **Skill Gap Analysis**: Identify missing skills.
2. **Recommended Learning Path**: Suggest courses, projects, and certifications.
3. **Emerging Technologies**: Recommend new trends relevant to the candidate's field.
4. **Soft Skills**: Suggest soft skills improvement if applicable.
5. **Action Plan**: Provide 3 key steps to improve the candidate's career prospects.

Ensure responses are actionable and tailored to the candidate’s resume and job description.
"""

input_prompt3 = """
You are an advanced ATS (Applicant Tracking System) scanner. Evaluate the resume against the job description.

**Output Format:**
- **Match Percentage:** XX%
- **Missing Keywords:** [List missing skills/tools]
- **Final Thoughts:** Summary of strengths, weaknesses, and a recommendation.

Ensure the evaluation is concise, relevant, and data-driven.
"""

# Actions
if submit1:
    if uploaded_file:
        pdf_image, pdf_base64 = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, [{"mime_type": "image/png", "data": pdf_base64}], input_prompt1)
        st.subheader("📌 Analysis")
        st.write(response)
    else:
        st.error("❌ Please upload your resume!")

elif submit2:
    if uploaded_file:
        pdf_image, pdf_base64 = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, [{"mime_type": "image/png", "data": pdf_base64}], input_prompt2)
        st.subheader("📌 Improvement Suggestions")
        st.write(response)
    else:
        st.error("❌ Please upload your resume!")

elif submit3:
    if uploaded_file:
        pdf_image, pdf_base64 = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, [{"mime_type": "image/png", "data": pdf_base64}], input_prompt3)
        match_percentage = extract_match_percentage(response)

        col1, col2 = st.columns(2)
        with col1:
            st.image(pdf_image, caption="Resume First Page", width=400)
        with col2:
            st.subheader("📊 Match Percentage")
            pie_chart = draw_pie_chart(match_percentage)
            st.pyplot(pie_chart)

        st.subheader("📌 Detailed Analysis")
        st.write(response)
    else:
        st.error("❌ Please upload your resume!")
