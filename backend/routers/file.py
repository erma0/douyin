"""
文件操作路由

提供文件夹打开、文件存在检查和配置文件读取接口。
"""

import os
import platform
import subprocess
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel

from ..constants import DOWNLOAD_DIR
from ..settings import settings

router = APIRouter(prefix="/api/file", tags=["文件操作"])


# ============================================================================
# 请求/响应模型
# ============================================================================


class OpenFolderRequest(BaseModel):
    """打开文件夹请求"""

    folder_path: str


class CheckFileExistsRequest(BaseModel):
    """检查文件存在请求"""

    file_path: str


class ReadConfigFileRequest(BaseModel):
    """读取配置文件请求"""

    file_path: str


class OpenFolderResponse(BaseModel):
    """打开文件夹响应"""

    success: bool


class CheckFileExistsResponse(BaseModel):
    """检查文件存在响应"""

    exists: bool


class ReadConfigFileResponse(BaseModel):
    """读取配置文件响应"""

    content: str


# ============================================================================
# 路由定义
# ============================================================================


@router.post("/open-folder", response_model=OpenFolderResponse)
def open_folder(request: OpenFolderRequest) -> Dict[str, bool]:
    """
    打开文件夹

    在系统文件管理器中打开指定的文件夹。
    """
    folder_path = request.folder_path
    logger.info(f"打开文件夹: {folder_path}")

    try:
        # 确保路径存在
        if not os.path.exists(folder_path):
            logger.error(f"文件夹不存在: {folder_path}")
            return {"success": False}

        # 如果是文件路径，获取其所在目录
        if os.path.isfile(folder_path):
            folder_path = os.path.dirname(folder_path)

        system = platform.system()

        if system == "Windows":
            # Windows: 使用 os.startfile
            normalized_path = os.path.abspath(folder_path).replace("/", "\\")
            os.startfile(normalized_path)
        elif system == "Darwin":
            # macOS: 使用 open
            subprocess.Popen(["open", folder_path])
        else:
            # Linux: 使用 xdg-open
            subprocess.Popen(["xdg-open", folder_path])

        logger.info(f"✓ 已打开文件夹: {folder_path}")
        return {"success": True}

    except Exception as e:
        logger.error(f"✗ 打开文件夹失败: {e}")
        return {"success": False}


@router.post("/check-exists", response_model=CheckFileExistsResponse)
def check_file_exists(request: CheckFileExistsRequest) -> Dict[str, bool]:
    """
    检查文件是否存在

    - file_path: 文件路径
    """

    file_path = request.file_path

    try:
        # 安全检查：确保文件路径在下载目录内
        download_dir = os.path.abspath(settings.get("downloadPath", DOWNLOAD_DIR))
        abs_path = os.path.abspath(file_path)

        if not abs_path.startswith(download_dir):
            return {"exists": False}

        return {"exists": os.path.exists(abs_path) and os.path.isfile(abs_path)}

    except Exception as e:
        logger.error(f"检查文件存在失败: {e}")
        return {"exists": False}


@router.post("/read-config", response_model=ReadConfigFileResponse)
def read_config_file(request: ReadConfigFileRequest) -> Dict[str, str]:
    """
    读取配置文件内容

    - file_path: 配置文件路径（必须在下载目录内，且为 .txt 文件）
    """

    file_path = request.file_path

    try:
        logger.info(f"开始读取配置文件: {file_path}")

        # 安全检查：确保文件路径在下载目录内
        download_dir = os.path.abspath(settings.get("downloadPath", DOWNLOAD_DIR))
        abs_path = os.path.abspath(file_path)

        if not abs_path.startswith(download_dir) or not abs_path.endswith(".txt"):
            logger.error(f"文件路径不安全: {abs_path}")
            raise HTTPException(status_code=400, detail="文件路径不安全")

        if not os.path.exists(abs_path):
            logger.error(f"配置文件不存在: {abs_path}")
            raise HTTPException(status_code=404, detail=f"配置文件不存在: {abs_path}")

        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()
            logger.info(f"配置文件读取成功，内容长度: {len(content)} 字符")
            return {"content": content}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"读取配置文件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
