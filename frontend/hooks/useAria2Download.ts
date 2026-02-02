/**
 * Aria2下载管理Hook
 * 封装所有下载相关逻辑
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { toast } from '../components/Toast';
import { aria2Service } from '../services/aria2Service';
import { bridge } from '../services/bridge';
import { logger } from '../services/logger';
import { parseAria2Config } from '../utils/aria2ConfigParser';

/**
 * 下载信息接口
 */
interface DownloadInfo {
  workId: string;
  gid: string;
  filename: string;
  url: string;
}



/**
 * 下载统计接口
 */
interface DownloadStats {
  activeCount: number;
  downloadSpeed: number;
  totalProgress: number;
}

/**
 * Aria2下载管理Hook
 */
export const useAria2Download = () => {
  // 状态管理
  const [connected, setConnected] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [progress, setProgress] = useState<Record<string, number>>({});
  const [downloadStats, setDownloadStats] = useState<DownloadStats>({
    activeCount: 0,
    downloadSpeed: 0,
    totalProgress: 0,
  });

  // 引用管理
  const downloadsRef = useRef<Map<string, DownloadInfo>>(new Map());
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const onCompleteCallbackRef = useRef<(() => void) | null>(null);
  const statsRef = useRef<{ completed: number; failed: number }>({ completed: 0, failed: 0 });
  const prevConnectedRef = useRef(false);

  /**
   * 初始化Aria2连接
   * 需求 6.3: 清理事件监听器和定时器，避免内存泄漏
   */
  useEffect(() => {
    const unsubscribe = aria2Service.onConnectionChange((isConnected) => {
      console.log(`[useAria2Download] 连接状态变化: ${isConnected}, 之前: ${prevConnectedRef.current}`);

      // 只在状态从 false 变为 true 时显示提示
      if (isConnected && !prevConnectedRef.current) {
        console.log('[useAria2Download] 显示连接成功提示');
        toast.success('Aria2 下载服务已连接');
        logger.success('Aria2 下载服务已连接');
      }
      prevConnectedRef.current = isConnected;
      setConnected(isConnected);
    });

    const initAria2 = async () => {
      const ready = await bridge.waitForReady(30000);
      if (!ready) return;

      try {
        const config = await bridge.getAria2Config();
        // 启动连接（后台异步进行）
        await aria2Service.connect(config.host, config.port, config.secret, true);
        logger.info('Aria2下载服务初始化完成');
      } catch (error) {
        console.error('[useAria2Download] 初始化失败:', error);
        logger.error('Aria2下载服务初始化失败', error instanceof Error ? error : undefined);
      }
    };

    initAria2();

    // 清理函数：确保组件卸载时清理所有资源
    return () => {
      // 取消订阅连接状态变化
      unsubscribe();

      // 清理轮询定时器
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }

      // 清理回调引用
      onCompleteCallbackRef.current = null;
    };
  }, []);

  /**
   * 开始轮询下载进度
   * 需求 6.2: 确保轮询间隔为1秒，实现智能轮询停止，避免重复启动轮询
   */
  const startPolling = useCallback(() => {
    // 避免重复启动轮询
    if (pollIntervalRef.current) {
      return;
    }

    // 如果没有任务，不启动轮询
    if (downloadsRef.current.size === 0) {
      return;
    }

    // 不要重置统计，保持累计数据
    if (!statsRef.current) {
      statsRef.current = { completed: 0, failed: 0 };
    }

    // 轮询间隔固定为1秒
    pollIntervalRef.current = setInterval(async () => {
      const downloads = downloadsRef.current;

      // 智能轮询停止：如果没有任务，立即停止轮询
      if (downloads.size === 0) {
        setDownloading(false);
        setDownloadStats({ activeCount: 0, downloadSpeed: 0, totalProgress: 0 });
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }

        const { completed, failed } = statsRef.current;
        if (completed > 0 || failed > 0) {
          logger.info(`所有下载任务完成：成功 ${completed} 个${failed > 0 ? `，失败 ${failed} 个` : ''}`);
          toast.success(`下载完成！成功 ${completed} 个${failed > 0 ? `，失败 ${failed} 个` : ''}`);

          if (onCompleteCallbackRef.current) {
            onCompleteCallbackRef.current();
            onCompleteCallbackRef.current = null;
          }
        }
        return;
      }

      setDownloading(true);
      const newProgress: Record<string, number> = {};
      let currentSpeed = 0;

      // 使用批量查询，包括已停止的任务（完成/失败）
      try {
        const activeTasks = await aria2Service.getActiveTasks();
        const waitingTasks = await aria2Service.getWaitingTasks();
        const stoppedTasks = await aria2Service.getStoppedTasks();
        const allTasks = [...activeTasks, ...waitingTasks, ...stoppedTasks];

        // 计算总下载速度
        currentSpeed = activeTasks.reduce((sum, task) => sum + (task.downloadSpeed || 0), 0);

        // 创建GID到任务的映射
        const taskMap = new Map(allTasks.map(task => [task.gid, task]));

        for (const [workId, info] of downloads.entries()) {
          const task = taskMap.get(info.gid);
          if (task) {
            newProgress[workId] = task.progress;

            if (task.status === 'waiting') {
              newProgress[workId] = 0;
            } else if (task.status === 'complete') {
              logger.info(`下载完成: ${info.filename}`);
              downloads.delete(workId);
              statsRef.current.completed++;
              newProgress[workId] = 100;
            } else if (task.status === 'error') {
              const errorMsg = task.errorMessage || task.errorCode || '未知错误';
              logger.error(`下载失败: ${info.filename} - ${errorMsg}`);
              downloads.delete(workId);
              newProgress[workId] = -1;
              statsRef.current.failed++;
            } else if (task.status === 'removed') {
              downloads.delete(workId);
              statsRef.current.failed++;
            }
          } else {
            // 任务不在任何列表中，可能已被清理
            // 从跟踪列表中移除，避免无限轮询
            console.log(`[useAria2Download] 任务 ${workId} 不在 aria2 列表中，移除跟踪`);
            downloads.delete(workId);
          }
        }
      } catch (error) {
        console.error('[useAria2Download] 批量查询失败:', error);
      }

      // 更新进度
      setProgress(prev => ({ ...prev, ...newProgress }));

      // 计算活跃任务数和总进度
      let activeCount = 0;
      let totalProgress = 0;
      for (const [workId, _] of downloads.entries()) {
        const prog = newProgress[workId] || 0;
        if (prog > 0 && prog < 100) {
          activeCount++;
          totalProgress += prog;
        }
      }

      // 更新下载统计
      setDownloadStats({
        activeCount: downloads.size,
        downloadSpeed: currentSpeed,
        totalProgress: activeCount > 0 ? Math.round(totalProgress / activeCount) : 0,
      });
    }, 1000);
  }, []);

  /**
   * 停止轮询
   */
  const stopPolling = useCallback(() => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  }, []);

  /**
   * 设置完成回调
   */
  const setOnComplete = useCallback((callback: () => void) => {
    onCompleteCallbackRef.current = callback;
  }, []);

  /**
   * 取消所有下载
   * 需求 6.3: 确保及时清理内存中的任务信息
   */
  const cancelAll = useCallback(async () => {
    const downloads = downloadsRef.current;
    if (downloads.size === 0) return;

    for (const [workId, info] of downloads.entries()) {
      try {
        await aria2Service.cancel(info.gid);
      } catch (error) {
        // 静默处理取消失败
      }
    }

    // 立即清空所有任务引用，避免内存泄漏
    downloads.clear();

    // 停止轮询并清理定时器
    setDownloading(false);
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }

    // 清空进度状态
    setProgress({});

    // 重置统计
    statsRef.current = { completed: 0, failed: 0 };

    // 清理完成回调
    onCompleteCallbackRef.current = null;

    toast.success('已取消所有下载任务');
    logger.info('已取消所有下载任务');
  }, []);

  /**
   * 添加单个下载任务
   */
  const addDownload = useCallback(async (
    workId: string,
    url: string,
    filename: string,
    downloadPath: string,
    cookie?: string
  ): Promise<boolean> => {
    if (!connected) {
      toast.error('Aria2下载服务未连接');
      logger.error('添加下载失败: Aria2服务未连接');
      return false;
    }

    // 将options定义移到try外面，这样catch块也能访问
    const options: Record<string, any> = {
      dir: downloadPath,
      out: filename
    };

    if (cookie) {
      options.header = [`Cookie: ${cookie}`];
    }

    try {
      const gid = await aria2Service.addDownload(url, options);

      if (!gid) {
        throw new Error('Aria2返回的GID为空');
      }

      // 确保任务添加后正确加入跟踪映射表
      downloadsRef.current.set(workId, { workId, gid, filename, url });

      // 初始化进度为0
      setProgress(prev => ({ ...prev, [workId]: 0 }));
      setDownloading(true);

      // 启动轮询（避免重复启动）
      if (!pollIntervalRef.current) {
        startPolling();
      }

      return true;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);

      if (errorMsg.includes('connect') || errorMsg.includes('连接')) {
        toast.error(`Aria2连接失败，请检查服务状态`);
        logger.error(`Aria2连接失败: ${errorMsg}`);
      } else if (errorMsg.includes('timeout') || errorMsg.includes('超时')) {
        toast.error(`下载请求超时: ${filename}`);
        logger.error(`下载请求超时: ${filename}`);
      } else {
        toast.error(`下载失败: ${filename} - ${errorMsg}`);
        logger.error(`下载失败: ${filename} - ${errorMsg}`);
      }

      return false;
    }
  }, [connected, startPolling]);



  /**
   * 暂停下载
   */
  const pauseDownload = useCallback(async (workId: string): Promise<boolean> => {
    const info = downloadsRef.current.get(workId);
    if (!info) return false;
    try {
      await aria2Service.pause(info.gid);
      return true;
    } catch (error) {
      return false;
    }
  }, []);

  /**
   * 恢复下载
   */
  const resumeDownload = useCallback(async (workId: string): Promise<boolean> => {
    const info = downloadsRef.current.get(workId);
    if (!info) return false;
    try {
      await aria2Service.resume(info.gid);
      return true;
    } catch (error) {
      return false;
    }
  }, []);

  /**
   * 取消下载
   * 需求 6.3: 确保任务取消后及时清理内存
   */
  const cancelDownload = useCallback(async (workId: string): Promise<boolean> => {
    const info = downloadsRef.current.get(workId);
    if (!info) return false;

    try {
      await aria2Service.cancel(info.gid);

      // 立即从跟踪映射表中移除
      downloadsRef.current.delete(workId);

      // 清除进度状态
      setProgress(prev => {
        const newProgress = { ...prev };
        delete newProgress[workId];
        return newProgress;
      });

      return true;
    } catch (error) {
      console.error('[useAria2Download] 取消任务失败:', error);
      // 即使取消失败也从映射表中移除，避免内存泄漏
      downloadsRef.current.delete(workId);
      return false;
    }
  }, []);

  /**
   * 获取全局统计
   */
  const getGlobalStat = useCallback(async () => {
    if (!connected) return null;
    return await aria2Service.getGlobalStat();
  }, [connected]);

  /**
   * 获取活动任务列表
   */
  const getActiveTasks = useCallback(async () => {
    if (!connected) return [];
    return await aria2Service.getActiveTasks();
  }, [connected]);

  /**
   * 从配置文件批量下载
   * 使用parseAria2Config解析配置文件，然后逐个调用addDownload提交任务
   */
  const batchDownloadFromConfig = useCallback(async (configFilePath: string): Promise<void> => {
    if (!connected) {
      toast.error('Aria2下载服务未连接，请检查服务状态');
      logger.error('批量下载失败: Aria2服务未连接');
      return;
    }

    try {
      logger.info(`开始批量下载，配置文件: ${configFilePath}`);

      // 添加文件存在性检查
      const fileExists = await bridge.checkFileExists(configFilePath);
      if (!fileExists) {
        const errorMsg = `配置文件不存在: ${configFilePath}`;
        toast.error(errorMsg);
        logger.error(errorMsg);
        return;
      }


      let configContent: string;
      try {
        configContent = await bridge.readConfigFile(configFilePath);
      } catch (error) {
        const errorMsg = `读取配置文件失败: ${configFilePath} - ${error instanceof Error ? error.message : String(error)}`;
        toast.error(errorMsg);
        logger.error(errorMsg);
        return;
      }

      // 解析任务列表
      const tasks = parseAria2Config(configContent);

      if (tasks.length === 0) {
        toast.warning('配置文件中没有找到有效的下载任务');
        logger.warn('配置文件中没有找到有效的下载任务');
        return;
      }

      logger.info(`开始批量下载 ${tasks.length} 个任务`);
      toast.info(`开始批量下载 ${tasks.length} 个任务`);

      let cookie = '';
      try {
        const settings = await bridge.getSettings();
        cookie = settings.cookie || '';
      } catch (error) {
        logger.warn('获取Cookie失败，将不使用Cookie进行下载');
      }

      // 重置统计
      statsRef.current = { completed: 0, failed: 0 };
      let successCount = 0;
      let failCount = 0;

      // 处理部分任务失败的情况：逐个调用addDownload提交任务
      for (let i = 0; i < tasks.length; i++) {
        const task = tasks[i];
        const workId = `batch_${i + 1}_${Date.now()}`;

        try {
          const result = await addDownload(workId, task.url, task.out, task.dir, cookie);

          if (result) {
            successCount++;
          } else {
            failCount++;
            logger.warn(`任务添加失败: ${task.out}`);
          }
        } catch (error) {
          failCount++;
          const errorMsg = error instanceof Error ? error.message : String(error);
          logger.error(`任务添加异常: ${task.out} - ${errorMsg}`);
        }
      }

      // 显示结果提示
      if (successCount > 0) {
        toast.success(`成功添加 ${successCount} 个下载任务${failCount > 0 ? `，${failCount} 个失败` : ''}`);
      } else if (failCount > 0) {
        toast.error(`所有任务添加失败 (${failCount} 个)`);
      }

      if (failCount > 0 && successCount > 0) {
        logger.warn(`批量任务添加部分失败: 成功 ${successCount} 个，失败 ${failCount} 个`);
      } else if (successCount > 0) {
        logger.info(`批量任务添加完成: 成功 ${successCount} 个，失败 ${failCount} 个，正在后台下载...`);
      } else {
        logger.info(`批量任务添加完成: 成功 ${successCount} 个，失败 ${failCount} 个`);
      }

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error(`批量下载失败: ${errorMsg}`);
      toast.error(`批量下载失败: ${errorMsg}`);
    }
  }, [connected, addDownload]);

  return {
    connected,
    downloading,
    progress,
    downloadStats,
    addDownload,
    batchDownloadFromConfig,
    pauseDownload,
    resumeDownload,
    cancelDownload,
    cancelAll,
    getGlobalStat,
    getActiveTasks,
    startPolling,
    stopPolling,
    setOnComplete,
  };
};
