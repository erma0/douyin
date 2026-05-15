"""
SSE 事件管理模块

提供 Server-Sent Events 功能，用于向前端推送实时数据：
- 采集任务结果（task_result）
- 任务状态变化（task_status）
- 任务错误（task_error）
- 日志消息（log）
"""

import asyncio
import json
import threading
from typing import Any, AsyncGenerator

from loguru import logger


# SSE 事件类型常量
class SSEEventType:
    """SSE 事件类型"""

    TASK_RESULT = "task_result"  # 采集结果
    TASK_STATUS = "task_status"  # 任务状态变化
    TASK_ERROR = "task_error"  # 任务错误
    LOG = "log"  # 日志消息
    PING = "ping"  # 心跳


SSE_HEARTBEAT_INTERVAL = 30.0


class SSEManager:
    """
    SSE 事件管理器

    管理所有 SSE 客户端连接，并广播事件到所有客户端。
    """

    def __init__(self, heartbeat_interval: float = SSE_HEARTBEAT_INTERVAL) -> None:
        self._clients: list[asyncio.Queue] = []
        self._sync_lock = threading.Lock()
        self._heartbeat_interval = heartbeat_interval

    async def connect(self) -> AsyncGenerator[str, None]:
        """
        创建新的 SSE 连接

        Yields:
            SSE 格式的消息字符串
        """
        queue: asyncio.Queue = asyncio.Queue()

        with self._sync_lock:
            self._clients.append(queue)
            client_count = len(self._clients)

        logger.info(f"[SSE] 新客户端连接，当前连接数: {client_count}")

        try:
            # 发送初始 ping
            yield ": ping\n\n"

            while True:
                try:
                    # 等待消息，超时后发送心跳
                    message = await asyncio.wait_for(queue.get(), timeout=self._heartbeat_interval)
                    yield message
                except asyncio.TimeoutError:
                    # 发送心跳保持连接
                    yield ": heartbeat\n\n"
        finally:
            with self._sync_lock:
                if queue in self._clients:
                    self._clients.remove(queue)
                    client_count = len(self._clients)
            logger.info(f"[SSE] 客户端断开，剩余连接数: {client_count}")

    async def broadcast(self, event_type: str, data: dict[str, Any]) -> None:
        if not self._clients:
            return

        message = self._format_sse_message(event_type, data)

        with self._sync_lock:
            clients_copy = list(self._clients)

        for queue in clients_copy:
            try:
                await queue.put(message)
            except asyncio.QueueFull:
                logger.warning(f"[SSE] 队列已满，丢弃消息: {event_type}")
            except Exception as e:
                logger.warning(f"[SSE] 发送消息失败: {e}")

    def broadcast_sync(self, event_type: str, data: dict[str, Any]) -> None:
        if not self._clients:
            return

        message = self._format_sse_message(event_type, data)

        with self._sync_lock:
            clients_snapshot = list(self._clients)
            client_count = len(clients_snapshot)

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        sent_count = 0
        for queue in clients_snapshot:
            try:
                if loop:
                    loop.call_soon_threadsafe(queue.put_nowait, message)
                else:
                    logger.warning(f"[SSE] 无事件循环，无法发送消息: {event_type}")
                    continue
                sent_count += 1
            except asyncio.QueueFull:
                logger.warning(f"[SSE] 队列已满，丢弃消息: {event_type}")
            except Exception as e:
                logger.warning(f"[SSE] 放入队列失败: {e}")

        logger.debug(f"[SSE] broadcast_sync: 发送到 {sent_count}/{client_count} 个客户端")

    def _format_sse_message(self, event_type: str, data: dict[str, Any]) -> str:
        """
        格式化 SSE 消息

        Args:
            event_type: 事件类型
            data: 事件数据

        Returns:
            SSE 格式的消息字符串
        """
        json_data = json.dumps(data, ensure_ascii=False)
        return f"event: {event_type}\ndata: {json_data}\n\n"

    @property
    def client_count(self) -> int:
        with self._sync_lock:
            return len(self._clients)

    # 便捷方法
    async def send_task_result(
        self, task_id: str, data: list[dict[str, Any]], total: int
    ) -> None:
        """发送采集结果事件"""
        await self.broadcast(
            SSEEventType.TASK_RESULT,
            {
                "task_id": task_id,
                "data": data,
                "total": total,
            },
        )

    async def send_task_status(
        self, task_id: str, status: str, progress: int = 0, result_count: int = 0
    ) -> None:
        """发送任务状态事件"""
        await self.broadcast(
            SSEEventType.TASK_STATUS,
            {
                "task_id": task_id,
                "status": status,
                "progress": progress,
                "result_count": result_count,
            },
        )

    async def send_task_error(self, task_id: str, error: str) -> None:
        """发送任务错误事件"""
        await self.broadcast(
            SSEEventType.TASK_ERROR,
            {
                "task_id": task_id,
                "error": error,
            },
        )

    async def send_log(
        self, log_id: str, timestamp: str, level: str, message: str
    ) -> None:
        """发送日志事件"""
        await self.broadcast(
            SSEEventType.LOG,
            {
                "id": log_id,
                "timestamp": timestamp,
                "level": level,
                "message": message,
            },
        )


# 全局 SSE 管理器实例
sse = SSEManager()
