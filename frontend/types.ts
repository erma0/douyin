
export enum TaskType {
  POST = 'post', // 指定作品
  USER_POST = 'user_post', // 用户主页
  USER_LIKE = 'user_like', // 用户喜欢
  USER_FAVORITE = 'user_favorite', // 用户收藏
  MUSIC = 'music', // 音乐原声
  CHALLENGE = 'challenge', // 挑战话题
  COLLECTION = 'collection', // 合集
  SEARCH = 'search', // 关键词搜索
  DOWNLOAD_MANAGER = 'download_manager', // 下载管理
}

export interface DouyinWork {
  id: string;
  desc: string;
  author: {
    nickname: string;
    avatar: string;
    uid: string;
    unique_id?: string; // 抖音号
    short_id?: string; // 短ID
  };
  type: 'video' | 'image';
  cover: string;
  videoUrl?: string; // For video type
  images?: string[]; // For image type
  music?: {
    id: string;
    title: string;
    url: string;
    cover: string;
  };
  stats: {
    digg_count: number;
    comment_count: number;
    share_count: number;
  };
  create_time: string;
  duration?: number; // 视频时长（毫秒）
}

export interface DownloadProgress {
  id: string;
  work_id?: string;
  filename: string;
  progress: number; // 0-100
  status: 'pending' | 'downloading' | 'completed' | 'error' | 'canceled' | 'paused';
  speed: number; // B/s
  path: string;
  error?: string;
  totalLength: number;
  completedLength: number;
}

export interface AppSettings {
  cookie: string;
  downloadPath: string;
  maxRetries: number;
  maxConcurrency: number;
  enableIncrementalFetch: boolean;
  aria2Host: string;
  aria2Port: number;
  aria2Secret: string;
}

export interface GlobalDownloadStat {
  downloadSpeed: string;
  numActive: string;
  numWaiting: string;
  numStopped: string;
}