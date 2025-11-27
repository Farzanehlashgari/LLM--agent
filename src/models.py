"""
Data models for the research crew system.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ResearchSource(BaseModel):
    """Model for a research source."""
    title: str
    url: str
    publication_date: Optional[str] = None
    authors: Optional[str] = None
    key_findings: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    

class ResearchResult(BaseModel):
    """Model for research results."""
    timestamp: datetime = Field(default_factory=datetime.now)
    sources: List[ResearchSource] = Field(default_factory=list)
    summary: str = ""
    

class AnalysisResult(BaseModel):
    """Model for analysis results."""
    timestamp: datetime = Field(default_factory=datetime.now)
    executive_summary: str = ""
    trends: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    

class CrewExecutionResult(BaseModel):
    """Model for crew execution results."""
    execution_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    status: str  # success, failure, partial
    report: str = ""
    error: Optional[str] = None
    execution_time_seconds: float = 0.0
