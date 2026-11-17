from datetime import datetime
from typing import Literal

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
from models import Event

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class EventIn(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    location: str = Field(min_length=1, max_length=150)
    date: datetime
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    host: str = Field(min_length=1, max_length=50)
    privacy: Literal["public", "approval", "private"] = "public"


class EventOut(EventIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


@app.on_event("startup")
def seed_sample_events():
    db = SessionLocal()
    try:
        if db.query(Event).count() == 0:
            db.add_all([
                Event(title="Rooftop Sundowner", location="Westlands, Nairobi",
                      date=datetime(2026, 12, 5, 18, 0), host="Mapesa",
                      latitude=-1.2676, longitude=36.8108, privacy="public"),
                Event(title="Game Night", location="Kilimani, Nairobi",
                      date=datetime(2026, 12, 7, 19, 30), host="Kate",
                      latitude=-1.2890, longitude=36.7860, privacy="public"),
            ])
            db.commit()
    finally:
        db.close()


@app.get("/events", response_model=list[EventOut])
def list_events(db: Session = Depends(get_db)):
    return db.query(Event).filter(Event.privacy != "private").all()


@app.post("/events", response_model=EventOut, status_code=201)
def create_event(event: EventIn, db: Session = Depends(get_db)):
    new_event = Event(**event.model_dump())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


@app.get("/map", include_in_schema=False)
def map_page():
    return FileResponse("static/map.html")


app.mount("/static", StaticFiles(directory="static"), name="static")
