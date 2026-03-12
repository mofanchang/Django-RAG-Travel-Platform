#!/bin/bash
# 資料庫遷移腳本

echo "開始資料庫遷移..."

# 1. 建立遷移檔案
python manage.py makemigrations

# 2. 執行遷移
python manage.py migrate

# 3. 建立超級使用者（如果需要）
echo "是否要建立超級使用者？(y/n)"
read create_superuser

if [ "$create_superuser" = "y" ]; then
    python manage.py createsuperuser
fi

echo "遷移完成！"
