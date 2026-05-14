
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { DetailModal } from './components/DetailModal';
import { DownloadPanel } from './components/DownloadPanel';
import { ErrorBoundary, LightErrorBoundary } from './components/ErrorBoundary';
import { LogPanel } from './components/LogPanel';
import { SearchFilter, FilterSettings } from './components/SearchFilter';
import { SettingsModal } from './components/SettingsModal';
import { Sidebar } from './components/Sidebar';
import { ToastContainer, toast } from './components/Toast';
import { WelcomeWizard } from './components/WelcomeWizard';
import { WorkCard } from './components/WorkCard';
import { useAria2Download } from './hooks/useAria2Download';
import { bridge } from './services/bridge';
import { sseClient, TaskResultEvent, TaskStatusEvent, TaskErrorEvent } from './services/sseClient';
import { logger } from './services/logger';
import { DouyinWork, TaskType } from './types';

// 延迟加载虚拟滚动库（这些库比较大）
import {
  ChevronDown, ChevronUp,
  Infinity as InfinityIcon, Layers,
  Loader2,
  Search,
  Sparkles
} from 'lucide-react';
import memoize from 'memoize-one';
import AutoSizer from 'react-virtualized-auto-sizer';
import { FixedSizeList } from 'react-window';

// --- 虚拟滚动列表辅助工具 ---

/**
 * 行数据接口
 * 用于传递给虚拟列表的每一行渲染器
 */
interface RowData {
  items: DouyinWork[];                          // 作品列表
  columnCount: number;                          // 每行列数
  width: number;                                // 容器宽度
  onClick: (work: DouyinWork) => void;          // 点击作品的回调
}

/**
 * 创建行数据的辅助函数
 * 使用memoize-one确保只在依赖项变化时重新创建，避免不必要的重渲染
 */
const createItemData = memoize(
  (
    items: DouyinWork[],
    columnCount: number,
    width: number,
    onClick: (work: DouyinWork) => void
  ) => ({
    items,
    columnCount,
    width,
    onClick,
  }),
  // 自定义比较函数
  (newArgs, oldArgs) => {
    const [newItems, newColumnCount, newWidth, newOnClick] = newArgs;
    const [oldItems, oldColumnCount, oldWidth, oldOnClick] = oldArgs;

    // 基本类型比较
    if (newColumnCount !== oldColumnCount) return false;
    if (newWidth !== oldWidth) return false;
    if (newOnClick !== oldOnClick) return false;
    if (newItems !== oldItems) return false;

    return true;
  }
);

/**
 * 根据容器宽度计算列数（响应式网格）
 * @param width 容器宽度（像素）
 * @returns 列数
 */
const getColumnCount = (width: number) => {
  if (width >= 1920) return 7; // 超大屏幕
  if (width >= 1600) return 6; // 大屏幕
  if (width >= 1280) return 5; // xl 标准窗口
  if (width >= 1024) return 4; // lg 中等屏幕
  if (width >= 768) return 3;  // md 平板
  return 2;                     // 小屏幕/手机
};

/**
 * 虚拟列表的行渲染器
 * 定义在组件外部以防止每次渲染时重新挂载
 * 
 * @param index 行索引
 * @param style 由FixedSizeList提供的样式（包含位置信息）
 * @param data 行数据（包含作品列表和回调函数）
 */
const Row = ({ index, style, data }: { index: number; style: React.CSSProperties; data: RowData }) => {
  const { items, columnCount, width, onClick } = data;
  const startIndex = index * columnCount;

  // 计算每列的宽度以实现响应式布局
  // 容器左右padding为p-8（32px * 2 = 64px）
  const availableWidth = width - 64;
  const gap = 12; // 进一步减小列间距
  const itemWidth = (availableWidth - (gap * (columnCount - 1))) / columnCount;

  // 获取当前行的作品列表
  const rowItems = [];
  for (let i = 0; i < columnCount; i++) {
    const itemIndex = startIndex + i;
    if (itemIndex < items.length) {
      rowItems.push(items[itemIndex]);
    }
  }

  return (
    <div style={style} className="flex gap-3 px-8 box-border">
      {rowItems.map((work: DouyinWork) => (
        <div key={work.id} style={{ width: itemWidth }}>
          <WorkCard
            work={work}
            onClick={onClick}
          />
        </div>
      ))}
    </div>
  );
};

/**
 * 主应用组件
 * 负责整体布局、任务采集、数据展示和下载管理
 */
export const App: React.FC = () => {
  // --- 任务相关状态 ---
  const [activeTab, setActiveTab] = useState<TaskType>(TaskType.POST);  // 当前选中的任务类型
  const [inputVal, setInputVal] = useState('');                              // 输入框的值
  const [inputError, setInputError] = useState<string | null>(null);         // 输入验证错误信息

  // --- 采集数量限制相关状态 ---
  const [maxCount, setMaxCount] = useState<number>(0);  // 0表示不限制数量
  const [showLimitMenu, setShowLimitMenu] = useState(false);  // 是否显示数量限制菜单
  const limitMenuRef = useRef<HTMLDivElement>(null);  // 数量限制菜单的引用，用于检测外部点击

  // --- 采集结果相关状态 ---
  const [isLoading, setIsLoading] = useState(false);  // 是否正在采集
  const [results, setResults] = useState<DouyinWork[]>([]);  // 采集结果列表
  const [selectedWorkId, setSelectedWorkId] = useState<string | null>(null);  // 当前查看详情的作品ID
  const [resultsTaskType, setResultsTaskType] = useState<TaskType | null>(null);  // 记录结果对应的任务类型
  const [savedInputVal, setSavedInputVal] = useState('');  // 保存采集时的输入框内容
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);  // 保存当前采集任务的ID
  const currentTaskIdRef = useRef<string | null>(null);

  // --- 模态框状态 ---
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);  // 设置模态框是否打开
  const [showLogs, setShowLogs] = useState(false);  // 日志面板是否显示
  const [showWelcomeWizard, setShowWelcomeWizard] = useState(false);  // 欢迎向导是否显示

  // --- 筛选相关状态 ---
  const [filters, setFilters] = useState<FilterSettings>({
    sort_type: '0',      // 默认综合排序
    publish_time: '0',   // 默认不限时间
    filter_duration: '', // 默认不限时长
    search_range: '0',   // 默认不限范围
    content_type: '1',   // 默认视频
  });

  // --- 下载管理 ---
  // 使用Aria2下载Hook，前端直接管理下载任务
  const {
    connected: aria2Connected,      // Aria2是否已连接
    downloading: isDownloading,     // 是否正在下载
    progress: downloadProgress,     // 下载进度映射表
    downloadStats,                  // 下载统计信息
    addDownload,                    // 添加单个下载任务
    batchDownloadFromConfig,        // 从配置文件批量下载
    startPolling,                   // 开始轮询下载进度
    cancelAll                       // 取消所有下载
  } = useAria2Download();

  /**
   * 计算当前选中作品在结果列表中的索引
   * 用于详情模态框的上一个/下一个导航
   */
  const selectedWorkIndex = useMemo(() => {
    return selectedWorkId ? results.findIndex(r => r.id === selectedWorkId) : -1;
  }, [selectedWorkId, results]);

  // 当前查看详情的作品对象
  const selectedWork = selectedWorkIndex >= 0 ? results[selectedWorkIndex] : null;

  /**
   * 在详情模态框中导航到上一个或下一个作品
   * @param direction 导航方向
   */
  const navigateWork = (direction: 'next' | 'prev') => {
    if (selectedWorkIndex === -1) return;
    const newIndex = direction === 'next' ? selectedWorkIndex + 1 : selectedWorkIndex - 1;
    if (newIndex >= 0 && newIndex < results.length) {
      setSelectedWorkId(results[newIndex].id);
    }
  };

  /**
   * 处理用户手动切换任务类型
   * 不清空数据，通过 resultsTaskType 控制显示
   */
  const handleTabChange = useCallback((newTab: TaskType) => {
    if (newTab !== activeTab) {
      setActiveTab(newTab);
      // 只有非下载管理页面才清空输入框
      if (newTab !== TaskType.DOWNLOAD_MANAGER) {
        setInputVal('');
      }
      logger.info(`手动切换任务模式: ${newTab}`);
    }
  }, [activeTab]);

  /**
   * 当任务类型切换时，记录日志
   */
  useEffect(() => {
    logger.info(`当前任务模式: ${activeTab}`);
  }, [activeTab]);

  /**
   * 处理点击数量限制菜单外部时关闭菜单
   */
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (limitMenuRef.current && !limitMenuRef.current.contains(event.target as Node)) {
        setShowLimitMenu(false);
      }
    };

    if (showLimitMenu) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
    return undefined;
  }, [showLimitMenu]);

  /**
   * 初始化系统和检查首次运行
   */
  useEffect(() => {
    bridge.waitForReady(30000).then(ready => {
      if (!ready) {
        console.error("后端服务连接超时");
        toast.error("后端服务连接失败，请重启应用");
        return;
      }

      // 并行检查首次运行和启动 Aria2
      // 注意：不在这里订阅日志，改为在用户打开日志面板时订阅
      Promise.all([
        bridge.isFirstRun().then(isFirstRun => {
          if (isFirstRun) {
            setShowWelcomeWizard(true);
          }
        }).catch(error => {
          console.error("检查首次运行失败:", error);
        }),
        // 在 API 就绪后启动 Aria2 服务
        bridge.startAria2().catch(error => {
          console.error("启动 Aria2 失败:", error);
        })
      ]);
    }).catch(error => {
      console.error("初始化失败:", error);
    });
  }, []);

  /**
   * 验证用户输入（简化版 - 只做基本验证）
   * 具体的类型判断由后端负责
   * @returns 验证是否通过
   */
  const validateInput = (): boolean => {
    // 清理输入：去除前后空格、去除前后斜杠
    const trimmedVal = inputVal.trim().replace(/^\/+|\/+$/g, '');

    if (!trimmedVal) {
      setInputError("请输入内容");
      return false;
    }

    if (trimmedVal.length < 2) {
      setInputError("输入内容过短");
      return false;
    }

    // 搜索关键词的特殊验证
    if (activeTab === TaskType.SEARCH) {
      if (trimmedVal.length > 20) {
        setInputError("搜索关键词不能超过20个字符");
        return false;
      }
      // 检查是否包含特殊字符（允许中文、英文、数字、空格）
      const hasInvalidChars = /[<>{}[\]\\\/|`~!@#$%^&*()+=;:'"?]/.test(trimmedVal);
      if (hasInvalidChars) {
        setInputError("搜索关键词不能包含特殊符号");
        return false;
      }
    }

    setInputError(null);
    return true;
  };

  /**
   * 处理采集任务
   * 验证输入后调用后端API开始采集，并处理各种错误情况
   * 后端会返回检测到的类型，前端根据结果自动切换面板
   */
  const handleSearch = async () => {
    // 验证输入
    if (!validateInput()) {
      return;
    }

    // 开始新采集时清空旧结果，记录当前面板和输入内容
    // 这样可以确保下载时使用的是当前采集任务的配置文件
    setResults([]);
    setResultsTaskType(activeTab);
    setSavedInputVal(inputVal);

    setIsLoading(true);
    setShowLimitMenu(false); // 关闭数量限制菜单

    // 用于存储当前任务ID
    let taskId: string | null = null;

    // 订阅 SSE 事件
    const unsubResult = sseClient.onTaskResult((event: TaskResultEvent) => {
      if (taskId && event.task_id === taskId) {
        // 实时追加新采集到的结果
        setResults(prev => [...prev, ...(event.data || [])]);
        logger.info(`已采集 ${event.total} 条数据`);
      }
    });

    const unsubStatus = sseClient.onTaskStatus((event: TaskStatusEvent) => {
      if (taskId && event.task_id === taskId && (event.status === 'completed' || event.status === 'cancelled')) {
        setIsLoading(false);
        setCurrentTaskId(taskId);
        logger.info(`保存任务ID: ${taskId}`);

        if (event.detected_type && event.detected_type !== activeTab) {
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
            logger.info("采集已取消");
            toast.info("采集已取消");
          }
        } else if (event.total && event.total > 0) {
          logger.success(`采集成功，共获取到 ${event.total} 条数据`);
          toast.success(`采集成功，共获取到 ${event.total} 条数据`);
        } else {
          if (event.is_incremental) {
            logger.info("✓ 增量采集完成，暂无新作品");
            toast.info("增量采集完成，暂无新作品（已是最新状态）");
          } else {
            logger.info("采集完成，但未获取到数据");
            toast.info("采集完成，但未获取到数据，请检查链接是否正确或cookie是否有效");
          }
        }

        unsubResult();
        unsubStatus();
        unsubError();
      }
    });

    const unsubError = sseClient.onTaskError((event: TaskErrorEvent) => {
      if (taskId && event.task_id === taskId) {
        // 采集失败
        setIsLoading(false);
        const errorMsg = event.error || '未知错误';
        logger.error(`任务执行失败: ${errorMsg}`);

        // 根据错误类型提供友好的提示信息
        if (errorMsg.includes("cookie") || errorMsg.includes("Cookie")) {
          toast.error("Cookie可能已失效，请在设置中更新Cookie");
        } else if (errorMsg.includes("网络") || errorMsg.includes("连接")) {
          toast.error("网络连接失败，请检查网络设置");
        } else {
          toast.error(`采集失败: ${errorMsg}`);
        }

        // 清理订阅
        unsubResult();
        unsubStatus();
        unsubError();
      }
    });

    try {
      // 调用后端API开始采集任务
      // 搜索任务传递筛选参数
      const taskFilters = activeTab === TaskType.SEARCH ? filters : undefined;
      const response = await bridge.startTask(
        activeTab, 
        inputVal, 
        maxCount,
        taskFilters
      );

      // 保存任务ID，用于匹配 SSE 事件
      taskId = response.task_id;
      setCurrentTaskId(taskId);
      currentTaskIdRef.current = taskId;
      logger.info(`采集任务已启动，任务ID: ${taskId}`);

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error(`任务启动失败: ${errorMsg}`);

      // 根据错误类型提供友好的提示信息
      if (errorMsg.includes("Backend not available")) {
        toast.error("后端服务不可用，请确保主程序正在运行");
      } else if (errorMsg.includes("cookie")) {
        toast.error("Cookie可能已失效，请在设置中更新Cookie");
      } else if (errorMsg.includes("网络") || errorMsg.includes("连接")) {
        toast.error("网络连接失败，请检查网络设置");
      } else {
        toast.error(`采集失败: ${errorMsg}`);
      }
      setIsLoading(false);
      
      // 清理 SSE 订阅
      unsubResult();
      unsubStatus();
      unsubError();
    }
  };



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



  /**
   * 处理点击作品卡片
   * 打开详情模态框
   */
  const handleWorkClick = useCallback((work: DouyinWork) => {
    setSelectedWorkId(work.id);
  }, []);



  /**
   * 一键下载全部函数
   * 直接从后端获取douyin.aria2_conf配置文件路径
   */
  const handleBatchDownload = async () => {
    if (results.length === 0) {
      toast.error('没有可下载的内容');
      return;
    }

    if (!aria2Connected) {
      toast.error('Aria2下载服务未连接，请检查配置');
      logger.error('✗ Aria2未连接，无法下载');
      return;
    }

    try {
      logger.info(`📦 开始一键下载全部 (${results.length} 个作品)`);

      // 使用当前采集任务的task_id获取配置文件路径
      const configFilePath = await bridge.getAria2ConfigPath(currentTaskId || undefined);
      logger.info(`使用配置文件: ${configFilePath}`);

      // 使用hook方法读取配置文件并批量下载
      await batchDownloadFromConfig(configFilePath);

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error(`✗ 批量下载异常: ${errorMsg}`);
      toast.error(`下载失败: ${errorMsg}`);
    }
  };



  /**
   * 根据当前任务类型返回输入框的占位符文本
   */
  const getPlaceholder = () => {
    switch (activeTab) {
      case TaskType.SEARCH:
        return '输入关键词搜索，例如：美食、旅游、科技...';
      case TaskType.AWEME:
        return '支持：长链接、短链接、纯数字ID';
      case TaskType.HASHTAG:
        return '支持：长链接、短链接、纯数字ID';
      case TaskType.MUSIC:
        return '支持：长链接、短链接、纯数字ID';
      case TaskType.MIX:
        return '支持：长链接、短链接、纯数字ID';
      case TaskType.POST:
        return '支持：长链接、短链接、SecUid';
      case TaskType.FAVORITE:
        return '支持：长链接、短链接、SecUid';
      case TaskType.COLLECTION:
        return '支持：长链接、短链接、SecUid';
      default:
        return '请输入目标链接';
    }
  };



  /**
   * 增加采集数量限制
   */
  const incrementMaxCount = () => setMaxCount(prev => (prev || 0) + 1);

  /**
   * 减少采集数量限制（最小为0）
   */
  const decrementMaxCount = () => setMaxCount(prev => Math.max(0, (prev || 0) - 1));

  return (
    <ErrorBoundary
      onError={(error, errorInfo) => {
        // 记录错误到日志系统
        logger.error(`应用错误: ${error.message}`);
        console.error('错误详情:', error, errorInfo);
      }}
    >
      <div className="flex h-screen bg-[#F8F9FB] overflow-hidden font-sans text-gray-900 selection:bg-blue-100 selection:text-blue-900">
        <LightErrorBoundary fallbackMessage="侧边栏加载失败">
          <Sidebar
            activeTab={activeTab}
            setActiveTab={handleTabChange}
            onOpenSettings={() => setIsSettingsOpen(true)}
            showLogs={showLogs}
            setShowLogs={setShowLogs}
            isDownloading={isDownloading}
            downloadStats={downloadStats}
          />
        </LightErrorBoundary>

        {/* 根据activeTab显示不同的主内容区域 */}
        {activeTab === TaskType.DOWNLOAD_MANAGER ? (
          <LightErrorBoundary fallbackMessage="下载面板加载失败">
            <DownloadPanel isOpen={true} showLogs={showLogs} />
          </LightErrorBoundary>
        ) : (
          <main className="flex-1 flex flex-col min-w-0 relative">
            {/* Sticky Header */}
            <div className="sticky top-0 z-30 bg-white/80 backdrop-blur-md border-b border-gray-200/60 shadow-sm transition-all">
              <div className="max-w-7xl mx-auto w-full px-8 py-5">
                {(activeTab as TaskType) !== TaskType.DOWNLOAD_MANAGER && (
                  <>
                    <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2 tracking-tight">
                      {activeTab === TaskType.SEARCH && <Search size={24} className="text-blue-500" />}
                      {activeTab === TaskType.SEARCH ? '关键词搜索' : '数据采集'}
                    </h2>

                    {/* 搜索框 */}
                    <div className="flex gap-3">
                      <div className="flex-1">
                        <div className={`relative flex group shadow-sm rounded-xl border transition-all bg-white z-20 ${inputError ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : 'border-gray-200 focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:border-blue-500'
                          }`}>
                          <div className="pl-4 flex items-center pointer-events-none bg-transparent">
                            <Search className={`h-5 w-5 transition-colors ${inputError ? 'text-red-500' : 'text-gray-400 group-focus-within:text-blue-500'
                              }`} />
                          </div>
                          <input
                              type="text"
                              className="block flex-1 px-4 py-3.5 leading-5 bg-transparent placeholder-gray-400 focus:outline-none"
                              placeholder={getPlaceholder()}
                              value={resultsTaskType === activeTab ? savedInputVal : inputVal}
                              onChange={(e) => {
                                // 自动清理输入：去除多余空格
                                const cleanedValue = e.target.value.replace(/\s+/g, ' ');
                                setInputVal(cleanedValue);
                                // 当用户开始输入新内容时，解绑resultsTaskType与activeTab，显示当前输入值
                                if (resultsTaskType === activeTab) {
                                  setResultsTaskType(null);
                                }

                                // 清除输入错误
                                if (inputError) {
                                  setInputError(null);
                                }
                              }}
                              onPaste={(e) => {
                                // 粘贴时自动清理：去除所有空格和前后斜杠
                                e.preventDefault();
                                const pastedText = e.clipboardData.getData('text');
                                const cleanedText = pastedText.trim().replace(/\s+/g, '').replace(/^\/+|\/+$/g, '');
                                setInputVal(cleanedText);
                                // 当用户粘贴新内容时，解绑resultsTaskType与activeTab，显示当前输入值
                                if (resultsTaskType === activeTab) {
                                  setResultsTaskType(null);
                                }

                                // 清除输入错误
                                if (inputError) {
                                  setInputError(null);
                                }
                              }}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                  handleSearch();
                                }
                              }}
                            />

                          {/* 粘贴按钮 - 通过后端读取剪贴板，无需浏览器权限 */}
                          <button
                            onClick={async () => {
                              try {
                                // 通过后端读取剪贴板（无需浏览器权限）
                                const text = await bridge.getClipboardText();

                                if (!text) {
                                  toast.info('剪贴板为空');
                                  return;
                                }

                                // 清理文本：去除空格和斜杠
                                const cleanedText = text.trim().replace(/\s+/g, '').replace(/^\/+|\/+$/g, '');
                                setInputVal(cleanedText);
                                // 当用户点击粘贴按钮时，解绑resultsTaskType与activeTab，显示当前输入值
                                if (resultsTaskType === activeTab) {
                                  setResultsTaskType(null);
                                }

                                if (inputError) {
                                  setInputError(null);
                                }

                                toast.success('已粘贴剪贴板内容');
                              } catch (err) {
                                logger.error(`粘贴失败: ${err}`);
                                toast.error('粘贴失败，请手动输入');
                              }
                            }}
                            className="px-3 text-gray-400 hover:text-blue-500 hover:bg-blue-50 transition-colors rounded-lg"
                            title="一键粘贴剪贴板内容"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                            </svg>
                          </button>

                          {/* Max Count Dropdown Trigger - 仅在非单个作品采集时显示 */}
                          {activeTab !== TaskType.AWEME && (
                            <>
                              <div className="relative border-l border-gray-100" ref={limitMenuRef}>
                                <button
                                  onClick={() => setShowLimitMenu(!showLimitMenu)}
                                  className="h-full px-4 flex items-center gap-2 hover:bg-gray-50 transition-colors text-sm font-medium text-gray-600 outline-none"
                                >
                                  <span className="text-xs text-gray-400">数量</span>
                                  <span className={`flex items-center gap-1 ${maxCount === 0 ? 'text-indigo-600 font-bold' : 'text-gray-700'}`}>
                                    {maxCount === 0 ? <InfinityIcon size={16} /> : maxCount}
                                  </span>
                                  <ChevronDown size={14} className={`text-gray-400 transition-transform ${showLimitMenu ? 'rotate-180' : ''}`} />
                                </button>

                              {/* Dropdown Menu */}
                              {showLimitMenu && (
                                <div className="absolute top-full right-0 mt-2 w-56 bg-white rounded-xl shadow-2xl border border-gray-200 z-20 px-4 py-3.5 animate-in fade-in slide-in-from-top-2 duration-200">
                                  <h4 className="text-xs font-medium text-gray-500 mb-2.5 flex items-center gap-2">
                                    <Layers size={12} /> 采集数量限制
                                  </h4>

                                  <div className="grid grid-cols-2 gap-2 mb-3">
                                    <button
                                      onClick={() => { setMaxCount(0); setShowLimitMenu(false); }}
                                      className={`flex items-center justify-center gap-2 py-1.5 rounded-lg text-xs border transition-all ${maxCount === 0
                                        ? 'bg-indigo-50 border-indigo-200 text-indigo-700 font-semibold'
                                        : 'border-gray-200 text-gray-600 hover:bg-gray-50'
                                        }`}
                                    >
                                      <InfinityIcon size={12} /> 全部
                                    </button>
                                    {[20, 50, 100].map(num => (
                                      <button
                                        key={num}
                                        onClick={() => { setMaxCount(num); setShowLimitMenu(false); }}
                                        className={`py-1.5 rounded-lg text-xs border transition-all ${maxCount === num
                                          ? 'bg-blue-50 border-blue-200 text-blue-700 font-semibold'
                                          : 'border-gray-200 text-gray-600 hover:bg-gray-50'
                                          }`}
                                      >
                                        {num} 条
                                      </button>
                                    ))}
                                  </div>

                                  <div className="relative group/input">
                                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-xs text-gray-400 pointer-events-none">自定义</span>
                                    <input
                                      type="number"
                                      min="1"
                                      value={maxCount === 0 ? '' : maxCount}
                                      onChange={(e) => {
                                        const val = parseInt(e.target.value);
                                        setMaxCount(isNaN(val) ? 0 : val);
                                      }}
                                      placeholder="输入数量"
                                      className="w-full pl-14 pr-8 py-1.5 text-xs bg-gray-50 border border-gray-200 rounded-lg text-gray-700 placeholder-gray-400 focus:outline-none focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 transition-all [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                                    />
                                    <div className="absolute right-1 top-1 bottom-1 flex flex-col w-5 border-l border-gray-200">
                                      <button
                                        onClick={incrementMaxCount}
                                        className="h-1/2 flex items-center justify-center hover:bg-gray-100 text-gray-500 rounded-tr-md transition-colors"
                                      >
                                        <ChevronUp size={10} />
                                      </button>
                                      <button
                                        onClick={decrementMaxCount}
                                        className="h-1/2 flex items-center justify-center hover:bg-gray-100 text-gray-500 rounded-br-md border-t border-gray-100 transition-colors"
                                      >
                                        <ChevronDown size={10} />
                                      </button>
                                    </div>
                                  </div>
                                </div>
                              )}
                              </div>

                              {/* 搜索筛选按钮 - 仅在搜索模式下显示 */}
                              {activeTab === TaskType.SEARCH && (
                                <SearchFilter
                                  filters={filters}
                                  onFilterChange={setFilters}
                                />
                              )}
                            </>
                          )}
                        </div>
                        {inputError && (
                          <p className="mt-1.5 text-xs text-red-500 pl-1">{inputError}</p>
                        )}
                      </div>

                      {isLoading ? (
                        <button
                          onClick={handleCancelTask}
                          className="bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700 text-white px-8 py-3.5 rounded-xl font-medium shadow-lg shadow-red-500/30 transition-all active:scale-95 flex items-center gap-2 z-20"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                          取消采集
                        </button>
                      ) : (
                        <button
                          onClick={handleSearch}
                          disabled={!inputVal.trim()}
                          className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-8 py-3.5 rounded-xl font-medium shadow-lg shadow-blue-500/30 transition-all active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed disabled:shadow-none flex items-center gap-2 z-20"
                        >
                          <Sparkles size={20} />
                          开始采集
                        </button>
                      )}
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Action Bar */}
            {results.length > 0 && resultsTaskType === activeTab && (
              <div className="px-8 py-3 border-b border-gray-200 bg-white/50 backdrop-blur-sm flex items-center justify-between sticky top-[120px] z-20">
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <span className="font-semibold bg-gray-100 px-2 py-1 rounded text-gray-700">共 {results.length} 个作品</span>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={handleBatchDownload}
                    disabled={results.length === 0 || !aria2Connected}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all transform active:scale-95 border ${results.length > 0 && aria2Connected
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700 shadow-md shadow-blue-600/20 border-transparent'
                      : 'bg-gray-50 border-gray-200 text-gray-300 cursor-not-allowed'
                      }`}
                    title="将所有采集结果添加到下载队列"
                  >
                    <Sparkles size={16} />
                    一键下载全部
                  </button>
                </div>
              </div>
            )}

            {/* Content Area with Virtual Scroll */}
            <div className={`flex-1 transition-all duration-300 ${showLogs ? 'mb-64' : 'mb-0'}`}>
              {(results.length === 0 || resultsTaskType !== activeTab) && !isLoading ? (
                // 空状态：等待任务开始
                <div className="h-full flex flex-col items-center justify-center text-gray-400 opacity-60">
                  <div className="w-32 h-32 bg-gray-100 rounded-full flex items-center justify-center mb-6 shadow-inner">
                    <Search size={64} className="text-gray-300" />
                  </div>
                  <p className="text-xl font-medium text-gray-500">等待任务开始...</p>
                  <p className="text-sm mt-2">请在上方输入目标链接或关键词</p>
                </div>
              ) : (results.length === 0 || resultsTaskType !== activeTab) && isLoading ? (
                // 加载状态：采集中
                <div className="h-full flex flex-col items-center justify-center">
                  <div className="relative w-32 h-32 mb-8">
                    {/* 外圈旋转动画 */}
                    <div className="absolute inset-0 rounded-full border-4 border-blue-100"></div>
                    <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-blue-500 border-r-blue-500 animate-spin"></div>

                    {/* 中心图标 */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Loader2 size={48} className="text-blue-500 animate-spin" style={{ animationDuration: '2s' }} />
                    </div>
                  </div>

                  <p className="text-xl font-semibold text-gray-700 mb-2">正在采集数据...</p>
                  <p className="text-sm text-gray-500">请稍候，这可能需要一些时间</p>

                  {/* 提示信息 */}
                  <div className="mt-8 px-6 py-4 bg-blue-50 border border-blue-100 rounded-xl max-w-md">
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center mt-0.5">
                        <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <div className="flex-1 text-sm text-blue-700">
                        <p className="font-medium mb-1">采集提示</p>
                        <p className="text-blue-600">采集过程中会实时显示进度，请关注日志面板查看详细信息</p>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <LightErrorBoundary fallbackMessage="列表加载失败">
                  <AutoSizer>
                    {({ height, width }) => {
                      const columnCount = getColumnCount(width);
                      const rowCount = Math.ceil(results.length / columnCount);
                      // 调整行高，增加行间距
                      const itemHeight = 296;

                      // Create item data bundle (memoized)
                      const itemData = createItemData(
                        results,
                        columnCount,
                        width,
                        handleWorkClick
                      );

                      return (
                        <FixedSizeList
                          height={height}
                          width={width}
                          itemCount={rowCount}
                          itemSize={itemHeight}
                          itemData={itemData}
                        >
                          {Row}
                        </FixedSizeList>
                      );
                    }}
                  </AutoSizer>
                </LightErrorBoundary>
              )}
            </div>

            <LightErrorBoundary fallbackMessage="详情弹窗加载失败">
              <DetailModal
                work={selectedWork}
                onClose={() => setSelectedWorkId(null)}
                onPrev={() => navigateWork('prev')}
                onNext={() => navigateWork('next')}
                hasPrev={selectedWorkIndex > 0}
                hasNext={selectedWorkIndex < results.length - 1}
                addDownload={addDownload}
                startPolling={startPolling}
                progress={downloadProgress}
              />
            </LightErrorBoundary>
          </main>
        )}

        {/* 全局组件：Toast容器 - 在所有面板中都显示 */}
        <ToastContainer />

        {/* 全局组件：设置弹窗 */}
        <LightErrorBoundary fallbackMessage="设置面板加载失败">
          <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
        </LightErrorBoundary>

        {/* 全局组件：日志面板 */}
        <LightErrorBoundary fallbackMessage="日志面板加载失败">
          <LogPanel isOpen={showLogs} onToggle={() => setShowLogs(!showLogs)} />
        </LightErrorBoundary>

        {/* 欢迎向导 */}
        <LightErrorBoundary fallbackMessage="欢迎向导加载失败">
          <WelcomeWizard
            isOpen={showWelcomeWizard}
            onClose={() => setShowWelcomeWizard(false)}
            onComplete={() => {
              setShowWelcomeWizard(false);
              logger.info("欢迎向导已完成");
              toast.success("配置已保存，欢迎使用！");
            }}
          />
        </LightErrorBoundary>
      </div>
    </ErrorBoundary>
  );
};
