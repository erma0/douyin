
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

// Global window extension for pywebview
declare global {
  interface Window {
    pywebview?: {
      api: {
        // 采集任务（支持流式返回）
        start_task: (type: TaskType, target: string, limit: number, callback?: (message: any) => void) => Promise<{ task_id: string; status: string }>;
        // 系统功能
        open_url: (url: string) => void;
        get_settings: () => Promise<AppSettings>;
        save_settings: (settings: AppSettings) => Promise<void>;
        select_folder: () => Promise<string>;
        // Aria2配置
        get_aria2_config: () => Promise<any>;
        // 任务状态
        get_task_status: (task_id?: string) => Promise<any[]>;
        // 日志订阅
        subscribe_to_logs: (callback: (log: any) => void) => void;
        unsubscribe_from_logs: (callback: (log: any) => void) => void;
        // Cookie相关
        get_browser_cookie: (browser: string) => Promise<{
          success: boolean;
          cookie: string;
          error?: string;
        }>;
        // 其他API方法
        is_first_run_check: () => Promise<boolean>;
        start_aria2_after_loaded: () => Promise<void>;
        get_task_results: (taskId: string) => Promise<any[]>;
        get_clipboard_text: () => Promise<string>;
        read_config_file: (filePath: string) => Promise<string>;
        get_aria2_config_path: (taskId?: string) => Promise<string>;
      };
    };
  }
}