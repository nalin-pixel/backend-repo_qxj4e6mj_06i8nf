import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents

app = FastAPI(title="StudyMate AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateTimetableEntry(BaseModel):
    title: str
    course: str
    day: str
    start_time: str
    end_time: str
    location: Optional[str] = None
    notes: Optional[str] = None
    priority: Optional[int] = 3


class CreateNoteFromText(BaseModel):
    title: str
    content: str


@app.get("/")
def read_root():
    return {"message": "StudyMate AI Backend is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


@app.post("/api/timetable")
def create_timetable_entry(payload: CreateTimetableEntry):
    try:
        inserted_id = create_document("timetableentry", payload.model_dump())
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/timetable")
def list_timetable_entries(day: Optional[str] = None):
    try:
        filter_dict = {"day": day} if day else {}
        docs = get_documents("timetableentry", filter_dict=filter_dict, limit=100)
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"ok": True, "items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/notes/summarize")
def summarize_text(payload: CreateNoteFromText):
    # Placeholder simple summarization (first 3 sentences).
    # In a production version you'd call GPT/FLAN via a provider.
    text = payload.content.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Content is empty")
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    summary = ". ".join(sentences[:3]) + ("." if sentences else "")
    try:
        note = {
            "title": payload.title,
            "source_type": "text",
            "content": payload.content,
            "summary": summary,
            "tags": ["summary"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        inserted_id = create_document("note", note)
        return {"ok": True, "id": inserted_id, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
