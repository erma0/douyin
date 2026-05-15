/**
 * Aria2配置文件解析工具
 * 
 * 解析Aria2输入文件格式的配置文件
 * 格式：每个任务占3行
 * - 第1行：下载URL
 * - 第2行：dir=<下载目录>
 * - 第3行：out=<输出文件名>
 */

import { logger } from '../services/logger';

/**
 * 解析后的任务接口
 */
export interface ParsedTask {
  url: string;        // 下载URL
  dir: string;        // 下载目录
  out: string;        // 输出文件名
}

/**
 * 解析Aria2配置文件
 * 
 * @param configContent 配置文件内容字符串
 * @returns 解析后的任务列表
 * 
 * @example
 * ```
 * const content = `
 * https://example.com/video1.mp4
 *   dir=/path/to/download
 *   out=video1.mp4
 * https://example.com/video2.mp4
 *   dir=/path/to/download
 *   out=video2.mp4
 * `;
 * const tasks = parseAria2Config(content);
 * // tasks = [
 * //   { url: 'https://example.com/video1.mp4', dir: '/path/to/download', out: 'video1.mp4' },
 * //   { url: 'https://example.com/video2.mp4', dir: '/path/to/download', out: 'video2.mp4' }
 * // ]
 * ```
 */
export function parseAria2Config(configContent: string): ParsedTask[] {
  if (!configContent || configContent.trim().length === 0) {
    logger.warn('配置文件内容为空');
    return [];
  }

  const lines = configContent
    .split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0);

  const tasks: ParsedTask[] = [];
  let skippedCount = 0;
  let currentUrl: string | null = null;
  let currentDir: string | null = null;
  let currentOut: string | null = null;

  const flushTask = () => {
    if (currentUrl && currentDir && currentOut) {
      if (currentUrl.startsWith('http://') || currentUrl.startsWith('https://')) {
        tasks.push({ url: currentUrl, dir: currentDir, out: currentOut });
      } else {
        logger.warn(`跳过无效URL的任务: ${currentUrl}`);
        skippedCount++;
      }
    } else if (currentUrl || currentDir || currentOut) {
      skippedCount++;
    }
    currentUrl = null;
    currentDir = null;
    currentOut = null;
  };

  for (const line of lines) {
    const dirMatch = line.match(/^\s*dir=(.+)$/);
    const outMatch = line.match(/^\s*out=(.+)$/);

    if (dirMatch) {
      currentDir = dirMatch[1].trim();
    } else if (outMatch) {
      currentOut = outMatch[1].trim();
    } else if (line.startsWith('http://') || line.startsWith('https://')) {
      flushTask();
      currentUrl = line;
    } else {
      if (!currentUrl) {
        currentUrl = line;
      }
    }

    if (currentUrl && currentDir && currentOut) {
      flushTask();
    }
  }

  flushTask();

  logger.info(`配置文件解析完成: 成功 ${tasks.length} 个任务${skippedCount > 0 ? `，跳过 ${skippedCount} 个` : ''}`);

  return tasks;
}
