from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    location = Column(String(150), nullable=False)
    date = Column(DateTime, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    host = Column(String(50), nullable=False)
    privacy = Column(String(10), nullable=False, default="public")
