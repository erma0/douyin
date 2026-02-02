import {
  ChevronLeft, ChevronRight,
  Download,
  HardDrive,
  Heart,
  Image as ImageIcon,
  Link,
  Loader2,
  MessageCircle,
  Music,
  Share2,
  X
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { bridge } from '../services/bridge';
import { logger } from '../services/logger';
import { DouyinWork } from '../types';
import { withErrorHandling } from '../utils/errorHandler';
import { toast } from './Toast';

/** 本地文件信息 */
interface LocalFileInfo {
  found: boolean;
  videoUrl?: string;
  imageUrls?: string[];
}

interface DetailModalProps {
  work: DouyinWork | null;
  onClose: () => void;
  onPrev?: () => void;
  onNext?: () => void;
  hasPrev?: boolean;
  hasNext?: boolean;
  addDownload: (workId: string, url: string, filename: string, downloadPath: string, cookie?: string) => Promise<boolean>;
  startPolling: () => void;
  progress: Record<string, number>;
}

export const DetailModal: React.FC<DetailModalProps> = ({
  work, onClose, onPrev, onNext, hasPrev, hasNext,
  addDownload, startPolling, progress
}) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isDownloading, setIsDownloading] = useState(false);
  const [localFile, setLocalFile] = useState<LocalFileInfo>({ found: false });
  const [isCheckingLocal, setIsCheckingLocal] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState<number | null>(null);

  // 检查本地文件
  const checkLocalFile = async (workId: string) => {
    setIsCheckingLocal(true);
    try {
      const result = await bridge.findLocalFile(workId);
      if (result.found) {
        if (result.video_path) {
          setLocalFile({
            found: true,
            videoUrl: bridge.getMediaUrl(result.video_path),
          });
        } else if (result.images && result.images.length > 0) {
          setLocalFile({
            found: true,
            imageUrls: result.images.map(p => bridge.getMediaUrl(p)),
          });
        }
      } else {
        setLocalFile({ found: false });
      }
    } catch {
      setLocalFile({ found: false });
    } finally {
      setIsCheckingLocal(false);
    }
  };

  useEffect(() => {
    setCurrentImageIndex(0);
    setLocalFile({ found: false });
    setDownloadProgress(null);
    setIsDownloading(false);
    if (work) {
      checkLocalFile(work.id);
    }
  }, [work]);

  // 监听下载进度变化
  useEffect(() => {
    if (!work) return;

    const workProgress = progress[work.id];
    
    console.log('[DetailModal] progress 更新:', { 
      workId: work.id, 
      workProgress, 
      allProgressKeys: Object.keys(progress),
    });
    
    if (workProgress === undefined || workProgress === null) {
      return;
    }
    
    setDownloadProgress(workProgress);
    
    if (workProgress >= 0 && workProgress < 100) {
      setIsDownloading(true);
    } else if (workProgress === 100) {
      logger.success(`✓ 作品下载完成: ${work.id}`);
      setIsDownloading(false);
      
      const checkAndPlay = async () => {
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const result = await bridge.findLocalFile(work.id);
        console.log('[DetailModal] 下载完成，检查本地文件:', result);
        
        if (result.found) {
          if (result.video_path) {
            setLocalFile({
              found: true,
              videoUrl: bridge.getMediaUrl(result.video_path),
            });
            toast.success('下载完成，开始播放');
          } else if (result.images && result.images.length > 0) {
            setLocalFile({
              found: true,
              imageUrls: result.images.map(p => bridge.getMediaUrl(p)),
            });
            toast.success('下载完成');
          }
        } else {
          let retryCount = 0;
          const maxRetries = 5;
          const retryInterval = setInterval(async () => {
            retryCount++;
            const retryResult = await bridge.findLocalFile(work.id);
            console.log(`[DetailModal] 重试检查本地文件 (${retryCount}/${maxRetries}):`, retryResult);
            
            if (retryResult.found || retryCount >= maxRetries) {
              clearInterval(retryInterval);
              if (retryResult.found) {
                if (retryResult.video_path) {
                  setLocalFile({
                    found: true,
                    videoUrl: bridge.getMediaUrl(retryResult.video_path),
                  });
                  toast.success('下载完成，开始播放');
                } else if (retryResult.images && retryResult.images.length > 0) {
                  setLocalFile({
                    found: true,
                    imageUrls: retryResult.images.map(p => bridge.getMediaUrl(p)),
                  });
                  toast.success('下载完成');
                }
              }
            }
          }, 1000);
        }
      };
      
      checkAndPlay();
    } else if (workProgress < 0) {
      logger.error(`✗ 作品下载失败: ${work.id}`);
      setIsDownloading(false);
      setDownloadProgress(null);
      toast.error('下载失败');
    }
  }, [progress, work]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'ArrowLeft') onPrev?.();
      if (e.key === 'ArrowRight') onNext?.();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose, onPrev, onNext]);

  if (!work) return null;


  const handleDownload = withErrorHandling(async () => {
    setIsDownloading(true);
    setDownloadProgress(0);

    try {
      const settings = await bridge.getSettings();
      const downloadPath = settings.downloadPath || '';
      const cookie = settings.cookie || '';
      const baseFilename = `${work.id}_${work.desc || '无标题'}`;

      let successCount = 0;

      if (work.type === 'video' && work.videoUrl) {
        const filename = `${baseFilename}.mp4`;
        toast.info(`正在添加视频下载任务...`);
        logger.download.start(`开始下载视频: ${filename}`, { workId: work.id });

        const result = await addDownload(
          work.id,
          work.videoUrl,
          filename,
          downloadPath,
          cookie
        );

        if (result === true) {
          successCount++;
          startPolling();
          logger.download.success(`视频下载已添加到队列: ${filename}`, { workId: work.id });
        } else {
          setIsDownloading(false);
          setDownloadProgress(null);
          throw new Error('视频下载添加失败');
        }
      } else if (work.type === 'image' && work.images) {
        const imageDir = `${downloadPath}/${baseFilename}`;
        toast.info(`正在添加图集下载任务: ${work.images.length} 张图片`);
        logger.download.start(`开始下载图集: ${work.images.length} 张图片`, { workId: work.id });

        for (let i = 0; i < work.images.length; i++) {
          try {
            const filename = `${work.id}_${i + 1}.jpeg`;
            const result = await addDownload(
              `${work.id}_${i}`,
              work.images[i],
              filename,
              imageDir,
              cookie
            );

            if (result === true) {
              successCount++;
              logger.download.progress(`图片 ${i + 1} 下载已添加`, { workId: work.id, progress: `${successCount}/${work.images.length}` });
            } else {
              logger.download.error(`图片 ${i + 1} 下载添加失败`, { workId: work.id, imageIndex: i });
            }
          } catch (err) {
            logger.download.error(`图片 ${i + 1} 下载失败`, err instanceof Error ? err : { workId: work.id, imageIndex: i, error: String(err) });
          }
        }

        if (successCount > 0) {
          toast.success(`已添加 ${successCount} 张图片到下载队列`);
          setIsDownloading(false);
          setDownloadProgress(null);
        }
      }

      if (work.type === 'video') {
        startPolling();
      }

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '下载失败';
      toast.error(errorMsg);
      setIsDownloading(false);
      setDownloadProgress(null);
      throw error;
    }
  }, { workId: work.id, workType: work.type }, {
    showToast: false,
    logLevel: 'error'
  });

  const downloadCover = async () => {
    try {
      const settings = await bridge.getSettings();
      const downloadPath = settings.downloadPath || '';
      const cookie = settings.cookie || '';
      const filename = `${work.id}_cover.jpg`;
      const result = await addDownload(`${work.id}_cover`, work.cover, filename, downloadPath, cookie);

      if (result === true) {
        toast.success('封面下载已添加到队列');
        logger.success(`[DetailModal] 封面下载已添加到队列: ${work.id}`);
      } else {
        toast.error('封面下载添加失败');
        logger.error(`[DetailModal] 封面下载添加失败: ${work.id}`);
      }
    } catch (e) {
      toast.error(`封面下载失败: ${e instanceof Error ? e.message : '未知错误'}`);
      logger.error(`[DetailModal] 封面下载失败: ${work.id} - ${e}`);
    }
  };

  const downloadMusic = async () => {
    if (work.music?.url) {
      try {
        const settings = await bridge.getSettings();
        const downloadPath = settings.downloadPath || '';
        const cookie = settings.cookie || '';
        const filename = `${work.id}_music.mp3`;
        const result = await addDownload(`${work.id}_music`, work.music.url, filename, downloadPath, cookie);

        if (result === true) {
          toast.success('音乐下载已添加到队列');
          logger.success(`[DetailModal] 音乐下载已添加到队列: ${work.id}`);
        } else {
          toast.error('音乐下载添加失败');
          logger.error(`[DetailModal] 音乐下载添加失败: ${work.id}`);
        }
      } catch (e) {
        toast.error(`音乐下载失败: ${e instanceof Error ? e.message : '未知错误'}`);
        logger.error(`[DetailModal] 音乐下载失败: ${work.id} - ${e}`);
      }
    } else {
      toast.error('该作品没有音乐资源');
    }
  };

  const copyLink = () => {
    navigator.clipboard.writeText(`https://www.douyin.com/video/${work.id}`);
    toast.success('链接已复制');
  };

  const nextImage = (e: React.MouseEvent) => {
    e.stopPropagation();
    const maxIndex = (localFile.found && localFile.imageUrls ? localFile.imageUrls.length : work.images?.length) || 1;
    if (currentImageIndex < maxIndex - 1) {
      setCurrentImageIndex(prev => prev + 1);
    }
  };

  const prevImage = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (currentImageIndex > 0) {
      setCurrentImageIndex(prev => prev - 1);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm animate-in fade-in duration-200" onClick={onClose}>
      <div
        className="bg-white rounded-2xl shadow-2xl flex overflow-hidden w-[720px] h-[85vh] relative animate-in zoom-in-95 duration-200 border border-gray-200/50"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Left Side: Media */}
        <div className="flex-1 bg-black relative flex items-center justify-center group overflow-hidden">
          {hasPrev && (
            <button
              onClick={(e) => { e.stopPropagation(); onPrev?.(); }}
              className="absolute left-4 top-1/2 -translate-y-1/2 z-30 p-2 rounded-full bg-white/10 hover:bg-white/20 text-white backdrop-blur-md transition-all opacity-0 group-hover:opacity-100 hover:scale-110"
            >
              <ChevronLeft size={24} />
            </button>
          )}
          {hasNext && (
            <button
              onClick={(e) => { e.stopPropagation(); onNext?.(); }}
              className="absolute right-4 top-1/2 -translate-y-1/2 z-30 p-2 rounded-full bg-white/10 hover:bg-white/20 text-white backdrop-blur-md transition-all opacity-0 group-hover:opacity-100 hover:scale-110"
            >
              <ChevronRight size={24} />
            </button>
          )}

          {work.type === 'video' ? (
            localFile.found && localFile.videoUrl ? (
              <div className="relative w-full h-full flex items-center justify-center">
                <video
                  key={localFile.videoUrl}
                  src={localFile.videoUrl}
                  controls
                  autoPlay
                  loop
                  playsInline
                  className="max-w-full max-h-full w-auto h-auto object-contain"
                />
                <div className="absolute top-4 left-4 flex items-center gap-1.5 px-2 py-1 bg-green-500/90 text-white text-xs rounded-full backdrop-blur-sm">
                  <HardDrive size={12} />
                  本地文件
                </div>
              </div>
            ) : (
              <div className="relative w-full h-full flex items-center justify-center">
                <img src={work.cover} className="absolute inset-0 w-full h-full object-cover blur-sm opacity-30" alt="" />
                <img src={work.cover} className="relative max-w-full max-h-full object-contain z-10" alt="" />
                {!isCheckingLocal && (
                  <div className="absolute inset-0 flex items-center justify-center z-20">
                    <div className="bg-black/60 backdrop-blur-md rounded-2xl p-6 max-w-[280px] text-center border border-white/10 shadow-2xl">
                      <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-white/10 flex items-center justify-center">
                        {isDownloading ? (
                          <Loader2 className="animate-spin text-white" size={24} />
                        ) : (
                          <Download size={24} className="text-white" />
                        )}
                      </div>
                      
                      {isDownloading && downloadProgress !== null && downloadProgress >= 0 ? (
                        <>
                          <p className="text-white text-sm font-medium mb-2">正在下载...</p>
                          <div className="w-full h-2 bg-white/20 rounded-full overflow-hidden mb-2">
                            <div 
                              className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-300"
                              style={{ width: `${downloadProgress}%` }}
                            />
                          </div>
                          <p className="text-white/80 text-xs">{downloadProgress}%</p>
                        </>
                      ) : (
                        <>
                          <p className="text-white text-sm font-medium mb-2">视频暂无法在线播放</p>
                          <p className="text-white/60 text-xs mb-4">受跨域限制，请下载后本地观看</p>
                          <button
                            onClick={handleDownload}
                            disabled={isDownloading}
                            className="w-full py-2.5 bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 rounded-lg text-white text-sm font-medium transition-all active:scale-95 shadow-lg disabled:opacity-50"
                          >
                            立即下载
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )
          ) : (
            <div className="relative w-full h-full flex items-center justify-center">
              {localFile.found && localFile.imageUrls && (
                <div className="absolute top-4 left-4 flex items-center gap-1.5 px-2 py-1 bg-green-500/90 text-white text-xs rounded-full backdrop-blur-sm z-10">
                  <HardDrive size={12} />
                  本地文件
                </div>
              )}
              <img
                src={
                  localFile.found && localFile.imageUrls
                    ? localFile.imageUrls[currentImageIndex] || work.cover
                    : work.images?.[currentImageIndex] || work.cover
                }
                className="max-w-full max-h-full object-contain"
                alt=""
              />

              {((localFile.found && localFile.imageUrls && localFile.imageUrls.length > 1) ||
                (work.images && work.images.length > 1)) && (
                <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-4 z-20">
                  <button
                    onClick={prevImage}
                    disabled={currentImageIndex === 0}
                    className="p-1.5 rounded-full bg-white/10 text-white hover:bg-white/20 disabled:opacity-30 disabled:cursor-not-allowed transition-all backdrop-blur-md border border-white/10"
                  >
                    <ChevronLeft size={16} />
                  </button>
                  <span className="text-xs font-medium text-white/90 bg-black/40 px-3 py-1 rounded-full backdrop-blur-md border border-white/10 tabular-nums">
                    {currentImageIndex + 1} / {localFile.found && localFile.imageUrls ? localFile.imageUrls.length : work.images?.length || 0}
                  </span>
                  <button
                    onClick={nextImage}
                    disabled={currentImageIndex === ((localFile.found && localFile.imageUrls ? localFile.imageUrls.length : work.images?.length) || 1) - 1}
                    className="p-1.5 rounded-full bg-white/10 text-white hover:bg-white/20 disabled:opacity-30 disabled:cursor-not-allowed transition-all backdrop-blur-md border border-white/10"
                  >
                    <ChevronRight size={16} />
                  </button>
                </div>
              )}
            </div>
          )}
        </div>


        {/* Right Side: Info */}
        <div className="w-[300px] bg-white flex flex-col border-l border-gray-100 shrink-0">
          <div className="px-5 py-4 flex items-center justify-between border-b border-gray-100 bg-gray-50/30">
            <span className="font-bold text-gray-800">作品详情</span>
            <div className="flex items-center gap-1">
              <button
                onClick={copyLink}
                className="p-2 hover:bg-gray-100 rounded-lg text-gray-500 hover:text-blue-600 transition-colors"
                title="复制链接"
              >
                <Link size={18} />
              </button>
              <div className="w-px h-4 bg-gray-200 mx-1"></div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 rounded-lg text-gray-400 hover:text-gray-800 transition-colors"
                title="关闭"
              >
                <X size={20} />
              </button>
            </div>
          </div>

          <div className="px-5 py-4 flex items-center gap-3">
            <img src={work.author.avatar} className="w-10 h-10 rounded-full border border-gray-100" />
            <div className="min-w-0 flex-1">
              <div className="font-semibold text-sm truncate text-gray-900">{work.author.nickname}</div>
              <div className="text-xs text-gray-400 truncate">
                {work.author.unique_id
                  ? `@${work.author.unique_id}`
                  : work.author.short_id
                    ? `ID: ${work.author.short_id}`
                    : `UID: ${work.author.uid.substring(0, 20)}...`}
              </div>
            </div>
          </div>

          <div className="px-5 py-2 flex-1 overflow-y-auto custom-scrollbar">
            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{work.desc}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {work.desc.match(/#\S+/g)?.map((tag, i) => (
                <span key={i} className="text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded cursor-pointer hover:bg-blue-100">
                  {tag}
                </span>
              ))}
            </div>
            <div className="mt-4 text-xs text-gray-400 border-t border-gray-50 pt-3">
              发布于 {work.create_time}
            </div>
          </div>

          <div className="px-5 py-3 border-t border-gray-50 grid grid-cols-3 gap-2">
            <div className="flex flex-col items-center gap-1 text-gray-600 p-2 rounded-lg bg-gray-50">
              <Heart size={16} className={work.stats.digg_count > 0 ? "fill-red-500 text-red-500" : ""} />
              <span className="text-xs font-medium">{work.stats.digg_count}</span>
            </div>
            <div className="flex flex-col items-center gap-1 text-gray-600 p-2 rounded-lg bg-gray-50">
              <MessageCircle size={16} />
              <span className="text-xs font-medium">{work.stats.comment_count}</span>
            </div>
            <div className="flex flex-col items-center gap-1 text-gray-600 p-2 rounded-lg bg-gray-50">
              <Share2 size={16} />
              <span className="text-xs font-medium">{work.stats.share_count}</span>
            </div>
          </div>

          <div className="p-5 border-t border-gray-100 bg-gray-50/50 space-y-3">
            <div className="flex gap-2">
              <button
                onClick={downloadCover}
                className="flex-1 flex items-center justify-center gap-1.5 py-2 bg-white border border-gray-200 text-gray-700 rounded-lg text-xs font-medium hover:bg-gray-50 hover:border-gray-300 transition-all active:scale-95 shadow-sm"
              >
                <ImageIcon size={14} />
                封面
              </button>

              <div className="relative group/tooltip flex-1">
                <button
                  onClick={downloadMusic}
                  className="w-full flex items-center justify-center gap-1.5 py-2 bg-white border border-gray-200 text-gray-700 rounded-lg text-xs font-medium hover:bg-gray-50 hover:border-gray-300 transition-all active:scale-95 shadow-sm"
                >
                  <Music size={14} />
                  原声
                </button>
                {work.music?.title && (
                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-[10px] rounded opacity-0 group-hover/tooltip:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-30 shadow-lg">
                    {work.music.title}
                    <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-900"></div>
                  </div>
                )}
              </div>
            </div>

            <button
              onClick={handleDownload}
              disabled={isDownloading}
              className="w-full py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg text-sm font-medium shadow-lg shadow-blue-500/30 hover:shadow-blue-500/40 hover:from-blue-700 hover:to-indigo-700 active:scale-95 transition-all flex items-center justify-center gap-2"
            >
              {isDownloading ? <Loader2 className="animate-spin" size={16} /> : <Download size={16} />}
              {work.type === 'video' ? '下载作品文件' : '打包下载图片'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
