import React, { useRef, useState, useEffect } from 'react';
import { SearchFilter } from './SearchFilter';
import { FilterSettings } from './SearchFilter';
import { toast } from './Toast';
import { bridge } from '../services/bridge';
import { logger } from '../services/logger';
import { TaskType } from '../types';
import {
  ChevronDown, ChevronUp,
  Infinity as InfinityIcon, Layers,
  Search,
  Sparkles
} from 'lucide-react';

interface SearchBarProps {
  activeTab: TaskType;
  inputVal: string;
  inputError: string | null;
  maxCount: number;
  isLoading: boolean;
  filters: FilterSettings;
  resultsTaskType: TaskType | null;
  savedInputVal: string;
  setInputVal: (val: string) => void;
  setInputError: (err: string | null) => void;
  setMaxCount: (count: number) => void;
  setFilters: (filters: FilterSettings) => void;
  setResultsTaskType: (type: TaskType | null) => void;
  handleSearch: () => void;
  handleCancelTask: () => void;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  activeTab,
  inputVal,
  inputError,
  maxCount,
  isLoading,
  filters,
  resultsTaskType,
  savedInputVal,
  setInputVal,
  setInputError,
  setMaxCount,
  setFilters,
  setResultsTaskType,
  handleSearch,
  handleCancelTask,
}) => {
  const [showLimitMenu, setShowLimitMenu] = useState(false);
  const limitMenuRef = useRef<HTMLDivElement>(null);

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

  const incrementMaxCount = () => setMaxCount((maxCount || 0) + 1);
  const decrementMaxCount = () => setMaxCount(Math.max(0, (maxCount || 0) - 1));

  return (
    <>
      <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2 tracking-tight">
        {activeTab === TaskType.SEARCH && <Search size={24} className="text-blue-500" />}
        {activeTab === TaskType.SEARCH ? '关键词搜索' : '数据采集'}
      </h2>

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
                const cleanedValue = e.target.value.replace(/\s+/g, ' ');
                setInputVal(cleanedValue);
                if (resultsTaskType === activeTab) {
                  setResultsTaskType(null);
                }

                if (inputError) {
                  setInputError(null);
                }
              }}
              onPaste={(e) => {
                e.preventDefault();
                const pastedText = e.clipboardData.getData('text');
                const cleanedText = pastedText.trim().replace(/\s+/g, '').replace(/^\/+|\/+$/g, '');
                setInputVal(cleanedText);
                if (resultsTaskType === activeTab) {
                  setResultsTaskType(null);
                }

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

            <button
              onClick={async () => {
                try {
                  const text = await bridge.getClipboardText();

                  if (!text) {
                    toast.info('剪贴板为空');
                    return;
                  }

                  const cleanedText = text.trim().replace(/\s+/g, '').replace(/^\/+|\/+$/g, '');
                  setInputVal(cleanedText);
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
  );
};
