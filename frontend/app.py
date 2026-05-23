import os

import requests
import streamlit as st


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1/analyze")

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

st.title("AI Resume Analyzer")
st.caption("Upload a resume, paste a job description, and get an ATS-style compatibility review.")

with st.sidebar:
    st.subheader("Configuration")
    st.write(f"Backend endpoint: `{BACKEND_URL}`")
    st.info("Supported formats: PDF and DOCX")

uploaded_file = st.file_uploader("Upload resume", type=["pdf", "docx"])
job_description = st.text_area(
    "Paste the job description",
    height=260,
    placeholder="Paste the full job description here...",
)

analyze_clicked = st.button("Analyze Resume", type="primary", use_container_width=True)

if analyze_clicked:
    if not uploaded_file:
        st.error("Please upload a PDF or DOCX resume.")
    elif not job_description.strip():
        st.error("Please enter a job description.")
    else:
        with st.spinner("Analyzing resume..."):
            try:
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type or "application/octet-stream",
                    )
                }
                data = {"job_description": job_description}
                response = requests.post(BACKEND_URL, files=files, data=data, timeout=120)
                response.raise_for_status()
                result = response.json()
            except requests.RequestException as exc:
                st.error(f"Could not connect to the backend service: {exc}")
            else:
                score_col, semantic_col, keyword_col, skill_col = st.columns(4)
                score_col.metric("Match Score", f"{result['match_score']}%")
                semantic_col.metric("Semantic Similarity", f"{result['semantic_similarity']}%")
                keyword_col.metric("Keyword Match", f"{result['keyword_match_score']}%")
                skill_col.metric("Skill Match", f"{result['skill_match_score']}%")

                st.subheader("Matched Skills")
                if result["matched_skills"]:
                    st.success(", ".join(result["matched_skills"]))
                else:
                    st.warning("No overlapping skills were detected.")

                st.subheader("Missing Skills")
                if result["missing_skills"]:
                    st.error(", ".join(result["missing_skills"]))
                else:
                    st.success("No missing skills detected from the current catalog.")

                st.subheader("Improvement Suggestions")
                for suggestion in result["suggestions"]:
                    st.write(f"- {suggestion}")

                st.subheader("Extracted Resume Skills")
                if result["extracted_skills"]:
                    st.write(", ".join(result["extracted_skills"]))
                else:
                    st.write("No skills were extracted from the resume.")

                storage = result.get("storage", {})
                st.subheader("Cloud Storage")
                if storage.get("storage_enabled") and storage.get("file_url"):
                    st.success(f"Resume stored in S3: {storage['file_url']}")
                else:
                    st.info("S3 upload is not enabled. Set AWS environment variables to store files in the cloud.")
