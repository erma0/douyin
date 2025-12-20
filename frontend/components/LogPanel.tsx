
import { ChevronDown, Copy, Terminal, Trash2 } from 'lucide-react';
import React, { useEffect, useRef, useState } from 'react';
import { LogEntry, logger } from '../services/logger';

interface LogPanelProps {
  isOpen: boolean;
  onToggle: () => void;
}

export const LogPanel: React.FC<LogPanelProps> = ({ isOpen, onToggle }) => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);

  // 订阅前端日志更新
  useEffect(() => {
    const unsubscribe = logger.subscribe((updatedLogs) => {
      setLogs(updatedLogs);
    });
    return unsubscribe;
  }, []);

  // 只在日志面板打开时订阅后端日志，关闭时取消订阅
  useEffect(() => {
    if (isOpen) {
      logger.initialize();
    } else {
      logger.uninitialize();
    }
  }, [isOpen]);

  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs, autoScroll, isOpen]);

  const handleScroll = () => {
    if (!scrollRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
    // If user scrolls up, disable auto-scroll. If at bottom, enable it.
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
    setAutoScroll(isAtBottom);
  };

  const copyLogs = () => {
    navigator.clipboard.writeText(logger.getAllLogsText());
    logger.success('日志已复制到剪贴板');
  };

  if (!isOpen) return null;

  return (
    <div className={`fixed bottom-0 left-64 right-0 bg-[#0c0c0c] border-t border-gray-800 shadow-[0_-4px_20px_rgba(0,0,0,0.3)] transition-all duration-300 z-40 flex flex-col font-mono h-64`}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-[#1a1a1a] border-b border-gray-800 select-none">
        <div className="flex items-center gap-2 text-gray-400">
          <Terminal size={14} className="text-blue-500" />
          <span className="text-xs font-bold tracking-wider">TERMINAL OUTPUT</span>
          <div className="flex gap-1.5 ml-2">
            <div className="w-2 h-2 rounded-full bg-red-500/80"></div>
            <div className="w-2 h-2 rounded-full bg-yellow-500/80"></div>
            <div className="w-2 h-2 rounded-full bg-green-500/80"></div>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={copyLogs}
            className="p-1.5 hover:bg-gray-700 rounded text-gray-400 hover:text-white transition-colors"
            title="复制日志"
          >
            <Copy size={12} />
          </button>
          <button
            onClick={() => logger.clear()}
            className="p-1.5 hover:bg-gray-700 rounded text-gray-400 hover:text-red-400 transition-colors"
            title="清空日志"
          >
            <Trash2 size={12} />
          </button>
          <button
            onClick={onToggle}
            className="p-1.5 hover:bg-gray-700 rounded text-gray-400 hover:text-white transition-colors"
          >
            <ChevronDown size={14} />
          </button>
        </div>
      </div>

      {/* Log Body */}
      <div
        className="flex-1 overflow-y-auto p-4 space-y-1 custom-scrollbar scroll-smooth"
        ref={scrollRef}
        onScroll={handleScroll}
      >
        {logs.length === 0 && (
          <div className="text-gray-600 text-xs italic opacity-50 select-none">Waiting for tasks...</div>
        )}
        {logs.map((log) => (
          <div key={log.id} className="text-xs flex gap-3 leading-relaxed hover:bg-white/5 px-1 -mx-1 rounded">
            <span className="text-gray-600 shrink-0 font-light select-none">[{log.timestamp}]</span>
            <span className={`break-all ${log.level === 'error' ? 'text-red-400 font-bold' :
                log.level === 'warn' ? 'text-yellow-400' :
                  log.level === 'success' ? 'text-emerald-400' :
                    'text-blue-300'
              }`}>
              {log.level === 'error' ? '✖ ' : log.level === 'success' ? '✔ ' : log.level === 'warn' ? '⚠ ' : 'ℹ '}
              {log.message}
            </span>
          </div>
        ))}
        {/* Blinking Cursor Effect */}
        <div className="flex items-center gap-2 mt-2">
          <span className="text-emerald-500 text-xs font-bold">➜</span>
          <span className="w-2 h-4 bg-emerald-500/50 animate-pulse"></span>
        </div>
      </div>
    </div>
  );
};
