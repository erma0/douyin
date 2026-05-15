
import React, { useCallback, useEffect, useMemo, useTransition } from 'react';
import { DetailModal } from './components/DetailModal';
import { DownloadPanel } from './components/DownloadPanel';
import { EmptyState } from './components/EmptyState';
import { ErrorBoundary, LightErrorBoundary } from './components/ErrorBoundary';
import { LogPanel } from './components/LogPanel';
import { SearchBar } from './components/SearchBar';
import { SettingsModal } from './components/SettingsModal';
import { Sidebar } from './components/Sidebar';
import { ToastContainer, toast } from './components/Toast';
import { WelcomeWizard } from './components/WelcomeWizard';
import { WorkCard } from './components/WorkCard';
import { useAria2Download } from './hooks/useAria2Download';
import { useTaskManager } from './hooks/useTaskManager';
import { bridge } from './services/bridge';
import { logger } from './services/logger';
import { useAppStore } from './stores/appStore';
import { DouyinWork, TaskType } from './types';

import { Sparkles } from 'lucide-react';
import memoize from 'memoize-one';
import AutoSizer from 'react-virtualized-auto-sizer';
import { FixedSizeList } from 'react-window';

interface RowData {
  items: DouyinWork[];
  columnCount: number;
  width: number;
  onClick: (work: DouyinWork) => void;
}

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
  (newArgs, oldArgs) => {
    const [newItems, newColumnCount, newWidth, newOnClick] = newArgs;
    const [oldItems, oldColumnCount, oldWidth, oldOnClick] = oldArgs;

    if (newColumnCount !== oldColumnCount) return false;
    if (newWidth !== oldWidth) return false;
    if (newOnClick !== oldOnClick) return false;
    if (newItems !== oldItems) return false;

    return true;
  }
);

const getColumnCount = (width: number) => {
  if (width >= 1920) return 7;
  if (width >= 1600) return 6;
  if (width >= 1280) return 5;
  if (width >= 1024) return 4;
  if (width >= 768) return 3;
  return 2;
};

const Row = ({ index, style, data }: { index: number; style: React.CSSProperties; data: RowData }) => {
  const { items, columnCount, width, onClick } = data;
  const startIndex = index * columnCount;

  const availableWidth = width - 64;
  const gap = 12;
  const itemWidth = (availableWidth - (gap * (columnCount - 1))) / columnCount;

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

export const App: React.FC = () => {
  const {
    activeTab,
    inputVal,
    inputError,
    maxCount,
    isLoading,
    results,
    selectedWorkId,
    resultsTaskType,
    savedInputVal,
    currentTaskId,
    isSettingsOpen,
    showLogs,
    showWelcomeWizard,
    filters,
    setActiveTab,
    setInputVal,
    setInputError,
    setMaxCount,
    setSelectedWorkId,
    setResultsTaskType,
    setIsSettingsOpen,
    setShowLogs,
    setShowWelcomeWizard,
    setFilters,
  } = useAppStore();

  const [, startTransition] = useTransition();

  const {
    connected: aria2Connected,
    downloading: isDownloading,
    progress: downloadProgress,
    downloadStats,
    addDownload,
    batchDownloadFromConfig,
    startPolling,
    cancelAll
  } = useAria2Download();

  const { handleSearch, handleCancelTask, currentTaskIdRef } = useTaskManager();

  const selectedWorkIndex = useMemo(() => {
    return selectedWorkId ? results.findIndex(r => r.id === selectedWorkId) : -1;
  }, [selectedWorkId, results]);

  const selectedWork = selectedWorkIndex >= 0 ? results[selectedWorkIndex] : null;

  const navigateWork = (direction: 'next' | 'prev') => {
    if (selectedWorkIndex === -1) return;
    const newIndex = direction === 'next' ? selectedWorkIndex + 1 : selectedWorkIndex - 1;
    if (newIndex >= 0 && newIndex < results.length) {
      setSelectedWorkId(results[newIndex].id);
    }
  };

  const handleTabChange = useCallback((newTab: TaskType) => {
    if (newTab !== activeTab) {
      startTransition(() => {
        setActiveTab(newTab);
      });
      if (newTab !== TaskType.DOWNLOAD_MANAGER) {
        setInputVal('');
      }
      logger.info(`手动切换任务模式: ${newTab}`);
    }
  }, [activeTab, setActiveTab, setInputVal]);

  useEffect(() => {
    logger.info(`当前任务模式: ${activeTab}`);
  }, [activeTab]);

  useEffect(() => {
    bridge.waitForReady(30000).then(ready => {
      if (!ready) {
        console.error("后端服务连接超时");
        toast.error("后端服务连接失败，请重启应用");
        return;
      }

      Promise.all([
        bridge.isFirstRun().then(isFirstRun => {
          if (isFirstRun) {
            setShowWelcomeWizard(true);
          }
        }).catch(error => {
          console.error("检查首次运行失败:", error);
        }),
        bridge.startAria2().catch(error => {
          console.error("启动 Aria2 失败:", error);
        })
      ]);
    }).catch(error => {
      console.error("初始化失败:", error);
    });
  }, []);

  const handleWorkClick = useCallback((work: DouyinWork) => {
    setSelectedWorkId(work.id);
  }, [setSelectedWorkId]);

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

      const configFilePath = await bridge.getAria2ConfigPath(currentTaskId || undefined);
      logger.info(`使用配置文件: ${configFilePath}`);

      await batchDownloadFromConfig(configFilePath);

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error(`✗ 批量下载异常: ${errorMsg}`);
      toast.error(`下载失败: ${errorMsg}`);
    }
  };

  return (
    <ErrorBoundary
      onError={(error, errorInfo) => {
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

        {activeTab === TaskType.DOWNLOAD_MANAGER ? (
          <LightErrorBoundary fallbackMessage="下载面板加载失败">
            <DownloadPanel isOpen={true} showLogs={showLogs} />
          </LightErrorBoundary>
        ) : (
          <main className="flex-1 flex flex-col min-w-0 relative">
            <div className="sticky top-0 z-30 bg-white/80 backdrop-blur-md border-b border-gray-200/60 shadow-sm transition-all">
              <div className="max-w-7xl mx-auto w-full px-8 py-5">
                {(activeTab as TaskType) !== TaskType.DOWNLOAD_MANAGER && (
                  <SearchBar
                    activeTab={activeTab}
                    inputVal={inputVal}
                    inputError={inputError}
                    maxCount={maxCount}
                    isLoading={isLoading}
                    filters={filters}
                    resultsTaskType={resultsTaskType}
                    savedInputVal={savedInputVal}
                    setInputVal={setInputVal}
                    setInputError={setInputError}
                    setMaxCount={setMaxCount}
                    setFilters={setFilters}
                    setResultsTaskType={setResultsTaskType}
                    handleSearch={handleSearch}
                    handleCancelTask={handleCancelTask}
                  />
                )}
              </div>
            </div>

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

            <div className={`flex-1 transition-all duration-300 ${showLogs ? 'mb-64' : 'mb-0'}`}>
              {(results.length === 0 || resultsTaskType !== activeTab) ? (
                <EmptyState isLoading={isLoading} />
              ) : (
                <LightErrorBoundary fallbackMessage="列表加载失败">
                  <AutoSizer>
                    {({ height, width }) => {
                      const columnCount = getColumnCount(width);
                      const rowCount = Math.ceil(results.length / columnCount);
                      const itemHeight = 296;

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

        <ToastContainer />

        <LightErrorBoundary fallbackMessage="设置面板加载失败">
          <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
        </LightErrorBoundary>

        <LightErrorBoundary fallbackMessage="日志面板加载失败">
          <LogPanel isOpen={showLogs} onToggle={() => setShowLogs(!showLogs)} />
        </LightErrorBoundary>

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
