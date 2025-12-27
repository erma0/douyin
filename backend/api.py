"""
API模块 - 后端核心接口

提供前端与后端交互的所有API接口，包括：
- 任务管理（采集任务的启动、状态查询）
- 设置管理（配置的加载、保存）
- 日志系统（日志订阅、实时推送）
- Aria2集成（下载管理器配置）
"""

import os
import queue
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import ujson as json
from loguru import logger

from .aria2_manager import Aria2Manager
from .lib.cookies import CookieManager
from .constants import ARIA2_DEFAULTS, DOWNLOAD_DEFAULTS, PATHS

# 设置类型别名，提高代码可读性
SettingsDict = Dict[str, Any]  # 设置字典类型
TaskType = str  # 任务类型（用户主页、搜索、音乐等）
TargetType = str  # 目标类型（链接或关键词）
LimitType = Union[int, float]  # 数量限制类型
IdsList = List[str]  # ID列表类型
LogLevel = str  # 日志级别类型
LogMessage = Dict[str, Any]  # 日志消息类型


class API:
    """
    API类 - 后端核心接口类

    负责管理应用的核心功能：
    1. 配置管理：加载、保存、验证应用配置
    2. 任务管理：启动采集任务、跟踪任务状态
    3. 日志系统：配置日志、推送日志到前端
    4. Aria2集成：管理下载服务
    5. Cookie管理：统一管理用户身份凭证

    Attributes:
        project_root: 项目根目录路径
        config_dir: 配置文件目录路径
        settings_file: 设置文件路径
        settings: 当前应用设置
        cookie_manager: Cookie管理器实例
        aria2_manager: Aria2下载管理器实例
        log_callbacks: 日志回调函数列表
        task_status: 任务状态跟踪字典
        task_results: 任务结果缓存字典
        window: PyWebView窗口实例
    """

    def __init__(self) -> None:
        """
        初始化API实例

        执行以下初始化步骤：
        1. 设置配置目录和文件路径
        2. 加载应用设置
        3. 初始化Cookie管理器
        4. 配置日志系统
        5. 初始化Aria2下载管理器
        """
        # 初始化状态标记（在所有初始化完成前为False）
        self._ready = False
        self._init_error = None

        # 获取可执行文件所在目录（打包后使用exe所在目录，开发时使用项目根目录）
        # 注意：不能使用 sys._MEIPASS，那是临时解压目录
        if getattr(sys, 'frozen', False):
            # 打包后：使用exe所在目录
            self.project_root = os.path.dirname(sys.executable)
        else:
            # 开发环境：使用项目根目录
            self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.config_dir = os.path.join(self.project_root, PATHS["CONFIG_DIR"])

        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("🚀 后端 API 初始化中...")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 自动创建配置目录
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.settings_file = os.path.join(self.config_dir, PATHS["SETTINGS_FILE"])
        
        # 检测是否首次运行（settings.json 文件不存在）
        self.is_first_run = not os.path.exists(self.settings_file)
        
        if self.is_first_run:
            logger.info("🎉 检测到首次运行，正在初始化配置...")

        # 定义默认配置
        self.default_settings = {
            "cookie": "",  # Cookie 保存在 settings.json 中
            "downloadPath": os.path.join(
                self.project_root, PATHS["DOWNLOAD_DIR"]
            ),  # 使用程序所在目录下的 download 文件夹
            "maxRetries": DOWNLOAD_DEFAULTS["MAX_RETRIES"],
            "maxConcurrency": DOWNLOAD_DEFAULTS["MAX_CONCURRENCY"],
            "windowWidth": 1200,
            "windowHeight": 800,
            "enableIncrementalFetch": True,  # 默认启用增量采集
            "aria2Host": ARIA2_DEFAULTS["HOST"],
            "aria2Port": ARIA2_DEFAULTS["PORT"],
            "aria2Secret": ARIA2_DEFAULTS["SECRET"],
        }

        # 配置验证规则：定义每个配置项的类型、范围和验证函数
        self.config_validators = {
            "cookie": {
                "type": str,
                "validator": lambda x: isinstance(x, str),
                "error_msg": "Cookie必须是字符串类型",
            },
            "downloadPath": {
                "type": str,
                "validator": lambda x: isinstance(x, str) and len(x) > 0,
                "error_msg": "下载路径必须是非空字符串",
            },
            "maxRetries": {
                "type": int,
                "validator": lambda x: isinstance(x, int) and 0 <= x <= 10,
                "error_msg": "最大重试次数必须是0-10之间的整数",
            },
            "maxConcurrency": {
                "type": int,
                "validator": lambda x: isinstance(x, int) and 1 <= x <= 10,
                "error_msg": "最大并发数必须是1-10之间的整数",
            },
            "windowWidth": {
                "type": int,
                "validator": lambda x: isinstance(x, int) and 800 <= x <= 3840,
                "error_msg": "窗口宽度必须是800-3840之间的整数",
            },
            "windowHeight": {
                "type": int,
                "validator": lambda x: isinstance(x, int) and 600 <= x <= 2160,
                "error_msg": "窗口高度必须是600-2160之间的整数",
            },
            "enableIncrementalFetch": {
                "type": bool,
                "validator": lambda x: isinstance(x, bool),
                "error_msg": "增量采集开关必须是布尔值",
            },
            "aria2Host": {
                "type": str,
                "validator": lambda x: isinstance(x, str) and len(x) > 0,
                "error_msg": "Aria2主机地址必须是非空字符串",
            },
            "aria2Port": {
                "type": int,
                "validator": lambda x: isinstance(x, int) and 1 <= x <= 65535,
                "error_msg": "Aria2端口必须是1-65535之间的整数",
            },
            "aria2Secret": {
                "type": str,
                "validator": lambda x: isinstance(x, str),
                "error_msg": "Aria2密钥必须是字符串类型",
            },
        }

        self.settings: SettingsDict = {}
        self.load_settings()

        # 初始化Cookie管理器（私有属性，避免序列化）
        self._cookie_manager = CookieManager(self.config_dir)

        # 日志回调列表，用于存储前端日志回调函数（私有属性，避免序列化JavaScript函数）
        self._log_callbacks: List[Callable[[LogMessage], None]] = []
        self._log_callbacks_lock = (
            threading.RLock()
        )  # 用于保护log_callbacks的线程安全锁

        # 日志队列，用于异步处理前端日志推送
        self._log_queue = queue.Queue(maxsize=1000)  # 限制队列大小，防止内存溢出

        # 任务状态跟踪
        self.task_status: Dict[str, Dict[str, Any]] = {}

        # 任务结果缓存
        self.task_results: Dict[str, List[Dict[str, Any]]] = {}

        # 配置loguru，添加自定义接收器
        self.setup_loguru()

        # webview窗口实例，用于调用pywebview的API（私有属性，避免序列化）
        self._window = None

        # 启动日志处理线程
        self._log_thread = threading.Thread(target=self._process_log_queue, daemon=True)
        self._log_thread.start()

        # 初始化Aria2管理器（简单初始化，不启动服务）（私有属性，避免序列化）
        self._aria2_manager = Aria2Manager(
            host=self.settings.get("aria2Host", ARIA2_DEFAULTS["HOST"]),
            port=self.settings.get("aria2Port", ARIA2_DEFAULTS["PORT"]),
            secret=self.settings.get("aria2Secret", ARIA2_DEFAULTS["SECRET"]),
            download_dir=self.settings.get(
                "downloadPath", os.path.join(self.project_root, PATHS["DOWNLOAD_DIR"])
            ),
            max_retries=self.settings.get("maxRetries", DOWNLOAD_DEFAULTS["MAX_RETRIES"]),  # 从配置面板获取重试次数
            max_concurrency=self.settings.get(
                "maxConcurrency", DOWNLOAD_DEFAULTS["MAX_CONCURRENCY"]
            ),  # 从配置面板获取并发数
        )

        # 标记初始化完成
        self._ready = True
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.success("✓ 后端 API 初始化完成")
        logger.info(f"  - 配置目录: {self.config_dir}")
        logger.info(f"  - 下载目录: {self.settings.get('downloadPath', 'N/A')}")
        logger.info(f"  - Aria2端口: {self.settings.get('aria2Port', 6800)}")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 注意：Aria2服务将在前端页面加载完成后启动
        # 参见 start_aria2_after_loaded() 方法

    def health_check(self) -> Dict[str, Any]:
        """
        健康检查接口

        供前端验证后端是否完全就绪，包括各个子系统的状态。

        Returns:
            健康状态字典，包含：
            - ready: 总体是否就绪
            - aria2: Aria2服务状态
            - config: 配置是否加载
            - error: 错误信息（如果有）
        """
        return {
            "ready": self._ready,
            "aria2": self._aria2_manager is not None
            and self._aria2_manager._check_connection(),
            "config": len(self.settings) > 0,
            "error": self._init_error,
        }

    def cleanup(self):
        """
        清理资源

        在应用退出时调用，负责：
        1. 停止Aria2服务进程
        2. 清理临时文件和连接
        3. 关闭日志系统，释放文件句柄
        4. 释放系统资源

        确保应用优雅退出，不留下僵尸进程
        """
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("🧹 开始清理资源...")

        # 1. 清理Aria2资源（停止进程、关闭连接）
        if self._aria2_manager:
            try:
                self._aria2_manager.cleanup()
                logger.info("✓ Aria2资源已清理")
            except Exception as e:
                logger.error(f"✗ 清理Aria2资源失败: {e}")

        # 2. 停止日志处理线程
        try:
            # 清空日志队列
            while not self._log_queue.empty():
                try:
                    self._log_queue.get_nowait()
                    self._log_queue.task_done()
                except:
                    break
            logger.info("✓ 日志队列已清空")
        except Exception as e:
            logger.error(f"✗ 清理日志队列失败: {e}")

        # 3. 移除所有日志处理器，释放文件句柄
        try:
            logger.info("✓ 准备关闭日志系统...")
            # 给一点时间让最后的日志写入
            import time
            time.sleep(0.1)
            # 移除所有handler，释放文件句柄
            logger.remove()
        except Exception as e:
            # 静默处理，避免影响退出
            pass

        # 4. 清理回调函数
        with self._log_callbacks_lock:
            self._log_callbacks.clear()

    def setup_loguru(self) -> None:
        """
        配置loguru日志系统

        设置三个日志输出目标：
        1. 文件日志：保存到config/app.log，支持自动轮转和压缩
        2. 控制台输出：带颜色的格式化输出，便于开发调试
        3. 前端推送：通过回调函数实时推送日志到前端界面

        日志轮转策略：
        - 单文件最大500MB
        - 保留最近7天的日志
        - 自动压缩旧日志为zip格式
        """
        # 移除默认的控制台输出，避免重复
        logger.remove()

        # 添加文件日志，存储在config目录下
        log_file = os.path.join(self.config_dir, "app.log")
        logger.add(
            log_file,
            rotation="500 MB",
            retention="7 days",
            compression="zip",
            encoding="utf-8",
            level="INFO",
        )

        # 添加控制台输出（仅开发环境）
        if not getattr(sys, 'frozen', False):
            logger.add(
                sys.stderr,
                level="INFO",
                format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            )

        # 添加自定义接收器，用于将日志发送到前端
        # 使用 DEBUG 级别，确保所有日志都能推送到前端
        logger.add(
            self._log_to_frontend,
            level="DEBUG",
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        )

    def _process_log_queue(self) -> None:
        """
        处理日志队列的后台线程

        从日志队列中获取日志消息，并异步推送到前端，避免阻塞主线程。
        线程会一直运行，直到程序退出。
        """
        while True:
            try:
                # 从队列中获取日志消息，使用超时避免无限阻塞
                try:
                    log_entry = self._log_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                # 调用所有注册的日志回调函数
                with self._log_callbacks_lock:
                    callbacks_copy = self._log_callbacks.copy()

                # 即使没有回调函数也要标记任务完成，避免队列堵塞
                if not callbacks_copy:
                    self._log_queue.task_done()
                    continue

                for callback in callbacks_copy:
                    try:
                        # 检查回调函数是否有效
                        if callback is not None and callable(callback):
                            callback(log_entry)
                    except Exception as e:
                        # 静默处理错误，避免影响主流程
                        # 但在开发时可以打印到控制台
                        import sys

                        print(f"日志回调错误: {e}", file=sys.stderr)

                # 标记任务完成
                self._log_queue.task_done()
            except Exception as e:
                # 捕获所有异常，防止日志处理线程崩溃
                import sys

                print(f"日志队列处理错误: {e}", file=sys.stderr)
                time.sleep(0.1)  # 发生异常时短暂休眠，避免CPU占用过高

    def _log_to_frontend(self, message: str) -> None:
        """
        将日志消息发送到前端

        作为loguru的自定义sink函数，接收格式化后的日志字符串，
        解析出时间、级别和消息内容，然后通过回调函数推送到前端。

        Args:
            message: loguru格式化后的日志字符串

        Note:
            - 使用正则表达式解析日志格式
            - 避免在此函数中使用logger，防止无限递归
            - 异常处理确保日志推送失败不影响主流程
        """
        # 构建日志消息对象
        # 注意：在loguru的sink函数中，message是一个格式化后的字符串，不是字典
        # 所以我们需要从字符串中解析出需要的信息
        import re
        from datetime import datetime

        # 尝试从日志字符串中提取时间、级别和消息
        # 实际格式: "2024-12-06 10:30:45.123 | INFO     | module:function:line - message"
        log_pattern = (
            r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\s*\|\s*(\w+)\s*\|.*?-\s*(.+)"
        )
        match = re.match(log_pattern, message)

        if match:
            timestamp = match.group(1)
            level = match.group(2).strip().lower()
            log_message = match.group(3).strip()
        else:
            # 如果无法匹配，使用默认值
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            level = "info"
            log_message = message.strip()

        log_entry = {
            "id": str(hash(f"{timestamp}{level}{log_message}")),
            "timestamp": timestamp,
            "level": level,
            "message": log_message,
        }

        try:
            # 将日志条目放入队列，异步处理（非阻塞）
            self._log_queue.put_nowait(log_entry)
        except queue.Full:
            # 如果队列已满，静默丢弃，避免阻塞
            pass
        except Exception:
            # 捕获所有异常，确保日志系统不会崩溃
            pass

    def subscribe_to_logs(self, callback: Callable[[LogMessage], None]) -> None:
        """
        注册日志回调函数

        前端通过此方法订阅日志消息，注册的回调函数会在每次
        产生新日志时被调用，实现日志的实时推送。

        Args:
            callback: 日志回调函数，接收LogMessage字典参数

        Returns:
            None（不返回取消订阅函数，避免序列化问题）

        Note:
            PyWebView 无法序列化 Python 函数，所以不返回取消订阅函数
            前端可以通过 unsubscribe_from_logs 方法手动取消订阅
        """
        with self._log_callbacks_lock:
            self._log_callbacks.append(callback)
            callback_count = len(self._log_callbacks)

        logger.info(f"✓ 前端已订阅日志（当前订阅数: {callback_count}）")

    def unsubscribe_from_logs(self, callback: Callable[[LogMessage], None]) -> None:
        """
        取消注册日志回调函数

        Args:
            callback: 要移除的日志回调函数
        """
        try:
            with self._log_callbacks_lock:
                if callback in self._log_callbacks:
                    self._log_callbacks.remove(callback)
                    callback_count = len(self._log_callbacks)
                    logger.info(f"✓ 前端已取消订阅日志（剩余订阅数: {callback_count}）")
        except (ValueError, TypeError):
            # 回调函数可能已经被移除或无效
            pass

    def get_logger(self):
        """
        获取loguru logger实例

        Returns:
            loguru的logger对象
        """
        return logger

    def load_settings(self) -> None:
        """
        加载应用设置
        
        从 settings.json 加载配置，自动处理文件不存在、损坏等情况
        """
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    loaded_settings = json.load(f)
                    logger.info("✓ 配置已加载")

                    # 验证并修复配置
                    is_valid, errors = self.validate_config(loaded_settings)
                    if not is_valid:
                        logger.warning("⚠ 配置包含无效项，自动修复中...")
                        for error in errors:
                            config_key = error.split(":")[0].strip()
                            if config_key in self.default_settings:
                                loaded_settings[config_key] = self.default_settings[config_key]
                                logger.warning(f"  - 已修复 {config_key}")

                    # 补充缺失的配置项（支持版本升级）
                    updated = False
                    for key, default_value in self.default_settings.items():
                        if key not in loaded_settings:
                            loaded_settings[key] = default_value
                            updated = True
                            logger.info(f"  - 新增配置项 {key}")

                    self.settings = loaded_settings
                    
                    # 如果有修复或更新，保存回文件
                    if not is_valid or updated:
                        self._save_settings_file()
                        logger.info("✓ 配置已自动修复并保存")
            else:
                # 首次运行，创建默认配置
                self.settings = self.default_settings.copy()
                self._save_settings_file()
                logger.info("✓ 默认配置已创建")
                
        except json.JSONDecodeError:
            logger.error("✗ 配置文件损坏，使用默认配置并备份旧文件")
            self._backup_and_reset_settings()
        except Exception as e:
            logger.error(f"✗ 加载配置失败: {e}，使用默认配置")
            self.settings = self.default_settings.copy()
    
    def _save_settings_file(self) -> None:
        """内部方法：保存配置到文件"""
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)
    
    def _backup_and_reset_settings(self) -> None:
        """内部方法：备份损坏的配置文件并重置"""
        try:
            # 备份损坏的文件
            if os.path.exists(self.settings_file):
                backup_file = f"{self.settings_file}.backup.{int(time.time())}"
                os.rename(self.settings_file, backup_file)
                logger.info(f"  - 已备份到: {backup_file}")
        except Exception as e:
            logger.warning(f"  - 备份失败: {e}")
        
        # 使用默认配置
        self.settings = self.default_settings.copy()
        self._save_settings_file()

    def start_task(
        self, type: TaskType, target: TargetType, limit: LimitType, filters: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        开始采集任务（支持流式返回）

        启动一个新的数据采集任务，从抖音平台采集指定类型的数据。
        采集过程中会通过 window.evaluate_js 实时调用前端回调函数返回结果。

        Args:
            type: 任务类型
            target: 目标链接或关键词
            limit: 采集数量限制（0表示不限制）

        Returns:
            任务信息字典：
            - task_id: 任务ID
            - status: 初始状态

        Note:
            - 采集在后台线程中执行，不阻塞主线程
            - 通过 window.evaluate_js 调用前端命名空间回调函数 window.__kiro_douyin.taskCallback
            - 前端需要在调用此方法前通过 callbackManager 注册回调函数
            - 任务状态会被记录到task_status字典
        """
        # 输入验证
        if not isinstance(type, str) or not type:
            logger.error("Invalid task type: must be a non-empty string")
            raise ValueError("Invalid task type")

        if not isinstance(target, str):
            logger.error("Invalid target: must be a string")
            raise ValueError("Invalid target")

        if not isinstance(limit, (int, float)) or limit < 0:
            logger.error("Invalid limit: must be a non-negative number")
            raise ValueError("Invalid limit")

        # 前端到后端的类型映射
        # 前端使用更明确的命名（如 user_post），后端爬虫使用简短命名（如 post）
        type_mapping = {
            "user_post": "post",  # 用户主页作品
            "user_like": "like",  # 用户喜欢
            "user_favorite": "favorite",  # 用户收藏
            "challenge": "hashtag",  # 挑战话题
            "post": "video",  # 单个作品（前端post对应后端video/note）
        }

        # 转换类型
        backend_type = type_mapping.get(type, type)
        if backend_type != type:
            logger.debug(f"类型映射: {type} -> {backend_type}")

        # 生成唯一的任务ID
        import uuid

        task_id = f"task_{uuid.uuid4().hex[:8]}"

        # 初始化任务状态
        self.task_status[task_id] = {
            "id": task_id,
            "type": type,
            "backend_type": backend_type,
            "target": target,
            "limit": limit,
            "filters": filters or {},
            "status": "running",
            "progress": 0,
            "result_count": 0,
            "error": None,
            "created_at": time.time(),
            "updated_at": time.time(),
        }

        # 初始化结果缓存
        self.task_results[task_id] = []

        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info(f"📥 开始采集任务")
        logger.info(f"  任务ID: {task_id}")
        logger.info(f"  前端类型: {type}")
        if backend_type != type:
            logger.info(f"  后端类型: {backend_type}")
        logger.info(f"  目标: {target}")
        logger.info(f"  数量限制: {'不限' if limit == 0 else f'{limit}条'}")
        if filters:
            logger.info(f"  筛选条件: {filters}")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 在后台线程中执行采集任务
        def run_task():
            try:
                # 导入爬虫模块
                from .lib.douyin import Douyin

                # 获取cookie
                cookie = self._cookie_manager.load_cookie(
                    self.settings.get("cookie", "")
                )

                # 验证cookie
                if not self._cookie_manager.validate_cookie(cookie):
                    logger.error("✗ Cookie验证失败")
                    raise Exception("Cookie无效或已过期，请在设置中更新Cookie")

                logger.info("✓ Cookie验证通过，开始采集...")

                # 创建爬虫实例（使用转换后的后端类型）
                douyin = Douyin(
                    target=target,
                    limit=int(limit) if limit > 0 else 0,
                    type=backend_type,
                    down_path=self.settings.get(
                        "downloadPath", os.path.join(self.project_root, PATHS["DOWNLOAD_DIR"])
                    ),
                    cookie=cookie,
                    filters=filters or {},
                )

                # 初始化aria2_config_paths字典，但不保存路径
                # aria2_conf路径将在采集完成后保存
                self._aria2_config_paths = getattr(self, "_aria2_config_paths", {})

                # 修改爬虫的 __append_awemes 方法，使其支持实时回调
                original_append = douyin._Douyin__append_awemes

                def append_with_callback(awemes_list):
                    # 调用原始方法
                    original_append(awemes_list)

                    # 如果有新结果，实时返回给前端
                    if douyin.results and self._window:
                        # 只返回新增的结果
                        new_results = douyin.results[len(self.task_results[task_id]) :]
                        if new_results:
                            logger.debug(
                                f"检测到 {len(new_results)} 条新结果，开始转换..."
                            )

                            # 转换格式
                            works = self._convert_douyin_results(
                                new_results, douyin.type
                            )
                            logger.debug(f"转换完成，得到 {len(works)} 条作品")

                            if not works:
                                logger.warning(
                                    f"转换后没有有效数据！原始数据: {len(new_results)} 条"
                                )
                                return

                            # 更新缓存
                            self.task_results[task_id].extend(new_results)

                            # 更新任务状态
                            self.task_status[task_id]["result_count"] = len(
                                self.task_results[task_id]
                            )
                            self.task_status[task_id]["updated_at"] = time.time()

                            # 回调前端
                            try:
                                logger.info(
                                    f"回调前端: {len(works)} 条新结果，累计 {len(self.task_results[task_id])} 条"
                                )

                                callback_data = {
                                    "type": "result",
                                    "task_id": task_id,
                                    "data": works,
                                    "total": len(self.task_results[task_id]),
                                }

                                callback_json = json.dumps(
                                    callback_data, ensure_ascii=False
                                )
                                js_code = f"window.__kiro_douyin && window.__kiro_douyin.taskCallback && window.__kiro_douyin.taskCallback({callback_json})"
                                self._window.evaluate_js(js_code)
                            except Exception as e:
                                logger.error(f"回调前端失败: {e}")
                                import traceback

                                traceback.print_exc()

                # 替换方法
                douyin._Douyin__append_awemes = append_with_callback

                # 执行采集
                logger.info("🚀 正在采集数据...")
                douyin.run()

                # 获取后端实际识别的类型
                detected_type = douyin.type

                # 采集完成后保存aria2_conf路径和相关信息，供后续批量下载使用
                self._aria2_config_paths[task_id] = douyin.aria2_conf

                # 在任务状态中保存aria2_conf路径
                self.task_status[task_id]["aria2_conf"] = douyin.aria2_conf

                # 采集完成后，检查是否有未回调的结果（如单个作品采集）
                logger.debug(
                    f"采集结果数: {len(douyin.results)}, 已回调数: {len(self.task_results[task_id])}"
                )

                if douyin.results and len(douyin.results) > len(
                    self.task_results[task_id]
                ):
                    new_results = douyin.results[len(self.task_results[task_id]) :]
                    logger.info(f"发现 {len(new_results)} 条未回调的结果，正在转换...")
                    works = self._convert_douyin_results(new_results, douyin.type)
                    logger.info(f"转换完成，得到 {len(works)} 条作品数据")
                    self.task_results[task_id].extend(new_results)

                    # 回调前端
                    if works and self._window:
                        try:
                            logger.info(f"准备回调前端: {len(works)} 条新结果")

                            # 构建回调数据
                            callback_data = {
                                "type": "result",
                                "task_id": task_id,
                                "data": works,
                                "total": len(self.task_results[task_id]),
                            }

                            logger.debug(
                                f"回调数据: type={callback_data['type']}, data_count={len(callback_data['data'])}, total={callback_data['total']}"
                            )

                            # 使用 window.evaluate_js 调用前端命名空间回调函数
                            callback_json = json.dumps(
                                callback_data, ensure_ascii=False
                            )
                            js_code = f"window.__kiro_douyin && window.__kiro_douyin.taskCallback && window.__kiro_douyin.taskCallback({callback_json})"
                            self._window.evaluate_js(js_code)
                            logger.info(
                                f"✓ 通过 evaluate_js 回调前端成功: {len(works)} 条"
                            )
                        except Exception as e:
                            logger.error(f"✗ 回调前端失败: {e}")
                            import traceback

                            traceback.print_exc()
                    else:
                        if not self._window:
                            logger.warning("⚠️ window 对象为空，无法回调前端")
                        if not works:
                            logger.warning("⚠️ 转换后的作品数据为空")

                # 更新任务状态为完成
                self.task_status[task_id]["status"] = "completed"
                self.task_status[task_id]["progress"] = 100
                self.task_status[task_id]["updated_at"] = time.time()

                logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                logger.success(
                    f"✓ 任务完成: 成功采集 {len(self.task_results[task_id])} 条数据"
                )
                if detected_type != type:
                    logger.info(f"  后端识别类型: {detected_type} (前端传入: {type})")
                logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

                # 通知前端任务完成
                if self._window:
                    try:
                        logger.info(
                            f"准备发送完成回调，总计 {len(self.task_results[task_id])} 条"
                        )

                        # 检查是否是增量采集且无新结果
                        is_incremental = (
                            detected_type == "post"
                            and len(self.task_results[task_id]) == 0
                        )

                        complete_data = {
                            "type": "complete",
                            "task_id": task_id,
                            "detected_type": detected_type,
                            "total": len(self.task_results[task_id]),
                            "is_incremental": is_incremental,  # 标记是否为增量采集
                        }

                        complete_json = json.dumps(complete_data, ensure_ascii=False)
                        js_code = f"window.__kiro_douyin && window.__kiro_douyin.taskCallback && window.__kiro_douyin.taskCallback({complete_json})"
                        self._window.evaluate_js(js_code)
                        logger.info("✓ 完成回调已发送")
                    except Exception as e:
                        logger.error(f"✗ 完成回调失败: {e}")
                        import traceback

                        traceback.print_exc()
                else:
                    logger.warning("⚠️ window 对象为空，无法发送完成通知")

            except Exception as e:
                # 更新任务状态为失败
                self.task_status[task_id]["status"] = "error"
                self.task_status[task_id]["error"] = str(e)
                self.task_status[task_id]["updated_at"] = time.time()

                logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                logger.error(f"✗ 任务失败: {str(e)}")
                logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

                # 通知前端任务失败
                if self._window:
                    try:
                        error_data = {
                            "type": "error",
                            "task_id": task_id,
                            "error": str(e),
                        }

                        error_json = json.dumps(error_data, ensure_ascii=False)
                        js_code = f"window.__kiro_douyin && window.__kiro_douyin.taskCallback && window.__kiro_douyin.taskCallback({error_json})"
                        self._window.evaluate_js(js_code)
                        logger.info("✓ 错误回调已发送")
                    except Exception as callback_error:
                        logger.warning(f"回调前端失败: {callback_error}")
            finally:
                # 任务完成后保留aria2_conf路径，供后续批量下载使用
                # 不需要清理，因为只是字符串路径，占用内存很小
                pass

        # 启动后台线程
        task_thread = threading.Thread(target=run_task, daemon=True)
        task_thread.start()

        # 立即返回任务ID
        return {"task_id": task_id, "status": "running"}

    def _convert_douyin_results(
        self, results: List[Dict[str, Any]], task_type: str
    ) -> List[Dict[str, Any]]:
        """
        将爬虫结果转换为前端期望的格式

        爬虫模块返回的原始数据格式与前端期望的格式不同，
        此方法负责进行数据转换和字段映射。

        Args:
            results: 爬虫模块返回的原始结果列表
            task_type: 任务类型（用于特殊处理）

        Returns:
            转换后的作品列表，符合前端数据模型

        Note:
            - 自动识别作品类型（视频/图集）
            - 处理缺失字段，提供默认值
            - 转换时间戳为可读格式
            - 跳过无法转换的数据项
        """
        works = []
        logger.debug(f"开始转换 {len(results)} 条结果，任务类型: {task_type}")

        for idx, item in enumerate(results):
            try:
                # 判断作品类型
                aweme_type = item.get("type", 4)
                is_image = aweme_type == 68

                work = {
                    "id": str(item.get("id", "")),
                    "desc": item.get("desc", ""),
                    "author": {
                        "nickname": item.get("author_nickname", "未知用户"),
                        "avatar": item.get("author_avatar", ""),
                        "uid": item.get("author_uid", ""),
                        "unique_id": item.get("author_unique_id", ""),  # 抖音号
                        "short_id": item.get("author_short_id", ""),  # 短ID
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
                logger.warning(f"转换第 {idx+1} 条数据失败: {e}")
                logger.debug(f"失败的数据项: {item}")
                continue

        logger.debug(
            f"转换完成，成功 {len(works)} 条，失败 {len(results) - len(works)} 条"
        )
        return works

    def get_browser_cookie(self, browser: str = "edge") -> Dict[str, Any]:
        """
        从浏览器获取Cookie（已废弃）

        该功能已移除，不同浏览器适配复杂且不稳定。
        请手动从浏览器复制Cookie。

        Returns:
            包含cookie字符串和状态的字典：
            - success: False
            - cookie: 空字符串
            - error: 错误信息
        """
        error_msg = "浏览器Cookie自动获取功能已移除，请手动从浏览器复制Cookie"
        logger.warning(error_msg)
        return {"success": False, "cookie": "", "error": error_msg}

    def get_aria2_config(self) -> Dict[str, Any]:
        """
        获取Aria2配置信息

        返回Aria2 RPC服务的连接配置，供前端直接与Aria2通信使用。

        Returns:
            包含以下字段的配置字典：
            - host: Aria2 RPC主机地址
            - port: Aria2 RPC端口
            - secret: Aria2 RPC密钥（如果设置）
        """
        # 如果用户没有设置密钥，使用默认密钥
        user_secret = self.settings.get("aria2Secret", ARIA2_DEFAULTS["SECRET"])
        default_secret = (
            ARIA2_DEFAULTS["SECRET"] if not user_secret else user_secret
        )

        return {
            "host": self.settings.get("aria2Host", ARIA2_DEFAULTS["HOST"]),
            "port": self.settings.get("aria2Port", ARIA2_DEFAULTS["PORT"]),
            "secret": default_secret,
        }

    def check_aria2_connection(self) -> Dict[str, Any]:
        """
        检查Aria2连接状态（快速检查）

        快速检查Aria2端口是否开放。

        Returns:
            包含以下字段的状态字典：
            - connected: Aria2端口是否开放
        """
        is_connected = False
        if self._aria2_manager:
            try:
                is_connected = self._aria2_manager._check_connection()
            except Exception:
                pass

        return {"connected": is_connected}

    def open_url(self, url: str) -> Optional[None]:
        """
        打开外部链接

        使用系统默认浏览器打开指定的URL。

        Args:
            url: 要打开的URL地址

        Raises:
            ValueError: URL参数无效

        Note:
            使用webbrowser模块，自动选择系统默认浏览器
        """
        # 输入验证
        if not isinstance(url, str) or not url:
            logger.error("Invalid URL: must be a non-empty string")
            raise ValueError("Invalid URL")

        logger.info(f"Opening URL: {url}")
        try:
            webbrowser.open(url)
            logger.debug(f"URL opened successfully: {url}")
        except Exception as e:
            logger.error(f"Failed to open URL: {e}")
        return None

    def get_settings(self) -> SettingsDict:
        """
        获取当前设置

        Returns:
            当前的应用设置字典，包含实际的Cookie值
        """
        # 直接返回settings，cookie已经在settings中
        return self.settings.copy()

    def is_first_run_check(self) -> bool:
        """
        检查是否首次运行

        Returns:
            True: 首次运行（settings.json 不存在）
            False: 非首次运行（settings.json 已存在）

        Note:
            首次运行的判断依据是 settings.json 文件是否存在
            简单可靠，settings.json 存在即表示已完成初始化
        """
        return self.is_first_run

    def validate_config(self, config: SettingsDict) -> tuple[bool, List[str]]:
        """
        验证配置项的有效性

        根据预定义的验证规则检查配置项的类型和范围，
        确保配置值符合要求。

        Args:
            config: 要验证的配置字典

        Returns:
            (is_valid, errors):
                - is_valid: 配置是否全部有效
                - errors: 错误信息列表，如果全部有效则为空列表

        Note:
            - 只验证config中存在的配置项
            - 缺失的配置项会使用默认值，不算错误
            - 验证失败会记录详细的错误日志
        """
        errors = []

        for key, value in config.items():
            # 跳过未定义验证规则的配置项
            if key not in self.config_validators:
                continue

            validator_info = self.config_validators[key]

            # 执行验证
            try:
                if not validator_info["validator"](value):
                    error_msg = f"{key}: {validator_info['error_msg']}"
                    errors.append(error_msg)
            except Exception as e:
                error_msg = f"{key}: 验证出错 - {str(e)}"
                errors.append(error_msg)

        is_valid = len(errors) == 0
        return is_valid, errors

    def save_settings(self, settings: SettingsDict) -> Optional[None]:
        """
        保存设置（支持部分更新）
        
        Args:
            settings: 要保存的设置字典，可以是部分更新
            
        Raises:
            ValueError: 设置验证失败
        """
        if not isinstance(settings, dict):
            raise ValueError("设置必须是字典类型")

        logger.info("💾 保存配置...")

        # 验证配置
        is_valid, errors = self.validate_config(settings)
        if not is_valid:
            error_msg = "配置验证失败:\n" + "\n".join(f"  - {err}" for err in errors)
            logger.error(f"✗ {error_msg}")
            raise ValueError(error_msg)

        try:
            # 更新内存配置
            self.settings.update(settings)
            
            # 保存到文件
            self._save_settings_file()

            # 简洁的日志输出
            updated_keys = list(settings.keys())
            logger.success(f"✓ 配置已保存: {', '.join(updated_keys)}")

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"✗ 保存失败: {e}")
            raise

        return None

    def get_task_status(self, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取任务状态

        查询采集任务的执行状态，支持查询单个任务或所有任务。

        Args:
            task_id: 任务ID，如果为None则返回所有任务状态

        Returns:
            任务状态列表，每个任务包含：
            - id: 任务ID
            - type: 任务类型
            - target: 目标
            - status: 状态（running/completed/error）
            - progress: 进度（0-100）
            - result_count: 结果数量
            - error: 错误信息（如果失败）
            - created_at: 创建时间戳
            - updated_at: 更新时间戳
        """
        logger.info(f"Getting task status for task: {task_id}")

        if task_id:
            # 返回指定任务的状态
            if task_id in self.task_status:
                return [self.task_status[task_id]]
            else:
                logger.warning(f"Task not found: {task_id}")
                return []
        else:
            # 返回所有任务的状态
            return list(self.task_status.values())

    def get_task_results(self, task_id: str) -> List[Dict[str, Any]]:
        """
        获取任务的采集结果

        返回指定任务的所有采集结果，供前端直接调用 Aria2 下载。

        Args:
            task_id: 任务ID

        Returns:
            采集结果列表

        Raises:
            ValueError: 任务不存在
        """
        logger.info(f"获取任务结果: {task_id}")

        # 检查任务是否存在
        if task_id not in self.task_results:
            logger.error(f"任务不存在: {task_id}")
            raise ValueError(f"任务不存在: {task_id}")

        results = self.task_results[task_id]
        logger.info(f"返回 {len(results)} 条结果")

        return results

    def get_clipboard_text(self) -> str:
        """
        获取系统剪贴板内容

        通过后端读取剪贴板，避免浏览器权限问题。

        Returns:
            剪贴板中的文本内容，如果失败返回空字符串

        Note:
            - 需要安装 pyperclip 库
            - 自动清理空白字符
            - 失败时返回空字符串而不是抛出异常
        """
        try:
            import pyperclip

            text = pyperclip.paste()
            if text:
                # 清理文本：去除首尾空白
                cleaned_text = text.strip()
                logger.debug(f"读取剪贴板成功，长度: {len(cleaned_text)}")
                return cleaned_text
            return ""
        except Exception as e:
            logger.warning(f"读取剪贴板失败: {e}")
            return ""

    def set_webview_window(self, window):
        """
        设置PyWebView窗口实例

        保存窗口实例的引用，用于调用PyWebView的原生API，
        如文件选择对话框等。

        Args:
            window: PyWebView窗口对象
        """
        self._window = window
        logger.info("Webview window instance set to API")

    def start_aria2_after_loaded(self):
        """
        在前端页面加载完成后启动Aria2服务

        此方法应在PyWebView的loaded事件回调中调用，
        确保窗口完全初始化后再启动Aria2，避免阻塞窗口加载。

        使用后台线程异步启动，不阻塞主线程。
        """

        def start_aria2_async():
            try:
                logger.info("🚀 前端加载完成，后台启动Aria2服务...")
                self._aria2_manager.start_aria2_server()
            except Exception as e:
                logger.warning(f"⚠ Aria2启动失败: {e}")
                logger.warning("  前端将持续尝试连接")

        # 在后台线程中启动，不阻塞
        threading.Thread(target=start_aria2_async, daemon=True).start()

    def select_folder(self) -> str:
        """
        选择文件夹

        打开系统文件夹选择对话框，让用户选择下载路径。

        Returns:
            选择的文件夹路径，如果取消则返回当前下载路径

        Note:
            - 使用PyWebView的create_file_dialog API
            - 兼容新旧版本的API（FileDialog.FOLDER / FOLDER_DIALOG）
            - 如果窗口未初始化，返回当前设置的下载路径
        """
        logger.info("Selecting folder")
        try:
            if self._window and hasattr(self._window, "create_file_dialog"):
                # 使用pywebview的API选择文件夹
                import webview

                try:
                    # 使用推荐的FileDialog.FOLDER枚举值
                    folder_path = self._window.create_file_dialog(
                        webview.FileDialog.FOLDER
                    )
                except AttributeError:
                    # 回退到旧版FOLDER_DIALOG常量
                    folder_path = self._window.create_file_dialog(webview.FOLDER_DIALOG)

                if folder_path:
                    # create_file_dialog返回的是列表，取第一个元素
                    selected_path = folder_path[0]
                    logger.info(f"Folder selected via pywebview: {selected_path}")
                    return selected_path
                else:
                    logger.info("Folder selection canceled by user")
                    return self.settings["downloadPath"]
            else:
                logger.error("Webview window not available for folder selection")
                return self.settings["downloadPath"]
        except Exception as e:
            logger.error(f"Error selecting folder: {e}")
            return self.settings["downloadPath"]

    def open_folder(self, folder_path: str) -> bool:
        """
        打开文件夹

        在系统文件管理器中打开指定的文件夹。

        Args:
            folder_path: 要打开的文件夹路径

        Returns:
            是否成功打开

        Note:
            - Windows: 使用 explorer
            - macOS: 使用 open
            - Linux: 使用 xdg-open
        """
        logger.info(f"打开文件夹: {folder_path}")
        
        try:
            import platform
            import subprocess
            
            # 确保路径存在
            if not os.path.exists(folder_path):
                logger.error(f"文件夹不存在: {folder_path}")
                return False
            
            # 如果是文件路径，获取其所在目录
            if os.path.isfile(folder_path):
                folder_path = os.path.dirname(folder_path)
            
            system = platform.system()
            
            # Windows 下隐藏控制台窗口
            startupinfo = None
            if system == "Windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            if system == "Windows":
                # Windows: 使用 explorer，需要规范化路径
                normalized_path = os.path.abspath(folder_path).replace('/', '\\')
                # 使用 os.startfile 更可靠
                os.startfile(normalized_path)
            elif system == "Darwin":
                # macOS: 使用 open
                subprocess.Popen(['open', folder_path])
            else:
                # Linux: 使用 xdg-open
                subprocess.Popen(['xdg-open', folder_path])
            
            logger.info(f"✓ 已打开文件夹: {folder_path}")
            return True
            
        except Exception as e:
            logger.error(f"✗ 打开文件夹失败: {e}")
            return False

    def get_aria2_config_path(self, task_id: str = None) -> str:
        """
        获取已完成任务的aria2配置文件路径

        Args:
            task_id: 任务ID（可选，如果不提供则使用最新的任务）

        Returns:
            aria2配置文件路径
        """
        logger.info(f"获取aria2配置文件路径，task_id: {task_id}")
        
        # 如果没有指定task_id，使用最新的任务
        if task_id is None:
            logger.info("未指定task_id，查找最新任务")
            
            if hasattr(self, "_aria2_config_paths") and self._aria2_config_paths:
                logger.info(f"找到 {len(self._aria2_config_paths)} 个缓存的配置路径")
                # 获取最新的配置文件路径
                latest_task_id = max(self._aria2_config_paths.keys())
                config_path = self._aria2_config_paths[latest_task_id]
                logger.info(f"最新任务ID: {latest_task_id}, 配置路径: {config_path}")

                # 检查配置文件是否存在
                if not os.path.exists(config_path):
                    logger.error(f"配置文件不存在: {config_path}")
                    raise ValueError(f"配置文件不存在: {config_path}，请确保采集任务已完成并生成了下载配置")

                logger.info(f"返回配置文件路径: {config_path}")
                return config_path
            else:
                # 检查任务状态中是否有已完成的任务
                completed_tasks = [
                    task_id for task_id, task_info in self.task_status.items()
                    if task_info.get("status") == "completed" and "aria2_conf" in task_info
                ]
                
                if completed_tasks:
                    logger.info(f"从任务状态中找到 {len(completed_tasks)} 个已完成任务")
                    latest_task_id = max(completed_tasks)
                    config_path = self.task_status[latest_task_id]["aria2_conf"]
                    logger.info(f"使用任务 {latest_task_id} 的配置文件: {config_path}")
                    
                    # 检查配置文件是否存在
                    if not os.path.exists(config_path):
                        logger.error(f"配置文件不存在: {config_path}")
                        raise ValueError(f"配置文件不存在: {config_path}")
                    
                    # 缓存到内存中
                    if not hasattr(self, "_aria2_config_paths"):
                        self._aria2_config_paths = {}
                    self._aria2_config_paths[latest_task_id] = config_path
                    
                    return config_path
                else:
                    logger.error("没有找到已完成的采集任务")
                    raise ValueError("没有已完成的采集任务，请先完成一次采集后再使用批量下载功能")

        # 从保存的路径中获取aria2_conf
        if hasattr(self, "_aria2_config_paths") and task_id in self._aria2_config_paths:
            config_path = self._aria2_config_paths[task_id]

            # 检查配置文件是否存在
            if not os.path.exists(config_path):
                raise ValueError(f"任务 {task_id} 的配置文件不存在")

            return config_path
        else:
            # 检查任务是否存在且已完成
            if task_id in self.task_status:
                task_info = self.task_status[task_id]
                if task_info["status"] != "completed":
                    raise ValueError(f"任务 {task_id} 尚未完成，无法获取配置文件")

                # 从任务状态中获取保存的aria2_conf路径
                if "aria2_conf" in task_info:
                    config_path = task_info["aria2_conf"]

                    # 检查配置文件是否存在
                    if not os.path.exists(config_path):
                        raise ValueError(f"任务 {task_id} 的配置文件不存在")

                    # 同时保存到内存缓存中
                    self._aria2_config_paths[task_id] = config_path
                    return config_path
                else:
                    raise ValueError(f"任务 {task_id} 缺少配置文件路径信息")
            else:
                raise ValueError(f"任务不存在: {task_id}")

    def read_config_file(self, file_path: str) -> str:
        """
        读取配置文件内容

        Args:
            file_path: 配置文件路径

        Returns:
            文件内容
        """
        try:
            logger.info(f"开始读取配置文件: {file_path}")
            
            # 安全检查：确保文件路径在下载目录内
            download_dir = os.path.abspath(
                self.settings.get("downloadPath", PATHS["DOWNLOAD_DIR"])
            )
            abs_path = os.path.abspath(file_path)
            
            logger.info(f"下载目录: {download_dir}")
            logger.info(f"绝对路径: {abs_path}")

            if not abs_path.startswith(download_dir) or not abs_path.endswith(".txt"):
                logger.error(f"文件路径不安全: {abs_path}")
                raise ValueError("文件路径不安全")
            
            if not os.path.exists(abs_path):
                logger.error(f"配置文件不存在: {abs_path}")
                raise ValueError(f"配置文件不存在: {abs_path}")

            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()
                logger.info(f"配置文件读取成功，内容长度: {len(content)} 字符")
                logger.debug(f"配置文件前100字符: {content[:100]}")
                return content

        except Exception as e:
            logger.error(f"读取配置文件失败: {e}")
            raise

    def check_file_exists(self, file_path: str) -> bool:
        """
        检查文件是否存在

        Args:
            file_path: 文件路径

        Returns:
            文件是否存在
        """
        try:
            # 安全检查：确保文件路径在下载目录内
            download_dir = os.path.abspath(
                self.settings.get("downloadPath", PATHS["DOWNLOAD_DIR"])
            )
            abs_path = os.path.abspath(file_path)

            if not abs_path.startswith(download_dir):
                return False

            return os.path.exists(abs_path) and os.path.isfile(abs_path)

        except Exception as e:
            logger.error(f"检查文件存在失败: {e}")
            return False
