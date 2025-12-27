
import { Heart, Image as ImageIcon, ImageOff, PlayCircle } from 'lucide-react';
import React, { useState } from 'react';
import { DouyinWork } from '../types';

interface WorkCardProps {
  work: DouyinWork;
  onClick: (work: DouyinWork) => void;
  style?: React.CSSProperties; // For virtual scrolling positioning
}

/**
 * 格式化时长显示
 * @param seconds 秒数
 * @returns 格式化的时长字符串 (mm:ss)
 */
const formatDuration = (seconds: number): string => {
  const mins = Math.floor(seconds / 1000 / 60);
  const secs = Math.floor((seconds / 1000) % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

export const WorkCard: React.FC<WorkCardProps> = React.memo(({
  work, onClick, style
}) => {
  const [imageError, setImageError] = useState(false);

  return (
    <div
      style={style}
      className="px-1.5 py-2" // 增加垂直padding
    >
      <div
        className="bg-white rounded-xl shadow-sm border border-gray-100 hover:border-blue-200 transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5 group relative overflow-hidden flex flex-col cursor-pointer"
        onClick={() => onClick(work)}
      >
        {/* Thumbnail Container - 调整为4:3比例 */}
        <div
          className="aspect-[4/3] relative bg-gray-100 overflow-hidden rounded-t-xl"
        >
          {!imageError ? (
            <img
              src={work.cover}
              alt={work.desc}
              loading="lazy"
              onError={() => setImageError(true)}
              className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center bg-gray-100 text-gray-400 p-4 text-center">
              <ImageOff size={28} className="mb-2 opacity-50" />
              <span className="text-xs">封面加载失败</span>
            </div>
          )}

          {/* Gradient Overlay */}
          {!imageError && (
            <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          )}

          {/* 时长显示 - 右下角 */}
          {work.type === 'video' && work.duration && (
            <div className="absolute bottom-2 right-2 bg-black/70 backdrop-blur-sm px-1.5 py-0.5 rounded text-white text-xs font-medium">
              {formatDuration(work.duration)}
            </div>
          )}

          {/* 点赞数 - 左下角 */}
          <div className="absolute bottom-2 left-2 flex items-center gap-1 bg-black/70 backdrop-blur-sm px-1.5 py-0.5 rounded text-white text-xs font-medium">
            <Heart size={11} className="text-white fill-white" />
            <span>
              {work.stats.digg_count > 10000 
                ? (work.stats.digg_count / 10000).toFixed(1) + 'w' 
                : work.stats.digg_count}
            </span>
          </div>
        </div>

        {/* Info Section - 紧凑布局 */}
        <div className="p-2.5 flex flex-col gap-1.5">
          {/* 标题 - 两行截断 */}
          <p className="text-sm text-gray-800 line-clamp-2 leading-snug font-medium min-h-[38px]" title={work.desc}>
            {work.desc || '无标题'}
          </p>
          
          {/* 作者和时间 */}
          <div className="flex items-center justify-between text-xs text-gray-500">
            <div className="flex items-center gap-1.5 max-w-[65%]">
              <img 
                src={work.author.avatar} 
                className="w-4 h-4 rounded-full border border-gray-200" 
                loading="lazy" 
                onError={(e) => (e.currentTarget.src = 'https://ui-avatars.com/api/?name=User&background=random')} 
              />
              <span className="truncate hover:text-blue-600 transition-colors">{work.author.nickname}</span>
            </div>
            <span className="text-gray-400 flex-shrink-0">{work.create_time}</span>
          </div>
        </div>
      </div>
    </div>
  );
}, (prev, next) => {
  return prev.work.id === next.work.id;
});