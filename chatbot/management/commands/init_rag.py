from django.core.management.base import BaseCommand
from chatbot.llm import initialize_rag_from_db


class Command(BaseCommand):
    help = '初始化或重建 RAG 向量索引'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('開始初始化 RAG 系統...'))
        
        success = initialize_rag_from_db()
        
        if success:
            self.stdout.write(
                self.style.SUCCESS(' RAG 系統初始化成功！')
            )
        else:
            self.stdout.write(
                self.style.ERROR(' RAG 系統初始化失敗')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS('RAG 向量索引已建立完成，可以開始使用聊天功能了！')
        )
