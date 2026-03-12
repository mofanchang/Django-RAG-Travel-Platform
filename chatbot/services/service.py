from chatbot.llm import query_rag_recommendations
from trips.models import Trip
import logging

logger = logging.getLogger(__name__)


def recommend_trips_with_rag(user_input, single_result=True):
    """
    使用 RAG 推薦旅遊產品 - 優化版本
    
    Args:
        user_input: 使用者查詢字串
        single_result: 是否只返回單一最佳結果
    
    Returns:
        QuerySet 或 list: 推薦的行程列表
    """
    try:
        if single_result:
            # 只搜尋一個最佳結果
            rag_results = query_rag_recommendations(user_input, top_k=1)
            
            if not rag_results:
                logger.warning("RAG 沒有找到匹配,返回預設行程")
                # 如果 RAG 沒結果,返回一個精選或最新的產品
                return Trip.objects.filter(is_active=True).order_by('-featured', '-created_at')[:1]
            
            # 獲取最佳匹配的產品
            best_result = rag_results[0]
            try:
                trip = Trip.objects.get(id=best_result['id'], is_active=True)
                trip.similarity_score = best_result['similarity_score']
                logger.info(
                    f"RAG 推薦: {trip.name} "
                    f"(相似度: {best_result['similarity_score']:.3f})"
                )
                return [trip]
            except Trip.DoesNotExist:
                logger.error(f"產品 ID {best_result['id']} 不存在或未啟用")
                return Trip.objects.filter(is_active=True).order_by('-featured')[:1]
        
        else:
            # 如果需要多個結果
            rag_results = query_rag_recommendations(user_input, top_k=5)
            
            if not rag_results:
                logger.warning("RAG 沒有找到匹配,返回預設行程列表")
                return Trip.objects.filter(is_active=True).order_by('-featured', '-created_at')[:5]
            
            # 根據 RAG 結果獲取 Django 物件
            trip_ids = [result['id'] for result in rag_results]
            trips = Trip.objects.filter(id__in=trip_ids, is_active=True)
            
            # 保持 RAG 的順序
            trip_dict = {trip.id: trip for trip in trips}
            ordered_trips = []
            for result in rag_results:
                if result['id'] in trip_dict:
                    trip = trip_dict[result['id']]
                    trip.similarity_score = result['similarity_score']
                    ordered_trips.append(trip)
            
            logger.info(f"RAG 推薦 {len(ordered_trips)} 個行程")
            return ordered_trips
        
    except Exception as e:
        logger.error(f"RAG 推薦錯誤: {e}", exc_info=True)
        # 出錯時返回預設推薦
        if single_result:
            return Trip.objects.filter(is_active=True).order_by('-featured')[:1]
        else:
            return Trip.objects.filter(is_active=True).order_by('-featured')[:5]


def get_single_best_recommendation(user_input):
    """
    專門用來獲取單一最佳推薦的方法
    
    Args:
        user_input: 使用者查詢字串
    
    Returns:
        Trip 或 None: 最佳推薦的行程
    """
    results = recommend_trips_with_rag(user_input, single_result=True)
    return results[0] if results else None


def get_recommendation_with_fallback(user_input, similarity_threshold=0.7):
    """
    帶有退避機制的推薦方法
    
    Args:
        user_input: 使用者查詢字串
        similarity_threshold: 相似度閾值
    
    Returns:
        Trip 或 None: 推薦的行程
    """
    try:
        # 先嘗試 RAG
        rag_results = query_rag_recommendations(user_input, top_k=1)
        
        if rag_results and rag_results[0]['similarity_score'] >= similarity_threshold:
            # 高品質匹配
            try:
                trip = Trip.objects.get(id=rag_results[0]['id'], is_active=True)
                trip.similarity_score = rag_results[0]['similarity_score']
                trip.match_type = "RAG_HIGH_QUALITY"
                logger.info(
                    f"高品質匹配: {trip.name} "
                    f"(相似度: {trip.similarity_score:.3f})"
                )
                return trip
            except Trip.DoesNotExist:
                logger.warning(f"高品質匹配的行程 {rag_results[0]['id']} 不存在")
        
        elif rag_results and rag_results[0]['similarity_score'] >= 0.5:
            # 中等品質匹配
            try:
                trip = Trip.objects.get(id=rag_results[0]['id'], is_active=True)
                trip.similarity_score = rag_results[0]['similarity_score']
                trip.match_type = "RAG_MEDIUM_QUALITY"
                logger.info(
                    f"中等品質匹配: {trip.name} "
                    f"(相似度: {trip.similarity_score:.3f})"
                )
                return trip
            except Trip.DoesNotExist:
                logger.warning(f"中等品質匹配的行程 {rag_results[0]['id']} 不存在")
        
        # 沒有好的 RAG 結果,回傳熱門產品
        popular_trip = Trip.objects.filter(is_active=True).order_by('-featured').first()
        if popular_trip:
            popular_trip.similarity_score = 0.0
            popular_trip.match_type = "FALLBACK_POPULAR"
            logger.info(f"使用退避機制推薦: {popular_trip.name}")
        
        return popular_trip
        
    except Exception as e:
        logger.error(f"推薦錯誤: {e}", exc_info=True)
        return None
