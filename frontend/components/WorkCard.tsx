
import { Heart, Image as ImageIcon, ImageOff, PlayCircle } from 'lucide-react';
import React, { useState } from 'react';
import { DouyinWork } from '../types';

interface WorkCardProps {
  work: DouyinWork;
  onClick: (work: DouyinWork) => void;
  style?: React.CSSProperties; // For virtual scrolling positioning
}

export const WorkCard: React.FC<WorkCardProps> = React.memo(({
  work, onClick, style
}) => {
  const [imageError, setImageError] = useState(false);

  return (
    <div
      style={style}
      className="p-3" // Add padding to simulate gap in virtual list
    >
      <div
        className="bg-white rounded-2xl shadow-sm border border-gray-100 hover:border-blue-200 transition-all duration-300 hover:shadow-xl hover:-translate-y-1 group relative overflow-hidden flex flex-col h-full"
      >
        {/* Thumbnail Container */}
        <div
          className="aspect-[3/4] relative bg-gray-100 cursor-pointer overflow-hidden"
          onClick={() => onClick(work)}
        >
          {!imageError ? (
            <img
              src={work.cover}
              alt={work.desc}
              loading="lazy"
              onError={() => setImageError(true)}
              className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center bg-gray-100 text-gray-400 p-4 text-center">
              <ImageOff size={32} className="mb-2 opacity-50" />
              <span className="text-xs">封面加载失败</span>
            </div>
          )}

          {/* Gradient Overlay (Only if image loaded) */}
          {!imageError && (
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-60 group-hover:opacity-40 transition-opacity"></div>
          )}

          {/* Type Badge */}
          <div className="absolute top-3 right-3 bg-black/40 backdrop-blur-md px-2.5 py-1 rounded-lg flex items-center gap-1.5 text-white text-xs font-medium border border-white/10 z-10">
            {work.type === 'video' ? <PlayCircle size={12} /> : <ImageIcon size={12} />}
            {work.type === 'video' ? '视频' : '图文'}
          </div>

          {/* Hover Action */}
          <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300 pointer-events-none z-10">
            <span className="bg-white/90 backdrop-blur text-gray-900 px-5 py-2 rounded-full text-sm font-bold shadow-xl transform translate-y-4 group-hover:translate-y-0 transition-transform">
              查看详情
            </span>
          </div>

          {/* Stats Overlay (Bottom) */}
          <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between text-white text-xs font-medium opacity-90 z-10">
            <div className="flex items-center gap-1.5 bg-black/20 px-2 py-0.5 rounded-md backdrop-blur-sm">
              <Heart size={12} className="text-white fill-white" />
              {work.stats.digg_count > 10000 ? (work.stats.digg_count / 10000).toFixed(1) + 'w' : work.stats.digg_count}
            </div>
          </div>
        </div>

        {/* Info Section */}
        <div className="p-4 flex flex-col flex-1">
          <p className="text-sm text-gray-700 line-clamp-2 mb-3 leading-relaxed font-medium flex-1 h-[42px]" title={work.desc}>
            {work.desc}
          </p>
          <div className="flex items-center justify-between mt-auto pt-3 border-t border-gray-50">
            <div className="flex items-center gap-2 max-w-[70%]">
              <img src={work.author.avatar} className="w-5 h-5 rounded-full border border-gray-100 shadow-sm" loading="lazy" onError={(e) => (e.currentTarget.src = 'https://ui-avatars.com/api/?name=User&background=random')} />
              <span className="text-xs text-gray-500 truncate hover:text-blue-600 cursor-pointer">{work.author.nickname}</span>
            </div>
            <span className="text-[10px] text-gray-400">{work.create_time.split(' ')[0]}</span>
          </div>
        </div>
      </div>
    </div>
  );
}, (prev, next) => {
  return prev.work.id === next.work.id;
});