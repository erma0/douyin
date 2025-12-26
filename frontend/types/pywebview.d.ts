/**
 * PyWebView 类型声明
 * 为 window.pywebview API 提供完整的类型定义
 */

import { AppSettings, TaskType } from '../types';

declare global {
  interface Window {
    /**
     * PyWebView API 对象
     * 提供前后端通信接口
     */
    pywebview?: {
      api: {
        // 采集任务（支持流式返回）
        start_task: (
          type: TaskType,
          target: string,
          limit: number,
          callback?: (message: any) => void
        ) => Promise<{ task_id: string; status: string }>;

        // 系统功能
        open_url: (url: string) => void;
        get_settings: () => Promise<AppSettings>;
        save_settings: (settings: AppSettings) => Promise<void>;
        select_folder: () => Promise<string>;

        // Aria2配置
        get_aria2_config: () => Promise<{
          host: string;
          port: number;
          secret: string;
        }>;

        // 任务状态
        get_task_status: (task_id?: string) => Promise<any[]>;

        // 日志订阅
        subscribe_to_logs: (callback: (log: any) => void) => Promise<void>;
        unsubscribe_from_logs: (callback: (log: any) => void) => void;

        // 其他API方法
        is_first_run_check: () => Promise<boolean>;
        start_aria2_after_loaded: () => Promise<void>;
        get_task_results: (taskId: string) => Promise<any[]>;
        get_clipboard_text: () => Promise<string>;
        read_config_file: (filePath: string) => Promise<string>;
        get_aria2_config_path: (taskId?: string) => Promise<string>;
        check_file_exists: (filePath: string) => Promise<boolean>;
        open_folder: (folderPath: string) => Promise<boolean>;
      };
    };

    /**
     * Kiro Douyin 命名空间
     * 用于安全地管理全局回调函数，避免命名冲突
     */
    __kiro_douyin?: {
      /**
       * 采集任务回调函数
       * 由后端通过 evaluate_js 调用
       */
      taskCallback?: (message: {
        type: 'result' | 'complete' | 'error';
        data?: any[];
        total?: number;
        detected_type?: string;
        is_incremental?: boolean;
        error?: string;
      }) => void;
    };
  }
}

export { };

