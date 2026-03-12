from sentence_transformers import SentenceTransformer
import numpy as np
import json
import logging
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class SimpleRAG:
    def __init__(self):
        """初始化 RAG 系統"""
        try:
            # 使用輕量級的中文向量模型
            logger.info("正在載入向量模型...")
            self.model = SentenceTransformer('shibing624/text2vec-base-chinese')
            logger.info("向量模型載入成功")
            self.trip_embeddings = None
            self.trips_data = None
        except Exception as e:
            logger.error(f"向量模型載入失敗: {e}", exc_info=True)
            raise
    
    def build_trip_database(self, trips):
        """建立旅遊產品向量資料庫"""
        try:
            trip_texts = []
            self.trips_data = []   
            
            for trip in trips:
                # 建立產品描述文本
                text = f"{trip.name} {trip.country} {trip.city} {trip.keywords} {trip.description}"
                trip_texts.append(text)
                
                # 儲存產品資料
                self.trips_data.append({
                    'id': trip.id,
                    'name': trip.name,
                    'country': trip.country,
                    'city': trip.city,
                    'duration': trip.duration,
                    'keywords': trip.keywords,
                    'description': trip.description
                })
            
            if not trip_texts:
                logger.warning("沒有可用的行程資料")
                return
            
            # 生成向量
            logger.info(f"正在生成 {len(trip_texts)} 個行程的向量...")
            self.trip_embeddings = self.model.encode(trip_texts)
            logger.info(f"向量資料庫建立完成，共 {len(trip_texts)} 個產品")
            
        except Exception as e:
            logger.error(f"建立向量資料庫失敗: {e}", exc_info=True)
            raise
    
    def search_similar_trips(self, query, top_k=1):
        """搜尋相似的旅遊產品"""
        try:
            if self.trip_embeddings is None:
                logger.warning("向量資料庫尚未建立")
                return []
            
            # 將查詢轉換為向量
            logger.debug(f"搜尋查詢: {query}")
            query_embedding = self.model.encode([query])
            
            # 計算相似度
            similarities = cosine_similarity(query_embedding, self.trip_embeddings)[0]
            
            # 取得最相似的產品
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                trip_data = self.trips_data[idx].copy()
                trip_data['similarity_score'] = float(similarities[idx])
                results.append(trip_data)
                logger.debug(
                    f"找到匹配: {trip_data['name']} "
                    f"(相似度: {trip_data['similarity_score']:.3f})"
                )
            
            return results
            
        except Exception as e:
            logger.error(f"搜尋相似產品失敗: {e}", exc_info=True)
            return []


# 全域 RAG 實例
rag_instance = SimpleRAG()


def initialize_rag_from_db():
    """從資料庫初始化 RAG"""
    from trips.models import Trip
    
    try:
        logger.info("開始初始化 RAG 系統...")
        trips = Trip.objects.filter(is_active=True)
        
        if not trips.exists():
            logger.warning("資料庫中沒有啟用的行程資料")
            return False
        
        rag_instance.build_trip_database(trips)
        logger.info(f"RAG 系統初始化成功，載入 {trips.count()} 筆行程資料")
        return True
        
    except Exception as e:
        logger.error(f"RAG 初始化失敗: {e}", exc_info=True)
        return False


def query_rag_recommendations(user_input, top_k=5):
    """使用 RAG 獲取推薦"""
    try:
        # 如果還沒初始化，先初始化
        if rag_instance.trip_embeddings is None:
            logger.info("RAG 尚未初始化，開始初始化...")
            if not initialize_rag_from_db():
                logger.error("RAG 初始化失敗，無法提供推薦")
                return []
        
        # 搜尋相似產品
        results = rag_instance.search_similar_trips(user_input, top_k)
        
        if results:
            logger.info(f"RAG 搜尋成功，找到 {len(results)} 個推薦")
            for result in results:
                logger.debug(
                    f"推薦: {result['name']} "
                    f"(相似度: {result['similarity_score']:.3f})"
                )
        else:
            logger.warning("RAG 搜尋沒有找到匹配結果")
        
        return results
        
    except Exception as e:
        logger.error(f"RAG 查詢錯誤: {e}", exc_info=True)
        return []
