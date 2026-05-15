import { useCallback, useRef } from 'react';
import { sseClient, TaskResultEvent, TaskStatusEvent, TaskErrorEvent } from '../services/sseClient';
import { bridge } from '../services/bridge';
import { logger } from '../services/logger';
import { toast } from '../components/Toast';
import { TaskType } from '../types';
import { FilterSettings } from '../components/SearchFilter';
import { useAppStore } from '../stores/appStore';

export function useTaskManager() {
  const currentTaskIdRef = useRef<string | null>(null);

  const activeTab = useAppStore((s) => s.activeTab);
  const inputVal = useAppStore((s) => s.inputVal);
  const maxCount = useAppStore((s) => s.maxCount);
  const filters = useAppStore((s) => s.filters);

  const validateInput = useCallback((): boolean => {
    const { inputVal: val, activeTab: tab, setInputError } = useAppStore.getState();
    const trimmedVal = val.trim().replace(/^\/+|\/+$/g, '');

    if (!trimmedVal) {
      setInputError('请输入内容');
      return false;
    }

    if (trimmedVal.length < 2) {
      setInputError('输入内容过短');
      return false;
    }

    if (tab === TaskType.SEARCH) {
      if (trimmedVal.length > 20) {
        setInputError('搜索关键词不能超过20个字符');
        return false;
      }
      const hasInvalidChars = /[<>{}[\]\\\/|`~!@#$%^&*()+=;:'"?]/.test(trimmedVal);
      if (hasInvalidChars) {
        setInputError('搜索关键词不能包含特殊符号');
        return false;
      }
    }

    setInputError(null);
    return true;
  }, []);

  const handleSearch = useCallback(async () => {
    if (!validateInput()) return;

    const {
      activeTab: tab,
      inputVal: val,
      maxCount: count,
      filters: f,
      setIsLoading,
      appendResults,
      setResultsTaskType,
      setSavedInputVal,
      setCurrentTaskId,
      setActiveTab,
      clearResults,
    } = useAppStore.getState();

    clearResults();
    setResultsTaskType(tab);
    setSavedInputVal(val);
    setIsLoading(true);

    let taskId: string | null = null;

    const unsubResult = sseClient.onTaskResult((event: TaskResultEvent) => {
      if (taskId && event.task_id === taskId) {
        appendResults(event.data || []);
        logger.info(`已采集 ${event.total} 条数据`);
      }
    });

    const unsubStatus = sseClient.onTaskStatus((event: TaskStatusEvent) => {
      if (taskId && event.task_id === taskId && (event.status === 'completed' || event.status === 'cancelled')) {
        setIsLoading(false);
        setCurrentTaskId(taskId);
        logger.info(`保存任务ID: ${taskId}`);

        if (event.detected_type && event.detected_type !== tab) {
          const detectedType = event.detected_type as TaskType;
          setActiveTab(detectedType);
          setResultsTaskType(detectedType);
          logger.info(`后端识别类型: ${event.detected_type}，自动切换面板`);
        }

        if (event.status === 'cancelled') {
          const total = event.total || 0;
          if (total > 0) {
            logger.info(`采集已取消，已获取到 ${total} 条数据`);
            toast.info(`采集已取消，已获取到 ${total} 条数据`);
          } else {
            logger.info('采集已取消');
            toast.info('采集已取消');
          }
        } else if (event.total && event.total > 0) {
          logger.success(`采集成功，共获取到 ${event.total} 条数据`);
          toast.success(`采集成功，共获取到 ${event.total} 条数据`);
        } else {
          if (event.is_incremental) {
            logger.info('✓ 增量采集完成，暂无新作品');
            toast.info('增量采集完成，暂无新作品（已是最新状态）');
          } else {
            logger.info('采集完成，但未获取到数据');
            toast.info('采集完成，但未获取到数据，请检查链接是否正确或cookie是否有效');
          }
        }

        unsubResult();
        unsubStatus();
        unsubError();
      }
    });

    const unsubError = sseClient.onTaskError((event: TaskErrorEvent) => {
      if (taskId && event.task_id === taskId) {
        setIsLoading(false);
        const errorMsg = event.error || '未知错误';
        logger.error(`任务执行失败: ${errorMsg}`);

        if (errorMsg.includes('cookie') || errorMsg.includes('Cookie')) {
          toast.error('Cookie可能已失效，请在设置中更新Cookie');
        } else if (errorMsg.includes('网络') || errorMsg.includes('连接')) {
          toast.error('网络连接失败，请检查网络设置');
        } else {
          toast.error(`采集失败: ${errorMsg}`);
        }

        unsubResult();
        unsubStatus();
        unsubError();
      }
    });

    try {
      const taskFilters = tab === TaskType.SEARCH ? f : undefined;
      const response = await bridge.startTask(tab, val, count, taskFilters);

      taskId = response.task_id;
      setCurrentTaskId(taskId);
      currentTaskIdRef.current = taskId;
      logger.info(`采集任务已启动，任务ID: ${taskId}`);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error(`任务启动失败: ${errorMsg}`);

      if (errorMsg.includes('Backend not available')) {
        toast.error('后端服务不可用，请确保主程序正在运行');
      } else if (errorMsg.includes('cookie')) {
        toast.error('Cookie可能已失效，请在设置中更新Cookie');
      } else if (errorMsg.includes('网络') || errorMsg.includes('连接')) {
        toast.error('网络连接失败，请检查网络设置');
      } else {
        toast.error(`采集失败: ${errorMsg}`);
      }
      setIsLoading(false);

      unsubResult();
      unsubStatus();
      unsubError();
    }
  }, [validateInput]);

  const handleCancelTask = useCallback(async () => {
    const taskId = currentTaskIdRef.current;
    if (!taskId) return;
    try {
      await bridge.cancelTask(taskId);
      logger.info(`已发送取消请求: ${taskId}`);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error(`取消任务失败: ${errorMsg}`);
      toast.error(`取消失败: ${errorMsg}`);
    }
  }, []);

  return {
    handleSearch,
    handleCancelTask,
    validateInput,
    currentTaskIdRef,
  };
}
