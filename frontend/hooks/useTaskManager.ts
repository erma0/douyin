import { useCallback, useRef } from 'react';
import { sseClient, TaskResultEvent, TaskStatusEvent, TaskErrorEvent } from '../services/sseClient';
import { bridge } from '../services/bridge';
import { logger } from '../services/logger';
import { toast } from '../components/Toast';
import { TaskType } from '../types';
import { FilterSettings } from '../components/SearchFilter';
import { useAppStore } from '../stores/appStore';

const TASK_STATUS_POLL_INTERVAL = 5000;

const TERMINAL_STATES = new Set(['completed', 'cancelled', 'error', 'failed']);

function isTerminalStatus(status: string): boolean {
  return TERMINAL_STATES.has(status);
}

export function useTaskManager() {
  const currentTaskIdRef = useRef<string | null>(null);
  const pollTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const unsubRefs = useRef<{ result: (() => void) | null; status: (() => void) | null; error: (() => void) | null }>({
    result: null,
    status: null,
    error: null,
  });

  const activeTab = useAppStore((s) => s.activeTab);
  const inputVal = useAppStore((s) => s.inputVal);
  const maxCount = useAppStore((s) => s.maxCount);
  const filters = useAppStore((s) => s.filters);

  const cleanupSubscriptions = useCallback(() => {
    if (unsubRefs.current.result) { unsubRefs.current.result(); unsubRefs.current.result = null; }
    if (unsubRefs.current.status) { unsubRefs.current.status(); unsubRefs.current.status = null; }
    if (unsubRefs.current.error) { unsubRefs.current.error(); unsubRefs.current.error = null; }
    if (pollTimerRef.current) { clearInterval(pollTimerRef.current); pollTimerRef.current = null; }
  }, []);

  const startStatusPolling = useCallback((taskId: string) => {
    if (pollTimerRef.current) clearInterval(pollTimerRef.current);

    pollTimerRef.current = setInterval(async () => {
      try {
        const statusList = await bridge.getTaskStatus(taskId);
        if (!statusList || statusList.length === 0) return;

        const taskStatus = statusList[0];
        if (isTerminalStatus(taskStatus.status)) {
          const { setIsLoading, setCurrentTaskId } = useAppStore.getState();
          setIsLoading(false);
          setCurrentTaskId(taskId);
          cleanupSubscriptions();

          if (taskStatus.status === 'error' || taskStatus.status === 'failed') {
            const errorMsg = taskStatus.error || '未知错误';
            logger.error(`任务执行失败(轮询检测): ${errorMsg}`);
            if (errorMsg.includes('cookie') || errorMsg.includes('Cookie')) {
              toast.error('Cookie可能已失效，请在设置中更新Cookie');
            } else {
              toast.error(`采集失败: ${errorMsg}`);
            }
          } else if (taskStatus.status === 'cancelled') {
            logger.info('采集已取消(轮询检测)');
            toast.info('采集已取消');
          } else if (taskStatus.status === 'completed') {
            const count = taskStatus.result_count || 0;
            if (count > 0) {
              logger.success(`采集成功(轮询检测)，共获取到 ${count} 条数据`);
              toast.success(`采集成功，共获取到 ${count} 条数据`);
            } else {
              logger.info('采集完成(轮询检测)，但未获取到数据');
              toast.info('采集完成，但未获取到数据，请检查链接是否正确或cookie是否有效');
            }
          }
        }
      } catch {
        logger.debug('轮询任务状态失败，将在下次重试');
      }
    }, TASK_STATUS_POLL_INTERVAL);
  }, [cleanupSubscriptions]);

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

    cleanupSubscriptions();
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
      if (!taskId || event.task_id !== taskId) return;

      if (event.status === 'error') {
        setIsLoading(false);
        setCurrentTaskId(taskId);
        const errorMsg = event.error || '未知错误';
        logger.error(`任务执行失败: ${errorMsg}`);
        if (errorMsg.includes('cookie') || errorMsg.includes('Cookie')) {
          toast.error('Cookie可能已失效，请在设置中更新Cookie');
        } else if (errorMsg.includes('网络') || errorMsg.includes('连接')) {
          toast.error('网络连接失败，请检查网络设置');
        } else {
          toast.error(`采集失败: ${errorMsg}`);
        }
        cleanupSubscriptions();
        return;
      }

      if (event.status === 'completed' || event.status === 'cancelled') {
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

        cleanupSubscriptions();
      }
    });

    const unsubError = sseClient.onTaskError((event: TaskErrorEvent) => {
      if (taskId && event.task_id === taskId) {
        setIsLoading(false);
        setCurrentTaskId(taskId);
        const errorMsg = event.error || '未知错误';
        logger.error(`任务执行失败: ${errorMsg}`);

        if (errorMsg.includes('cookie') || errorMsg.includes('Cookie')) {
          toast.error('Cookie可能已失效，请在设置中更新Cookie');
        } else if (errorMsg.includes('网络') || errorMsg.includes('连接')) {
          toast.error('网络连接失败，请检查网络设置');
        } else {
          toast.error(`采集失败: ${errorMsg}`);
        }

        cleanupSubscriptions();
      }
    });

    unsubRefs.current = { result: unsubResult, status: unsubStatus, error: unsubError };

    try {
      const taskFilters = tab === TaskType.SEARCH ? f : undefined;
      const response = await bridge.startTask(tab, val, count, taskFilters);

      taskId = response.task_id;
      setCurrentTaskId(taskId);
      currentTaskIdRef.current = taskId;
      logger.info(`采集任务已启动，任务ID: ${taskId}`);

      startStatusPolling(taskId);
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

      cleanupSubscriptions();
    }
  }, [validateInput, cleanupSubscriptions, startStatusPolling]);

  const handleCancelTask = useCallback(async () => {
    const taskId = currentTaskIdRef.current;
    if (!taskId) return;
    try {
      const result = await bridge.cancelTask(taskId);

      if (result.status === 'cancelling') {
        logger.info(`已发送取消请求: ${taskId}`);
      } else if (isTerminalStatus(result.status)) {
        const { setIsLoading } = useAppStore.getState();
        setIsLoading(false);
        cleanupSubscriptions();

        if (result.status === 'error' || result.status === 'failed') {
          logger.info('任务已失败，恢复界面状态');
          toast.error('任务已失败');
        } else if (result.status === 'completed') {
          logger.info('任务已完成，恢复界面状态');
        } else if (result.status === 'cancelled') {
          logger.info('任务已取消，恢复界面状态');
        }
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error(`取消任务失败: ${errorMsg}`);

      const { setIsLoading } = useAppStore.getState();
      setIsLoading(false);
      cleanupSubscriptions();
      toast.error(`取消失败: ${errorMsg}`);
    }
  }, [cleanupSubscriptions]);

  return {
    handleSearch,
    handleCancelTask,
    validateInput,
    currentTaskIdRef,
  };
}
