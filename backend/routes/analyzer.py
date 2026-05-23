from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.models.schemas import AnalysisResponse, StorageMetadata, UploadResponse
from backend.services.analysis_service import ResumeAnalyzerService
from backend.services.resume_parser import ResumeParser
from cloud.s3_upload import S3Uploader

router = APIRouter(prefix="/api/v1", tags=["resume-analyzer"])

resume_parser = ResumeParser()
resume_analyzer = ResumeAnalyzerService()
s3_uploader = S3Uploader()


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/upload", response_model=UploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    try:
        file_bytes = await resume_parser.read_upload(file)
        upload_result = s3_uploader.upload_bytes(
            file_bytes=file_bytes,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return UploadResponse(
        filename=file.filename,
        storage=StorageMetadata(
            bucket=upload_result.bucket,
            object_key=upload_result.object_key,
            file_url=upload_result.file_url,
            storage_enabled=upload_result.storage_enabled,
        ),
    )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...),
):
    try:
        file_bytes = await resume_parser.read_upload(file)
        resume_text = resume_parser.parse_resume(file_bytes, file.filename)
        analysis = resume_analyzer.analyze(resume_text=resume_text, job_description=job_description)
        upload_result = s3_uploader.upload_bytes(
            file_bytes=file_bytes,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}") from exc

    return AnalysisResponse(
        filename=file.filename,
        match_score=analysis.match_score,
        semantic_similarity=analysis.semantic_similarity,
        keyword_match_score=analysis.keyword_match_score,
        skill_match_score=analysis.skill_match_score,
        extracted_skills=analysis.extracted_skills,
        matched_skills=analysis.matched_skills,
        missing_skills=analysis.missing_skills,
        suggestions=analysis.suggestions,
        storage=StorageMetadata(
            bucket=upload_result.bucket,
            object_key=upload_result.object_key,
            file_url=upload_result.file_url,
            storage_enabled=upload_result.storage_enabled,
        ),
    )
