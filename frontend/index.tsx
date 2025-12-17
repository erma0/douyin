import React from "react";
import ReactDOM from "react-dom/client";
import { App } from "./App";
import "./index.css";

// 性能监控：记录启动时间
const perfStart = performance.now();
console.log("[Perf] React 启动开始...");

// 检查 pywebview 对象
if (window.pywebview) {
  console.log(`[Perf] pywebview 对象已存在 (${(performance.now() - perfStart).toFixed(2)}ms)`);
  if (window.pywebview.api) {
    console.log(`[Perf] pywebview.api 已注入 (${(performance.now() - perfStart).toFixed(2)}ms)`);
  } else {
    console.log(`[Perf] pywebview.api 尚未注入 (${(performance.now() - perfStart).toFixed(2)}ms)`);
  }
} else {
  console.log(`[Perf] pywebview 对象尚未创建 (${(performance.now() - perfStart).toFixed(2)}ms)`);
}

const rootElement = document.getElementById("root");
if (!rootElement) {
  console.error("Could not find root element to mount to");
  throw new Error("Could not find root element to mount to");
}

console.log(`[Perf] 找到根元素 (${(performance.now() - perfStart).toFixed(2)}ms)`);

const root = ReactDOM.createRoot(rootElement);

console.log(`[Perf] 创建 Root (${(performance.now() - perfStart).toFixed(2)}ms)`);

// Add error boundaries around the app to catch any errors
interface ErrorBoundaryProps {
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error('React Error:', error);
    console.error('Error Info:', errorInfo);
  }

  render(): React.ReactNode {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', color: 'red', backgroundColor: '#f0f0f0' }}>
          <h1>应用发生错误</h1>
          <pre>{this.state.error?.toString()}</pre>
          <button onClick={() => this.setState({ hasError: false, error: null })}>
            重试
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

root.render(
  <ErrorBoundary>
    <App />
  </ErrorBoundary>
);

console.log(`[Perf] App 渲染完成 (${(performance.now() - perfStart).toFixed(2)}ms)`);

// 监听 DOMContentLoaded 和 load 事件
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    console.log(`[Perf] DOMContentLoaded (${(performance.now() - perfStart).toFixed(2)}ms)`);
  });
}

window.addEventListener('load', () => {
  console.log(`[Perf] Window Load 完成 (${(performance.now() - perfStart).toFixed(2)}ms)`);
});
