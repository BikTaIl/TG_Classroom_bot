from .admin_router import admin_router
from .common_router import common_router


__all__ = [
    "admin_router"
]

routers = [
    admin_router,
    common_router
]