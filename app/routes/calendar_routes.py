# app/routes/calendar_routes.py
from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.services.calendar_service import CalendarService
from app.models.calendar_models import EventCreate, EventInfo

router = APIRouter(prefix="/calendar", tags=["Calendar"])

@router.post("/events")
async def create_event(event: EventCreate):
    """Create a calendar event"""
    try:
        calendar = CalendarService()
        result = calendar.create_event(
            summary=event.summary,
            start_time=event.start.date_time,
            end_time=event.end.date_time,
            description=event.description,
            attendees=event.attendees
        )
        
        if result:
            return {"message": "Event created successfully", "result": result}
        else:
            raise HTTPException(status_code=500, detail="Failed to create event")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events")
async def list_events(max_results: int = 10, days_ahead: int = 7):
    """List upcoming calendar events"""
    try:
        calendar = CalendarService()
        
        # Calculate time range
        from datetime import timedelta
        time_min = datetime.utcnow()
        
        result = calendar.list_events(max_results, time_min)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/events/{event_id}")
async def update_event(
    event_id: str,
    summary: str = None,
    start_time: datetime = None,
    end_time: datetime = None
):
    """Update an existing event"""
    try:
        calendar = CalendarService()
        result = calendar.update_event(
            event_id=event_id,
            summary=summary,
            start_time=start_time,
            end_time=end_time
        )
        
        if result:
            return {"message": "Event updated successfully", "result": result}
        else:
            raise HTTPException(status_code=404, detail="Event not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/events/{event_id}")
async def delete_event(event_id: str):
    """Delete an event"""
    try:
        calendar = CalendarService()
        success = calendar.delete_event(event_id)
        if success:
            return {"message": "Event deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Event not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))