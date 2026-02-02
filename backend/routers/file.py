"""
文件操作路由

提供文件夹打开、文件存在检查、配置文件读取和媒体文件流接口。
"""

import glob
import mimetypes
import os
import platform
import subprocess
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from loguru import logger
from pydantic import BaseModel

from ..constants import DOWNLOAD_DIR
from ..settings import settings

router = APIRouter(prefix="/api/file", tags=["文件操作"])

# 允许的媒体文件扩展名
ALLOWED_MEDIA_EXTENSIONS = {".mp4", ".webm", ".jpg", ".jpeg", ".png", ".gif", ".webp"}


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


class FindLocalFileResponse(BaseModel):
    """查找本地文件响应"""

    found: bool
    video_path: Optional[str] = None
    images: Optional[list[str]] = None


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


@router.get("/find-local/{work_id}", response_model=FindLocalFileResponse)
def find_local_file(work_id: str) -> Dict[str, Any]:
    """
    根据作品 ID 查找本地已下载的文件

    - work_id: 作品 ID

    返回:
    - found: 是否找到
    - video_path: 视频文件的相对路径（相对于下载目录）
    - images: 图片文件的相对路径列表
    """
    try:
        download_dir = os.path.abspath(settings.get("downloadPath", DOWNLOAD_DIR))

        # 查找视频文件
        # 1. 直接在下载目录: {work_id}_*.mp4
        # 2. 在子目录中: aweme_{work_id}/{work_id}_*.mp4 或 {work_id}_*/{work_id}_*.mp4
        video_patterns = [
            os.path.join(download_dir, f"{work_id}_*.mp4"),
            os.path.join(download_dir, f"aweme_{work_id}", f"{work_id}_*.mp4"),
            os.path.join(download_dir, f"{work_id}_*", f"{work_id}_*.mp4"),
        ]

        for pattern in video_patterns:
            video_files = glob.glob(pattern)
            if video_files:
                rel_path = os.path.relpath(video_files[0], download_dir)
                return {"found": True, "video_path": rel_path, "images": None}

        # 查找图集文件
        # 1. 在子目录中: aweme_{work_id}/*.jpg 或 {work_id}_*/*.jpg
        image_dir_patterns = [
            os.path.join(download_dir, f"aweme_{work_id}"),
            os.path.join(download_dir, f"{work_id}_*"),
        ]

        for pattern in image_dir_patterns:
            dirs = glob.glob(pattern)
            for dir_path in dirs:
                if os.path.isdir(dir_path):
                    images = []
                    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
                        images.extend(glob.glob(os.path.join(dir_path, f"*{ext}")))

                    if images:
                        images.sort()
                        rel_paths = [
                            os.path.relpath(img, download_dir) for img in images
                        ]
                        return {"found": True, "video_path": None, "images": rel_paths}

        return {"found": False, "video_path": None, "images": None}

    except Exception as e:
        logger.error(f"查找本地文件失败: {e}")
        return {"found": False, "video_path": None, "images": None}


@router.get("/media/{file_path:path}")
def serve_media(file_path: str):
    """
    提供媒体文件流服务

    - file_path: 相对于下载目录的文件路径

    支持 Range 请求，可用于视频播放进度拖动。
    """
    try:
        download_dir = os.path.abspath(settings.get("downloadPath", DOWNLOAD_DIR))
        abs_path = os.path.abspath(os.path.join(download_dir, file_path))

        # 安全检查：确保路径在下载目录内
        if not abs_path.startswith(download_dir):
            logger.warning(f"非法路径访问: {file_path}")
            raise HTTPException(status_code=403, detail="禁止访问")

        # 检查文件是否存在
        if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
            raise HTTPException(status_code=404, detail="文件不存在")

        # 检查文件扩展名
        ext = os.path.splitext(abs_path)[1].lower()
        if ext not in ALLOWED_MEDIA_EXTENSIONS:
            raise HTTPException(status_code=403, detail="不支持的文件类型")

        # 获取 MIME 类型
        content_type = mimetypes.guess_type(abs_path)[0] or "application/octet-stream"

        # 使用 FileResponse，自动支持 Range 请求
        return FileResponse(
            path=abs_path,
            media_type=content_type,
            filename=os.path.basename(abs_path),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"提供媒体文件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
