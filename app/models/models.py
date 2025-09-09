from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Snapshot(Base):
    """
    Model for storing options chain snapshots
    TODO: Add database migrations and connection setup
    """
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_id = Column(String(50), unique=True, index=True)
    index_name = Column(String(20), index=True)
    expiry_date = Column(String(20))
    underlying_value = Column(Float)
    atm_strike = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    data_path = Column(String(255))  # Path to CSV file
    metadata_path = Column(String(255))  # Path to JSON metadata
    status = Column(String(20), default="completed")  # pending, completed, failed

class Alert(Base):
    """
    Model for storing user alerts and their configurations
    TODO: Add database migrations and connection setup
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    name = Column(String(100))
    index_name = Column(String(20))
    rule_config = Column(JSON)  # Store alert rule configuration
    notify_config = Column(JSON)  # Store notification settings
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_triggered = Column(DateTime, nullable=True)

class Job(Base):
    """
    Model for tracking background jobs
    TODO: Add database migrations and connection setup
    """
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(50), unique=True, index=True)
    job_type = Column(String(50))  # fetch_options, backtest, etc.
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    user_id = Column(Integer, index=True, nullable=True)
    params = Column(JSON)  # Job parameters
    result = Column(JSON, nullable=True)  # Job result data
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
