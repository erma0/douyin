
import { bridge } from './bridge';

/**
 * 日志级别类型
 */
export type LogLevel = 'debug' | 'info' | 'success' | 'warn' | 'error';

/**
 * 日志条目接口
 * 描述单条日志的完整信息
 */
export interface LogEntry {
  id: string;           // 日志唯一标识符
  timestamp: string;    // 时间戳（HH:MM:SS.mmm格式）
  level: LogLevel;      // 日志级别
  message: string;      // 日志消息内容
  context?: Record<string, any>;  // 上下文信息
  stack?: string;       // 错误堆栈信息
  source?: string;      // 日志来源（frontend/backend）
  category?: string;    // 日志分类（download/collection/error等）
}

/**
 * 日志监听器类型
 * 用于订阅日志更新
 */
type Listener = (logs: LogEntry[]) => void;

/**
 * 日志服务类
 * 
 * 功能：
 * - 管理前端日志：记录、存储、通知
 * - 订阅后端日志：接收并整合后端日志
 * - 日志查询：提供日志列表和文本导出
 * 
 * 特性：
 * - 自动限制日志数量（默认1000条）
 * - 支持多个监听器订阅
 * - 前后端日志统一管理
 */
class LoggerService {
  private logs: LogEntry[] = [];                    // 日志列表
  private listeners: Set<Listener> = new Set();     // 监听器集合
  private maxLogs = 1000;                           // 最大日志数量
  private unsubscribeFromBackend?: () => void;      // 取消后端订阅的函数
  private _isInitialized = false;                   // 是否已初始化
  private _isNotifying = false;                     // 是否正在通知监听器
  private _pendingNotify = false;                   // 是否有待处理的通知

  constructor() {
    // 构造函数中不立即订阅，改为延迟订阅
    // 避免在后端未就绪时订阅失败
  }

  /**
   * 检查是否已初始化
   */
  public get isInitialized(): boolean {
    return this._isInitialized;
  }

  /**
   * 手动初始化后端日志订阅
   * 应在用户打开日志面板时调用，避免不必要的性能开销（需求 6.4）
   */
  public async initialize(): Promise<void> {
    if (!this._isInitialized) {
      await this.subscribeToBackendLogs();
      this._isInitialized = true;
    }
  }

  /**
   * 取消后端日志订阅
   * 在用户关闭日志面板时调用，减少性能开销（需求 6.4）
   */
  public uninitialize(): void {
    if (this._isInitialized && this.unsubscribeFromBackend) {
      this.unsubscribeFromBackend();
      this._isInitialized = false;
    }
  }

  /**
   * 通知所有监听器日志已更新
   * 使用节流机制，避免短时间内频繁通知，减少性能开销（需求 6.4）
   */
  private notify() {
    if (this._isNotifying) {
      // 如果正在通知，标记有待处理的通知
      this._pendingNotify = true;
      return;
    }

    this._isNotifying = true;

    try {
      // 克隆日志列表，避免监听器直接修改原始数据
      const logsCopy = [...this.logs];
      this.listeners.forEach(listener => listener(logsCopy));
    } finally {
      this._isNotifying = false;
    }

    // 检查是否有待处理的通知
    if (this._pendingNotify) {
      this._pendingNotify = false;
      // 使用setTimeout进行节流，延迟10ms处理下一次通知
      setTimeout(() => this.notify(), 10);
    }
  }

  /**
   * 创建日志条目
   * 
   * @param level 日志级别
   * @param message 日志消息
   * @param options 额外选项
   * @returns 日志条目对象
   */
  private createEntry(
    level: LogLevel,
    message: string,
    options?: {
      context?: Record<string, any>;
      stack?: string;
      source?: string;
      category?: string;
    }
  ): LogEntry {
    const now = new Date();
    const timeString = now.toTimeString().split(' ')[0] + '.' + now.getMilliseconds().toString().padStart(3, '0');
    return {
      id: Math.random().toString(36).substr(2, 9),
      timestamp: timeString,
      level,
      message,
      context: options?.context,
      stack: options?.stack,
      source: options?.source || 'frontend',
      category: options?.category
    };
  }

  /**
   * 记录日志
   * 
   * @param level 日志级别
   * @param message 日志消息
   * @param options 额外选项
   */
  public log(
    level: LogLevel,
    message: string,
    options?: {
      context?: Record<string, any>;
      stack?: string;
      source?: string;
      category?: string;
    }
  ) {
    const entry = this.createEntry(level, message, options);
    this.logs.push(entry);

    // 限制日志数量，超出时移除最旧的日志
    if (this.logs.length > this.maxLogs) {
      this.logs.shift();
    }

    this.notify();
  }

  /**
   * 记录调试级别日志
   * 用于详细的调试信息，默认不显示在UI中
   */
  public debug(
    message: string,
    context?: Record<string, any>,
    category?: string
  ) {
    this.log('debug', message, { context, category });
  }

  /**
   * 记录信息级别日志
   * 用于关键事件和重要信息
   */
  public info(
    message: string,
    context?: Record<string, any>,
    category?: string
  ) {
    this.log('info', message, { context, category });
  }

  /**
   * 记录成功级别日志
   * 用于操作成功的提示
   */
  public success(
    message: string,
    context?: Record<string, any>,
    category?: string
  ) {
    this.log('success', message, { context, category });
  }

  /**
   * 记录警告级别日志
   * 用于非致命性问题
   */
  public warn(
    message: string,
    context?: Record<string, any>,
    category?: string
  ) {
    this.log('warn', message, { context, category });
  }

  /**
   * 记录错误级别日志
   * 用于错误和异常情况
   */
  public error(
    message: string,
    contextOrError?: Record<string, any> | Error,
    category?: string
  ) {
    let context: Record<string, any> | undefined;
    let stack: string | undefined;

    if (contextOrError instanceof Error) {
      stack = contextOrError.stack;
      context = {
        errorName: contextOrError.name,
        errorMessage: contextOrError.message
      };
    } else {
      context = contextOrError;
    }

    this.log('error', message, { context, stack, category });
  }

  /**
   * 订阅日志更新
   * 
   * @param listener 监听器函数，接收日志列表作为参数
   * @returns 取消订阅的函数
   */
  public subscribe(listener: Listener): () => void {
    this.listeners.add(listener);
    listener([...this.logs]); // 立即发送当前日志列表
    return () => {
      this.listeners.delete(listener);
    };
  }

  /**
   * 清空所有日志
   */
  public clear() {
    this.logs = [];
    this.notify();
  }

  /**
   * 记录下载相关日志
   */
  public download = {
    start: (message: string, context?: Record<string, any>) =>
      this.info(message, context, 'download'),
    progress: (message: string, context?: Record<string, any>) =>
      this.info(message, context, 'download'),
    success: (message: string, context?: Record<string, any>) =>
      this.success(message, context, 'download'),
    error: (message: string, errorOrContext?: Error | Record<string, any>) =>
      this.error(message, errorOrContext, 'download')
  };

  /**
   * 记录采集相关日志
   */
  public collection = {
    start: (message: string, context?: Record<string, any>) =>
      this.info(message, context, 'collection'),
    progress: (message: string, context?: Record<string, any>) =>
      this.info(message, context, 'collection'),
    success: (message: string, context?: Record<string, any>) =>
      this.success(message, context, 'collection'),
    error: (message: string, errorOrContext?: Error | Record<string, any>) =>
      this.error(message, errorOrContext, 'collection')
  };

  /**
   * 记录API相关日志
   */
  public api = {
    request: (message: string, context?: Record<string, any>) =>
      this.info(message, context, 'api'),
    response: (message: string, context?: Record<string, any>) =>
      this.info(message, context, 'api'),
    error: (message: string, errorOrContext?: Error | Record<string, any>) =>
      this.error(message, errorOrContext, 'api')
  };

  /**
   * 记录用户操作日志
   */
  public user = {
    action: (message: string, context?: Record<string, any>) =>
      this.info(message, context, 'user'),
    error: (message: string, errorOrContext?: Error | Record<string, any>) =>
      this.error(message, errorOrContext, 'user')
  };

  /**
   * 获取所有日志的文本格式
   * 用于导出或复制日志
   * 
   * @param includeContext 是否包含上下文信息
   * @param includeStack 是否包含堆栈信息
   * @returns 格式化的日志文本
   */
  public getAllLogsText(includeContext = false, includeStack = false): string {
    return this.logs.map(l => {
      let logLine = `[${l.timestamp}] [${l.level.toUpperCase()}]`;

      if (l.source) {
        logLine += ` [${l.source.toUpperCase()}]`;
      }

      if (l.category) {
        logLine += ` [${l.category}]`;
      }

      logLine += ` ${l.message}`;

      if (includeContext && l.context) {
        logLine += `\n  Context: ${JSON.stringify(l.context, null, 2)}`;
      }

      if (includeStack && l.stack) {
        logLine += `\n  Stack: ${l.stack}`;
      }

      return logLine;
    }).join('\n');
  }

  /**
   * 订阅后端日志
   * 接收后端发送的日志并整合到前端日志列表
   */
  private async subscribeToBackendLogs(): Promise<void> {
    try {
      // 订阅后端日志（异步）
      this.unsubscribeFromBackend = await bridge.subscribeToLogs((backendLog: any) => {
        try {
          // 将后端日志转换为前端日志格式
          const logLevel = this.mapBackendLogLevel(backendLog.level);
          const logEntry: LogEntry = {
            id: backendLog.id || Math.random().toString(36).substr(2, 9),
            timestamp: backendLog.timestamp || this.createEntry('info', '').timestamp,
            level: logLevel,
            message: backendLog.message || '',
            context: backendLog.context,
            stack: backendLog.stack,
            source: 'backend',
            category: backendLog.category
          };

          // 将后端日志添加到日志列表
          this.logs.push(logEntry);

          if (this.logs.length > this.maxLogs) {
            this.logs.shift();
          }

          this.notify();
        } catch (error) {
          // 减少日志输出，避免影响性能
        }
      });
    } catch (error) {
      // 减少日志输出，避免影响性能
    }
  }

  /**
   * 映射后端日志级别到前端日志级别
   * 
   * @param backendLevel 后端日志级别字符串
   * @returns 前端日志级别
   */
  private mapBackendLogLevel(backendLevel: string): LogLevel {
    const level = backendLevel.toLowerCase();
    switch (level) {
      case 'info':
      case 'debug':  // DEBUG 级别映射为 info
        return 'info';
      case 'success':
        return 'success';
      case 'warning':
      case 'warn':
        return 'warn';
      case 'error':
      case 'critical':  // CRITICAL 级别映射为 error
        return 'error';
      default:
        // 未知级别默认为 info
        return 'info';
    }
  }
}

// 导出单例实例
export const logger = new LoggerService();
