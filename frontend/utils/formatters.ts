/**
 * 通用格式化工具函数
 */

/**
 * 格式化文件大小
 */
export const formatSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
};

/**
 * 格式化下载速度
 */
export const formatSpeed = (bytesPerSecond: number): string => {
  return `${formatSize(bytesPerSecond)}/s`;
};

/**
 * 格式化时间（秒转 HH:MM:SS）
 */
export const formatTime = (seconds: number): string => {
  if (seconds === Infinity || seconds < 0) return '--:--:--';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
};

/**
 * 格式化速度（简化版，用于 Sidebar）
 */
export const formatSpeedSimple = (bytesPerSecond: number): string => {
  const mbps = bytesPerSecond / 1024 / 1024;
  return mbps >= 0.1 ? `${mbps.toFixed(1)} MB/s` : '0 MB/s';
};