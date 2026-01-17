"""
Aria2 管理路由

提供 Aria2 下载服务的配置、启动和状态查询接口。
"""

import os
import threading
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel

from ..constants import ARIA2_DEFAULTS
from ..settings import settings
from ..state import state

router = APIRouter(prefix="/api/aria2", tags=["Aria2管理"])


# ============================================================================
# 响应模型
# ============================================================================


class Aria2ConfigResponse(BaseModel):
    """Aria2 配置响应"""

    host: str
    port: int
    secret: str


class Aria2StatusResponse(BaseModel):
    """Aria2 状态响应"""

    connected: bool


class Aria2ConfigPathResponse(BaseModel):
    """Aria2 配置文件路径响应"""

    config_path: str


class StartResponse(BaseModel):
    """启动响应"""

    status: str
    message: str


# ============================================================================
# 路由定义
# ============================================================================


@router.get("/config", response_model=Aria2ConfigResponse)
def get_aria2_config() -> Dict[str, Any]:
    """
    获取 Aria2 配置信息

    返回 Aria2 RPC 服务的连接配置。
    """

    user_secret = settings.get("aria2Secret", ARIA2_DEFAULTS["SECRET"])
    default_secret = ARIA2_DEFAULTS["SECRET"] if not user_secret else user_secret

    return {
        "host": settings.get("aria2Host", ARIA2_DEFAULTS["HOST"]),
        "port": settings.get("aria2Port", ARIA2_DEFAULTS["PORT"]),
        "secret": default_secret,
    }


@router.get("/status", response_model=Aria2StatusResponse)
def get_aria2_status() -> Dict[str, bool]:
    """
    获取 Aria2 连接状态

    检查 Aria2 服务是否可用。
    """

    is_connected = False
    if state.aria2_manager:
        try:
            is_connected = state.aria2_manager._check_connection()
        except Exception:
            pass

    return {"connected": is_connected}


@router.post("/start", response_model=StartResponse)
def start_aria2() -> Dict[str, str]:
    """
    启动 Aria2 服务

    在后台线程中启动 Aria2 服务。
    """

    if not state.aria2_manager:
        raise HTTPException(status_code=500, detail="Aria2 管理器未初始化")

    def start_aria2_async():
        try:
            logger.info("🚀 后台启动 Aria2 服务...")
            state.aria2_manager.start_aria2_server()
        except Exception as e:
            logger.warning(f"⚠ Aria2 启动失败: {e}")

    # 在后台线程中启动
    threading.Thread(target=start_aria2_async, daemon=True).start()

    return {"status": "success", "message": "Aria2 服务启动中"}


@router.get("/config-path", response_model=Aria2ConfigPathResponse)
def get_aria2_config_path(task_id: Optional[str] = None) -> Dict[str, str]:
    """
    获取已完成任务的 aria2 配置文件路径

    - task_id: 任务ID（可选，不提供则使用最新的任务）
    """

    try:
        # 如果没有指定 task_id，使用最新的任务
        if task_id is None:
            if state.aria2_config_paths:
                latest_task_id = max(state.aria2_config_paths.keys())
                config_path = state.aria2_config_paths[latest_task_id]
            else:
                # 从任务状态中查找
                completed_tasks = [
                    tid
                    for tid, info in state.task_status.items()
                    if info.get("status") == "completed" and "aria2_conf" in info
                ]

                if completed_tasks:
                    latest_task_id = max(completed_tasks)
                    config_path = state.task_status[latest_task_id]["aria2_conf"]
                    state.aria2_config_paths[latest_task_id] = config_path
                else:
                    raise HTTPException(
                        status_code=404,
                        detail="没有已完成的采集任务，请先完成一次采集后再使用批量下载功能",
                    )
        else:
            # 指定了 task_id
            if task_id in state.aria2_config_paths:
                config_path = state.aria2_config_paths[task_id]
            elif task_id in state.task_status:
                task_info = state.task_status[task_id]
                if task_info["status"] != "completed":
                    raise HTTPException(
                        status_code=400, detail=f"任务 {task_id} 尚未完成"
                    )
                if "aria2_conf" not in task_info:
                    raise HTTPException(
                        status_code=404, detail=f"任务 {task_id} 缺少配置文件路径"
                    )
                config_path = task_info["aria2_conf"]
                state.aria2_config_paths[task_id] = config_path
            else:
                raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

        # 检查文件是否存在
        if not os.path.exists(config_path):
            raise HTTPException(
                status_code=404, detail=f"配置文件不存在: {config_path}"
            )

        return {"config_path": config_path}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取配置文件路径失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
