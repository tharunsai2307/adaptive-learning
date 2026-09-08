from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.subject import Subject
from ..models.topic import Topic
from ..models.user import User
from ..auth import get_current_user

router = APIRouter(prefix="/api/subjects", tags=["subjects"])

DEPARTMENT_MAP = {
    "B.Tech": ["Computer Science", "Information Technology", "Electronics", "Mechanical"],
    "B.Sc": ["Computer Science", "Physics", "Chemistry", "Mathematics"],
    "BCA": ["Computer Science", "Information Technology"],
    "MCA": ["Computer Science", "Information Technology", "Data Science"],
}

EDUCATIONS = ["B.Tech", "B.Sc", "BCA", "MCA"]
YEARS = ["1st Year", "2nd Year", "3rd Year", "4th Year"]


@router.get("/")
def list_subjects(
    education: str = "",
    year: str = "",
    department: str = "",
    include_empty: bool = False,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List subjects, optionally filtered by education / year / department."""
    query = db.query(Subject)
    if education:
        query = query.filter(Subject.education == education)
    if year:
        query = query.filter(Subject.year == year)
    if department:
        query = query.filter(Subject.department == department)

    out = []
    for s in query.order_by(Subject.name).all():
        topic_count = (
            db.query(Topic).filter(Topic.subject_id == s.id).count()
        )
        # A subject with no seeded topics would lead to an empty learning
        # path, so it is not offered for selection.
        if topic_count == 0 and not include_empty:
            continue
        out.append(
            {
                "id": s.id,
                "name": s.name,
                "department": s.department,
                "education": s.education,
                "year": s.year,
                "topic_count": topic_count,
            }
        )
    return out


@router.get("/departments")
def get_departments(education: str = ""):
    """Return available departments for a given education level."""
    if education:
        return {"departments": DEPARTMENT_MAP.get(education, [])}
    return {"departments": DEPARTMENT_MAP}


@router.get("/options")
def get_options():
    """Return every selectable education / year / department option."""
    return {
        "educations": EDUCATIONS,
        "years": YEARS,
        "departments": DEPARTMENT_MAP,
    }
