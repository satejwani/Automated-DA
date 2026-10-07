from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.core.database import Base

class GeneratedChart(Base):
    __tablename__ = "generated_charts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_results.id", ondelete="CASCADE"), nullable=False, index=True)
    chart_type = Column(String(100), nullable=False, index=True)
    chart_title = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    chart_metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dataset = relationship("Dataset", back_populates="charts")
    analysis_result = relationship("AnalysisResult", back_populates="charts")
