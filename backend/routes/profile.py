from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..models.student_profile import StudentProfile
from ..schemas import ProfileRequest
from ..auth import get_current_user

router = APIRouter(prefix="/api/profile", tags=["profile"])


def _profile_payload(profile: StudentProfile) -> dict:
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "education": profile.education,
        "year": profile.year,
        "department": profile.department,
        "selected_subject_id": profile.selected_subject_id,
        "current_topic_index": profile.current_topic_index,
        "learning_streak": profile.learning_streak,
    }


@router.get("/me")
def get_profile(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the current student's academic profile (or null if not set up yet)."""
    profile = (
        db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    )
    return {
        "profile": _profile_payload(profile) if profile else None,
        "user": {"id": user.id, "name": user.name, "email": user.email},
    }


@router.post("/save")
def save_profile(
    body: ProfileRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create or update the student's education / year / department selection."""
    profile = (
        db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    )
    if profile:
        profile.education = body.education
        profile.year = body.year
        profile.department = body.department
    else:
        profile = StudentProfile(
            user_id=user.id,
            education=body.education,
            year=body.year,
            department=body.department,
        )
        db.add(profile)
    db.commit()
    db.refresh(profile)
    return {"message": "Profile saved", "profile_id": profile.id}


@router.post("/select-subject")
def select_subject(
    subject_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Select the subject to study and reset progress to its first topic."""
    from ..models.subject import Subject

    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    profile = (
        db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    )
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found. Please set up your profile first.",
        )

    # Re-selecting a different subject restarts the path; re-selecting the same
    # one keeps the student's progress.
    if profile.selected_subject_id != subject_id:
        profile.selected_subject_id = subject_id
        profile.current_topic_index = 0
    db.commit()
    return {"message": "Subject selected", "subject_id": subject_id}
