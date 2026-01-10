/**
 * SSE 客户端 - 接收后端的 evaluate_js 调用
 *
 * 在 HTTP 模式下，后端通过 SSE 向前端推送 JavaScript 代码执行请求。
 * 这些代码会调用 window.__kiro_douyin.taskCallback，触发前端的回调机制。
 */

class SSEClient {
  private eventSource: EventSource | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000; // 2秒后重连

  /**
   * 连接到 SSE 端点
   * @param url SSE 端点 URL
   */
  connect(url: string): void {
    if (this.eventSource?.readyState === EventSource.OPEN) {
      console.warn('[SSE] 已连接，忽略重复连接');
      return;
    }

    console.log('[SSE] 正在连接...', url);
    this.eventSource = new EventSource(url);

    this.eventSource.onopen = () => {
      console.log('[SSE] ✓ 连接成功');
      this.reconnectAttempts = 0; // 重置重连计数
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer);
        this.reconnectTimer = null;
      }
    };

    this.eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'evaluate_js' && data.code) {
          const codePreview = data.code.substring(0, 80);
          console.log('[SSE] 收到 evaluate_js:', codePreview + '...');
          // 执行后端发送的 JS 代码
          // 这些代码会调用 window.__kiro_douyin.taskCallback
          eval(data.code);
        }
      } catch (error) {
        console.error('[SSE] 消息处理失败:', error);
      }
    };

    this.eventSource.onerror = (error) => {
      console.error('[SSE] 连接错误:', error);

      // EventSource 会自动重连，但我们可以添加额外逻辑
      if (this.eventSource?.readyState === EventSource.CLOSED) {
        console.log('[SSE] 连接已关闭');
        this.handleReconnect(url);
      }
    };
  }

  /**
   * 处理重连逻辑
   */
  private handleReconnect(url: string): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[SSE] 达到最大重连次数，放弃重连');
      return;
    }

    this.reconnectAttempts++;
    console.log(`[SSE] ${this.reconnectDelay / 1000}秒后尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

    this.reconnectTimer = setTimeout(() => {
      if (this.eventSource?.readyState === EventSource.CLOSED) {
        console.log('[SSE] 重新连接...');
        this.connect(url);
      }
    }, this.reconnectDelay);
  }

  /**
   * 断开 SSE 连接
   */
  disconnect(): void {
    if (this.eventSource) {
      console.log('[SSE] 断开连接');
      this.eventSource.close();
      this.eventSource = null;
    }
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.reconnectAttempts = 0;
  }

  /**
   * 检查是否已连接
   */
  isConnected(): boolean {
    return this.eventSource?.readyState === EventSource.OPEN;
  }
}

// 导出单例
export const sseClient = new SSEClient();
