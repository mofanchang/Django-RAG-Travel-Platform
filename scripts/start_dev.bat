@echo off
REM 快速啟動開發環境腳本 (Windows)

echo ================================
echo TRAVELTRIP_PROJECT 快速啟動
echo ================================
echo.

REM 檢查虛擬環境
if not exist "venv\" (
    echo 未找到虛擬環境，正在建立...
    python -m venv venv
    echo 虛擬環境建立完成
)

REM 啟動虛擬環境
echo 啟動虛擬環境...
call venv\Scripts\activate.bat

REM 檢查 .env 檔案
if not exist ".env" (
    echo 未找到 .env 檔案
    echo 正在從 .env.example 複製...
    copy .env.example .env
    echo 請編輯 .env 檔案並設定必要的環境變數
    pause
    exit /b 1
)

REM 安裝依賴
echo.
echo 檢查並安裝依賴套件...
pip install -q -r requirements-basic.txt
pip install -q -r requirements-ml.txt
echo 依賴套件已安裝

REM 執行資料庫遷移
echo.
echo 執行資料庫遷移...
python manage.py migrate --noinput
echo 資料庫遷移完成

REM 初始化 RAG
echo.
echo 初始化 RAG 系統...
python manage.py init_rag
echo RAG 系統已初始化

REM 收集靜態檔案
echo.
echo 收集靜態檔案...
python manage.py collectstatic --noinput
echo 靜態檔案已收集

REM 系統健康檢查
echo.
echo 執行系統健康檢查...
python scripts\health_check.py

REM 啟動伺服器
echo.
echo ================================
echo 準備啟動開發伺服器...
echo ================================
echo.
echo Django 後端: http://localhost:8000
echo Django Admin: http://localhost:8000/admin
echo.
echo 按 Ctrl+C 停止伺服器
echo.

python manage.py runserver
