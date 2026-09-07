from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..models.student_profile import StudentProfile
from ..schemas import ProfileRequest, ProfileResponse
from ..auth import decode_token

router = APIRouter(prefix="/api/profile", tags=["profile"])


def get_current_user(authorization: str, db: Session):
    """Extract user from Authorization header."""
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/me")
def get_profile(
    authorization: str = Header(""),
    db: Session = Depends(get_db),
):
    user = get_current_user(authorization, db)
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        return {"profile": None, "user": {"id": user.id, "name": user.name, "email": user.email}}
    return {
        "profile": {
            "id": profile.id,
            "user_id": profile.user_id,
            "education": profile.education,
            "year": profile.year,
            "department": profile.department,
            "selected_subject_id": profile.selected_subject_id,
            "current_topic_index": profile.current_topic_index,
            "learning_streak": profile.learning_streak,
        },
        "user": {"id": user.id, "name": user.name, "email": user.email},
    }


@router.post("/save")
def save_profile(
    body: ProfileRequest,
    authorization: str = Header(""),
    db: Session = Depends(get_db),
):
    user = get_current_user(authorization, db)
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
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
    authorization: str = Header(""),
    db: Session = Depends(get_db),
):
    user = get_current_user(authorization, db)
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Please set up your profile first.")
    profile.selected_subject_id = subject_id
    profile.current_topic_index = 0
    db.commit()
    return {"message": "Subject selected", "subject_id": subject_id}
