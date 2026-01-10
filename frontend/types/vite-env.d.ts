/**
 * Vite 环境变量类型声明
 */

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  // 添加其他 VITE_ 前缀的环境变量
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
