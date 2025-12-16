from .admin_router import admin_router
from .common_router import common_router
from .teacher_router import teacher_router
from .assistant_router import assistant_router
from .student_router import student_router


__all__ = [
    "admin_router",
    "common_router",
    "teacher_router",
    "assistant_router",
    "student_router"
]

routers = [
    admin_router,
    common_router,
    teacher_router,
    assistant_router,
    student_router
]