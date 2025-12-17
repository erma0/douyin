/**
 * 全局回调管理器
 * 提供安全的全局回调函数注册和清理机制
 * 
 * 解决问题：
 * 1. 避免全局命名空间污染
 * 2. 防止回调函数被意外覆盖
 * 3. 确保回调函数能被正确清理，避免内存泄漏
 */

/**
 * 任务回调消息类型
 */
export interface TaskCallbackMessage {
  type: 'result' | 'complete' | 'error';
  data?: any[];
  total?: number;
  detected_type?: string;
  is_incremental?: boolean;
  error?: string;
}

/**
 * 任务回调函数类型
 */
export type TaskCallback = (message: TaskCallbackMessage) => void;

/**
 * 全局回调管理器类
 */
class CallbackManager {
  private static instance: CallbackManager;
  private isInitialized: boolean = false;

  private constructor() {
    this.initializeNamespace();
  }

  /**
   * 获取单例实例
   */
  public static getInstance(): CallbackManager {
    if (!CallbackManager.instance) {
      CallbackManager.instance = new CallbackManager();
    }
    return CallbackManager.instance;
  }

  /**
   * 初始化全局命名空间
   * 确保 window.__kiro_douyin 对象存在
   */
  private initializeNamespace(): void {
    if (this.isInitialized) {
      return;
    }

    if (typeof window !== 'undefined') {
      // 创建命名空间，避免覆盖已存在的对象
      window.__kiro_douyin = window.__kiro_douyin || {};
      this.isInitialized = true;
    }
  }

  /**
   * 注册任务回调函数
   * 
   * @param callback 回调函数
   * @returns 清理函数，用于取消注册
   * 
   * @example
   * const cleanup = callbackManager.registerTaskCallback((message) => {
   *   console.log('收到消息:', message);
   * });
   * 
   * // 使用完毕后清理
   * cleanup();
   */
  public registerTaskCallback(callback: TaskCallback): () => void {
    this.initializeNamespace();

    if (!window.__kiro_douyin) {
      console.error('[CallbackManager] 命名空间初始化失败');
      return () => {};
    }

    // 检查是否已有回调函数注册
    if (window.__kiro_douyin.taskCallback) {
      console.warn('[CallbackManager] 已存在任务回调函数，将被覆盖');
    }

    // 注册回调函数
    window.__kiro_douyin.taskCallback = callback;

    // 返回清理函数
    return () => {
      this.unregisterTaskCallback();
    };
  }

  /**
   * 取消注册任务回调函数
   * 清理全局回调引用，避免内存泄漏
   */
  public unregisterTaskCallback(): void {
    if (window.__kiro_douyin) {
      delete window.__kiro_douyin.taskCallback;
    }
  }

  /**
   * 检查是否已注册回调函数
   */
  public hasTaskCallback(): boolean {
    return !!(window.__kiro_douyin && window.__kiro_douyin.taskCallback);
  }

  /**
   * 手动触发回调（用于测试）
   * 
   * @param message 回调消息
   */
  public triggerTaskCallback(message: TaskCallbackMessage): void {
    if (window.__kiro_douyin?.taskCallback) {
      window.__kiro_douyin.taskCallback(message);
    } else {
      console.warn('[CallbackManager] 没有注册的任务回调函数');
    }
  }
}

// 导出单例实例
export const callbackManager = CallbackManager.getInstance();

/**
 * 便捷函数：注册任务回调
 * 
 * @param callback 回调函数
 * @returns 清理函数
 */
export function registerTaskCallback(callback: TaskCallback): () => void {
  return callbackManager.registerTaskCallback(callback);
}

/**
 * 便捷函数：取消注册任务回调
 */
export function unregisterTaskCallback(): void {
  callbackManager.unregisterTaskCallback();
}
