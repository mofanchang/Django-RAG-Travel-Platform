FROM python:3.10-slim

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 安裝套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式代碼
COPY . .

# 暴露埠號
EXPOSE 8000

# 啟動命令
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]