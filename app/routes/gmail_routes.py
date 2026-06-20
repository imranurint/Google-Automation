# app/routes/gmail_routes.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from typing import Optional, List
import tempfile
import os
from app.services.gmail_service import GmailService
from app.models.gmail_models import EmailSend, EmailList

router = APIRouter(prefix="/gmail", tags=["Gmail"])

@router.post("/send")
async def send_email(
    to: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    cc: Optional[str] = Form(None),
    bcc: Optional[str] = Form(None),
    attachments: Optional[List[UploadFile]] = File(None)
):
    """Send an email with optional attachments"""
    try:
        from app.services.gmail_service import GmailService
        
        gmail = GmailService()
        
        # Save attachments temporarily
        attachment_paths = []
        if attachments:
            for file in attachments:
                if file.filename:  # Check if file exists
                    # Use tempfile for better handling
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
                        content = await file.read()
                        temp_file.write(content)
                        attachment_paths.append(temp_file.name)
        
        cc_list = [email.strip() for email in cc.split(',') if email.strip()] if cc else []
        bcc_list = [email.strip() for email in bcc.split(',') if email.strip()] if bcc else []
        
        result = gmail.send_email(
            to=to.strip(),
            subject=subject.strip(),
            body=body.strip(),
            cc=cc_list,
            bcc=bcc_list,
            attachments=attachment_paths
        )
        
        # Clean up temporary files
        for path in attachment_paths:
            try:
                os.unlink(path)
            except:
                pass
        
        return {
            "message": "Email sent successfully", 
            "result": result,
            "details": {
                "to": to,
                "subject": subject,
                "cc": cc_list,
                "bcc": bcc_list,
                "attachments": len(attachment_paths)
            }
        }
        
    except Exception as e:
        # Log the error for debugging
        import traceback
        error_detail = traceback.format_exc()
        print(f"Error sending email: {error_detail}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )

@router.get("/list", response_model=EmailList)
async def list_emails(max_results: int = 10, query: Optional[str] = None):
    """List emails from Gmail"""
    try:
        gmail = GmailService()
        result = gmail.list_emails(max_results, query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{message_id}")
async def delete_email(message_id: str):
    """Delete an email by ID"""
    try:
        gmail = GmailService()
        success = gmail.delete_email(message_id)
        if success:
            return {"message": "Email deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Email not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

