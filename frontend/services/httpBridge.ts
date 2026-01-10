/**
 * HTTP Bridge - 通过 FastAPI 与后端通信
 *
 * 使用 fetch API 调用 FastAPI 提供的 RESTful 接口
 * 与 pywebview bridge 保持完全相同的接口定义
 */

import { AppSettings, TaskType } from '../types';
import { handleError } from '../utils/errorHandler';
import { logger } from './logger';
import type { Bridge } from './bridge';
import { sseClient } from './sseClient';

/**
 * FastAPI 服务器配置
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

/**
 * 检查后端服务是否可用
 * 通过访问根路由来判断
 */
async function checkBackendAvailable(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api`, {
      method: 'GET',
      signal: AbortSignal.timeout(1000), // 1秒超时
    });
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * 通用 fetch 封装
 */
async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    logger.api.request('HTTP 请求', { url, options });

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    logger.api.response('HTTP 响应成功', { data });
    return data as T;
  } catch (error) {
    logger.api.error('HTTP 请求失败', error);
    throw error;
  }
}

/**
 * HTTP Bridge 实现
 * 与 pywebview bridge 保持完全相同的接口
 */
export const httpBridge: Bridge = {
  /**
   * 检查 HTTP 后端是否可用
   * 直接返回 true，实际可用性在调用时会体现
   */
  isAvailable: (): boolean => {
    return true;
  },

  /**
   * 等待后端 API 就绪
   * 通过轮询根路由来确认，并建立 SSE 连接
   */
  waitForReady: async (timeout: number = 30000): Promise<boolean> => {
    const startTime = Date.now();
    const checkInterval = 500; // 每 500ms 检查一次

    while (Date.now() - startTime < timeout) {
      const isAvailable = await checkBackendAvailable();

      if (isAvailable) {
        const elapsed = Date.now() - startTime;
        console.log(`[HTTP Bridge] FastAPI 服务已就绪 (${elapsed}ms)`);

        // 立即连接 SSE（这是关键！后端可能随时发送 evaluate_js）
        sseClient.connect(`${API_BASE_URL}/api/events`);

        // 等待 SSE 连接建立
        await new Promise(resolve => setTimeout(resolve, 500));

        if (sseClient.isConnected()) {
          console.log('[HTTP Bridge] SSE 连接成功，ready for evaluate_js');
          return true;
        } else {
          console.warn('[HTTP Bridge] SSE 连接失败，evaluate_js 将不可用');
          return true; // 即使 SSE 失败也返回 true，其他功能仍可用
        }
      }

      await new Promise(resolve => setTimeout(resolve, checkInterval));
    }

    console.error('[HTTP Bridge] 连接超时');
    return false;
  },

  /**
   * 开始采集任务
   */
  startTask: async (
    type: TaskType,
    target: string,
    limit: number = 0,
    filters?: Record<string, string>
  ): Promise<{ task_id: string; status: string }> => {
    try {
      logger.api.request('开始采集任务', { type, target, limit, filters });

      const result = await fetchAPI<{ task_id: string; status: string }>('/api/task/start', {
        method: 'POST',
        body: JSON.stringify({ type, target, limit, filters: filters || null }),
      });

      logger.api.response('采集任务启动成功', { taskId: result.task_id, status: result.status });
      return result;
    } catch (error) {
      handleError(error, { type, target, limit, filters }, {
        customMessage: '采集任务启动失败'
      });
      throw error;
    }
  },

  /**
   * 打开外部链接
   * HTTP 模式下使用 window.open
   */
  openExternal: (url: string) => {
    window.open(url, '_blank');
  },

  /**
   * 获取应用设置
   */
  getSettings: async (): Promise<AppSettings> => {
    try {
      const settings = await fetchAPI<AppSettings>('/api/settings');
      logger.api.response('获取应用设置成功');
      return settings;
    } catch (error) {
      handleError(error, {}, {
        customMessage: '获取应用设置失败',
        showToast: false
      });
      throw error;
    }
  },

  /**
   * 保存应用设置
   */
  saveSettings: async (settings: AppSettings): Promise<void> => {
    try {
      logger.api.request('保存应用设置', settings);

      await fetchAPI('/api/settings', {
        method: 'POST',
        body: JSON.stringify(settings),
      });

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
   * HTTP 模式下返回默认路径，无法打开系统对话框
   */
  selectFolder: async (): Promise<string> => {
    try {
      const result = await fetchAPI<{ folder_path: string }>('/api/file/select-folder', {
        method: 'POST',
      });
      return result.folder_path;
    } catch (error) {
      handleError(error, {}, {
        customMessage: '选择文件夹失败'
      });
      throw error;
    }
  },

  /**
   * 订阅后端日志
   * HTTP 模式不支持实时日志订阅，返回空函数
   * 注意：evaluate_js 通过 SSE 实现，但日志订阅仍不可用
   */
  subscribeToLogs: async (_callback: (log: any) => void): Promise<(() => void)> => {
    console.warn('[HTTP Bridge] 日志订阅功能在 HTTP 模式下不可用，请查看日志文件');
    return () => { }; // 返回空函数
  },

  /**
   * 获取任务状态
   */
  getTaskStatus: async (taskId?: string): Promise<any[]> => {
    try {
      const params = taskId ? `?task_id=${encodeURIComponent(taskId)}` : '';
      return await fetchAPI<any[]>(`/api/task/status${params}`);
    } catch (error) {
      handleError(error, { taskId }, {
        customMessage: '获取任务状态失败'
      });
      throw error;
    }
  },

  /**
   * 获取 Aria2 配置
   */
  getAria2Config: async (): Promise<{ host: string; port: number; secret: string }> => {
    try {
      return await fetchAPI<{ host: string; port: number; secret: string }>('/api/aria2/config');
    } catch (error) {
      handleError(error, {}, {
        customMessage: '获取 Aria2 配置失败'
      });
      throw error;
    }
  },

  /**
   * 检查是否首次运行
   */
  isFirstRun: async (): Promise<boolean> => {
    try {
      const result = await fetchAPI<{ is_first_run: boolean }>('/api/settings/first-run');
      return result.is_first_run;
    } catch (error) {
      handleError(error, {}, {
        customMessage: '检查首次运行失败'
      });
      return false;
    }
  },

  /**
   * 启动 Aria2 服务
   */
  startAria2: async (): Promise<void> => {
    try {
      await fetchAPI('/api/aria2/start', {
        method: 'POST',
      });
    } catch (error) {
      handleError(error, {}, {
        customMessage: '启动 Aria2 失败'
      });
      throw error;
    }
  },

  /**
   * 获取任务的采集结果
   */
  getTaskResults: async (taskId: string): Promise<any[]> => {
    try {
      const params = `?task_id=${encodeURIComponent(taskId)}`;
      return await fetchAPI<any[]>(`/api/task/results${params}`);
    } catch (error) {
      handleError(error, { taskId }, {
        customMessage: '获取任务结果失败'
      });
      throw error;
    }
  },

  /**
   * 获取系统剪贴板内容
   */
  getClipboardText: async (): Promise<string> => {
    try {
      const result = await fetchAPI<{ text: string }>('/api/system/clipboard');
      return result.text;
    } catch (error) {
      handleError(error, {}, {
        customMessage: '获取剪贴板内容失败'
      });
      throw error;
    }
  },

  /**
   * 读取配置文件
   */
  readConfigFile: async (filePath: string): Promise<string> => {
    try {
      const result = await fetchAPI<{ content: string }>('/api/file/read-config', {
        method: 'POST',
        body: JSON.stringify({ file_path: filePath }),
      });
      return result.content;
    } catch (error) {
      handleError(error, { filePath }, {
        customMessage: '读取配置文件失败'
      });
      throw error;
    }
  },

  /**
   * 获取 aria2 配置文件路径
   */
  getAria2ConfigPath: async (taskId?: string): Promise<string> => {
    try {
      const params = taskId ? `?task_id=${encodeURIComponent(taskId)}` : '';
      const result = await fetchAPI<{ config_path: string }>(`/api/aria2/config-path${params}`);
      return result.config_path;
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
      const result = await fetchAPI<{ exists: boolean }>('/api/file/check-exists', {
        method: 'POST',
        body: JSON.stringify({ file_path: filePath }),
      });
      return result.exists;
    } catch (error) {
      console.error('[HTTP Bridge] 检查文件存在失败:', error);
      return false;
    }
  },

  /**
   * 打开文件夹
   */
  openFolder: async (folderPath: string): Promise<boolean> => {
    try {
      console.log('[HTTP Bridge] 准备打开文件夹:', folderPath);
      const result = await fetchAPI<{ success: boolean }>('/api/file/open-folder', {
        method: 'POST',
        body: JSON.stringify({ folder_path: folderPath }),
      });
      console.log('[HTTP Bridge] 打开文件夹返回结果:', result);
      return result.success;
    } catch (error) {
      console.error('[HTTP Bridge] 打开文件夹失败:', error);
      return false;
    }
  }
};
