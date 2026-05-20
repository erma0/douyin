/**
 * 通用格式化工具函数
 */

import { DouyinWork } from '../types';

export interface FilenameFieldDef {
  key: string;
  label: string;
}

export const FILENAME_FIELDS: FilenameFieldDef[] = [
  { key: 'id', label: '作品ID' },
  { key: 'title', label: '标题' },
  { key: 'author', label: '作者' },
  { key: 'date', label: '发布日期' },
  { key: 'type', label: '类型' },
  { key: 'duration', label: '时长' },
  { key: 'music', label: '音乐' },
];

function resolveField(work: DouyinWork, field: string): string {
  switch (field) {
    case 'id':
      return work.id || '';
    case 'title':
      return work.desc || '无标题';
    case 'author':
      return work.author?.nickname || '';
    case 'date': {
      if (work.create_timestamp) {
        const d = new Date(work.create_timestamp * 1000);
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${y}-${m}-${day}`;
      }
      return work.create_time || '';
    }
    case 'type':
      return work.type === 'image' ? '图文' : '视频';
    case 'duration': {
      if (work.duration) {
        const seconds = Math.floor(work.duration / 1000);
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return `${String(m).padStart(2, '0')}-${String(s).padStart(2, '0')}`;
      }
      return '';
    }
    case 'music':
      return work.music?.title || '';
    default:
      return '';
  }
}

export function generateFilename(
  work: DouyinWork,
  fields: string[],
  separator: string = '_',
): string {
  const parts: string[] = [];
  for (const field of fields) {
    const value = resolveField(work, field);
    if (value) {
      parts.push(sanitizeFilenamePart(value));
    }
  }

  if (parts.length === 0) {
    return work.id || 'unknown';
  }

  return parts.join(separator);
}

function sanitizeFilenamePart(text: string): string {
  return text
    .replace(/[<>:"/\\|?*\x00-\x1f]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

export function generateFilenamePreview(
  fields: string[],
  separator: string = '_',
): string {
  const exampleWork: DouyinWork = {
    id: '7123456789',
    desc: '示例作品标题',
    author: {
      nickname: '张三',
      avatar: '',
      uid: 'abc123',
    },
    type: 'video',
    cover: '',
    create_time: '2024-01-15',
    create_timestamp: 1705276800,
    duration: 125000,
    music: {
      id: 'm1',
      title: '背景音乐',
      url: '',
      cover: '',
    },
    stats: {
      digg_count: 100,
      comment_count: 10,
      share_count: 5,
    },
  };

  const filename = generateFilename(exampleWork, fields, separator);
  return `${filename}.mp4`;
}

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