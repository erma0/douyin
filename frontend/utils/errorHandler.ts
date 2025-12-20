/**
 * 统一错误处理工具
 * 提供错误分类、友好提示和日志记录功能
 */

import { toast } from '../components/Toast';
import { logger } from '../services/logger';

/**
 * 错误类型枚举
 */
export enum ErrorType {
  NETWORK = 'network',           // 网络错误
  PERMISSION = 'permission',     // 权限错误
  COOKIE = 'cookie',            // Cookie相关错误
  FILE_NOT_FOUND = 'file_not_found', // 文件不存在
  ARIA2 = 'aria2',              // Aria2服务错误
  BACKEND = 'backend',          // 后端服务错误
  VALIDATION = 'validation',    // 输入验证错误
  UNKNOWN = 'unknown'           // 未知错误
}

/**
 * 错误信息接口
 */
export interface ErrorInfo {
  type: ErrorType;
  message: string;
  originalError?: Error | string;
  context?: Record<string, any>;
  timestamp: Date;
  userMessage: string;  // 用户友好的错误提示
  actionable?: boolean; // 是否可操作（用户可以采取行动解决）
  suggestion?: string;  // 解决建议
}

/**
 * 错误分类器
 * 根据错误消息内容自动识别错误类型
 */
export class ErrorClassifier {
  private static patterns: Record<ErrorType, RegExp[]> = {
    [ErrorType.NETWORK]: [
      /网络/i,
      /连接/i,
      /network/i,
      /connection/i,
      /timeout/i,
      /fetch/i,
      /ECONNREFUSED/i,
      /ENOTFOUND/i
    ],
    [ErrorType.PERMISSION]: [
      /权限/i,
      /permission/i,
      /access denied/i,
      /forbidden/i,
      /unauthorized/i,
      /403/,
      /401/
    ],
    [ErrorType.COOKIE]: [
      /cookie/i,
      /登录/i,
      /身份/i,
      /认证/i,
      /authentication/i,
      /session/i,
      /token/i
    ],
    [ErrorType.FILE_NOT_FOUND]: [
      /文件不存在/i,
      /未找到/i,
      /配置文件/i,
      /file not found/i,
      /no such file/i,
      /ENOENT/i,
      /404/
    ],
    [ErrorType.ARIA2]: [
      /aria2/i,
      /下载服务/i,
      /download service/i,
      /rpc.*失败/i,
      /rpc.*连接/i,
      /6800/
    ],
    [ErrorType.BACKEND]: [
      /backend not available/i,
      /后端服务/i,
      /pywebview/i,
      /主程序/i
    ],
    [ErrorType.VALIDATION]: [
      /输入/i,
      /验证/i,
      /validation/i,
      /invalid/i,
      /格式/i,
      /长度/i
    ],
    [ErrorType.UNKNOWN]: [
      // UNKNOWN类型不需要匹配模式，作为默认类型
    ]
  };

  /**
   * 分类错误类型
   */
  static classify(error: Error | string): ErrorType {
    const errorMessage = typeof error === 'string' ? error : error.message;

    // 按优先级顺序检查，更具体的错误类型优先
    const priorityOrder = [
      ErrorType.ARIA2,
      ErrorType.BACKEND,
      ErrorType.COOKIE,
      ErrorType.FILE_NOT_FOUND,
      ErrorType.VALIDATION,
      ErrorType.PERMISSION,
      ErrorType.NETWORK,
      ErrorType.UNKNOWN
    ];

    for (const type of priorityOrder) {
      const patterns = this.patterns[type];
      if (patterns.some(pattern => pattern.test(errorMessage))) {
        return type;
      }
    }

    return ErrorType.UNKNOWN;
  }
}

/**
 * 错误消息生成器
 * 根据错误类型生成用户友好的提示消息
 */
export class ErrorMessageGenerator {
  private static messages: Record<ErrorType, {
    userMessage: string;
    suggestion?: string;
    actionable: boolean;
  }> = {
      [ErrorType.NETWORK]: {
        userMessage: '网络连接失败，请检查网络设置',
        suggestion: '请检查网络连接或稍后重试',
        actionable: true
      },
      [ErrorType.PERMISSION]: {
        userMessage: '权限不足，无法执行操作',
        suggestion: '请检查文件权限或以管理员身份运行',
        actionable: true
      },
      [ErrorType.COOKIE]: {
        userMessage: 'Cookie可能已失效，请更新登录信息',
        suggestion: '请在设置中更新Cookie',
        actionable: true
      },
      [ErrorType.FILE_NOT_FOUND]: {
        userMessage: '未找到相关文件或数据',
        suggestion: '请先完成采集任务或检查文件路径',
        actionable: true
      },
      [ErrorType.ARIA2]: {
        userMessage: 'Aria2下载服务异常',
        suggestion: '请检查下载服务配置或重启应用',
        actionable: true
      },
      [ErrorType.BACKEND]: {
        userMessage: '后端服务不可用',
        suggestion: '请确保主程序正在运行',
        actionable: true
      },
      [ErrorType.VALIDATION]: {
        userMessage: '输入内容格式不正确',
        suggestion: '请检查输入内容并重新输入',
        actionable: true
      },
      [ErrorType.UNKNOWN]: {
        userMessage: '发生未知错误',
        suggestion: '请稍后重试或联系技术支持',
        actionable: false
      }
    };

  /**
   * 生成用户友好的错误信息
   */
  static generate(type: ErrorType, originalMessage?: string): {
    userMessage: string;
    suggestion?: string;
    actionable: boolean;
  } {
    const template = this.messages[type];

    // 对于某些错误类型，可以使用原始消息的部分内容
    if (originalMessage && type === ErrorType.VALIDATION) {
      return {
        ...template,
        userMessage: originalMessage
      };
    }

    return template;
  }
}

/**
 * 统一错误处理器
 */
export class ErrorHandler {
  /**
   * 处理错误
   * @param error 原始错误
   * @param context 错误上下文信息
   * @param showToast 是否显示Toast提示
   * @param logLevel 日志级别
   */
  static handle(
    error: Error | string,
    context?: Record<string, any>,
    options?: {
      showToast?: boolean;
      logLevel?: 'error' | 'warn' | 'info';
      customMessage?: string;
    }
  ): ErrorInfo {
    const {
      showToast = true,
      logLevel = 'error',
      customMessage
    } = options || {};

    // 分类错误
    const type = ErrorClassifier.classify(error);

    // 生成用户友好消息
    const messageInfo = customMessage
      ? { userMessage: customMessage, actionable: true }
      : ErrorMessageGenerator.generate(type, typeof error === 'string' ? error : error.message);

    // 构建错误信息对象
    const errorInfo: ErrorInfo = {
      type,
      message: typeof error === 'string' ? error : error.message,
      originalError: error,
      context,
      timestamp: new Date(),
      userMessage: messageInfo.userMessage,
      actionable: messageInfo.actionable,
      suggestion: messageInfo.suggestion
    };

    // 记录详细日志
    const logMessage = `[${type.toUpperCase()}] ${errorInfo.message}`;
    const logContext = {
      type,
      context,
      timestamp: errorInfo.timestamp.toISOString(),
      stack: error instanceof Error ? error.stack : undefined
    };

    switch (logLevel) {
      case 'error':
        logger.error(logMessage, logContext);
        break;
      case 'warn':
        logger.warn(logMessage, logContext);
        break;
      case 'info':
        logger.info(logMessage, logContext);
        break;
    }

    // 显示用户提示
    if (showToast) {
      const toastMessage = messageInfo.suggestion
        ? `${messageInfo.userMessage}。${messageInfo.suggestion}`
        : messageInfo.userMessage;

      switch (type) {
        case ErrorType.NETWORK:
        case ErrorType.BACKEND:
        case ErrorType.ARIA2:
          toast.error(toastMessage);
          break;
        case ErrorType.COOKIE:
        case ErrorType.FILE_NOT_FOUND:
          toast.warning(toastMessage);
          break;
        case ErrorType.VALIDATION:
          toast.info(toastMessage);
          break;
        default:
          toast.error(toastMessage);
      }
    }

    return errorInfo;
  }

  /**
   * 处理异步操作错误
   * 专门用于Promise.catch()
   */
  static async handleAsync(
    error: Error | string,
    context?: Record<string, any>,
    options?: {
      showToast?: boolean;
      logLevel?: 'error' | 'warn' | 'info';
      customMessage?: string;
      rethrow?: boolean;
    }
  ): Promise<ErrorInfo> {
    const { rethrow = false, ...handlerOptions } = options || {};

    const errorInfo = this.handle(error, context, handlerOptions);

    if (rethrow) {
      throw error;
    }

    return errorInfo;
  }

  /**
   * 创建错误处理装饰器
   * 用于包装函数，自动处理错误
   */
  static withErrorHandling<T extends (...args: any[]) => any>(
    fn: T,
    context?: Record<string, any>,
    options?: {
      showToast?: boolean;
      logLevel?: 'error' | 'warn' | 'info';
      fallbackValue?: any;
    }
  ): T {
    const { fallbackValue, ...handlerOptions } = options || {};

    return ((...args: Parameters<T>) => {
      try {
        const result = fn(...args);

        // 处理Promise返回值
        if (result instanceof Promise) {
          return result.catch((error) => {
            this.handle(error, { ...context, args }, handlerOptions);
            return fallbackValue;
          });
        }

        return result;
      } catch (error) {
        this.handle(error, { ...context, args }, handlerOptions);
        return fallbackValue;
      }
    }) as T;
  }
}

/**
 * 便捷的错误处理函数
 */
export const handleError = ErrorHandler.handle;
export const handleAsyncError = ErrorHandler.handleAsync;
export const withErrorHandling = ErrorHandler.withErrorHandling;