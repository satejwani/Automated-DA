from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.core.database import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False, index=True)
    file_size_bytes = Column(BigInteger, nullable=False)
    storage_path = Column(String(500), nullable=False)
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    upload_timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    columns = relationship("DatasetColumn", back_populates="dataset", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="dataset", cascade="all, delete-orphan")
    charts = relationship("GeneratedChart", back_populates="dataset", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="dataset", cascade="all, delete-orphan")


class DatasetColumn(Base):
    __tablename__ = "dataset_columns"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    column_name = Column(String(255), nullable=False)
    data_type = Column(String(100), nullable=False)
    inferred_type = Column(String(100), nullable=False, index=True)
    is_nullable = Column(Boolean, default=True)
    null_count = Column(Integer, default=0)
    unique_count = Column(Integer, default=0)

    dataset = relationship("Dataset", back_populates="columns")
