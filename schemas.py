"""
Database Schemas for StudyMate AI

Each Pydantic model represents a MongoDB collection. The collection
name is the lowercase of the class name (e.g., TimetableEntry -> "timetableentry").
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Student(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    major: Optional[str] = Field(None, description="Major/Discipline")
    year: Optional[str] = Field(None, description="Year of study")


class TimetableEntry(BaseModel):
    title: str = Field(..., description="Session title, e.g., Thermodynamics Lecture")
    course: str = Field(..., description="Course code or name")
    day: str = Field(..., description="Day of week")
    start_time: str = Field(..., description="Start time (HH:MM)")
    end_time: str = Field(..., description="End time (HH:MM)")
    location: Optional[str] = Field(None, description="Location or link")
    notes: Optional[str] = Field(None, description="Notes or focus topics")
    priority: Optional[int] = Field(3, ge=1, le=5, description="Priority 1-5")


class Note(BaseModel):
    title: str = Field(..., description="Note title")
    source_type: str = Field(..., description="text | pdf | audio")
    content: str = Field(..., description="Raw note content")
    summary: Optional[str] = Field(None, description="Summarized text")
    tags: List[str] = Field(default_factory=list, description="Tags for organization")


class Reminder(BaseModel):
    message: str = Field(..., description="Reminder message")
    due_at: datetime = Field(..., description="Due date/time in ISO format")
    status: str = Field("pending", description="pending | done | snoozed")


class StudySession(BaseModel):
    subject: str = Field(..., description="Subject or course")
    duration_minutes: int = Field(..., ge=1, description="Duration in minutes")
    date: datetime = Field(default_factory=datetime.utcnow)
    score: Optional[int] = Field(None, ge=0, le=100, description="Self-assessed score")


class Recommendation(BaseModel):
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Actionable suggestion")
    action: Optional[str] = Field(None, description="Suggested action keyword")
