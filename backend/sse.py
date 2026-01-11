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
from typing import Any, AsyncGenerator, Dict, List, Optional

from loguru import logger


# SSE 事件类型常量
class SSEEventType:
    """SSE 事件类型"""

    TASK_RESULT = "task_result"  # 采集结果
    TASK_STATUS = "task_status"  # 任务状态变化
    TASK_ERROR = "task_error"  # 任务错误
    LOG = "log"  # 日志消息
    PING = "ping"  # 心跳


class SSEManager:
    """
    SSE 事件管理器

    管理所有 SSE 客户端连接，并广播事件到所有客户端。
    """

    def __init__(self) -> None:
        """初始化 SSE 管理器"""
        self._clients: List[asyncio.Queue] = []
        self._lock = asyncio.Lock()

    async def connect(self) -> AsyncGenerator[str, None]:
        """
        创建新的 SSE 连接

        Yields:
            SSE 格式的消息字符串
        """
        queue: asyncio.Queue = asyncio.Queue()

        async with self._lock:
            self._clients.append(queue)
            client_count = len(self._clients)

        logger.info(f"[SSE] 新客户端连接，当前连接数: {client_count}")

        try:
            # 发送初始 ping
            yield ": ping\n\n"

            while True:
                try:
                    # 等待消息，超时后发送心跳
                    message = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield message
                except asyncio.TimeoutError:
                    # 发送心跳保持连接
                    yield ": heartbeat\n\n"
        finally:
            # 客户端断开时清理
            async with self._lock:
                if queue in self._clients:
                    self._clients.remove(queue)
                    client_count = len(self._clients)
            logger.info(f"[SSE] 客户端断开，剩余连接数: {client_count}")

    async def broadcast(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        广播事件到所有连接的客户端

        Args:
            event_type: 事件类型（task_result、task_status、task_error、log）
            data: 事件数据
        """
        if not self._clients:
            return

        # 构建 SSE 消息格式
        message = self._format_sse_message(event_type, data)

        async with self._lock:
            clients_copy = self._clients.copy()

        # 广播到所有客户端
        for queue in clients_copy:
            try:
                await queue.put(message)
            except Exception as e:
                logger.warning(f"[SSE] 发送消息失败: {e}")

    def broadcast_sync(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        同步版本的广播方法（供非异步代码调用）

        Args:
            event_type: 事件类型
            data: 事件数据
        """
        if not self._clients:
            return

        message = self._format_sse_message(event_type, data)
        client_count = len(self._clients)

        # 直接放入队列（后台线程没有事件循环）
        sent_count = 0
        for queue in self._clients:
            try:
                queue.put_nowait(message)
                sent_count += 1
            except Exception as e:
                logger.warning(f"[SSE] 放入队列失败: {e}")

        logger.debug(f"[SSE] broadcast_sync: 发送到 {sent_count}/{client_count} 个客户端")

    async def _broadcast_message(self, message: str) -> None:
        """内部方法：广播消息"""
        async with self._lock:
            clients_copy = self._clients.copy()

        for queue in clients_copy:
            try:
                await queue.put(message)
            except Exception:
                pass

    def _format_sse_message(self, event_type: str, data: Dict[str, Any]) -> str:
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
        """获取当前连接的客户端数量"""
        return len(self._clients)

    # 便捷方法
    async def send_task_result(
        self, task_id: str, data: List[Dict[str, Any]], total: int
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
