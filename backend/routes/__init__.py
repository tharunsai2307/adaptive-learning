from .auth import router as auth_router
from .profile import router as profile_router
from .subjects import router as subjects_router
from .topics import router as topics_router
from .quiz import router as quiz_router
from .tutor import router as tutor_router
from .dashboard import router as dashboard_router
from .qlearning import router as qlearning_router

all_routers = [
    auth_router,
    profile_router,
    subjects_router,
    topics_router,
    quiz_router,
    tutor_router,
    dashboard_router,
    qlearning_router,
]
