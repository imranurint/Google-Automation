# app/routes/drive_routes.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from app.services.drive_service import DriveService
from app.models.drive_models import FileList

router = APIRouter(prefix="/drive", tags=["Drive"])

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    parent_folder: Optional[str] = Form(None)
):
    """Upload a file to Google Drive"""
    try:
        drive = DriveService()
        
        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        parents = [parent_folder] if parent_folder else None
        
        result = drive.upload_file(
            file_path=temp_path,
            name=name or file.filename,
            parents=parents
        )
        
        return {"message": "File uploaded successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=FileList)
async def list_files(page_size: int = 10, query: Optional[str] = None):
    """List files from Google Drive"""
    try:
        drive = DriveService()
        result = drive.list_files(page_size, query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{file_id}")
async def download_file(file_id: str):
    """Download a file from Google Drive"""
    try:
        drive = DriveService()
        # Get file info first
        file_info = drive.service.files().get(fileId=file_id).execute()
        file_name = file_info.get('name', 'downloaded_file')
        
        temp_path = f"temp_{file_name}"
        success = drive.download_file(file_id, temp_path)
        
        if success:
            return {"message": "File downloaded successfully", "path": temp_path}
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{file_id}")
async def delete_file(file_id: str):
    """Delete a file from Google Drive"""
    try:
        drive = DriveService()
        success = drive.delete_file(file_id)
        if success:
            return {"message": "File deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/folder")
async def create_folder(name: str, parent_folder: Optional[str] = None):
    """Create a folder in Google Drive"""
    try:
        drive = DriveService()
        parents = [parent_folder] if parent_folder else None
        result = drive.create_folder(name, parents)
        
        if result:
            return {"message": "Folder created successfully", "result": result}
        else:
            raise HTTPException(status_code=500, detail="Failed to create folder")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

