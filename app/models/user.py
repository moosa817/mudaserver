from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from app.core.config import config


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    pfp = Column(String, nullable=True)
    root_foldername = Column(String, nullable=True)
    max_storage = Column(BigInteger, default=config.MAX_STORAGE)
    storage_used = Column(BigInteger, default=0)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    folders = relationship(
        "Folder", back_populates="user", cascade="all, delete-orphan"
    )
    files = relationship("File", back_populates="user", cascade="all, delete-orphan")
    devices = relationship("Device", back_populates="user", cascade="all, delete-orphan")
