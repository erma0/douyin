# 回调管理器使用说明

## 概述

`callbackManager` 提供了安全的全局回调函数管理机制，解决了以下问题：

1. **避免命名冲突**：使用 `window.__kiro_douyin` 命名空间，而不是直接在 window 上挂载
2. **防止意外覆盖**：通过单例模式管理回调函数
3. **内存泄漏防护**：提供清理函数，确保回调能被正确释放

## 使用方法

### 基本用法

```typescript
import { registerTaskCallback, unregisterTaskCallback } from './utils/callbackManager';

// 注册回调
const cleanup = registerTaskCallback((message) => {
  if (message.type === 'result') {
    console.log('收到结果:', message.data);
  } else if (message.type === 'complete') {
    console.log('任务完成');
  } else if (message.type === 'error') {
    console.error('任务失败:', message.error);
  }
});

// 使用完毕后清理
cleanup();
```

### 在 React 组件中使用

```typescript
import { useEffect } from 'react';
import { registerTaskCallback } from './utils/callbackManager';

function MyComponent() {
  useEffect(() => {
    // 注册回调
    const cleanup = registerTaskCallback((message) => {
      // 处理消息
    });

    // 组件卸载时自动清理
    return cleanup;
  }, []);

  return <div>...</div>;
}
```

## 后端调用

后端通过 `window.evaluate_js` 调用前端回调：

```python
# Python 后端代码
js_code = f"window.__kiro_douyin && window.__kiro_douyin.taskCallback && window.__kiro_douyin.taskCallback({json_data})"
window.evaluate_js(js_code)
```

## 消息格式

### 结果消息
```typescript
{
  type: 'result',
  data: [...],  // 采集到的数据
  total: 100    // 累计数量
}
```

### 完成消息
```typescript
{
  type: 'complete',
  total: 100,
  detected_type: 'post'
}
```

### 错误消息
```typescript
{
  type: 'error',
  error: '错误信息'
}
```

## 注意事项

1. **必须在调用后端 API 前注册回调**
2. **使用完毕后务必调用清理函数**，避免内存泄漏
3. **不要在回调函数中执行耗时操作**，会阻塞 UI
4. **回调函数应该是纯函数**，避免副作用
