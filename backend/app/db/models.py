from datetime import datetime, timezone
import json
from typing import Dict, Any, List, Optional
from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    Integer,
    DateTime,
    ForeignKey,
    Index
)
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

def utcnow():
    return datetime.now(timezone.utc)

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(128), primary_key=True, index=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    title = Column(String(255), default="Maritime Inquiry", nullable=False)
    language = Column(String(32), default="en", nullable=False)
    status = Column(String(64), default="ACTIVE", nullable=False)

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.sequence_number")
    context = relationship("ConversationContextModel", back_populates="conversation", uselist=False, cascade="all, delete-orphan")
    results = relationship("AnalysisResult", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(String(128), primary_key=True, index=True)
    conversation_id = Column(String(128), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(32), nullable=False)  # USER, ASSISTANT, SYSTEM, TOOL
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    sequence_number = Column(Integer, default=1, nullable=False)
    metadata_json = Column(Text, nullable=True)

    conversation = relationship("Conversation", back_populates="messages")

    __table_args__ = (
        Index("ix_messages_conv_seq", "conversation_id", "sequence_number"),
    )

class ConversationContextModel(Base):
    __tablename__ = "conversation_context"

    conversation_id = Column(String(128), ForeignKey("conversations.id", ondelete="CASCADE"), primary_key=True)
    location_lat = Column(Float, nullable=True)
    location_lon = Column(Float, nullable=True)
    location_accuracy = Column(Float, nullable=True)
    location_timestamp = Column(String(128), nullable=True)

    activity = Column(String(128), nullable=True, default="Fishing Operations")
    vessel_context = Column(String(128), nullable=True, default="Small Craft")
    time_context = Column(String(128), nullable=True, default="Tomorrow Morning")
    constraints = Column(Text, nullable=True)  # JSON array of strings
    current_intent = Column(String(128), nullable=True)
    current_result_id = Column(String(128), nullable=True)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    conversation = relationship("Conversation", back_populates="context")

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(String(128), primary_key=True, index=True)
    conversation_id = Column(String(128), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    result_type = Column(String(128), nullable=False)  # ROUTE_RESULT, PFZ_RESULTS, HAZARD_ALERT, RISK_MAP, MARINE_CONDITIONS
    payload_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    valid_until = Column(DateTime, nullable=True)

    conversation = relationship("Conversation", back_populates="results")
    entities = relationship("ResultEntity", back_populates="analysis_result", cascade="all, delete-orphan")
    source_evidence = relationship("SourceEvidence", back_populates="analysis_result", cascade="all, delete-orphan")

class ResultEntity(Base):
    __tablename__ = "result_entities"

    id = Column(String(128), primary_key=True, index=True)
    analysis_result_id = Column(String(128), ForeignKey("analysis_results.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(String(128), nullable=False, index=True)
    entity_type = Column(String(64), nullable=False)  # ROUTE, PFZ_CANDIDATE, HAZARD_ALERT, AVOID_AREA, MARINE_CONDITIONS
    entity_id = Column(String(128), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    geometry_json = Column(Text, nullable=True)
    properties_json = Column(Text, nullable=True)

    analysis_result = relationship("AnalysisResult", back_populates="entities")

class SourceEvidence(Base):
    __tablename__ = "source_evidence"

    id = Column(String(128), primary_key=True, index=True)
    analysis_result_id = Column(String(128), ForeignKey("analysis_results.id", ondelete="CASCADE"), nullable=False, index=True)
    source = Column(String(128), nullable=False)  # INCOIS, IMD, MOSDAC, GIS_CADASTRE
    dataset = Column(String(128), nullable=True)
    authority_type = Column(String(128), nullable=True)
    retrieved_at = Column(DateTime, default=utcnow, nullable=False)
    valid_time = Column(String(128), nullable=True)
    metadata_json = Column(Text, nullable=True)

    analysis_result = relationship("AnalysisResult", back_populates="source_evidence")
