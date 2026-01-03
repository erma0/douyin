import { useCallback, useEffect, useState } from 'react';
import { toast } from '../components/Toast';
import { aria2Service, Aria2Task } from '../services/aria2Service';

export const useAria2Manager = (isOpen: boolean) => {
  const [activeTasks, setActiveTasks] = useState<Aria2Task[]>([]);
  const [waitingTasks, setWaitingTasks] = useState<Aria2Task[]>([]);
  const [stoppedTasks, setStoppedTasks] = useState<Aria2Task[]>([]);
  const [globalStats, setGlobalStats] = useState<any>(null);

  useEffect(() => {
    if (!isOpen) return;

    const fetchTasks = async () => {
      try {
        const [active, waiting, stopped, stats] = await Promise.all([
          aria2Service.getActiveTasks(),
          aria2Service.getWaitingTasks(),
          aria2Service.getStoppedTasks(),
          aria2Service.getGlobalStat()
        ]);

        setActiveTasks(active);
        setWaitingTasks(waiting);
        setStoppedTasks(stopped);
        setGlobalStats(stats);
      } catch (error) {
        console.error('获取任务列表失败:', error);
      }
    };

    fetchTasks();
    const interval = setInterval(fetchTasks, 1000);
    return () => clearInterval(interval);
  }, [isOpen]);

  const pauseAll = useCallback(async () => {
    try {
      await aria2Service.pauseAll();
      toast.success('已暂停所有任务');
      return true;
    } catch (error) {
      toast.error('暂停失败');
      return false;
    }
  }, []);

  const resumeAll = useCallback(async () => {
    try {
      await aria2Service.resumeAll();
      toast.success('已恢复所有任务');
      return true;
    } catch (error) {
      toast.error('恢复失败');
      return false;
    }
  }, []);

  const cancelAll = useCallback(async () => {
    try {
      // 取消所有活动任务
      for (const task of activeTasks) {
        await aria2Service.cancel(task.gid);
      }
      // 取消所有等待任务
      for (const task of waitingTasks) {
        await aria2Service.cancel(task.gid);
      }
      toast.success('已取消所有任务');
      return true;
    } catch (error) {
      toast.error('取消失败');
      return false;
    }
  }, [activeTasks, waitingTasks]);

  const purgeStoppedTasks = useCallback(async () => {
    try {
      await aria2Service.purgeDownloadResult();
      toast.success('已清空记录');
      return true;
    } catch (error) {
      toast.error('清空失败');
      return false;
    }
  }, []);

  return {
    activeTasks,
    waitingTasks,
    stoppedTasks,
    globalStats,
    pauseAll,
    resumeAll,
    cancelAll,
    purgeStoppedTasks,
  };
};
