# app/services/gmail_service.py
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from googleapiclient.discovery import build
from app.auth import GoogleAuth
from typing import List, Optional
import os
from googleapiclient.errors import HttpError

class GmailService:
    def __init__(self, user_id: str = "default"):
        try:
            self.auth = GoogleAuth(user_id)
            self.service = build('gmail', 'v1', credentials=self.auth.get_gmail_credentials())
        except Exception as e:
            print(f"Error initializing Gmail service: {e}")
            raise
    
    def send_email(self, to: str, subject: str, body: str, 
                   cc: List[str] = None, bcc: List[str] = None,
                   attachments: List[str] = None) -> dict:
        """Send an email using Gmail API"""
        try:
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = ','.join(cc)
            if bcc:
                message['bcc'] = ','.join(bcc)
            
            # Attach body
            message.attach(MIMEText(body, 'plain'))
            
            # Attach files
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            file_name = os.path.basename(file_path)
                            part = MIMEApplication(f.read(), Name=file_name)
                            part['Content-Disposition'] = f'attachment; filename="{file_name}"'
                            message.attach(part)
            
            # Create raw message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send email
            send_message = self.service.users().messages().send(
                userId='me', 
                body={'raw': raw_message}
            ).execute()
            
            return send_message
            
        except HttpError as error:
            print(f'An HTTP error occurred: {error}')
            raise Exception(f"Gmail API error: {error}")
        except Exception as e:
            print(f'An error occurred: {e}')
            raise
    
    def list_emails(self, max_results: int = 10, query: str = None) -> dict:
        """List emails from Gmail"""
        try:
            result = self.service.users().messages().list(
                userId='me', 
                maxResults=max_results,
                q=query or ''
            ).execute()
            
            messages = result.get('messages', [])
            next_page_token = result.get('nextPageToken')
            
            emails = []
            for msg in messages[:max_results]:
                email_data = self.get_email(msg['id'])
                if email_data:
                    emails.append(email_data)
            
            return {
                'emails': emails,
                'total': len(emails),
                'next_page_token': next_page_token
            }
        except Exception as e:
            print(f"Error listing emails: {e}")
            return {'emails': [], 'total': 0, 'next_page_token': None}
    
    def get_email(self, message_id: str) -> dict:
        """Get a specific email by ID"""
        try:
            message = self.service.users().messages().get(
                userId='me', 
                id=message_id, 
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            from_ = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), None)
            
            # Get body
            body = ''
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                        data = part['body']['data']
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
            elif 'body' in message['payload']:
                if message['payload']['mimeType'] == 'text/plain' and 'data' in message['payload']['body']:
                    data = message['payload']['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
            
            return {
                'id': message_id,
                'subject': subject,
                'from_': from_,
                'date': date,
                'snippet': message.get('snippet', ''),
                'body': body
            }
        except Exception as e:
            print(f"Error getting email {message_id}: {e}")
            return None
    
    def delete_email(self, message_id: str) -> bool:
        """Delete an email"""
        try:
            self.service.users().messages().delete(
                userId='me', 
                id=message_id
            ).execute()
            return True
        except Exception as e:
            print(f"Error deleting email {message_id}: {e}")
            return False
