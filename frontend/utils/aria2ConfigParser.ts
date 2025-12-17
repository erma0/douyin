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
  // 处理空内容
  if (!configContent || configContent.trim().length === 0) {
    logger.warn('配置文件内容为空');
    return [];
  }

  // 按行分割并过滤空行
  const lines = configContent
    .split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0);

  const tasks: ParsedTask[] = [];
  let skippedCount = 0;

  // 按3行一组解析
  for (let i = 0; i < lines.length; i += 3) {
    // 检查是否有完整的3行
    if (i + 2 >= lines.length) {
      logger.warn(`配置文件格式不完整，跳过最后 ${lines.length - i} 行`);
      skippedCount += lines.length - i;
      break;
    }

    const url = lines[i];
    const dirLine = lines[i + 1];
    const outLine = lines[i + 2];

    // 解析dir和out（支持制表符或空格开头）
    const dirMatch = dirLine.match(/^\s*dir=(.+)$/);
    const outMatch = outLine.match(/^\s*out=(.+)$/);

    // 验证格式
    if (!url || !dirMatch || !outMatch) {
      logger.warn(`跳过格式错误的任务组 ${Math.floor(i / 3) + 1}`, {
        url: url || '(空)',
        dirLine: dirLine || '(空)',
        outLine: outLine || '(空)'
      });
      skippedCount++;
      continue;
    }

    // 提取值
    const dir = dirMatch[1].trim();
    const out = outMatch[1].trim();

    // 验证URL格式（基本检查）
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      logger.warn(`跳过无效URL的任务: ${url}`);
      skippedCount++;
      continue;
    }

    // 验证dir和out不为空
    if (!dir || !out) {
      logger.warn(`跳过dir或out为空的任务组 ${Math.floor(i / 3) + 1}`);
      skippedCount++;
      continue;
    }

    // 添加到任务列表
    tasks.push({ url, dir, out });
  }

  // 输出解析结果统计
  logger.info(`配置文件解析完成: 成功 ${tasks.length} 个任务${skippedCount > 0 ? `，跳过 ${skippedCount} 个` : ''}`);

  return tasks;
}
