from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Device identification
    device_id = Column(String(64), unique=True, index=True, nullable=False)  # UUID generated on first sync
    device_name = Column(String(255), nullable=False)  # User-friendly name: "Lenovo T440", "MacBook Pro"
    device_type = Column(String(50), default="desktop")  # desktop, laptop, tablet, phone
    os_name = Column(String(100), nullable=True)  # Windows 11, macOS Sonoma, Ubuntu 22.04
    os_version = Column(String(50), nullable=True)  # Version details
    hostname = Column(String(255), nullable=True)  # Computer hostname for auto-detection
    
    # Sync settings
    folder_name = Column(String(255), nullable=False)  # Folder name on server (sanitized device_name)
    sync_enabled = Column(Boolean, default=True)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    last_sync_files_count = Column(Integer, default=0)
    last_sync_bytes = Column(BigInteger, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)  # False if device is unlinked but folder kept
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="devices")
    
    def __repr__(self):
        return f"<Device {self.device_name} ({self.device_id})>"
