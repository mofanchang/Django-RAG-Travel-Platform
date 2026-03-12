#!/usr/bin/env python
"""
系統健康檢查腳本
用於檢查各項服務和配置是否正常
"""

import os
import sys

# 將專案根目錄加入 Python 路徑
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import django

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TRAVELTRIP_PROJECT.settings')
django.setup()

from django.conf import settings
from django.db import connection
from django.core.management import call_command


def check_database():
    """檢查資料庫連接"""
    try:
        connection.ensure_connection()
        print(" 資料庫連接正常")
        return True
    except Exception as e:
        print(f" 資料庫連接失敗: {e}")
        return False


def check_static_files():
    """檢查靜態檔案配置"""
    static_root = settings.STATIC_ROOT
    if os.path.exists(static_root):
        print(f" 靜態檔案目錄存在: {static_root}")
        return True
    else:
        print(f" 靜態檔案目錄不存在: {static_root}")
        print("  提示: 執行 python manage.py collectstatic")
        return False


def check_media_files():
    """檢查媒體檔案配置"""
    media_root = settings.MEDIA_ROOT
    if os.path.exists(media_root):
        print(f" 媒體檔案目錄存在: {media_root}")
        return True
    else:
        print(f" 媒體檔案目錄不存在: {media_root}")
        return False


def check_logs_directory():
    """檢查日誌目錄"""
    logs_dir = settings.BASE_DIR / 'logs'
    if os.path.exists(logs_dir):
        print(f" 日誌目錄存在: {logs_dir}")
        return True
    else:
        print(f" 日誌目錄不存在: {logs_dir}")
        try:
            os.makedirs(logs_dir)
            print(f"  已自動建立日誌目錄")
            return True
        except:
            return False


def check_environment_variables():
    """檢查必要的環境變數"""
    required_vars = [
        'SECRET_KEY',
        'DB_NAME',
        'DB_USER',
        'DB_PASS',
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f" 缺少環境變數: {', '.join(missing)}")
        return False
    else:
        print(" 所有必要環境變數已設定")
        return True


def check_rag_system():
    """檢查 RAG 系統"""
    try:
        from chatbot.llm import rag_instance
        if rag_instance.trip_embeddings is not None:
            print(" RAG 系統已初始化")
            return True
        else:
            print(" RAG 系統尚未初始化")
            print("  提示: 執行 python manage.py init_rag")
            return False
    except Exception as e:
        print(f" RAG 系統檢查失敗: {e}")
        return False


def check_migrations():
    """檢查是否有未執行的遷移"""
    try:
        from io import StringIO
        from django.core.management import call_command
        
        out = StringIO()
        call_command('showmigrations', '--plan', stdout=out)
        output = out.getvalue()
        
        if '[X]' in output or '[ ]' in output:
            unapplied = output.count('[ ]')
            if unapplied > 0:
                print(f" 有 {unapplied} 個未執行的遷移")
                print("  提示: 執行 python manage.py migrate")
                return False
            else:
                print(" 所有遷移已執行")
                return True
        return True
    except Exception as e:
        print(f" 無法檢查遷移狀態: {e}")
        return True


def main():
    """主函數"""
    print("=" * 50)
    print("TRAVELTRIP_PROJECT 系統健康檢查")
    print("=" * 50)
    print()
    
    checks = [
        ("環境變數", check_environment_variables),
        ("資料庫連接", check_database),
        ("資料庫遷移", check_migrations),
        ("靜態檔案", check_static_files),
        ("媒體檔案", check_media_files),
        ("日誌目錄", check_logs_directory),
        ("RAG 系統", check_rag_system),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n檢查 {name}...")
        results.append(check_func())
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"檢查完成: {passed}/{total} 項通過")
    print("=" * 50)
    
    if passed == total:
        print("\n 系統狀態良好！")
        return 0
    else:
        print("\n  部分檢查未通過，請查看上方詳細資訊")
        return 1


if __name__ == "__main__":
    sys.exit(main())
