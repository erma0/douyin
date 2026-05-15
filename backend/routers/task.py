"""
任务管理路由

提供采集任务的启动、状态查询和结果获取接口。
"""

import os
import threading
import time
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel

from ..constants import DOWNLOAD_DIR
from ..lib.cookies import CookieManager
from ..lib.exceptions import VerifyCheckError
from ..settings import settings
from ..sse import SSEEventType, sse
from ..state import state

router = APIRouter(prefix="/api/task", tags=["任务管理"])


# ============================================================================
# 请求/响应模型
# ============================================================================


class StartTaskRequest(BaseModel):
    """启动采集任务的请求模型"""

    type: str
    target: str
    limit: int = 0
    filters: dict[str, str] | None = None


class TaskResponse(BaseModel):
    """任务响应模型"""

    task_id: str
    status: str


class TaskStatus(BaseModel):
    """任务状态模型"""

    id: str
    type: str
    target: str
    status: str
    progress: int
    result_count: int
    error: str | None
    created_at: float
    updated_at: float


class CancelTaskRequest(BaseModel):
    """取消采集任务的请求模型"""

    task_id: str


# ============================================================================
# 路由定义
# ============================================================================


@router.post("/start", response_model=TaskResponse)
def start_task(request: StartTaskRequest) -> dict[str, Any]:
    """
    启动采集任务

    - type: 任务类型（user/post/search/music等）
    - target: 目标链接或关键词
    - limit: 采集数量限制（0表示不限制）
    - filters: 筛选条件（可选）
    """

    # 输入验证
    if not request.type:
        raise HTTPException(status_code=400, detail="任务类型不能为空")

    if not isinstance(request.target, str):
        raise HTTPException(status_code=400, detail="目标必须是字符串")

    if request.limit < 0:
        raise HTTPException(status_code=400, detail="数量限制不能为负数")

    # 生成唯一的任务ID
    task_id = f"task_{uuid.uuid4().hex[:8]}"

    state.init_task(task_id, {
        "id": task_id,
        "type": request.type,
        "target": request.target,
        "limit": request.limit,
        "filters": request.filters or {},
        "status": "running",
        "progress": 0,
        "result_count": 0,
        "error": None,
        "created_at": time.time(),
        "updated_at": time.time(),
    })

    # 注册取消信号事件
    cancel_event = state.register_cancel_event(task_id)

    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info(f"📥 开始采集任务")
    logger.info(f"  任务ID: {task_id}")
    logger.info(f"  类型: {request.type}")
    logger.info(f"  目标: {request.target}")
    logger.info(f"  数量限制: {'不限' if request.limit == 0 else f'{request.limit}条'}")
    if request.filters:
        logger.info(f"  筛选条件: {request.filters}")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # 在后台线程中执行采集任务
    def run_task():
        _execute_task(
            task_id=task_id,
            task_type=request.type,
            target=request.target,
            limit=request.limit,
            filters=request.filters,
            cancel_event=cancel_event,
        )

    task_thread = threading.Thread(target=run_task, daemon=True)
    task_thread.start()

    return {"task_id": task_id, "status": "running"}


@router.post("/cancel", response_model=TaskResponse)
def cancel_task(request: CancelTaskRequest) -> dict[str, Any]:
    """
    取消采集任务

    - task_id: 要取消的任务ID
    """
    task_id = request.task_id

    if not state.task_exists(task_id):
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

    task_info = state.get_task_status(task_id)[0]

    if task_info["status"] == "cancelling":
        return {"task_id": task_id, "status": "cancelling"}

    if task_info["status"] not in ("running",):
        raise HTTPException(status_code=400, detail=f"任务当前状态为 {task_info['status']}，无法取消")

    if not state.request_cancel(task_id):
        raise HTTPException(status_code=500, detail="取消信号发送失败")

    state.set_task_status(task_id, status="cancelling", updated_at=time.time())

    logger.info(f"⏹ 发送取消信号: 任务 {task_id}")

    return {"task_id": task_id, "status": "cancelling"}


@router.get("/status")
def get_task_status(task_id: str | None = None) -> list[dict[str, Any]]:
    """
    获取任务状态

    - task_id: 任务ID（可选，不提供则返回所有任务状态）
    """

    if task_id:
        return state.get_task_status(task_id)
    else:
        return state.get_task_status()


@router.get("/results/{task_id}")
def get_task_results(task_id: str) -> list[dict[str, Any]]:
    """
    获取任务的采集结果

    - task_id: 任务ID
    """

    if not state.task_exists(task_id):
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

    return state.get_task_results(task_id)


# ============================================================================
# 内部函数
# ============================================================================


def _execute_task(
    task_id: str,
    task_type: str,
    target: str,
    limit: int,
    filters: dict[str, str] | None,
    cancel_event: threading.Event = None,
) -> None:
    """执行采集任务（在后台线程中运行）"""

    try:
        from ..lib.douyin import Douyin

        cookie = settings.get("cookie", "").strip()

        if not CookieManager.validate_cookie(cookie):
            logger.error("✗ Cookie验证失败")
            raise Exception("Cookie无效或已过期，请在设置中更新Cookie")

        logger.info("✓ Cookie验证通过，开始采集...")

        seen_ids: set[str] = set()

        def handle_new_items(new_items, item_type):
            if not new_items:
                return

            unique_items = []
            for item in new_items:
                item_id = str(item.get("id", ""))
                if item_id and item_id not in seen_ids:
                    seen_ids.add(item_id)
                    unique_items.append(item)

            if not unique_items:
                logger.warning(f"所有数据已存在，跳过 {len(new_items)} 条重复数据")
                return

            logger.debug(f"收到 {len(unique_items)} 条新结果，开始转换...")

            works = _convert_douyin_results(unique_items, item_type)

            if not works:
                logger.warning(f"转换后没有有效数据！原始数据: {len(unique_items)} 条")
                return

            count = state.add_results(task_id, works)

            logger.info(
                f"推送 SSE: {len(works)} 条新结果，累计 {count} 条"
            )
            sse.broadcast_sync(
                SSEEventType.TASK_RESULT,
                {
                    "task_id": task_id,
                    "data": works,
                    "total": count,
                },
            )

        with Douyin(
            target=target,
            limit=int(limit) if limit > 0 else 0,
            type=task_type,
            down_path=settings.get("downloadPath", DOWNLOAD_DIR),
            cookie=cookie,
            user_agent=settings.get("userAgent", ""),
            filters=filters or {},
            on_new_items=handle_new_items,
            enable_download_title=settings.get("enableDownloadTitle", False),
            enable_download_cover=settings.get("enableDownloadCover", False),
            cancel_event=cancel_event,
        ) as douyin:

            logger.info("🚀 正在采集数据...")
            douyin.run()

            detected_type = douyin.type

            state.set_aria2_config(task_id, douyin.aria2_conf)

            is_cancelled = cancel_event is not None and cancel_event.is_set()

            if is_cancelled:
                state.set_task_status(task_id, status="cancelled", updated_at=time.time())

                result_count = len(state.get_task_results(task_id))
                logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                logger.info(
                    f"⏹ 任务已取消: 已采集 {result_count} 条数据"
                )
                logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

                sse.broadcast_sync(
                    SSEEventType.TASK_STATUS,
                    {
                        "task_id": task_id,
                        "status": "cancelled",
                        "detected_type": detected_type,
                        "total": result_count,
                    },
                )
            else:
                result_count = len(state.get_task_results(task_id))
                state.set_task_status(task_id, status="completed", progress=100, updated_at=time.time())

                logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                logger.success(
                    f"✓ 任务完成: 成功采集 {result_count} 条数据"
                )
                logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

                is_incremental = (
                    detected_type == "post"
                    and result_count == 0
                    and len(douyin.results_old) > 0
                    and douyin._has_received_data
                )
                sse.broadcast_sync(
                    SSEEventType.TASK_STATUS,
                    {
                        "task_id": task_id,
                        "status": "completed",
                        "detected_type": detected_type,
                        "total": result_count,
                        "is_incremental": is_incremental,
                    },
                )

    except VerifyCheckError as e:
        state.set_task_status(task_id, status="error", error="触发验证码，请完成验证后再继续", updated_at=time.time())

        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.error(f"✗ 检测到验证码: {e}")
        logger.error(f"  请在浏览器中打开抖音完成验证后再继续")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        sse.broadcast_sync(
            SSEEventType.TASK_ERROR,
            {
                "task_id": task_id,
                "error": "触发验证码，请完成验证后再继续",
            },
        )
    except Exception as e:
        state.set_task_status(task_id, status="error", error=str(e), updated_at=time.time())

        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.error(f"✗ 任务失败: {str(e)}")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        sse.broadcast_sync(
            SSEEventType.TASK_ERROR,
            {
                "task_id": task_id,
                "error": str(e),
            },
        )
    finally:
        state.cleanup_cancel_event(task_id)


def _convert_douyin_results(
    results: list[dict[str, Any]], task_type: str
) -> list[dict[str, Any]]:
    """将爬虫结果转换为前端期望的格式"""
    works = []

    for item in results:
        try:
            aweme_type = item.get("type", 4)
            is_image = aweme_type == 68

            work = {
                "id": str(item.get("id", "")),
                "desc": item.get("desc", ""),
                "author": {
                    "nickname": item.get("author_nickname", "未知用户"),
                    "avatar": item.get("author_avatar", ""),
                    "uid": item.get("author_uid", ""),
                    "unique_id": item.get("author_unique_id", ""),
                    "short_id": item.get("author_short_id", ""),
                },
                "type": "image" if is_image else "video",
                "cover": item.get("cover", ""),
                "stats": {
                    "digg_count": item.get("digg_count", 0),
                    "comment_count": item.get("comment_count", 0),
                    "share_count": item.get("share_count", 0),
                },
                "create_time": time.strftime(
                    "%Y-%m-%d", time.localtime(item.get("time", time.time()))
                ),
            }

            # 添加视频时长
            if not is_image and item.get("duration"):
                work["duration"] = item.get("duration")

            # 添加下载地址
            download_addr = item.get("download_addr")
            if isinstance(download_addr, list):
                work["images"] = download_addr
            elif isinstance(download_addr, str):
                work["videoUrl"] = download_addr

            # 添加音乐信息
            if item.get("music_title"):
                work["music"] = {
                    "id": "",
                    "title": item.get("music_title", ""),
                    "url": item.get("music_url", ""),
                    "cover": "",
                }

            works.append(work)
        except Exception as e:
            logger.warning(f"转换数据失败: {e}")
            continue

    return works
