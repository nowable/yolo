# 构建阶段
FROM python:3.9-slim-bookworm AS builder

# 安装编译依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev libffi-dev libjpeg-dev libpng-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

# 用阿里源安装依赖（更稳定）
RUN pip install --user --no-cache-dir -r requirements.txt \
    -i https://mirrors.aliyun.com/pypi/simple/

# 运行阶段
FROM python:3.9-slim-bookworm

# 安装运行时必需的系统库（YOLO 依赖）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo libpng16-16 libgl1 libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app
# 复制构建好的依赖
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

COPY . .
RUN mkdir -p uploads

EXPOSE 5000
CMD ["python", "app.py"]
