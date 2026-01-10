# Stage 1: 构建前端
FROM node:20-alpine AS frontend-builder

# 接受构建参数
ARG VITE_API_BASE_URL=http://localhost:8000

# 设置为环境变量，Vite 在构建时可以访问
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

WORKDIR /app

# 复制源代码
COPY frontend/ ./

# 安装 pnpm 和依赖
RUN npm install -g pnpm && export CI='true' && pnpm install --frozen-lockfile

# 构建前端
RUN pnpm build

# Stage 2: Python 后端
FROM nikolaik/python-nodejs:python3.12-nodejs22-slim

WORKDIR /app

# 安装系统依赖
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#         libwebkit2gtk-4.1-dev \
#         libglib2.0-dev \
#         && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt ./

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制其余项目文件
COPY . .


# 从 stage 1 复制前端构建产物
COPY --from=frontend-builder /app/dist ./frontend/dist/

# 启动服务器
CMD ["python", "-m", "backend.server"]
