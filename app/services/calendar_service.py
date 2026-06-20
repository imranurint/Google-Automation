# app/services/calendar_service.py
from googleapiclient.discovery import build
from app.auth import GoogleAuth
from datetime import datetime

class CalendarService:
    def __init__(self, user_id: str = "default"):
        self.auth = GoogleAuth(user_id)
        self.service = build('calendar', 'v3', credentials=self.auth.get_calendar_credentials())
    
    def create_event(self, summary: str, start_time: datetime, end_time: datetime,
                     description: str = None, attendees: list = None) -> dict:
        """Create a calendar event"""
        try:
            event = {
                'summary': summary,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            if description:
                event['description'] = description
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return created_event
        except Exception as e:
            print(f"Error creating event: {e}")
            return None
    
    def list_events(self, max_results: int = 10, time_min: datetime = None) -> dict:
        """List calendar events"""
        try:
            if not time_min:
                time_min = datetime.utcnow()
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min.isoformat() + 'Z',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            next_page_token = events_result.get('nextPageToken')
            
            return {
                'events': events,
                'next_page_token': next_page_token
            }
        except Exception as e:
            print(f"Error listing events: {e}")
            return {'events': [], 'next_page_token': None}
    
    def update_event(self, event_id: str, summary: str = None, 
                     start_time: datetime = None, end_time: datetime = None) -> dict:
        """Update an existing event"""
        try:
            # Get existing event
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            if summary:
                event['summary'] = summary
            
            if start_time:
                event['start'] = {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC'
                }
            
            if end_time:
                event['end'] = {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC'
                }
            
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            return updated_event
        except Exception as e:
            print(f"Error updating event: {e}")
            return None
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            return True
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False