#!/bin/bash
# 快速啟動開發環境腳本

echo "================================"
echo "TRAVELTRIP_PROJECT 快速啟動"
echo "================================"
echo ""

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "  未找到虛擬環境，正在建立..."
    python3 -m venv venv
    echo " 虛擬環境建立完成"
fi

# 啟動虛擬環境
echo "啟動虛擬環境..."
source venv/bin/activate

# 檢查 .env 檔案
if [ ! -f ".env" ]; then
    echo "  未找到 .env 檔案"
    echo "正在從 .env.example 複製..."
    cp .env.example .env
    echo " 請編輯 .env 檔案並設定必要的環境變數"
    exit 1
fi

# 安裝依賴
echo ""
echo "檢查並安裝依賴套件..."
pip install -q -r requirements-basic.txt
pip install -q -r requirements-ml.txt
echo " 依賴套件已安裝"

# 執行資料庫遷移
echo ""
echo "執行資料庫遷移..."
python manage.py migrate --noinput
echo " 資料庫遷移完成"

# 初始化 RAG
echo ""
echo "初始化 RAG 系統..."
python manage.py init_rag
echo " RAG 系統已初始化"

# 收集靜態檔案
echo ""
echo "收集靜態檔案..."
python manage.py collectstatic --noinput
echo " 靜態檔案已收集"

# 系統健康檢查
echo ""
echo "執行系統健康檢查..."
python scripts/health_check.py

# 啟動伺服器
echo ""
echo "================================"
echo "準備啟動開發伺服器..."
echo "================================"
echo ""
echo "Django 後端: http://localhost:8000"
echo "Django Admin: http://localhost:8000/admin"
echo ""
echo "按 Ctrl+C 停止伺服器"
echo ""

python manage.py runserver
