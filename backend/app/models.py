import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    skin_tone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    lesions = relationship("Lesion", back_populates="owner", cascade="all, delete-orphan")


class Lesion(Base):
    __tablename__ = "lesions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body_part = Column(String, nullable=False)  # e.g. "left_upper_arm"
    label = Column(String, nullable=True)  # user-given nickname
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="lesions")
    captures = relationship(
        "Capture", back_populates="lesion", cascade="all, delete-orphan", order_by="Capture.created_at"
    )


class Capture(Base):
    __tablename__ = "captures"

    id = Column(Integer, primary_key=True, index=True)
    lesion_id = Column(Integer, ForeignKey("lesions.id"), nullable=False)
    image_path = Column(String, nullable=False)
    heatmap_path = Column(String, nullable=True)
    classification = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    urgency = Column(String, nullable=False)  # "high" | "low"
    gemini_report = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    lesion = relationship("Lesion", back_populates="captures")
