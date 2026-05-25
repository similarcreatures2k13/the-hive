#!/usr/bin/env python3
"""
Google Calendar tool for Hermes Agent.
Direct API — no MCP, no timeouts.
"""

import os
import sys
import json
import datetime
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CREDS_FILE = Path.home() / "credentials.json"
TOKEN_FILE = Path.home() / ".google_calendar_token.json"

def get_service():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
            flow.redirect_uri = "http://localhost:8090"
            auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
            print(f"\nOpen this URL in your browser:\n{auth_url}\n")
            print("After authorizing, copy the FULL URL from the blank page.\n")
            redirect_response = input("Paste the full redirect URL: ")
            flow.fetch_token(authorization_response=redirect_response)
            creds = flow.credentials
        TOKEN_FILE.write_text(creds.to_json())
    return build("calendar", "v3", credentials=creds)

def list_calendars():
    service = get_service()
    result = service.calendarList().list().execute()
    calendars = result.get("items", [])
    for cal in calendars:
        print(f"  {cal['summary']} ({cal['id']})")
    return calendars


def list_events(days=7, calendar_id="primary"):
    service = get_service()
    now = datetime.datetime.utcnow().isoformat() + "Z"
    end = (datetime.datetime.utcnow() + datetime.timedelta(days=days)).isoformat() + "Z"
    result = service.events().list(
        calendarId=calendar_id, timeMin=now, timeMax=end,
        maxResults=20, singleEvents=True, orderBy="startTime"
    ).execute()
    events = result.get("items", [])
    if not events:
        print("No upcoming events.")
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(f"  {start} — {event.get('summary', 'No title')}")
    return events


def create_event(summary, start_time, duration_minutes=60, calendar_id="primary", description=""):
    service = get_service()
    start_dt = datetime.datetime.fromisoformat(start_time)
    end_dt = start_dt + datetime.timedelta(minutes=duration_minutes)
    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"},
    }
    created = service.events().insert(calendarId=calendar_id, body=event).execute()
    print(f"  Created: {created.get('summary')} at {created['start']['dateTime']}")
    print(f"  Link: {created.get('htmlLink')}")
    return created


def delete_event(event_id, calendar_id="primary"):
    service = get_service()
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    print(f"  Deleted event: {event_id}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 calendar_tool.py list-calendars")
        print("  python3 calendar_tool.py list-events [days]")
        print('  python3 calendar_tool.py create "Meeting" "2026-05-25T14:00:00" [duration_min]')
        print("  python3 calendar_tool.py delete <event_id>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "list-calendars":
        list_calendars()
    elif cmd == "list-events":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        list_events(days)
    elif cmd == "create":
        summary = sys.argv[2]
        start = sys.argv[3]
        duration = int(sys.argv[4]) if len(sys.argv) > 4 else 60
        create_event(summary, start, duration)
    elif cmd == "delete":
        delete_event(sys.argv[2])
    else:
        print(f"Unknown command: {cmd}")
