# -*- encoding: utf-8 -*-
"""
业务逻辑模块

包含应用的核心业务逻辑和通用服务。

模块结构：
- douyin/: 抖音爬虫模块（核心业务）
  - crawler.py: 爬虫主类，协调各模块完成数据采集
  - client.py: API客户端，封装抖音API调用
  - parser.py: 数据解析器，解析API返回的数据
  - target.py: 目标处理器，识别和解析用户输入
  - types.py: 类型定义和常量（作品类型、API端点、请求参数等）
  - request.py: HTTP请求封装，处理签名和Cookie
  - js/: JavaScript脚本（签名生成）
- cookies.py: Cookie管理和验证
- download.py: 文件下载管理（aria2配置生成）
- aria2_manager.py: Aria2进程管理和配置生成

使用示例：
    from backend.lib.douyin import Douyin

    douyin = Douyin(target="https://www.douyin.com/user/xxx", limit=10)
    douyin.run()
"""

# 向后兼容：保持原有的导入方式
from .douyin import Douyin

__all__ = ["Douyin"]
