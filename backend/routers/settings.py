# -*- encoding: utf-8 -*-
"""
设置管理路由

提供应用设置的查询和保存接口。
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, Field

from ..constants import ARIA2_DEFAULTS, DEFAULT_SETTINGS, DOWNLOAD_DEFAULTS
from ..settings import settings

router = APIRouter(prefix="/api/settings", tags=["设置管理"])


# ============================================================================
# 请求/响应模型
# ============================================================================


class SettingsUpdate(BaseModel):
    """设置更新请求模型（支持部分更新）"""

    cookie: Optional[str] = None
    userAgent: Optional[str] = None
    downloadPath: Optional[str] = None
    maxRetries: Optional[int] = Field(None, ge=0, le=10)
    maxConcurrency: Optional[int] = Field(None, ge=1, le=10)
    windowWidth: Optional[int] = Field(None, ge=800, le=3840)
    windowHeight: Optional[int] = Field(None, ge=600, le=2160)
    enableIncrementalFetch: Optional[bool] = None
    aria2Host: Optional[str] = None
    aria2Port: Optional[int] = Field(None, ge=1, le=65535)
    aria2Secret: Optional[str] = None


class SettingsResponse(BaseModel):
    """设置响应模型"""

    cookie: str = ""
    userAgent: str = ""
    downloadPath: str = ""
    maxRetries: int = DOWNLOAD_DEFAULTS["MAX_RETRIES"]
    maxConcurrency: int = DOWNLOAD_DEFAULTS["MAX_CONCURRENCY"]
    windowWidth: int = DEFAULT_SETTINGS["windowWidth"]
    windowHeight: int = DEFAULT_SETTINGS["windowHeight"]
    enableIncrementalFetch: bool = True
    aria2Host: str = ARIA2_DEFAULTS["HOST"]
    aria2Port: int = ARIA2_DEFAULTS["PORT"]
    aria2Secret: str = ""


class FirstRunResponse(BaseModel):
    """首次运行检查响应"""

    is_first_run: bool


class SaveResponse(BaseModel):
    """保存响应"""

    status: str
    message: str


# ============================================================================
# 路由定义
# ============================================================================


@router.get("", response_model=SettingsResponse)
def get_settings() -> Dict[str, Any]:
    """获取当前应用设置"""
    return settings.data


@router.post("", response_model=SaveResponse)
def save_settings(request: SettingsUpdate) -> Dict[str, str]:
    """
    保存应用设置（支持部分更新）

    只需要提供要更新的字段，未提供的字段保持不变。
    """
    try:
        # 过滤掉 None 值，只传递需要更新的字段
        settings_update = request.model_dump(exclude_none=True)

        if not settings_update:
            return {"status": "success", "message": "没有需要更新的设置"}

        settings.save(settings_update)
        return {"status": "success", "message": "设置已保存"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"保存设置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/first-run", response_model=FirstRunResponse)
def is_first_run_check() -> Dict[str, bool]:
    """检查是否首次运行"""
    return {"is_first_run": settings.is_first_run}
