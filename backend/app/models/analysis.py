from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.core.database import Base

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    quality_score = Column(Float, default=0.0)
    data_quality_json = Column(JSON, nullable=True)
    numerical_stats_json = Column(JSON, nullable=True)
    categorical_stats_json = Column(JSON, nullable=True)
    correlation_matrix_json = Column(JSON, nullable=True)

    # Relationships
    dataset = relationship("Dataset", back_populates="analysis_results")
    charts = relationship("GeneratedChart", back_populates="analysis_result", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="analysis_result", cascade="all, delete-orphan")
