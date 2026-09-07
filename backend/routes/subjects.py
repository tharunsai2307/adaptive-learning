from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.subject import Subject
from ..models.student_profile import StudentProfile
from ..models.user import User
from ..auth import decode_token

router = APIRouter(prefix="/api/subjects", tags=["subjects"])


def _get_user(authorization: str, db: Session) -> User:
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/")
def list_subjects(
    education: str = "",
    year: str = "",
    department: str = "",
    authorization: str = Depends(lambda request: request.headers.get("Authorization", "")),
    db: Session = Depends(get_db),
):
    """List subjects, optionally filtered by education/year/department."""
    query = db.query(Subject)
    if education:
        query = query.filter(Subject.education == education)
    if year:
        query = query.filter(Subject.year == year)
    if department:
        query = query.filter(Subject.department == department)

    subjects = query.all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "department": s.department,
            "education": s.education,
            "year": s.year,
        }
        for s in subjects
    ]


@router.get("/departments")
def get_departments(education: str = ""):
    """Return available departments for a given education level."""
    dept_map = {
        "B.Tech": ["Computer Science", "Information Technology", "Electronics", "Mechanical"],
        "B.Sc": ["Computer Science", "Physics", "Chemistry", "Mathematics"],
        "BCA": ["Computer Science", "Information Technology"],
        "MCA": ["Computer Science", "Information Technology", "Data Science"],
    }
    if education:
        return {"departments": dept_map.get(education, [])}
    return {"departments": dept_map}
