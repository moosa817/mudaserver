from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.device import Device
from app.schemas.device import (
    DeviceRegister,
    DeviceUpdate,
    DeviceResponse,
    DeviceListResponse,
)
from app.services.devices.device_utils import sanitize_folder_name, get_unique_folder_name
from app.core.config import config
import os
import uuid
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

devicerouter = APIRouter()


@devicerouter.post("/register", response_model=DeviceResponse)
async def register_device(
    device_data: DeviceRegister,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Register a new device or return existing device if hostname matches.
    """
    try:
        # Check if device with same hostname already exists for user
        if device_data.hostname:
            existing_device = db.query(Device).filter(
                Device.user_id == user.id,
                Device.hostname == device_data.hostname,
                Device.is_active == True
            ).first()
            
            if existing_device:
                logger.info(f"Returning existing device for hostname: {device_data.hostname}")
                return existing_device
        
        # Generate unique device_id
        device_id = str(uuid.uuid4())
        
        # Sanitize device name for folder name
        sanitized_name = sanitize_folder_name(device_data.device_name)
        
        # Get existing device folder names to ensure uniqueness
        existing_devices = db.query(Device).filter(Device.user_id == user.id).all()
        existing_folders = [d.folder_name for d in existing_devices]
        
        # Get unique folder name
        folder_name = get_unique_folder_name(sanitized_name, existing_folders)
        
        # Create the device folder on filesystem
        user_base_path = os.path.join(config.DIR_LOCATION, "data", user.root_foldername)
        device_folder_path = os.path.join(user_base_path, folder_name)
        os.makedirs(device_folder_path, exist_ok=True)
        
        # Create device in database
        new_device = Device(
            user_id=user.id,
            device_id=device_id,
            device_name=device_data.device_name,
            device_type=device_data.device_type,
            os_name=device_data.os_name,
            os_version=device_data.os_version,
            hostname=device_data.hostname,
            folder_name=folder_name,
            sync_enabled=True,
            is_active=True
        )
        
        db.add(new_device)
        db.commit()
        db.refresh(new_device)
        
        logger.info(f"Device registered: {device_id} - {device_data.device_name}")
        
        return new_device
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error registering device: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to register device")


@devicerouter.get("/list", response_model=DeviceListResponse)
async def list_devices(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all devices for the current user.
    """
    try:
        devices = db.query(Device).filter(Device.user_id == user.id).all()
        
        return DeviceListResponse(
            devices=devices,
            total=len(devices)
        )
    
    except Exception as e:
        logger.error(f"Error listing devices: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list devices")


@devicerouter.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific device.
    """
    try:
        device = db.query(Device).filter(
            Device.device_id == device_id,
            Device.user_id == user.id
        ).first()
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        return device
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting device: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get device")


@devicerouter.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    device_data: DeviceUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update device information.
    Note: folder_name does NOT change when renaming device to preserve file paths.
    """
    try:
        device = db.query(Device).filter(
            Device.device_id == device_id,
            Device.user_id == user.id
        ).first()
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Update fields if provided
        if device_data.device_name is not None:
            device.device_name = device_data.device_name
        
        if device_data.sync_enabled is not None:
            device.sync_enabled = device_data.sync_enabled
        
        db.commit()
        db.refresh(device)
        
        logger.info(f"Device updated: {device_id}")
        
        return device
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating device: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update device")


@devicerouter.delete("/{device_id}")
async def delete_device(
    device_id: str,
    delete_files: bool = Query(False, description="If true, also delete the device folder and all files"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unlink/delete a device.
    - If delete_files=false: Set is_active=false, keep folder
    - If delete_files=true: Delete device record AND folder from filesystem
    """
    try:
        device = db.query(Device).filter(
            Device.device_id == device_id,
            Device.user_id == user.id
        ).first()
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        if delete_files:
            # Delete the device folder from filesystem
            user_base_path = os.path.join(config.DIR_LOCATION, "data", user.root_foldername)
            device_folder_path = os.path.join(user_base_path, device.folder_name)
            
            if os.path.exists(device_folder_path):
                import shutil
                shutil.rmtree(device_folder_path)
                logger.info(f"Deleted device folder: {device_folder_path}")
            
            # Delete device record
            db.delete(device)
            db.commit()
            
            return {
                "device_id": device_id,
                "message": "Device deleted successfully",
                "files_deleted": True
            }
        else:
            # Just mark as inactive
            device.is_active = False
            db.commit()
            
            return {
                "device_id": device_id,
                "message": "Device unlinked successfully",
                "files_deleted": False
            }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting device: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete device")
