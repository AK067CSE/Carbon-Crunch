from pydantic import BaseModel
from typing import List, Dict, Optional

class CodeReviewRequest(BaseModel):
    code: str
    language: str = "python"
    context: str = None
    file_name: Optional[str] = None

class CodeReviewResponse(BaseModel):
    overall_score: int
    breakdown: Dict[str, int]
    recommendations: List[str]
    detailed_feedback: str
    file_name: Optional[str] = None
    language: Optional[str] = None