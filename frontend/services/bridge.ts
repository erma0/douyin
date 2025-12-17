
import { TaskType, AppSettings } from '../types';
import { logger } from './logger';
import { handleError } from '../utils/errorHandler';

/**
 * 前后端通信桥接服务
 */
export const bridge = {
  /**
   * 检查后端是否可用
   */
  isAvailable: (): boolean => {
    return typeof window.pywebview !== 'undefined' && typeof window.pywebview.api !== 'undefined';
  },

  /**
   * 等待后端 API 就绪
   * 使用 pywebviewready 事件确保 API 完全可用
   */
  waitForReady: (timeout: number = 30000): Promise<boolean> => {
    return new Promise((resolve) => {
      const startTime = Date.now();
      
      // 检查是否已经就绪
      if (window.pywebview?.api) {
        console.log('[Bridge] pywebview API 已就绪');
        resolve(true);
        return;
      }

      // 监听 pywebviewready 事件
      const onReady = () => {
        const elapsed = Date.now() - startTime;
        console.log(`[Bridge] pywebview API就绪 (${elapsed}ms)`);
        window.removeEventListener('pywebviewready', onReady);
        clearTimeout(timeoutId);
        resolve(true);
      };

      window.addEventListener('pywebviewready', onReady);

      // 超时处理
      const timeoutId = setTimeout(() => {
        window.removeEventListener('pywebviewready', onReady);
        console.error('[Bridge] 连接超时');
        resolve(false);
      }, timeout);
    });
  },

  /**
   * 开始采集任务（支持流式返回）
   * 
   * 注意：PyWebView 不支持直接传递 JavaScript 回调函数
   * 后端会通过 window.evaluate_js 调用前端全局函数 window.__douyinCallback
   * 前端需要在调用此方法前注册全局回调函数
   * 
   * @param type 任务类型
   * @param target 目标链接或关键词
   * @param limit 采集数量限制
   */
  startTask: async (
    type: TaskType, 
    target: string, 
    limit: number = 0
  ): Promise<{ task_id: string; status: string }> => {
    try {
      if (!window.pywebview) {
        throw new Error('Backend not available');
      }
      
      logger.api.request('开始采集任务', { type, target, limit });
      
      const result = await window.pywebview.api.start_task(type, target, limit);
      
      logger.api.response('采集任务启动成功', { taskId: result.task_id, status: result.status });
      return result as { task_id: string; status: string };
    } catch (error) {
      handleError(error, { type, target, limit }, { 
        customMessage: '采集任务启动失败' 
      });
      throw error;
    }
  },

  /**
   * 打开外部链接
   */
  openExternal: (url: string) => {
    if(window.pywebview) {
      window.pywebview.api.open_url(url);
    } else {
      window.open(url, '_blank');
    }
  },

  /**
   * 获取应用设置
   */
  getSettings: async (): Promise<AppSettings> => {
    try {
      if (!window.pywebview) {
        throw new Error('Backend not available');
      }
      
      const settings = await window.pywebview.api.get_settings();
      logger.api.response('获取应用设置成功');
      return settings;
    } catch (error) {
      handleError(error, {}, { 
        customMessage: '获取应用设置失败',
        showToast: false  // 设置获取失败不显示Toast，避免干扰用户
      });
      throw error;
    }
  },

  /**
   * 保存应用设置
   */
  saveSettings: async (settings: AppSettings): Promise<void> => {
    try {
      if (!window.pywebview) {
        throw new Error('Backend not available');
      }
      
      logger.api.request('保存应用设置', settings);
      await window.pywebview.api.save_settings(settings);
      logger.api.response('保存应用设置成功');
    } catch (error) {
      handleError(error, settings, { 
        customMessage: '保存应用设置失败' 
      });
      throw error;
    }
  },

  /**
   * 选择文件夹
   */
  selectFolder: async (): Promise<string> => {
    if (window.pywebview) {
      return await window.pywebview.api.select_folder();
    }
    throw new Error('Backend not available');
  },
  
  /**
   * 订阅后端日志
   */
  subscribeToLogs: async (callback: (log: any) => void): Promise<(() => void)> => {
    if (window.pywebview) {
      await (window.pywebview.api as any).subscribe_to_logs(callback);
      return () => {
        try {
          (window.pywebview.api as any).unsubscribe_from_logs(callback);
        } catch (error) {
          console.error('[Bridge] 取消订阅失败:', error);
        }
      };
    }
    return () => {};
  },
  
  /**
   * 获取任务状态
   */
  getTaskStatus: async (taskId?: string): Promise<any[]> => {
    if (window.pywebview) {
      return await (window.pywebview.api as any).get_task_status(taskId);
    }
    throw new Error('Backend not available');
  },
  
  /**
   * 获取 Aria2 配置
   */
  getAria2Config: async (): Promise<any> => {
    if (window.pywebview) {
      return await (window.pywebview.api as any).get_aria2_config();
    }
    throw new Error('Backend not available');
  },

  /**
   * 检查是否首次运行
   */
  isFirstRun: async (): Promise<boolean> => {
    if (window.pywebview) {
      return await (window.pywebview.api as any).is_first_run_check();
    }
    return false;
  },

  /**
   * 启动 Aria2 服务
   * 在前端 API 就绪后调用，确保不会过早启动
   */
  startAria2: async (): Promise<void> => {
    if (window.pywebview) {
      await (window.pywebview.api as any).start_aria2_after_loaded();
    }
  },

  /**
   * 获取任务的采集结果
   */
  getTaskResults: async (taskId: string): Promise<any[]> => {
    if (window.pywebview) {
      return await (window.pywebview.api as any).get_task_results(taskId);
    }
    throw new Error('Backend not available');
  },

  /**
   * 获取系统剪贴板内容（无需浏览器权限）
   */
  getClipboardText: async (): Promise<string> => {
    if (window.pywebview) {
      return await (window.pywebview.api as any).get_clipboard_text();
    }
    throw new Error('Backend not available');
  },

  /**
   * 读取配置文件
   */
  readConfigFile: async (filePath: string): Promise<string> => {
    try {
      if (!window.pywebview) {
        throw new Error('Backend not available');
      }
      
      return await (window.pywebview.api as any).read_config_file(filePath);
    } catch (error) {
      handleError(error, { filePath }, { 
        customMessage: '读取配置文件失败' 
      });
      throw error;
    }
  },

  /**
   * 从浏览器获取Cookie
   */
  getBrowserCookie: async (browser: string = 'chrome'): Promise<{
    success: boolean;
    cookie: string;
    error?: string;
  }> => {
    try {
      const result = await window.pywebview.api.get_browser_cookie(browser);
      return result;
    } catch (error) {
      handleError(error, { browser }, { 
        customMessage: '获取浏览器Cookie失败' 
      });
      throw error;
    }
  },

  /**
   * 获取aria2配置文件路径
   */
  getAria2ConfigPath: async (taskId?: string): Promise<string> => {
    try {
      if (!window.pywebview) {
        throw new Error('Backend not available');
      }
      
      return await (window.pywebview.api as any).get_aria2_config_path(taskId);
    } catch (error) {
      handleError(error, { taskId }, { 
        customMessage: '获取配置文件路径失败' 
      });
      throw error;
    }
  },

  /**
   * 检查文件是否存在
   */
  checkFileExists: async (filePath: string): Promise<boolean> => {
    try {
      if (!window.pywebview) {
        throw new Error('Backend not available');
      }
      
      return await (window.pywebview.api as any).check_file_exists(filePath);
    } catch (error) {
      console.error('[Bridge] 检查文件存在失败:', error);
      return false;
    }
  }
};