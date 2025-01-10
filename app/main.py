from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, database, sentiment

app = FastAPI(
    title="Mood Journal API",
    description="A journaling API with AI-powered sentiment analysis",
    version="1.0.0",
)

# Mount the static directory so we can serve CSS and JS files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Route for the main compose page
@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")

# Route for the past entries page
@app.get("/entries")
async def serve_entries():
    return FileResponse("static/entries.html")

models.Base.metadata.create_all(bind=database.engine)


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": str(exc)})


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health", response_model=schemas.HealthResponse)
def health_check():
    return {"status": "ok", "message": "Mood Journal API is running"}


@app.post("/journal", response_model=schemas.JournalEntryResponse, status_code=201)
async def create_journal_entry(
    entry: schemas.JournalEntryCreate, db: Session = Depends(get_db)
):
    analysis = await sentiment.analyze_sentiment(entry.text)

    db_entry = models.JournalEntry(
        text=entry.text,
        mood=analysis["mood"],
        reflection=analysis["reflection"],
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@app.get("/journal", response_model=List[schemas.JournalEntryResponse])
def get_journal_entries(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    entries = (
        db.query(models.JournalEntry)
        .order_by(models.JournalEntry.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return entries
