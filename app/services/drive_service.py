# app/services/drive_service.py
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from app.auth import GoogleAuth
import io

class DriveService:
    def __init__(self, user_id: str = "default"):
        self.auth = GoogleAuth(user_id)
        self.service = build('drive', 'v3', credentials=self.auth.get_drive_credentials())
    
    def list_files(self, page_size: int = 10, query: str = None) -> dict:
        """List files from Google Drive"""
        try:
            results = self.service.files().list(
                pageSize=page_size,
                q=query,
                fields="nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            next_page_token = results.get('nextPageToken')
            
            return {
                'files': files,
                'next_page_token': next_page_token
            }
        except Exception as e:
            print(f"Error listing files: {e}")
            return {'files': [], 'next_page_token': None}
    
    def upload_file(self, file_path: str, name: str = None, 
                    parents: list = None, mime_type: str = None) -> dict:
        """Upload a file to Google Drive"""
        try:
            if not name:
                name = os.path.basename(file_path)
            
            file_metadata = {
                'name': name
            }
            
            if parents:
                file_metadata['parents'] = parents
            
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, mimeType, size, webViewLink'
            ).execute()
            
            return file
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None
    
    def download_file(self, file_id: str, destination_path: str) -> bool:
        """Download a file from Google Drive"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.FileIO(destination_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%.")
            
            return True
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file from Google Drive"""
        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def create_folder(self, name: str, parents: list = None) -> dict:
        """Create a folder in Google Drive"""
        try:
            file_metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parents:
                file_metadata['parents'] = parents
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id, name, webViewLink'
            ).execute()
            
            return folder
        except Exception as e:
            print(f"Error creating folder: {e}")
            return None

