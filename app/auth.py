# app/auth.py
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from app.config import settings
from pathlib import Path

class GoogleAuth:
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.token_path = settings.TOKEN_DIR / f"token_{user_id}.pickle"
        self.credentials_path = settings.CREDENTIALS_PATH
        
        # Ensure token directory exists
        settings.TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    
    # Head full 
    def get_credentials(self, scopes: list) -> Credentials:
        """Get credentials for a specific set of scopes"""
        creds = None
        
        # Load existing token if available
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If credentials are expired or invalid, refresh or get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, scopes
                )
                creds = flow.run_local_server(port=8081)
            
            # Save credentials for future use
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds
    
    # ## Head less
    # def get_credentials(self, scopes: list) -> Credentials:
    #     """Get credentials for a specific set of scopes"""
    #     creds = None
        
    #     if self.token_path.exists():
    #         with open(self.token_path, 'rb') as token:
    #             creds = pickle.load(token)
        
    #     if not creds or not creds.valid:
    #         if creds and creds.expired and creds.refresh_token:
    #             creds.refresh(Request())
    #         else:
    #             flow = InstalledAppFlow.from_client_secrets_file(
    #                 self.credentials_path, scopes
    #             )
                
    #             # Run the OAuth flow without a local server
    #             # This will print a URL for you to visit manually
    #             auth_url, _ = flow.authorization_url(
    #                 prompt='consent'
    #             )
                
    #             print(f'Please go to this URL and authorize the application: {auth_url}')
                
    #             # Get the authorization code from user input
    #             code = input('Enter the authorization code: ')
                
    #             # Exchange the code for credentials
    #             flow.fetch_token(code=code)
    #             creds = flow.credentials
            
    #         with open(self.token_path, 'wb') as token:
    #             pickle.dump(creds, token)
        
    #     return creds

    def get_gmail_credentials(self):
        return self.get_credentials(settings.GMAIL_SCOPES)
    
    def get_drive_credentials(self):
        return self.get_credentials(settings.DRIVE_SCOPES)
    
    def get_calendar_credentials(self):
        return self.get_credentials(settings.CALENDAR_SCOPES)