from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from app.models import CodeReviewRequest, CodeReviewResponse
from app.code_reviewer import AiCodeReviewer
import json
import uvicorn

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

code_reviewer = AiCodeReviewer()

@app.post("/api/v1/code-review", response_model=CodeReviewResponse)
async def analyze_code(request: CodeReviewRequest):
    try:
        result = code_reviewer.analyze_code(
            code=request.code,
            language=request.language,
            context=request.context
        )
        return CodeReviewResponse(
            overall_score=result["overall_score"],
            breakdown=result["breakdown"],
            recommendations=result["recommendations"],
            detailed_feedback=result["detailed_feedback"],
            language=request.language
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing code: {str(e)}"
        )

@app.post("/api/v1/upload-code", response_model=CodeReviewResponse)
async def upload_code(file: UploadFile = File(...)):
    try:
        content = await file.read()
        language = file.filename.split('.')[-1]
        if language not in ['py', 'js', 'jsx']:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Only .py, .js, and .jsx files are supported."
            )
            
        result = code_reviewer.analyze_code(
            code=content.decode(),
            language=language,
            context=f"File: {file.filename}"
        )
        
        return CodeReviewResponse(
            overall_score=result["overall_score"],
            breakdown=result["breakdown"],
            recommendations=result["recommendations"],
            detailed_feedback=result["detailed_feedback"],
            language=language
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Code Reviewer API",
        "endpoints": {
            "/api/v1/code-review": "POST - Analyze code directly",
            "/api/v1/upload-code": "POST - Upload file for analysis"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)