from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.sql import func
from sqlalchemy import DateTime


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    size = Column(BigInteger, nullable=False)
    type = Column(String, nullable=False)  # file or media
    thumbnail = Column(String, nullable=True)  # for media files only
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="files")
    folders = relationship("Folder", back_populates="files")
