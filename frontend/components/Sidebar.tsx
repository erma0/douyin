
import {
  Download,
  Film,
  Github,
  Hash,
  Heart,
  Layers,
  Music,
  Search,
  Settings,
  Star,
  Terminal,
  User
} from 'lucide-react';
import React from 'react';
import { bridge } from '../services/bridge';
import { TaskType } from '../types';
import { formatSpeedSimple } from '../utils/formatters';

interface SidebarProps {
  activeTab: TaskType;
  setActiveTab: (tab: TaskType) => void;
  onOpenSettings: () => void;
  showLogs: boolean;
  setShowLogs: (show: boolean) => void;
  isDownloading: boolean;
  downloadStats: {
    activeCount: number;
    downloadSpeed: number;
  };
}

const menuItems = [
  { id: TaskType.AWEME, label: '单个作品', icon: Film },
  { id: TaskType.POST, label: '用户主页', icon: User },
  { id: TaskType.FAVORITE, label: '用户喜欢', icon: Heart },
  { id: TaskType.COLLECTION, label: '用户收藏', icon: Star },
  { id: TaskType.MUSIC, label: '音乐原声', icon: Music },
  { id: TaskType.HASHTAG, label: '话题挑战', icon: Hash },
  { id: TaskType.MIX, label: '合集作品', icon: Layers },
  { id: TaskType.SEARCH, label: '关键词搜索', icon: Search },
];

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab, setActiveTab, onOpenSettings, showLogs, setShowLogs,
  isDownloading, downloadStats
}) => {
  return (
    <div className="w-64 bg-slate-900 text-white flex flex-col h-full shadow-2xl relative z-50">
      {/* Brand */}
      <div className="p-6 pb-2 flex items-center gap-3 select-none">
        <div className="w-9 h-9 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20">
          <span className="font-bold text-white text-xl">D</span>
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-wide">Douyin</h1>
          <div className="text-[10px] text-slate-500 uppercase font-semibold tracking-wider">Crawler Tool</div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-6 px-3 custom-scrollbar">
        <div className="px-3 mb-3 text-xs font-bold text-slate-500 uppercase tracking-wider">
          数据源
        </div>
        <ul className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;

            return (
              <li key={item.id}>
                <button
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group ${isActive
                      ? 'bg-blue-600 text-white shadow-md shadow-blue-900/20'
                      : 'text-slate-400 hover:bg-slate-800 hover:text-slate-100'
                    }`}
                >
                  <Icon size={18} className={`transition-colors ${isActive ? 'text-white' : 'text-slate-500 group-hover:text-slate-300'}`} />
                  <span className="font-medium text-sm">{item.label}</span>
                  {isActive && <div className="ml-auto w-1.5 h-1.5 bg-white rounded-full opacity-50"></div>}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer / Settings */}
      <div className="p-4 bg-slate-950/30 border-t border-slate-800 space-y-1">
        {/* 下载管理 */}
        <button
          onClick={() => setActiveTab(TaskType.DOWNLOAD_MANAGER)}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 group ${activeTab === TaskType.DOWNLOAD_MANAGER
              ? 'bg-blue-600 text-white shadow-md shadow-blue-900/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
        >
          <Download size={18} className={activeTab === TaskType.DOWNLOAD_MANAGER ? 'text-white' : 'text-slate-500 group-hover:text-slate-300'} />
          <span className="font-medium flex-1 text-left">下载管理</span>

          {/* 右侧显示：速度 > 任务数 > 激活点 */}
          {isDownloading && downloadStats.downloadSpeed > 0 ? (
            <span className="text-xs text-emerald-400 font-medium whitespace-nowrap">
              {formatSpeedSimple(downloadStats.downloadSpeed)}
            </span>
          ) : downloadStats.activeCount > 0 ? (
            <span className="px-2 py-0.5 bg-white/20 text-white rounded-full text-xs font-medium">
              {downloadStats.activeCount}
            </span>
          ) : activeTab === TaskType.DOWNLOAD_MANAGER ? (
            <div className="w-1.5 h-1.5 bg-white rounded-full opacity-50"></div>
          ) : null}
        </button>

        <div className="h-px bg-slate-800 my-2"></div>

        {/* 运行日志 */}
        <button
          onClick={() => setShowLogs(!showLogs)}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 group ${showLogs ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
        >
          <Terminal size={18} className={showLogs ? 'text-emerald-400' : 'text-slate-500 group-hover:text-slate-300'} />
          <span className="font-medium">运行日志</span>
          <div className={`ml-auto w-2 h-2 rounded-full ${showLogs ? 'bg-emerald-500 animate-pulse' : 'bg-slate-700'}`}></div>
        </button>

        <div className="h-px bg-slate-800 my-2"></div>

        <button
          onClick={onOpenSettings}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-slate-400 hover:text-white hover:bg-slate-800 transition-all duration-200 group"
        >
          <Settings size={18} className="text-slate-500 group-hover:text-slate-300" />
          <span className="font-medium">系统配置</span>
        </button>

        <button
          onClick={() => bridge.openExternal('https://github.com/erma0/douyin')}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-slate-400 hover:text-white hover:bg-slate-800 transition-all duration-200 group"
        >
          <Github size={18} className="text-slate-500 group-hover:text-slate-300" />
          <span className="font-medium">GitHub 仓库</span>
        </button>
      </div>
    </div>
  );
};
