/**
 * SSE 客户端 - 接收后端实时事件
 * 
 * 事件类型：
 * - task_result: 采集结果
 * - task_status: 任务状态变化
 * - task_error: 任务错误
 * - log: 日志消息
 */

import { DouyinWork } from '../types';

// ============================================================================
// 类型定义
// ============================================================================

/** SSE 事件类型 */
export type SSEEventType = 'task_result' | 'task_status' | 'task_error' | 'log';

/** 采集结果事件数据 */
export interface TaskResultEvent {
  task_id: string;
  data: DouyinWork[];
  total: number;
}

/** 任务状态事件数据 */
export interface TaskStatusEvent {
  task_id: string;
  status: string;
  progress?: number;
  result_count?: number;
  detected_type?: string;
  total?: number;
  is_incremental?: boolean;
}

/** 任务错误事件数据 */
export interface TaskErrorEvent {
  task_id: string;
  error: string;
}

/** 日志事件数据 */
export interface LogEvent {
  id: string;
  timestamp: string;
  level: string;
  message: string;
}

/** 事件处理器类型 */
type EventHandler<T> = (data: T) => void;

// ============================================================================
// SSE 客户端类
// ============================================================================

class SSEClient {
  private eventSource: EventSource | null = null;
  private url: string = '';
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000;
  
  // 事件处理器
  private handlers: {
    task_result: Set<EventHandler<TaskResultEvent>>;
    task_status: Set<EventHandler<TaskStatusEvent>>;
    task_error: Set<EventHandler<TaskErrorEvent>>;
    log: Set<EventHandler<LogEvent>>;
  } = {
    task_result: new Set(),
    task_status: new Set(),
    task_error: new Set(),
    log: new Set(),
  };
  
  /**
   * 连接到 SSE 端点
   */
  connect(url: string): void {
    // 检查是否已连接或正在连接中
    if (this.eventSource) {
      const state = this.eventSource.readyState;
      if (state === EventSource.OPEN || state === EventSource.CONNECTING) {
        console.warn('[SSE] 已连接或正在连接中，忽略重复连接');
        return;
      }
    }
    
    this.url = url;
    console.log('[SSE] 正在连接...', url);
    
    this.eventSource = new EventSource(url);
    
    this.eventSource.onopen = () => {
      console.log('[SSE] ✓ 连接成功');
      this.reconnectAttempts = 0;
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer);
        this.reconnectTimer = null;
      }
    };
    
    // 监听各类事件
    this.eventSource.addEventListener('task_result', (event) => {
      this.handleEvent('task_result', event);
    });
    
    this.eventSource.addEventListener('task_status', (event) => {
      this.handleEvent('task_status', event);
    });
    
    this.eventSource.addEventListener('task_error', (event) => {
      this.handleEvent('task_error', event);
    });
    
    this.eventSource.addEventListener('log', (event) => {
      this.handleEvent('log', event);
    });
    
    this.eventSource.onerror = (error) => {
      console.error('[SSE] 连接错误:', error);
      
      if (this.eventSource?.readyState === EventSource.CLOSED) {
        console.log('[SSE] 连接已关闭');
        this.handleReconnect();
      }
    };
  }
  
  /**
   * 处理事件
   */
  private handleEvent<T extends SSEEventType>(
    eventType: T,
    event: MessageEvent
  ): void {
    try {
      const data = JSON.parse(event.data);
      const handlers = this.handlers[eventType] as Set<EventHandler<unknown>>;
      
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (e) {
          console.error(`[SSE] 处理 ${eventType} 事件失败:`, e);
        }
      });
    } catch (e) {
      console.error(`[SSE] 解析 ${eventType} 事件数据失败:`, e);
    }
  }
  
  /**
   * 处理重连
   */
  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[SSE] 达到最大重连次数，放弃重连');
      return;
    }
    
    this.reconnectAttempts++;
    console.log(`[SSE] ${this.reconnectDelay / 1000}秒后尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
    
    this.reconnectTimer = setTimeout(() => {
      if (this.eventSource?.readyState === EventSource.CLOSED) {
        console.log('[SSE] 重新连接...');
        this.connect(this.url);
      }
    }, this.reconnectDelay);
  }
  
  /**
   * 断开连接
   */
  disconnect(): void {
    if (this.eventSource) {
      console.log('[SSE] 断开连接');
      this.eventSource.close();
      this.eventSource = null;
    }
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.reconnectAttempts = 0;
  }
  
  /**
   * 检查是否已连接
   */
  isConnected(): boolean {
    return this.eventSource?.readyState === EventSource.OPEN;
  }
  
  // ========================================================================
  // 事件订阅方法
  // ========================================================================
  
  /**
   * 订阅采集结果事件
   * @returns 取消订阅函数
   */
  onTaskResult(handler: EventHandler<TaskResultEvent>): () => void {
    this.handlers.task_result.add(handler);
    return () => this.handlers.task_result.delete(handler);
  }
  
  /**
   * 订阅任务状态事件
   * @returns 取消订阅函数
   */
  onTaskStatus(handler: EventHandler<TaskStatusEvent>): () => void {
    this.handlers.task_status.add(handler);
    return () => this.handlers.task_status.delete(handler);
  }
  
  /**
   * 订阅任务错误事件
   * @returns 取消订阅函数
   */
  onTaskError(handler: EventHandler<TaskErrorEvent>): () => void {
    this.handlers.task_error.add(handler);
    return () => this.handlers.task_error.delete(handler);
  }
  
  /**
   * 订阅日志事件
   * @returns 取消订阅函数
   */
  onLog(handler: EventHandler<LogEvent>): () => void {
    this.handlers.log.add(handler);
    return () => this.handlers.log.delete(handler);
  }
  
  /**
   * 通用事件订阅
   * @returns 取消订阅函数
   */
  on<T extends SSEEventType>(
    eventType: T,
    handler: EventHandler<
      T extends 'task_result' ? TaskResultEvent :
      T extends 'task_status' ? TaskStatusEvent :
      T extends 'task_error' ? TaskErrorEvent :
      LogEvent
    >
  ): () => void {
    const handlers = this.handlers[eventType] as Set<EventHandler<unknown>>;
    handlers.add(handler);
    return () => handlers.delete(handler);
  }
  
  /**
   * 移除所有事件处理器
   */
  removeAllHandlers(): void {
    this.handlers.task_result.clear();
    this.handlers.task_status.clear();
    this.handlers.task_error.clear();
    this.handlers.log.clear();
  }
}

// 导出单例
export const sseClient = new SSEClient();

export default sseClient;
