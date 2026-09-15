"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from abc import ABC, abstractmethod
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
import re
from pathlib import Path


class Email(ABC):
    """Common interface for email handling and validation."""

    @property
    @abstractmethod
    def value(self) -> str:
        """Return the raw email value."""

    @abstractmethod
    def normalized(self) -> str:
        """Return a canonical representation of the email."""

    @abstractmethod
    def is_valid(self) -> bool:
        """Return whether the email is valid."""


class StudentEmail(Email):
    """A simple, useful email implementation for school signups."""

    _EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

    def __init__(self, value: str):
        self._value = value.strip()

    @property
    def value(self) -> str:
        return self._value

    def normalized(self) -> str:
        return self._value.lower()

    def is_valid(self) -> bool:
        return bool(self._EMAIL_PATTERN.fullmatch(self.normalized()))


app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    student_email = StudentEmail(email)
    if not student_email.is_valid():
        raise HTTPException(status_code=400, detail="Invalid email format")

    normalized_email = student_email.normalized()

    # Get the specific activity
    activity = activities[activity_name]

    if normalized_email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up for this activity"
    )

    # Add student
    activity["participants"].append(normalized_email)
    return {"message": f"Signed up {normalized_email} for {activity_name}"}
