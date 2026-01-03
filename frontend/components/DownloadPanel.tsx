/**
 * 下载管理面板
 * 整体显示的下载管理界面，类似采集结果展示
 */

import {
  AlertCircle,
  CheckCircle,
  ChevronDown,
  ChevronUp,
  Clock,
  Download,
  FileText,
  FolderOpen,
  HardDrive,
  Link as LinkIcon,
  Loader2,
  Pause,
  PauseCircle,
  Play,
  PlayCircle,
  Trash2,
  TrendingDown,
  X,
  XCircle
} from 'lucide-react';
import React, { useState } from 'react';
import { useAria2Manager } from '../hooks/useAria2Manager';
import { aria2Service, Aria2Task } from '../services/aria2Service';
import { bridge } from '../services/bridge';
import { formatSize, formatSpeed } from '../utils/formatters';

interface DownloadPanelProps {
  isOpen: boolean;
  showLogs?: boolean;
}

export const DownloadPanel: React.FC<DownloadPanelProps> = ({ isOpen, showLogs = false }) => {
  const [activeTab, setActiveTab] = useState<'active' | 'waiting' | 'stopped'>('active');
  const [showPurgeConfirm, setShowPurgeConfirm] = useState(false);
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);
  const [showOnlyErrors, setShowOnlyErrors] = useState(false);
  const [aria2Connected, setAria2Connected] = useState(false);

  const {
    activeTasks,
    waitingTasks,
    stoppedTasks,
    globalStats,
    pauseAll,
    resumeAll,
    cancelAll,
    purgeStoppedTasks,
  } = useAria2Manager(isOpen);

  // 监听Aria2连接状态
  React.useEffect(() => {
    const unsubscribe = aria2Service.onConnectionChange((connected) => {
      setAria2Connected(connected);
    });
    return unsubscribe;
  }, []);

  // 重试失败的任务
  const handleRetry = async (task: Aria2Task) => {
    try {
      // 获取任务的详细信息，包括原始URL
      const details = await aria2Service.getTaskDetails(task.gid);

      if (details?.files?.[0]?.uris?.[0]?.uri) {
        const url = details.files[0].uris[0].uri;

        // 先移除失败的任务记录
        await aria2Service.remove(task.gid);

        // 重新添加下载任务
        const options: Record<string, any> = {
          dir: task.dir || '',
          out: task.filename || ''
        };

        await aria2Service.addDownload(url, options);
        console.log(`重试任务: ${task.filename}`);
        
        // 重试成功后，如果当前在"仅失败"筛选模式，自动切换回"全部"
        if (showOnlyErrors) {
          setShowOnlyErrors(false);
        }
      } else {
        console.error('无法获取任务的原始URL，请手动重新下载');
      }
    } catch (error) {
      console.error('重试任务失败:', error);
    }
  };

  // 重试所有失败的任务
  const handleRetryAllFailed = async () => {
    const failedTasks = stoppedTasks.filter(t => t.status === 'error');
    for (const task of failedTasks) {
      await handleRetry(task);
    }
    // 重试全部后，自动切换回"全部"视图
    if (showOnlyErrors) {
      setShowOnlyErrors(false);
    }
  };

  // 统计失败任务数量
  const errorCount = stoppedTasks.filter(t => t.status === 'error').length;



  // 渲染任务列表
  const renderTaskList = (tasks: Aria2Task[], type: 'active' | 'waiting' | 'stopped') => {
    // 如果在已停止标签且开启了仅显示失败，则过滤任务
    const filteredTasks = (type === 'stopped' && showOnlyErrors)
      ? tasks.filter(t => t.status === 'error')
      : tasks;

    if (filteredTasks.length === 0) {
      return (
        <div className="h-full flex flex-col items-center justify-center text-gray-400">
          <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-6 shadow-inner">
            <FileText size={48} className="text-gray-300" />
          </div>
          <p className="text-lg font-medium text-gray-500">暂无{type === 'active' ? '活动' : type === 'waiting' ? '等待' : '已停止'}任务</p>
          <p className="text-sm text-gray-400 mt-2">
            {type === 'active' && '开始下载后，任务将显示在这里'}
            {type === 'waiting' && '等待中的任务将显示在这里'}
            {type === 'stopped' && '已完成或失败的任务将显示在这里'}
          </p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {/* 已停止标签的筛选器 */}
        {type === 'stopped' && tasks.length > 0 && errorCount > 0 && (
          <div className="flex items-center gap-2 pb-2 border-b border-gray-200">
            <button
              onClick={() => setShowOnlyErrors(false)}
              className={`px-3 py-1.5 text-sm rounded-lg transition-all ${!showOnlyErrors
                  ? 'bg-blue-100 text-blue-700 font-medium'
                  : 'text-gray-600 hover:bg-gray-100'
                }`}
            >
              全部 ({tasks.length})
            </button>
            <button
              onClick={() => setShowOnlyErrors(true)}
              className={`px-3 py-1.5 text-sm rounded-lg transition-all flex items-center gap-1.5 ${showOnlyErrors
                  ? 'bg-red-100 text-red-700 font-medium'
                  : 'text-gray-600 hover:bg-gray-100'
                }`}
            >
              <AlertCircle size={14} />
              仅失败 ({errorCount})
            </button>
          </div>
        )}

        <div className="grid gap-4">
          {filteredTasks.map((task) => (
            <TaskItem
              key={task.gid}
              task={task}
              type={type}
              onPause={aria2Service.pause.bind(aria2Service)}
              onResume={aria2Service.resume.bind(aria2Service)}
              onCancel={aria2Service.cancel.bind(aria2Service)}
              onRemove={aria2Service.remove.bind(aria2Service)}
              onRetry={handleRetry}
              formatSize={formatSize}
              formatSpeed={formatSpeed}

            />
          ))}
        </div>
      </div>
    );
  };

  if (!isOpen) return null;

  const totalActive = activeTasks.length;
  const totalWaiting = waitingTasks.length;
  const totalStopped = stoppedTasks.length;
  const totalTasks = totalActive + totalWaiting + totalStopped;

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-[#F8F9FB]">
      {/* 头部统计 */}
      <div className="sticky top-0 z-30 bg-white/80 backdrop-blur-md border-b border-gray-200/60 shadow-sm">
        <div className="w-full px-8 py-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30">
                <Download size={20} className="text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-800 tracking-tight flex items-center gap-2">
                  下载管理
                  {/* Aria2连接状态指示器 */}
                  <span className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                    aria2Connected 
                      ? 'bg-green-100 text-green-700 border border-green-200' 
                      : 'bg-red-100 text-red-700 border border-red-200'
                  }`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${
                      aria2Connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                    }`}></span>
                    {aria2Connected ? '已连接' : '未连接'}
                  </span>
                </h2>
                <p className="text-sm text-gray-500">共 {totalTasks} 个任务</p>
              </div>
            </div>

            {/* 全局统计 */}
            {globalStats && (
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center">
                    <TrendingDown size={16} className="text-blue-600" />
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">下载速度</div>
                    <div className="text-sm font-bold text-gray-900">{formatSpeed(globalStats.downloadSpeed || 0)}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-green-50 rounded-lg flex items-center justify-center">
                    <HardDrive size={16} className="text-green-600" />
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">活动任务</div>
                    <div className="text-sm font-bold text-gray-900">{totalActive} 个</div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* 标签页和批量操作 */}
          <div className="flex items-center justify-between gap-4">
            {/* 左侧：标签页 */}
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab('active')}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${activeTab === 'active'
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                    : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
                  }`}
              >
                活动中 {totalActive > 0 && <span className="ml-1.5 px-2 py-0.5 bg-white/20 rounded-full text-xs">{totalActive}</span>}
              </button>
              <button
                onClick={() => setActiveTab('waiting')}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${activeTab === 'waiting'
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                    : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
                  }`}
              >
                等待中 {totalWaiting > 0 && <span className="ml-1.5 px-2 py-0.5 bg-white/20 rounded-full text-xs">{totalWaiting}</span>}
              </button>
              <button
                onClick={() => setActiveTab('stopped')}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${activeTab === 'stopped'
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                    : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
                  }`}
              >
                已停止
                {totalStopped > 0 && <span className="ml-1.5 px-2 py-0.5 bg-white/20 rounded-full text-xs">{totalStopped}</span>}
                {errorCount > 0 && <span className="ml-1.5 px-2 py-0.5 bg-red-500 text-white rounded-full text-xs">{errorCount}</span>}
              </button>
            </div>

            {/* 右侧：批量操作按钮（根据标签页动态显示） */}
            <div className="flex gap-1.5">
              {/* 活动中/等待中标签：显示暂停、恢复、取消 */}
              {(activeTab === 'active' || activeTab === 'waiting') && (
                <>
                  <button
                    onClick={pauseAll}
                    disabled={!activeTasks.some(t => t.status === 'active')}
                    className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${activeTasks.some(t => t.status === 'active')
                        ? 'text-orange-700 bg-gradient-to-r from-orange-50 to-amber-50 border border-orange-200 hover:from-orange-100 hover:to-amber-100'
                        : 'text-gray-400 bg-gray-50 border border-gray-200 cursor-not-allowed'
                      }`}
                    title={activeTasks.some(t => t.status === 'active') ? "暂停全部活动任务" : "没有正在下载的任务"}
                  >
                    <PauseCircle size={14} />
                    暂停全部
                  </button>

                  <button
                    onClick={resumeAll}
                    disabled={!activeTasks.some(t => t.status === 'paused') && !waitingTasks.some(t => t.status === 'paused')}
                    className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${activeTasks.some(t => t.status === 'paused') || waitingTasks.some(t => t.status === 'paused')
                        ? 'text-green-700 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 hover:from-green-100 hover:to-emerald-100'
                        : 'text-gray-400 bg-gray-50 border border-gray-200 cursor-not-allowed'
                      }`}
                    title={activeTasks.some(t => t.status === 'paused') || waitingTasks.some(t => t.status === 'paused') ? "恢复全部暂停任务" : "没有暂停的任务"}
                  >
                    <PlayCircle size={14} />
                    恢复全部
                  </button>

                  <button
                    onClick={() => setShowCancelConfirm(true)}
                    disabled={totalActive === 0 && totalWaiting === 0}
                    className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${totalActive > 0 || totalWaiting > 0
                        ? 'text-red-700 bg-gradient-to-r from-red-50 to-rose-50 border border-red-200 hover:from-red-100 hover:to-rose-100'
                        : 'text-gray-400 bg-gray-50 border border-gray-200 cursor-not-allowed'
                      }`}
                    title={totalActive > 0 || totalWaiting > 0 ? "取消全部任务" : "没有可取消的任务"}
                  >
                    <XCircle size={14} />
                    取消全部
                  </button>
                </>
              )}

              {/* 已停止标签：显示重试失败、清空记录 */}
              {activeTab === 'stopped' && (
                <>
                  {errorCount > 0 && (
                    <button
                      onClick={handleRetryAllFailed}
                      className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all text-blue-700 bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 hover:from-blue-100 hover:to-cyan-100"
                      title={`重试 ${errorCount} 个失败任务`}
                    >
                      <AlertCircle size={14} />
                      重试失败({errorCount})
                    </button>
                  )}

                  <button
                    onClick={() => setShowPurgeConfirm(true)}
                    disabled={totalStopped === 0}
                    className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${totalStopped > 0
                        ? 'text-gray-700 bg-gradient-to-r from-gray-50 to-slate-50 border border-gray-200 hover:from-gray-100 hover:to-slate-100'
                        : 'text-gray-400 bg-gray-50 border border-gray-200 cursor-not-allowed'
                      }`}
                    title={totalStopped > 0 ? "清空所有已停止任务记录" : "没有已停止的任务"}
                  >
                    <Trash2 size={14} />
                    清空记录
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 任务列表 */}
      <div className={`flex-1 overflow-y-auto px-8 py-6 transition-all duration-300 ${showLogs ? 'mb-64' : 'mb-0'}`}>
        <div className="w-full h-full">
          {activeTab === 'active' && renderTaskList(activeTasks, 'active')}
          {activeTab === 'waiting' && renderTaskList(waitingTasks, 'waiting')}
          {activeTab === 'stopped' && renderTaskList(stoppedTasks, 'stopped')}
        </div>
      </div>

      {/* 清空确认对话框 */}
      {showPurgeConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-md mx-4 shadow-2xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <Trash2 size={20} className="text-red-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">清空记录</h3>
                <p className="text-sm text-gray-500">此操作不可撤销</p>
              </div>
            </div>
            <p className="text-gray-700 mb-6">
              确定要清空所有已停止的任务记录吗？这将移除 {totalStopped} 个任务的记录。
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowPurgeConfirm(false)}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                取消
              </button>
              <button
                onClick={async () => {
                  await purgeStoppedTasks();
                  setShowPurgeConfirm(false);
                }}
                className="px-4 py-2 bg-red-600 text-white hover:bg-red-700 rounded-lg transition-colors"
              >
                确定清空
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 取消任务确认对话框 */}
      {showCancelConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-md mx-4 shadow-2xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <XCircle size={20} className="text-red-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">取消任务</h3>
                <p className="text-sm text-gray-500">此操作不可撤销</p>
              </div>
            </div>
            <p className="text-gray-700 mb-6">
              确定要取消所有活动和等待任务吗？这将取消 {totalActive + totalWaiting} 个任务。
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowCancelConfirm(false)}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                取消
              </button>
              <button
                onClick={async () => {
                  await cancelAll();
                  setShowCancelConfirm(false);
                }}
                className="px-4 py-2 bg-red-600 text-white hover:bg-red-700 rounded-lg transition-colors"
              >
                确定取消
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// 任务项组件
interface TaskItemProps {
  task: Aria2Task;
  type: 'active' | 'waiting' | 'stopped';
  onPause: (gid: string) => void;
  onResume: (gid: string) => void;
  onCancel: (gid: string) => void;
  onRemove: (gid: string) => void;
  onRetry: (task: Aria2Task) => void;
  formatSize: (bytes: number) => string;
  formatSpeed: (bytesPerSecond: number) => string;

}

const TaskItem: React.FC<TaskItemProps> = ({
  task,
  type,
  onPause,
  onResume,
  onCancel,
  onRemove,
  onRetry,
  formatSize,
  formatSpeed
}) => {
  const [expanded, setExpanded] = useState(false);

  // 获取状态图标和颜色
  const getStatusInfo = () => {
    switch (task.status) {
      case 'active':
        return { icon: Loader2, color: 'text-blue-600', bg: 'bg-blue-50', borderColor: 'border-blue-200', label: '下载中', animate: true };
      case 'waiting':
        return { icon: Clock, color: 'text-yellow-600', bg: 'bg-yellow-50', borderColor: 'border-yellow-200', label: '等待中', animate: false };
      case 'paused':
        return { icon: Pause, color: 'text-gray-600', bg: 'bg-gray-50', borderColor: 'border-gray-200', label: '已暂停', animate: false };
      case 'complete':
        return { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50', borderColor: 'border-green-200', label: '已完成', animate: false };
      case 'error':
        return { icon: AlertCircle, color: 'text-red-600', bg: 'bg-red-50', borderColor: 'border-red-200', label: '失败', animate: false };
      default:
        return { icon: FileText, color: 'text-gray-600', bg: 'bg-gray-50', borderColor: 'border-gray-200', label: '未知', animate: false };
    }
  };

  const statusInfo = getStatusInfo();
  const StatusIcon = statusInfo.icon;

  return (
    <div className={`bg-white border ${statusInfo.borderColor} rounded-xl overflow-hidden hover:shadow-lg transition-shadow duration-200`}>
      <div className="p-5">
        {/* 任务头部 */}
        <div className="flex items-start gap-4 mb-3">
          <div className={`${statusInfo.bg} p-3 rounded-xl shadow-sm shrink-0`}>
            <StatusIcon size={24} className={`${statusInfo.color} ${statusInfo.animate ? 'animate-spin' : ''}`} />
          </div>

          <div className="flex-1 min-w-0 overflow-hidden">
            <h3 className="text-sm font-semibold text-gray-900 truncate pr-4">{task.filename}</h3>
          </div>

          {/* 右侧操作区 */}
          <div className="flex items-center gap-2 shrink-0">
            <span className={`px-3 py-1 ${statusInfo.bg} ${statusInfo.color} rounded-full text-xs font-medium border ${statusInfo.borderColor} whitespace-nowrap`}>
              {statusInfo.label}
            </span>

            {/* 单个任务操作按钮 */}
            <div className="flex items-center gap-1">
              {type === 'active' && task.status === 'active' && (
                <button
                  onClick={() => onPause(task.gid)}
                  className="p-2 hover:bg-orange-50 rounded-lg transition-colors group"
                  title="暂停"
                >
                  <Pause size={16} className="text-gray-600 group-hover:text-orange-600" />
                </button>
              )}
              {(type === 'active' || type === 'waiting') && task.status === 'paused' && (
                <button
                  onClick={() => onResume(task.gid)}
                  className="p-2 hover:bg-green-50 rounded-lg transition-colors group"
                  title="继续"
                >
                  <Play size={16} className="text-gray-600 group-hover:text-green-600" />
                </button>
              )}
              {(type === 'active' || type === 'waiting') && (
                <button
                  onClick={() => onCancel(task.gid)}
                  className="p-2 hover:bg-red-50 rounded-lg transition-colors group"
                  title="取消"
                >
                  <X size={16} className="text-gray-600 group-hover:text-red-600" />
                </button>
              )}
              {type === 'stopped' && (
                <>
                  {/* 打开文件夹按钮 - 只对已完成的任务显示 */}
                  {task.status === 'complete' && task.dir && (
                    <button
                      onClick={async () => {
                        console.log('点击打开文件夹，路径:', task.dir);
                        const success = await bridge.openFolder(task.dir!);
                        console.log('打开文件夹结果:', success);
                        if (!success) {
                          console.error('打开文件夹失败，路径:', task.dir);
                        }
                      }}
                      className="p-2 hover:bg-blue-50 rounded-lg transition-colors group"
                      title="打开文件夹"
                    >
                      <FolderOpen size={16} className="text-gray-600 group-hover:text-blue-600" />
                    </button>
                  )}
                  {/* 重试按钮 - 只对失败的任务显示 */}
                  {task.status === 'error' && (
                    <button
                      onClick={() => onRetry(task)}
                      className="p-2 hover:bg-blue-50 rounded-lg transition-colors group"
                      title="重试下载"
                    >
                      <Play size={16} className="text-gray-600 group-hover:text-blue-600" />
                    </button>
                  )}
                  <button
                    onClick={() => onRemove(task.gid)}
                    className="p-2 hover:bg-red-50 rounded-lg transition-colors group"
                    title="移除"
                  >
                    <Trash2 size={16} className="text-gray-600 group-hover:text-red-600" />
                  </button>
                </>
              )}
              <button
                onClick={() => setExpanded(!expanded)}
                className="p-2 hover:bg-gray-50 rounded-lg transition-colors group"
                title={expanded ? '收起' : '展开'}
              >
                {expanded ? <ChevronUp size={16} className="text-gray-400 group-hover:text-gray-600" /> : <ChevronDown size={16} className="text-gray-400 group-hover:text-gray-600" />}
              </button>
            </div>
          </div>
        </div>

        {/* 进度条区域 */}
        <div className="ml-16">
          {/* 进度条 */}
          {type === 'active' && task.totalLength > 0 && (
            <div className="mb-3">
              <div className="flex items-center justify-between text-xs text-gray-600 mb-2">
                <span className="font-medium">{task.progress.toFixed(1)}%</span>
                <span className="text-gray-500">{formatSize(task.completedLength)} / {formatSize(task.totalLength)}</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-blue-500 via-blue-600 to-indigo-600 h-2 rounded-full transition-all duration-500 relative overflow-hidden"
                  style={{ width: `${task.progress}%` }}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>
                </div>
              </div>
            </div>
          )}

          {/* 任务信息 */}
          <div className="flex items-center gap-3 text-xs text-gray-600 flex-wrap">
            {task.downloadSpeed > 0 && (
              <div className="flex items-center gap-1.5 bg-blue-50 px-2.5 py-1 rounded-lg">
                <TrendingDown size={14} className="text-blue-600" />
                <span className="font-medium text-blue-700">{formatSpeed(task.downloadSpeed)}</span>
              </div>
            )}
            {task.connections > 0 && (
              <div className="flex items-center gap-1.5 bg-gray-50 px-2.5 py-1 rounded-lg">
                <LinkIcon size={14} className="text-gray-600" />
                <span className="font-medium">{task.connections} 连接</span>
              </div>
            )}
            {task.status === 'error' && task.errorMessage && (
              <span className="text-red-600 font-medium truncate">{task.errorMessage}</span>
            )}
          </div>
        </div>
      </div>

      {/* 展开的详细信息 */}
      {expanded && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-gray-500 mb-1">任务 GID</div>
              <div className="font-mono text-gray-900 truncate">{task.gid}</div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-gray-500 mb-1">连接数</div>
              <div className="font-semibold text-gray-900">{task.connections}</div>
            </div>
            {task.totalLength > 0 && (
              <>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-gray-500 mb-1">文件大小</div>
                  <div className="font-semibold text-gray-900">{formatSize(task.totalLength)}</div>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-gray-500 mb-1">已下载</div>
                  <div className="font-semibold text-gray-900">{formatSize(task.completedLength)}</div>
                </div>
              </>
            )}
          </div>
          {task.dir && (
            <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-100">
              <div className="text-xs text-blue-600 mb-1 font-medium">保存路径</div>
              <div className="text-xs text-gray-700 break-all font-mono">{task.dir}/{task.filename}</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
