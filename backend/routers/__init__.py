"""
路由模块

包含所有 FastAPI 路由定义。
"""

from .aria2 import router as aria2_router
from .file import router as file_router
from .settings import router as settings_router
from .system import router as system_router
from .task import router as task_router

__all__ = [
    "task_router",
    "settings_router",
    "aria2_router",
    "file_router",
    "system_router",
]
