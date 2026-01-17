
export enum TaskType {
  AWEME = 'aweme',           // 单个作品
  POST = 'post',             // 用户主页作品
  FAVORITE = 'favorite',     // 用户喜欢
  COLLECTION = 'collection', // 用户收藏
  MUSIC = 'music',           // 音乐原声
  HASHTAG = 'hashtag',       // 话题挑战
  MIX = 'mix',               // 合集
  SEARCH = 'search',         // 关键词搜索
  FOLLOWING = 'following',   // 用户关注
  FOLLOWER = 'follower',     // 用户粉丝
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
  userAgent: string;
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