"""
系统工具路由

提供系统相关功能接口，如剪贴板访问和打开外部链接。
"""

import webbrowser
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel

router = APIRouter(prefix="/api/system", tags=["系统工具"])


# ============================================================================
# 请求/响应模型
# ============================================================================


class OpenUrlRequest(BaseModel):
    """打开 URL 请求"""

    url: str


class ClipboardResponse(BaseModel):
    """剪贴板响应"""

    text: str


class OpenUrlResponse(BaseModel):
    """打开 URL 响应"""

    status: str
    message: str


# ============================================================================
# 路由定义
# ============================================================================


@router.get("/clipboard", response_model=ClipboardResponse)
def get_clipboard_text() -> Dict[str, str]:
    """
    获取系统剪贴板内容

    返回剪贴板中的文本内容。
    """
    try:
        import pyperclip

        text = pyperclip.paste()
        if text:
            cleaned_text = text.strip()
            logger.debug(f"读取剪贴板成功，长度: {len(cleaned_text)}")
            return {"text": cleaned_text}
        return {"text": ""}

    except ImportError:
        logger.warning("pyperclip 未安装，无法读取剪贴板")
        return {"text": ""}
    except Exception as e:
        logger.warning(f"读取剪贴板失败: {e}")
        return {"text": ""}


@router.post("/open-url", response_model=OpenUrlResponse)
def open_url(request: OpenUrlRequest) -> Dict[str, str]:
    """
    打开外部链接

    使用系统默认浏览器打开指定的 URL。
    """
    url = request.url

    if not url:
        raise HTTPException(status_code=400, detail="URL 不能为空")

    logger.info(f"打开 URL: {url}")

    try:
        webbrowser.open(url)
        logger.debug(f"URL 已打开: {url}")
        return {"status": "success", "message": "URL 已打开"}
    except Exception as e:
        logger.error(f"打开 URL 失败: {e}")
        raise HTTPException(status_code=500, detail=f"打开 URL 失败: {e}")
