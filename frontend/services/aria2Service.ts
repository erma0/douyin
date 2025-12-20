/**
 * Aria2下载管理服务
 * 
 * 前端直接通过JSON-RPC与Aria2通信，无需经过Python后端
 * 使用原生fetch实现RPC调用，无需第三方依赖
 * 
 * 主要功能：
 * - 连接管理：初始化和维护与Aria2的连接
 * - 任务管理：添加、暂停、恢复、取消下载任务
 * - 状态查询：获取任务状态和全局统计信息
 */

import { bridge } from './bridge';
import { logger } from './logger';

/**
 * 下载任务接口
 * 描述单个下载任务的完整状态
 */
export interface DownloadTask {
  gid: string;                                                              // 任务唯一标识符
  status: 'active' | 'waiting' | 'paused' | 'error' | 'complete' | 'removed';  // 任务状态
  totalLength: number;                                                      // 文件总大小（字节）
  completedLength: number;                                                  // 已下载大小（字节）
  downloadSpeed: number;                                                    // 下载速度（字节/秒）
  uploadSpeed: number;                                                      // 上传速度（字节/秒）
  progress: number;                                                         // 下载进度（百分比）
  files: Array<{                                                            // 文件列表
    path: string;                                                           // 文件路径
    length: number;                                                         // 文件大小
    completedLength: number;                                                // 已下载大小
    uris?: Array<{                                                          // URI列表
      uri: string;                                                          // 下载URL
      status: string;                                                       // URI状态
    }>;
  }>;
  errorCode?: string;                                                       // 错误代码（如果有）
  errorMessage?: string;                                                    // 错误信息（如果有）
  filename?: string;                                                        // 文件名
  dir?: string;                                                             // 下载目录
  connections?: number;                                                     // 连接数
}

// 导出为Aria2Task别名，供其他组件使用
export type Aria2Task = DownloadTask;

/**
 * 全局统计信息接口
 * 描述Aria2的整体下载状态
 */
export interface GlobalStat {
  downloadSpeed: number;    // 全局下载速度（字节/秒）
  uploadSpeed: number;      // 全局上传速度（字节/秒）
  numActive: number;        // 活动任务数
  numWaiting: number;       // 等待任务数
  numStopped: number;       // 已停止任务数
}

/**
 * Aria2服务类
 * 封装所有与Aria2的交互逻辑
 */
class Aria2Service {
  private rpcUrl: string = '';          // Aria2 RPC服务地址
  private secret: string = '';          // RPC密钥（用于认证）
  private connected: boolean = false;   // 连接状态
  private requestId: number = 1;        // RPC请求ID计数器
  private connectionCheckInterval: NodeJS.Timeout | null = null;  // 连接检查定时器
  private connectionAttempts: number = 0;  // 连接尝试次数
  private maxConnectionAttempts: number = 0;  // 最大连接尝试次数（0表示无限重试）
  private connectionCheckDelay: number = 1000;  // 连接检查间隔（毫秒）- 1秒间隔，平衡响应速度和资源消耗
  private connectionCallbacks: Set<(connected: boolean) => void> = new Set();  // 连接状态回调函数

  /**
   * 初始化Aria2连接
   * 
   * @param host Aria2主机地址
   * @param port Aria2 RPC端口
   * @param secret RPC密钥，默认为空
   * @param autoReconnect 是否自动重连，默认true
   * @returns 连接是否成功（立即返回，不等待异步连接）
   */
  async connect(
    host: string,
    port: number,
    secret: string = '',
    autoReconnect: boolean = true
  ): Promise<boolean> {
    // 如果已经连接到相同的RPC服务，并且连接状态为已连接，则通知状态后返回
    const newRpcUrl = `http://${host}:${port}/jsonrpc`;
    if (this.rpcUrl === newRpcUrl && this.secret === secret && this.connected) {
      console.log('[aria2Service] 已连接到相同的RPC服务，通知当前状态');
      // 热更新时确保通知当前连接状态
      this.notifyConnectionStatus(true);
      return true;
    }

    this.rpcUrl = newRpcUrl;
    this.secret = secret;
    this.connectionAttempts = 0;

    // 如果需要自动重连，直接启动连接检查
    if (autoReconnect) {
      this.startConnectionCheck();
    }

    // 立即返回true，实际连接在后台进行
    // 参考AriaNg的做法：不阻塞初始化，让轮询自动处理连接
    return true;
  }

  /**
   * 测试Aria2连接
   * @returns 连接是否成功
   */
  private async testConnection(): Promise<boolean> {
    this.connectionAttempts++;

    // 前几次尝试时显示详细日志，后续静默
    const showDetailedLog = this.connectionAttempts <= 5;

    if (showDetailedLog) {
      console.log(`[aria2Service] 测试连接 (尝试 ${this.connectionAttempts})`);
    }

    try {
      // 测试连接：调用getVersion方法
      const version = await this.call('aria2.getVersion');

      // 连接成功
      const wasDisconnected = !this.connected;
      this.connected = true;

      // 连接成功后停止轮询，避免浪费资源
      this.stopConnectionCheck();

      if (showDetailedLog || wasDisconnected) {
        console.log(`[aria2Service] ✓ 连接成功! Aria2版本: ${version?.version || 'unknown'}`);
      }

      // 只在状态变化时通知
      if (wasDisconnected) {
        console.log('[aria2Service] 状态从断开变为连接，准备通知...');
        console.log(`[aria2Service] 通知 ${this.connectionCallbacks.size} 个回调`);
        this.notifyConnectionStatus(true);
        console.log('[aria2Service] 通知完成');
      }

      return true;
    } catch (error) {
      if (showDetailedLog) {
        console.log(`[aria2Service] 连接失败:`, error);
      }

      // 检查是否达到最大尝试次数
      if (this.maxConnectionAttempts > 0 && this.connectionAttempts >= this.maxConnectionAttempts) {
        console.error(`✗ Aria2连接失败，已达到最大尝试次数 ${this.maxConnectionAttempts}`);
        this.connected = false;
        this.stopConnectionCheck();
        this.notifyConnectionStatus(false);
        return false;
      }

      // 静默失败，不输出日志（避免日志刷屏）
      // 只在状态变化时通知
      const wasConnected = this.connected;
      this.connected = false;

      if (wasConnected) {
        // 从连接变为断开，才通知
        this.notifyConnectionStatus(false);
      }

      return false;
    }
  }

  /**
   * 启动连接状态检查
   * 避免重复启动，防止内存泄漏
   */
  private startConnectionCheck(): void {
    // 如果已经在检查连接，直接返回，避免重复启动
    if (this.connectionCheckInterval) {
      return;
    }

    console.log('[aria2Service] 开始连接检查');

    // 立即执行一次连接测试，不延迟
    this.testConnection();

    // 启动新的定时器，定期检查连接状态
    this.connectionCheckInterval = setInterval(async () => {
      await this.testConnection();
    }, this.connectionCheckDelay);
  }

  /**
   * 停止连接状态检查
   * 清理定时器，避免内存泄漏
   */
  private stopConnectionCheck(): void {
    if (this.connectionCheckInterval) {
      clearInterval(this.connectionCheckInterval);
      this.connectionCheckInterval = null;
      console.log('[aria2Service] 已停止连接检查');
    }
  }

  /**
   * 注册连接状态变化回调
   * @param callback 连接状态变化时调用的回调函数
   * @returns 取消注册的函数
   */
  onConnectionChange(callback: (connected: boolean) => void): () => void {
    this.connectionCallbacks.add(callback);
    // 立即通知当前连接状态
    callback(this.connected);
    return () => {
      this.connectionCallbacks.delete(callback);
    };
  }

  /**
   * 通知所有注册的回调函数连接状态变化
   * @param connected 新的连接状态
   */
  private notifyConnectionStatus(connected: boolean): void {
    console.log(`[aria2Service] notifyConnectionStatus(${connected}), 回调数量: ${this.connectionCallbacks.size}`);
    console.trace('[aria2Service] notifyConnectionStatus 调用栈');
    let index = 0;
    this.connectionCallbacks.forEach((callback) => {
      console.log(`[aria2Service] 调用回调 #${index}`);
      callback(connected);
      index++;
    });
    console.log('[aria2Service] 所有回调已调用');
  }

  /**
   * 检查是否已连接到Aria2
   * @returns 连接状态
   */
  isConnected(): boolean {
    return this.connected;
  }

  /**
   * 调用Aria2 JSON-RPC方法
   * 
   * 实现JSON-RPC 2.0协议规范
   * 如果配置了secret，会自动添加token认证
   * 
   * @param method RPC方法名
   * @param params 方法参数数组
   * @returns RPC调用结果
   * @throws 当Aria2未初始化或RPC调用失败时抛出错误
   */
  private async call(method: string, params: any[] = []): Promise<any> {
    if (!this.rpcUrl) {
      throw new Error('Aria2未初始化');
    }

    // 如果有secret，添加token到参数前面
    const finalParams = this.secret ? [`token:${this.secret}`, ...params] : params;

    const requestBody = {
      jsonrpc: '2.0',
      id: String(this.requestId++),
      method,
      params: finalParams,
    };

    try {
      const response = await fetch(this.rpcUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP错误: ${response.status} - ${errorText}`);
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(`RPC错误: ${data.error.message} (code: ${data.error.code})`);
      }

      return data.result;
    } catch (error) {
      // 减少日志输出，避免影响性能
      throw error;
    }
  }

  /**
   * 批量调用Aria2 JSON-RPC方法
   * 使用 system.multicall 在单次HTTP请求中执行多个RPC调用
   * 
   * @param calls 调用列表，每个包含 methodName 和 params
   * @returns 调用结果数组，每个结果包含 result 或 error
   * @throws 当Aria2未初始化或HTTP请求失败时抛出错误
   */
  private async callMulti(calls: Array<{ methodName: string, params: any[] }>): Promise<any[]> {
    if (!this.rpcUrl) {
      throw new Error('Aria2未初始化');
    }

    const requestBody = {
      jsonrpc: '2.0',
      id: String(this.requestId++),
      method: 'system.multicall',
      params: [calls],
    };

    try {
      const response = await fetch(this.rpcUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP错误: ${response.status} - ${errorText}`);
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(`RPC错误: ${data.error.message} (code: ${data.error.code})`);
      }

      // system.multicall 返回一个数组，每个元素是 [result] 或 {faultCode, faultString}
      const results = data.result;

      if (!Array.isArray(results)) {
        throw new Error('system.multicall 返回格式错误');
      }

      return results.map((item: any) => {
        if (Array.isArray(item)) {
          // 成功的调用返回 [result]
          return { result: item[0] };
        } else if (item.faultCode) {
          // 失败的调用返回 {faultCode, faultString}
          return { error: { code: item.faultCode, message: item.faultString } };
        } else {
          return { result: item };
        }
      });
    } catch (error) {
      // 减少日志输出
      throw error;
    }
  }

  /**
   * 添加下载任务
   * 
   * @param url 下载URL
   * @param options Aria2下载选项（如dir、out、header等）
   * @returns 任务GID（全局唯一标识符）
   * @throws 当Aria2未连接或添加失败时抛出错误
   * 
   * 需求 2.3: 确保正确处理Cookie头信息
   * 需求 2.4: 返回Aria2分配的GID
   */
  async addDownload(url: string, options: Record<string, any> = {}): Promise<string> {
    if (!this.connected) {
      const error = 'Aria2未连接，请确保Aria2服务正在运行';
      console.error(`[aria2Service] ✗ ${error}`);
      logger.error(`✗ ${error}`);
      throw new Error(error);
    }

    try {
      // 验证URL格式
      if (!url || typeof url !== 'string') {
        const error = `无效的URL: ${url}`;
        logger.error(`✗ ${error}`);
        throw new Error(error);
      }

      // 验证必要的选项
      if (!options.dir) {
        const error = '缺少下载目录 (dir)';
        logger.error(`✗ ${error}`);
        throw new Error(error);
      }

      if (!options.out) {
        const error = '缺少输出文件名 (out)';
        logger.error(`✗ ${error}`);
        throw new Error(error);
      }

      // 调用Aria2 RPC添加任务
      const gid = await this.call('aria2.addUri', [[url], options]);

      // 验证返回的GID（需求 2.4）
      if (!gid || typeof gid !== 'string') {
        const error = `Aria2返回了无效的GID: ${gid}`;
        // ERROR级别：错误情况
        logger.error(error);
        throw new Error(error);
      }

      // INFO级别：关键事件
      logger.info(`下载任务已添加: ${options.out}`);

      return gid;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);

      // ERROR级别：错误情况
      logger.error(`添加下载失败: ${options.out || url} - ${errorMsg}`);
      throw error;
    }
  }

  /**
   * 批量添加下载任务
   * 
   * @param urls 下载URL列表
   * @param optionsList 每个URL对应的选项列表（可选）
   * @returns 成功添加的任务GID列表
   */
  async addBatchDownloads(
    urls: string[],
    optionsList?: Record<string, string>[]
  ): Promise<string[]> {
    const gids: string[] = [];
    const options = optionsList || urls.map(() => ({}));

    for (let i = 0; i < urls.length; i++) {
      try {
        const gid = await this.addDownload(urls[i], options[i]);
        gids.push(gid);
      } catch (error) {
        console.error(`✗ 添加第${i + 1}个任务失败:`, error);
      }
    }

    return gids;
  }

  /**
   * 从配置文件批量添加下载任务
   * 解析配置文件并逐个添加任务，保持对每个任务的精确控制
   * 
   * 优势：
   * - 精确控制每个任务的添加过程
   * - 详细的错误报告和进度反馈
   * - 单个任务失败不影响其他任务
   * - 支持实时状态更新
   * 
   * @param configFilePath 配置文件路径
   * @returns 添加结果统计，包含任务信息用于跟踪
   */
  async addBatchFromConfig(configFilePath: string): Promise<{
    successCount: number,
    failCount: number,
    tasks: Array<{ workId: string, gid: string, filename: string, url: string }>
  }> {
    if (!this.connected) {
      throw new Error('Aria2未连接');
    }

    try {
      console.log(`[aria2Service] 开始读取配置文件: ${configFilePath}`);

      // 通过bridge调用后端API读取配置文件
      const configContent = await bridge.readConfigFile(configFilePath);
      console.log(`[aria2Service] 配置文件读取成功，内容长度: ${configContent.length}`);

      const lines = configContent.split('\n').filter(line => line.trim());
      console.log(`[aria2Service] 解析得到 ${lines.length} 行有效内容`);

      let successCount = 0;
      let failCount = 0;
      const tasks: Array<{ workId: string, gid: string, filename: string, url: string }> = [];
      const totalTasks = Math.floor(lines.length / 3);

      console.log(`[aria2Service] 开始批量添加 ${totalTasks} 个下载任务`);

      if (totalTasks === 0) {
        console.warn(`[aria2Service] 配置文件中没有找到有效的下载任务`);
        return { successCount: 0, failCount: 0, tasks: [] };
      }

      // 按3行一组解析（URL、dir、out）
      for (let i = 0; i < lines.length; i += 3) {
        if (i + 2 >= lines.length) break;

        const url = lines[i].trim();
        const dirLine = lines[i + 1].trim();
        const outLine = lines[i + 2].trim();

        console.log(`[aria2Service] 处理任务组 ${Math.floor(i / 3) + 1}:`);
        console.log(`  URL: ${url}`);
        console.log(`  Dir: ${dirLine}`);
        console.log(`  Out: ${outLine}`);

        // 验证格式 - 支持制表符或空格开头
        const dirMatch = dirLine.match(/^\s*dir=(.+)$/);
        const outMatch = outLine.match(/^\s*out=(.+)$/);

        if (!url || !dirMatch || !outMatch) {
          console.warn(`[aria2Service] 跳过格式错误的任务组 ${Math.floor(i / 3) + 1}`);
          console.warn(`  URL有效: ${!!url}, Dir匹配: ${!!dirMatch}, Out匹配: ${!!outMatch}`);
          failCount++;
          continue;
        }

        const dir = dirMatch[1]; // 提取dir值
        const out = outMatch[1]; // 提取out值

        console.log(`[aria2Service] 解析结果: dir="${dir}", out="${out}"`);

        try {
          const gid = await this.addDownload(url, {
            dir,
            out
          });

          // 生成workId用于跟踪
          const workId = `batch_${Math.floor(i / 3) + 1}_${Date.now()}`;

          tasks.push({
            workId,
            gid,
            filename: out,
            url
          });

          successCount++;
          console.log(`[aria2Service] 任务 ${Math.floor(i / 3) + 1} 添加成功，GID: ${gid}`);

          // 每10个任务输出一次进度
          if (successCount % 10 === 0) {
            console.log(`[aria2Service] 已添加 ${successCount}/${totalTasks} 个任务`);
          }
        } catch (error) {
          console.error(`[aria2Service] 添加任务失败: ${out}`, error);
          failCount++;
        }
      }

      console.log(`[aria2Service] 批量添加完成: 成功 ${successCount} 个，失败 ${failCount} 个`);
      return { successCount, failCount, tasks };

    } catch (error) {
      console.error('[aria2Service] 从配置文件批量添加失败:', error);
      console.error('[aria2Service] 错误详情:', {
        message: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
        configFilePath
      });
      throw error;
    }
  }

  /**
   * 获取下载任务状态
   * 
   * @param gid 任务GID
   * @returns 任务状态对象，失败时返回null
   */
  async getStatus(gid: string): Promise<DownloadTask | null> {
    if (!this.connected) {
      throw new Error('Aria2未连接');
    }

    try {
      const status = await this.call('aria2.tellStatus', [
        gid,
        [
          'gid',
          'status',
          'totalLength',
          'completedLength',
          'downloadSpeed',
          'uploadSpeed',
          'files',
          'errorCode',
          'errorMessage',
          'dir',
          'connections'
        ],
      ]);

      const totalLength = parseInt(status.totalLength) || 0;
      const completedLength = parseInt(status.completedLength) || 0;

      // 改进进度计算逻辑
      let progress = 0;
      if (totalLength > 0) {
        progress = (completedLength / totalLength) * 100;
      } else if (status.status === 'complete') {
        progress = 100;
      } else if (completedLength > 0) {
        // 如果有已下载数据但总长度为0，可能是流媒体或未知大小文件
        progress = 50; // 显示50%表示正在下载
      }

      // 提取文件名
      let filename = '未知文件';
      if (status.files && status.files.length > 0) {
        const path = status.files[0].path;
        filename = path.split(/[/\\]/).pop() || '未知文件';
      }

      return {
        gid: status.gid,
        status: status.status,
        totalLength,
        completedLength,
        downloadSpeed: parseInt(status.downloadSpeed) || 0,
        uploadSpeed: parseInt(status.uploadSpeed) || 0,
        progress: Math.round(progress * 10) / 10, // 保留1位小数
        files: status.files || [],
        errorCode: status.errorCode,
        errorMessage: status.errorMessage,
        filename,
        dir: status.dir || '',
        connections: parseInt(status.connections) || 0
      };
    } catch (error) {
      // 减少日志输出
      return null;
    }
  }

  /**
   * 批量获取任务状态
   * 使用单次RPC调用查询多个任务，提高查询效率
   * 
   * @param gids 任务GID列表
   * @returns GID到任务状态的映射表
   * 
   * 需求 3.2: 一次查询多个任务，减少RPC调用次数
   */
  async getBatchStatus(gids: string[]): Promise<Map<string, DownloadTask>> {
    const statusMap = new Map<string, DownloadTask>();

    if (!this.connected) {
      console.warn('[aria2Service] Aria2未连接，无法查询批量状态');
      return statusMap;
    }

    if (gids.length === 0) {
      return statusMap;
    }

    try {
      // 使用 system.multicall 进行批量RPC调用
      // 这样可以在一次HTTP请求中查询所有任务状态
      const multicallParams = gids.map(gid => ({
        methodName: 'aria2.tellStatus',
        params: this.secret
          ? [`token:${this.secret}`, gid, [
            'gid',
            'status',
            'totalLength',
            'completedLength',
            'downloadSpeed',
            'uploadSpeed',
            'files',
            'errorCode',
            'errorMessage',
          ]]
          : [gid, [
            'gid',
            'status',
            'totalLength',
            'completedLength',
            'downloadSpeed',
            'uploadSpeed',
            'files',
            'errorCode',
            'errorMessage',
          ]]
      }));

      // 调用批量RPC方法
      const results = await this.callMulti(multicallParams);

      // 处理每个结果
      results.forEach((result, index) => {
        const gid = gids[index];

        // 检查是否有错误
        if (result.error) {
          return;
        }

        // 解析状态数据
        const status = result.result;
        if (!status) {
          return;
        }

        const totalLength = parseInt(status.totalLength) || 0;
        const completedLength = parseInt(status.completedLength) || 0;

        // 计算进度
        let progress = 0;
        if (totalLength > 0) {
          progress = (completedLength / totalLength) * 100;
        } else if (status.status === 'complete') {
          progress = 100;
        } else if (completedLength > 0) {
          progress = 50; // 未知大小但有下载数据
        }

        const task: DownloadTask = {
          gid: status.gid,
          status: status.status,
          totalLength,
          completedLength,
          downloadSpeed: parseInt(status.downloadSpeed) || 0,
          uploadSpeed: parseInt(status.uploadSpeed) || 0,
          progress: Math.round(progress * 10) / 10,
          files: status.files || [],
          errorCode: status.errorCode,
          errorMessage: status.errorMessage,
        };

        statusMap.set(gid, task);
      });

    } catch (error) {
      // 如果批量查询失败，回退到逐个查询
      await Promise.all(
        gids.map(async (gid) => {
          try {
            const status = await this.getStatus(gid);
            if (status) {
              statusMap.set(gid, status);
            }
          } catch (err) {
            // 减少日志输出
          }
        })
      );
    }

    return statusMap;
  }

  /**
   * 暂停下载任务
   * 
   * @param gid 任务GID
   * @returns 操作是否成功
   */
  async pause(gid: string): Promise<boolean> {
    if (!this.connected) {
      throw new Error('Aria2未连接');
    }

    try {
      await this.call('aria2.pause', [gid]);
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * 恢复下载任务
   * 
   * @param gid 任务GID
   * @returns 操作是否成功
   */
  async resume(gid: string): Promise<boolean> {
    if (!this.connected) {
      throw new Error('Aria2未连接');
    }

    try {
      await this.call('aria2.unpause', [gid]);
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * 取消下载任务
   * 
   * @param gid 任务GID
   * @returns 操作是否成功
   */
  async cancel(gid: string): Promise<boolean> {
    if (!this.connected) {
      throw new Error('Aria2未连接');
    }

    try {
      await this.call('aria2.remove', [gid]);
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * 获取全局统计信息
   * 包括全局下载速度、活动任务数等
   * 
   * @returns 全局统计对象，失败时返回null
   */
  async getGlobalStat(): Promise<GlobalStat | null> {
    if (!this.connected) {
      throw new Error('Aria2未连接');
    }

    try {
      const stat = await this.call('aria2.getGlobalStat');
      return {
        downloadSpeed: parseInt(stat.downloadSpeed),
        uploadSpeed: parseInt(stat.uploadSpeed),
        numActive: parseInt(stat.numActive),
        numWaiting: parseInt(stat.numWaiting),
        numStopped: parseInt(stat.numStopped),
      };
    } catch (error) {
      return null;
    }
  }

  /**
   * 获取所有活动任务列表
   * 
   * @returns 活动任务列表
   */
  async getActiveTasks(): Promise<Aria2Task[]> {
    if (!this.connected) {
      throw new Error('Aria2未连接');
    }

    try {
      const tasks = await this.call('aria2.tellActive', [
        [
          'gid',
          'status',
          'totalLength',
          'completedLength',
          'downloadSpeed',
          'uploadSpeed',
          'files',
          'dir',
          'connections'
        ],
      ]);

      return tasks.map((task: any) => this.parseTask(task));
    } catch (error) {
      return [];
    }
  }

  /**
   * 获取等待任务列表
   * @returns 等待任务列表
   */
  async getWaitingTasks(): Promise<Aria2Task[]> {
    if (!this.connected) return [];

    try {
      const tasks = await this.call('aria2.tellWaiting', [0, 1000, [
        'gid',
        'status',
        'totalLength',
        'completedLength',
        'downloadSpeed',
        'uploadSpeed',
        'files',
        'dir',
        'connections'
      ]]);

      return tasks.map((task: any) => this.parseTask(task));
    } catch (error) {
      return [];
    }
  }

  /**
   * 获取已停止任务列表
   * @returns 已停止任务列表
   */
  async getStoppedTasks(): Promise<Aria2Task[]> {
    if (!this.connected) return [];

    try {
      const tasks = await this.call('aria2.tellStopped', [0, 1000, [
        'gid',
        'status',
        'totalLength',
        'completedLength',
        'downloadSpeed',
        'uploadSpeed',
        'files',
        'dir',
        'connections',
        'errorCode',
        'errorMessage'
      ]]);

      return tasks.map((task: any) => this.parseTask(task));
    } catch (error) {
      return [];
    }
  }

  /**
   * 移除已停止的任务
   * @param gid 任务GID
   * @returns 操作是否成功
   */
  async remove(gid: string): Promise<boolean> {
    if (!this.connected) {
      throw new Error('Aria2未连接');
    }

    try {
      await this.call('aria2.removeDownloadResult', [gid]);
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * 解析任务数据
   * @param task 原始任务数据
   * @returns 格式化的任务对象
   */
  private parseTask(task: any): Aria2Task {
    const totalLength = parseInt(task.totalLength) || 0;
    const completedLength = parseInt(task.completedLength) || 0;

    let progress = 0;
    if (totalLength > 0) {
      progress = (completedLength / totalLength) * 100;
    } else if (task.status === 'complete') {
      progress = 100;
    } else if (completedLength > 0) {
      progress = 50;
    }

    // 提取文件名
    let filename = '未知文件';
    if (task.files && task.files.length > 0) {
      const path = task.files[0].path;
      filename = path.split(/[/\\]/).pop() || '未知文件';
    }

    return {
      gid: task.gid,
      status: task.status,
      totalLength,
      completedLength,
      downloadSpeed: parseInt(task.downloadSpeed) || 0,
      uploadSpeed: parseInt(task.uploadSpeed) || 0,
      progress: Math.round(progress * 10) / 10,
      files: task.files || [],
      errorCode: task.errorCode,
      errorMessage: task.errorMessage,
      filename,
      dir: task.dir || '',
      connections: parseInt(task.connections) || 0
    };
  }

  /**
   * 暂停所有活动任务
   * 
   * @returns 操作是否成功
   */
  async pauseAll(): Promise<boolean> {
    if (!this.connected) {
      throw new Error('Aria2未连接');
    }

    try {
      await this.call('aria2.pauseAll');
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * 恢复所有暂停的任务
   * 
   * @returns 操作是否成功
   */
  async resumeAll(): Promise<boolean> {
    if (!this.connected) {
      throw new Error('Aria2未连接');
    }

    try {
      await this.call('aria2.unpauseAll');
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * 清理已完成的任务记录
   * 从Aria2内存中移除已完成/错误/已移除的任务
   * 
   * @returns 操作是否成功
   */
  async purgeDownloadResult(): Promise<boolean> {
    if (!this.connected) {
      throw new Error('Aria2未连接');
    }

    try {
      await this.call('aria2.purgeDownloadResult');
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * 更新Aria2全局配置
   * 用于即时应用配置更改，无需重启Aria2服务
   * 
   * @param options 要更新的配置项
   * @returns 操作是否成功
   */
  async updateGlobalOptions(options: Record<string, string>): Promise<boolean> {
    if (!this.connected) {
      throw new Error('Aria2未连接');
    }

    try {
      await this.call('aria2.changeGlobalOption', [options]);
      logger.success('✓ Aria2配置已即时更新');
      return true;
    } catch (error) {
      logger.warn('⚠ Aria2配置更新失败，将在下次启动时生效');
      console.error('Failed to update Aria2 global options:', error);
      return false;
    }
  }

  /**
   * 获取任务的详细信息，包括原始URL
   * @param gid 任务GID
   * @returns 任务详细信息，失败时返回null
   */
  async getTaskDetails(gid: string): Promise<{ files: Array<{ uris: Array<{ uri: string }> }> } | null> {
    if (!this.connected) {
      throw new Error('Aria2未连接');
    }

    try {
      const details = await this.call('aria2.tellStatus', [gid, ['files']]);
      return details;
    } catch (error) {
      console.error('获取任务详情失败:', error);
      return null;
    }
  }

  /**
   * 断开与Aria2的连接
   * 清理所有资源，避免内存泄漏
   */
  disconnect(): void {
    this.connected = false;
    this.stopConnectionCheck();  // 停止连接检查，清理定时器

    // 清理所有回调引用
    this.connectionCallbacks.clear();

    console.log('[aria2Service] 连接已关闭，资源已清理');
  }
}

// 导出单例实例
export const aria2Service = new Aria2Service();
