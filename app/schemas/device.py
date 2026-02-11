from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DeviceRegister(BaseModel):
    device_name: str = Field(..., min_length=1, max_length=255)
    device_type: str = Field(default="desktop", max_length=50)
    os_name: Optional[str] = Field(None, max_length=100)
    os_version: Optional[str] = Field(None, max_length=50)
    hostname: Optional[str] = Field(None, max_length=255)


class DeviceUpdate(BaseModel):
    device_name: Optional[str] = Field(None, min_length=1, max_length=255)
    sync_enabled: Optional[bool] = None


class DeviceResponse(BaseModel):
    device_id: str
    device_name: str
    device_type: str
    os_name: Optional[str]
    os_version: Optional[str]
    hostname: Optional[str]
    folder_name: str
    sync_enabled: bool
    last_sync_at: Optional[datetime]
    last_sync_files_count: int
    last_sync_bytes: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class DeviceListResponse(BaseModel):
    devices: list[DeviceResponse]
    total: int


class SyncCompleteRequest(BaseModel):
    device_id: str
    files_synced: int = 0
    bytes_synced: int = 0
