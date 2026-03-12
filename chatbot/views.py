from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import json
import logging
from .services.service import recommend_trips_with_rag

logger = logging.getLogger(__name__)


def _generate_reply(user_input, trips):
    """根據使用者輸入和推薦行程產生對話回應"""
    user_input_lower = user_input.lower()

    # 問候語
    greetings = ['你好', '嗨', 'hi', 'hello', '哈囉', '早安', '午安', '晚安']
    if any(g in user_input_lower for g in greetings):
        return "你好！我是旅遊助理,可以幫你推薦適合的行程。請問你想去哪裡旅遊,或是有什麼旅遊需求呢？"

    # 詢問功能
    if any(k in user_input for k in ['你可以', '你能', '你會', '怎麼用', '功能']):
        return "我可以幫你根據目的地、活動類型或旅遊偏好推薦行程！你可以問我像是「我想去日本」、「推薦海島行程」、「三天的韓國之旅」等等。"

    # 有推薦結果時
    if trips:
        trip = trips[0]
        country = trip.country
        city = trip.city
        name = trip.name

        if any(k in user_input for k in ['推薦', '建議', '幫我找', '有什麼']):
            return f"根據你的需求,我推薦「{name}」！這是一個位於{country}{city}的精彩行程,非常適合你。"

        if any(k in user_input for k in ['日本', '東京', '大阪', '京都', '沖繩', '北海道', '神戶']):
            return f"日本是個很棒的選擇！我幫你找到「{name}」,讓你深度體驗{city}的魅力。"

        if any(k in user_input for k in ['韓國', '首爾', '釜山', '濟州', '仁川']):
            return f"韓國旅遊超熱門！推薦你「{name}」,{city}有豐富的美食和文化等你探索。"

        if any(k in user_input for k in ['台灣', '台北', '高雄', '台中', '花蓮', '墾丁']):
            return f"台灣寶島不容錯過！推薦「{name}」,{city}有讓人難忘的自然與人文風景。"

        if any(k in user_input for k in ['海島', '海灘', '潛水', '沙灘', '度假']):
            return f"想放鬆度假嗎？「{name}」非常適合你,享受陽光與海洋的完美假期！"

        if any(k in user_input for k in ['美食', '吃', '料理', '小吃']):
            return f"美食之旅聽起來很棒！推薦「{name}」,{city}有各種令人垂涎的在地美味。"

        if any(k in user_input for k in ['文化', '歷史', '古蹟', '博物館', '傳統']):
            return f"喜歡文化探索？「{name}」讓你深入了解{country}的歷史與傳統文化。"

        if any(k in user_input for k in ['自然', '山', '健行', '爬山', '生態']):
            return f"喜歡親近大自然？推薦「{name}」,在{city}感受壯闊的自然景觀。"

        # 通用回應
        return f"我幫你找到「{name}」,這是一個位於{country}{city}的熱門行程,相信你會喜歡！"

    # 沒有推薦結果
    return "抱歉,目前沒有找到完全符合的行程。你可以試試其他關鍵字,例如目的地名稱或活動類型！"


def _check_rate_limit(request):
    """簡單的速率限制檢查"""
    ip = request.META.get('REMOTE_ADDR', '')
    cache_key = f'chat_rate_limit_{ip}'
    
    # 檢查快取中的請求次數
    request_count = cache.get(cache_key, 0)
    
    # 每分鐘最多 10 次請求
    if request_count >= 10:
        return False, "請求過於頻繁,請稍後再試"
    
    # 增加計數
    cache.set(cache_key, request_count + 1, 60)  # 60 秒過期
    return True, None


@csrf_exempt
def chat_api(request):
    """聊天 API"""
    if request.method != "POST":
        return JsonResponse({"error": "只允許 POST 請求"}, status=405)

    try:
        # 速率限制檢查
        is_allowed, error_msg = _check_rate_limit(request)
        if not is_allowed:
            logger.warning(f"速率限制觸發: {request.META.get('REMOTE_ADDR')}")
            return JsonResponse({"error": error_msg}, status=429)
        
        # 解析請求
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            logger.error("無法解析 JSON 請求")
            return JsonResponse({"error": "無效的 JSON 格式"}, status=400)
        
        user_input = body.get("message", "").strip()

        if not user_input:
            return JsonResponse({"error": "請輸入查詢內容"}, status=400)
        
        if len(user_input) > 200:
            return JsonResponse({"error": "查詢內容過長,請限制在 200 字以內"}, status=400)

        logger.info(f"收到聊天請求: {user_input}")

        # RAG 推薦
        trips = recommend_trips_with_rag(user_input)

        # 格式化行程資料
        trip_list = []
        for trip in trips:
            trip_data = {
                "id": trip.id,
                "name": trip.name,
                "description": trip.description,
                "country": trip.country,
                "city": trip.city,
                "duration": trip.duration,
                "keywords": trip.keywords,
                "link": f"/trips/{trip.id}/"
            }
            if hasattr(trip, 'similarity_score'):
                trip_data["similarity_score"] = round(trip.similarity_score, 3)
            trip_list.append(trip_data)

        # 產生自然語言回應
        reply = _generate_reply(user_input, trips)
        
        logger.info(f"成功回應,推薦 {len(trip_list)} 個行程")

        return JsonResponse({
            "reply": reply,
            "recommended_trips": trip_list,
            "total": len(trip_list),
        })

    except Exception as e:
        logger.error(f"聊天 API 錯誤: {e}", exc_info=True)
        return JsonResponse({
            "error": "系統錯誤,請稍後再試",
            "detail": str(e) if request.user.is_staff else None
        }, status=500)


from django.contrib.auth.decorators import user_passes_test

@csrf_exempt
@user_passes_test(lambda u: u.is_superuser)
def rebuild_rag_index(request):
    """重建 RAG 索引的 API（管理員用）"""
    if request.method != "POST":
        return JsonResponse({"error": "只允許 POST 請求"}, status=405)

    # 簡單的權限檢查
    if not request.user.is_authenticated or not request.user.is_staff:
        logger.warning(f"未授權的 RAG 重建請求: {request.META.get('REMOTE_ADDR')}")
        return JsonResponse({"error": "需要管理員權限"}, status=403)

    try:
        from .llm import initialize_rag_from_db
        logger.info(f"管理員 {request.user.email} 請求重建 RAG 索引")
        
        success = initialize_rag_from_db()
        
        if success:
            logger.info("RAG 索引重建成功")
            return JsonResponse({"message": "RAG 索引重建成功"})
        else:
            logger.error("RAG 索引重建失敗")
            return JsonResponse({"error": "RAG 索引重建失敗"}, status=500)
            
    except Exception as e:
        logger.error(f"RAG 重建錯誤: {e}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)
