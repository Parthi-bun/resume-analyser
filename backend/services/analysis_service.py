from dataclasses import dataclass
from typing import Dict, List, Set

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.text_processing import clean_text, extract_keywords, normalize_token, unique_preserve_order


SKILL_CATALOG = {
    "python",
    "java",
    "c++",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "terraform",
    "linux",
    "git",
    "github",
    "fastapi",
    "flask",
    "django",
    "streamlit",
    "rest api",
    "microservices",
    "machine learning",
    "deep learning",
    "nlp",
    "spacy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "transformers",
    "data analysis",
    "pandas",
    "numpy",
    "power bi",
    "tableau",
    "excel",
    "spark",
    "hadoop",
    "airflow",
    "ci/cd",
    "jenkins",
    "agile",
    "scrum",
    "javascript",
    "typescript",
    "react",
    "node.js",
    "html",
    "css",
}


@dataclass
class AnalysisResult:
    match_score: float
    semantic_similarity: float
    keyword_match_score: float
    skill_match_score: float
    extracted_skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    suggestions: List[str]


class ResumeAnalyzerService:
    def analyze(self, resume_text: str, job_description: str) -> AnalysisResult:
        cleaned_resume = clean_text(resume_text)
        cleaned_jd = clean_text(job_description)

        if not cleaned_resume:
            raise ValueError("Resume text is empty after cleaning.")
        if not cleaned_jd:
            raise ValueError("Job description cannot be empty.")

        resume_skills = self._extract_skills(cleaned_resume)
        jd_skills = self._extract_skills(cleaned_jd)
        matched_skills = sorted(resume_skills & jd_skills)
        missing_skills = sorted(jd_skills - resume_skills)

        semantic_similarity = self._semantic_similarity(cleaned_resume, cleaned_jd)
        keyword_match_score = self._keyword_match_score(cleaned_resume, cleaned_jd)
        skill_match_score = (len(matched_skills) / len(jd_skills) * 100) if jd_skills else 0.0

        weighted_score = (
            0.45 * semantic_similarity
            + 0.20 * keyword_match_score
            + 0.35 * skill_match_score
        )

        suggestions = self._build_suggestions(
            missing_skills=missing_skills,
            semantic_similarity=semantic_similarity,
            keyword_match_score=keyword_match_score,
            skill_match_score=skill_match_score,
        )

        return AnalysisResult(
            match_score=round(min(weighted_score, 100.0), 2),
            semantic_similarity=round(semantic_similarity, 2),
            keyword_match_score=round(keyword_match_score, 2),
            skill_match_score=round(skill_match_score, 2),
            extracted_skills=sorted(resume_skills),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            suggestions=suggestions,
        )

    def _extract_skills(self, text: str) -> Set[str]:
        normalized_text = f" {normalize_token(text)} "
        found_skills = {
            skill for skill in SKILL_CATALOG if f" {normalize_token(skill)} " in normalized_text
        }
        return found_skills

    @staticmethod
    def _semantic_similarity(resume_text: str, job_description: str) -> float:
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        matrix = vectorizer.fit_transform([resume_text, job_description])
        score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return max(score, 0.0) * 100

    def _keyword_match_score(self, resume_text: str, job_description: str) -> float:
        resume_keywords = {normalize_token(word) for word in extract_keywords(resume_text, limit=40)}
        jd_keywords = {normalize_token(word) for word in extract_keywords(job_description, limit=40)}
        if not jd_keywords:
            return 0.0
        overlap = resume_keywords & jd_keywords
        return len(overlap) / len(jd_keywords) * 100

    @staticmethod
    def _build_suggestions(
        missing_skills: List[str],
        semantic_similarity: float,
        keyword_match_score: float,
        skill_match_score: float,
    ) -> List[str]:
        suggestions: List[str] = []

        if missing_skills:
            top_missing = ", ".join(missing_skills[:8])
            suggestions.append(f"Add evidence of these missing skills if you have them: {top_missing}.")

        if skill_match_score < 50:
            suggestions.append(
                "Align your resume with the job description by mirroring the technical stack and tools more explicitly."
            )

        if keyword_match_score < 45:
            suggestions.append(
                "Reuse important job-description keywords in your summary, skills, and project bullets where they genuinely apply."
            )

        if semantic_similarity < 55:
            suggestions.append(
                "Rewrite a few experience bullets to focus on measurable outcomes that match the target role."
            )

        if not suggestions:
            suggestions.append(
                "Your resume is well aligned. Improve it further by quantifying impact with metrics and recent achievements."
            )

        return unique_preserve_order(suggestions)
