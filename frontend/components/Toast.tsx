import { AlertTriangle, CheckCircle, Clock, Info, Loader2, X, XCircle } from 'lucide-react';
import React, { useEffect, useState } from 'react';

export type ToastType = 'success' | 'error' | 'info' | 'warning' | 'loading' | 'progress';

interface ToastMessage {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;  // 持续时间（毫秒），0表示不自动关闭
  progress?: number;  // 进度百分比（0-100）
  actionable?: boolean; // 是否可操作
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface ToastOptions {
  duration?: number;  // 持续时间（毫秒），默认3000，0表示不自动关闭
  progress?: number;  // 进度百分比（0-100）
  actionable?: boolean; // 是否可操作
  action?: {
    label: string;
    onClick: () => void;
  };
}

export const toast = {
  success: (msg: string, options?: ToastOptions) => dispatchToast('success', msg, options),
  error: (msg: string, options?: ToastOptions) => dispatchToast('error', msg, options),
  info: (msg: string, options?: ToastOptions) => dispatchToast('info', msg, options),
  warning: (msg: string, options?: ToastOptions) => dispatchToast('warning', msg, options),
  loading: (msg: string, options?: ToastOptions) => dispatchToast('loading', msg, { duration: 0, ...options }),
  progress: (msg: string, progress: number, options?: Omit<ToastOptions, 'progress'>) =>
    dispatchToast('progress', msg, { progress, duration: 0, ...options }),

  // 便捷方法
  downloadStart: (filename: string) =>
    dispatchToast('loading', `开始下载: ${filename}`, { duration: 2000 }),
  downloadProgress: (filename: string, progress: number) =>
    dispatchToast('progress', `下载中: ${filename}`, { progress, duration: 0 }),
  downloadComplete: (filename: string) =>
    dispatchToast('success', `下载完成: ${filename}`, { duration: 3000 }),
  downloadError: (filename: string, error: string) =>
    dispatchToast('error', `下载失败: ${filename} - ${error}`, {
      duration: 5000,
      actionable: true,
      action: { label: '查看详情', onClick: () => console.log('查看下载错误详情') }
    }),

  batchProgress: (current: number, total: number, operation: string = '处理') =>
    dispatchToast('progress', `${operation}中 ${current}/${total}`, {
      progress: (current / total) * 100,
      duration: 0
    })
};

const dispatchToast = (type: ToastType, message: string, options?: ToastOptions) => {
  if (typeof window !== 'undefined') {
    const event = new CustomEvent('toast-show', {
      detail: {
        type,
        message,
        duration: options?.duration ?? (type === 'loading' || type === 'progress' ? 0 : 3000),
        progress: options?.progress,
        actionable: options?.actionable,
        action: options?.action
      }
    });
    window.dispatchEvent(event);
  }
};

export const ToastContainer: React.FC = () => {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  useEffect(() => {
    const handleToast = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      const id = Math.random().toString(36).substr(2, 9);
      const duration = detail.duration ?? 3000;  // 默认3秒

      setToasts((prev) => [...prev, { id, ...detail }]);

      // 如果duration为0，不自动关闭
      if (duration > 0) {
        setTimeout(() => {
          removeToast(id);
        }, duration);
      }
    };

    window.addEventListener('toast-show', handleToast);
    return () => window.removeEventListener('toast-show', handleToast);
  }, []);

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const updateToastProgress = (id: string, progress: number) => {
    setToasts((prev) => prev.map(t =>
      t.id === id ? { ...t, progress } : t
    ));
  };

  const updateToastMessage = (id: string, message: string) => {
    setToasts((prev) => prev.map(t =>
      t.id === id ? { ...t, message } : t
    ));
  };

  // 监听各种Toast事件
  useEffect(() => {
    const handleProgressUpdate = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      updateToastProgress(detail.id, detail.progress);
    };

    const handleMessageUpdate = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      updateToastMessage(detail.id, detail.message);
    };

    const handleToastRemove = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      removeToast(detail.id);
    };

    window.addEventListener('toast-update-progress', handleProgressUpdate);
    window.addEventListener('toast-update-message', handleMessageUpdate);
    window.addEventListener('toast-remove', handleToastRemove);

    return () => {
      window.removeEventListener('toast-update-progress', handleProgressUpdate);
      window.removeEventListener('toast-update-message', handleMessageUpdate);
      window.removeEventListener('toast-remove', handleToastRemove);
    };
  }, []);

  return (
    <div className="fixed bottom-6 right-6 z-[100] flex flex-col gap-2 w-full max-w-sm pointer-events-none">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`pointer-events-auto rounded-xl shadow-[0_8px_30px_rgb(0,0,0,0.12)] border animate-in slide-in-from-bottom-2 fade-in duration-300 overflow-hidden ${t.type === 'success' ? 'bg-white border-emerald-100' :
              t.type === 'error' ? 'bg-white border-red-100' :
                t.type === 'warning' ? 'bg-white border-amber-100' :
                  t.type === 'loading' ? 'bg-white border-blue-100' :
                    t.type === 'progress' ? 'bg-white border-indigo-100' :
                      'bg-white border-blue-100'
            }`}
        >
          {/* 进度条 */}
          {(t.type === 'progress' && typeof t.progress === 'number') && (
            <div className="h-1 bg-gray-100">
              <div
                className="h-full bg-indigo-500 transition-all duration-300 ease-out"
                style={{ width: `${Math.max(0, Math.min(100, t.progress))}%` }}
              />
            </div>
          )}

          <div className="flex items-center gap-3 px-4 py-3">
            {/* 图标 */}
            <div className="shrink-0">
              {t.type === 'success' && <CheckCircle size={18} className="text-emerald-500" />}
              {t.type === 'error' && <XCircle size={18} className="text-red-500" />}
              {t.type === 'warning' && <AlertTriangle size={18} className="text-amber-500" />}
              {t.type === 'info' && <Info size={18} className="text-blue-500" />}
              {t.type === 'loading' && <Loader2 size={18} className="text-blue-500 animate-spin" />}
              {t.type === 'progress' && <Clock size={18} className="text-indigo-500" />}
            </div>

            {/* 消息内容 */}
            <div className="flex-1 min-w-0">
              <p className={`text-sm font-medium ${t.type === 'success' ? 'text-emerald-800' :
                  t.type === 'error' ? 'text-red-800' :
                    t.type === 'warning' ? 'text-amber-800' :
                      t.type === 'loading' ? 'text-blue-800' :
                        t.type === 'progress' ? 'text-indigo-800' :
                          'text-blue-800'
                }`}>
                {t.message}
              </p>

              {/* 进度百分比 */}
              {(t.type === 'progress' && typeof t.progress === 'number') && (
                <p className="text-xs text-gray-500 mt-1">
                  {Math.round(t.progress)}% 完成
                </p>
              )}
            </div>

            {/* 操作按钮 */}
            {t.actionable && t.action && (
              <button
                onClick={t.action.onClick}
                className="text-xs px-2 py-1 rounded bg-gray-100 hover:bg-gray-200 text-gray-700 transition-colors"
              >
                {t.action.label}
              </button>
            )}

            {/* 关闭按钮 */}
            <button
              onClick={() => removeToast(t.id)}
              className="text-gray-400 hover:text-gray-600 transition-colors p-1 ml-2"
            >
              <X size={14} />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};
