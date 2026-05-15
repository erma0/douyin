import React from 'react';
import { Loader2, Search } from 'lucide-react';

interface EmptyStateProps {
  isLoading: boolean;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ isLoading }) => {
  if (isLoading) {
    return (
      <div className="h-full flex flex-col items-center justify-center">
        <div className="relative w-32 h-32 mb-8">
          <div className="absolute inset-0 rounded-full border-4 border-blue-100"></div>
          <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-blue-500 border-r-blue-500 animate-spin"></div>

          <div className="absolute inset-0 flex items-center justify-center">
            <Loader2 size={48} className="text-blue-500 animate-spin" style={{ animationDuration: '2s' }} />
          </div>
        </div>

        <p className="text-xl font-semibold text-gray-700 mb-2">正在采集数据...</p>
        <p className="text-sm text-gray-500">请稍候，这可能需要一些时间</p>

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
    );
  }

  return (
    <div className="h-full flex flex-col items-center justify-center text-gray-400 opacity-60">
      <div className="w-32 h-32 bg-gray-100 rounded-full flex items-center justify-center mb-6 shadow-inner">
        <Search size={64} className="text-gray-300" />
      </div>
      <p className="text-xl font-medium text-gray-500">等待任务开始...</p>
      <p className="text-sm mt-2">请在上方输入目标链接或关键词</p>
    </div>
  );
};
