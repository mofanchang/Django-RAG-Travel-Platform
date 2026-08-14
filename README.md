**繁體中文**

## 專案簡介
Django-RAG-Travel-Platform 是一個結合 Django 後端與自製 RAG(Retrieval-Augmented Generation)語意搜尋的智慧旅遊電商平台。使用者可以透過 AI 聊天機器人輸入自然語言需求,系統即時推薦最符合的旅遊行程並完成線上訂購。

## 技術堆疊
Python · Django · PostgreSQL · React · Docker · Hugging Face

| 類別 | 技術選擇 |
|---|---|
| 頂層框架 | Django 4.2 + Gunicorn |
| 資料庫 | PostgreSQL |
| 前端 | React |
| 人工智慧/搜尋 | Sentence Transformer(text2vec-base-chinese) |
| 相似度計算 | 餘弦相似度 |
| 身份驗證 | django-allauth(密碼 + Google OAuth,session-based) |
| 金流 | PayPal Checkout Server SDK |
| 容器化 | Docker + Docker Compose |
| 靜態檔案 | WhiteNoise |

## 系統架構
```
Django-RAG-Travel-Platform/
├── accounts/           # 使用者認證（django-allauth，session-based + Google OAuth）
├── trips/               # 旅遊行程 CRUD 與搜尋，含 ETL 資料匯入管線
├── cart/                 # 購物車（資料庫模型 Cart / CartItem，非 session）
├── bookings/          # 訂單管理與狀態追蹤
├── chatbot/            # RAG 引擎（向量化 + 語意搜尋）
├── rag_service/     # 獨立 FastAPI 微服務，處理語意搜尋的向量運算
├── frontend/          # React 前端應用
└── docker-compose.yml  # 多容器編排
```

## RAG 設計
**為什麼選 RAG 而不直接用 LLM？**

本專案的推薦依托於平台自身資料庫中的旅遊產品,LLM 本身無法掌握這些私有資料。RAG 的做法是:

1. **預先向量化**:啟動時將所有行程資料編碼為向量索引
2. **語意搜尋**:收到使用者問題時,將問題向量化,利用餘弦相似度找出最相關的行程
3. **回應產生**:將搜尋結果格式化回傳,不依賴外部 LLM API(降低延遲與成本)

**模型選擇:** `shibing624/text2vec-base-chinese`(Hugging Face)——專為繁/簡體中文語意相似度優化、模型輕量(~400MB)、適合 CPU 推論不需 GPU、開源免費無 API 呼叫費用。

**服務拆分:** 語意搜尋獨立為 FastAPI 微服務,透過 HTTP 與主系統通訊,避免核心服務背負 `torch` 等大型 ML 套件依賴;資料匯入與索引重建交由 Celery + Redis 非同步排程處理,搭配任務狀態查詢 API。

## API 範例

**聊天/行程推薦**
```
POST /chatbot/chat/
Content-Type: application/json

Request:
{
  "message": "我想去東南亞，預算3萬，適合親子旅遊的行程"
}

Response:
{
  "reply": "根據您的需求，以下是推薦行程：",
  "recommended_trips": [
    {
      "id": 12,
      "name": "峇里島親子歡樂5日遊",
      "country": "印尼",
      "city": "峇里島",
      "duration": 5,
      "similarity_score": 0.923
    }
  ],
  "total": 1
}
```

**行程列表(REST API,含分頁,DRF)**
```
GET /trips/api/?page=1

Response:
{
  "count": 15,
  "next": "http://localhost:8000/trips/api/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "東京賞櫻 5 日遊",
      "country": "日本",
      "city": "東京",
      "duration": 5,
      "is_available": true
    }
  ]
}
```
完整 API 文件(Swagger)：`/api/docs/`

**使用者登入(Google OAuth 流程)**
```
GET /accounts/google/login/                # 導向 Google 同意頁面
GET /accounts/google/login/callback/  # OAuth callback，建立 session
```
登入狀態以 Django session(`sessionid` cookie)維持,不使用 JWT。另提供 `POST /user/api/login/` 供 API 測試工具(如 Postman)以 email/password 直接登入,同樣是設定 session cookie,不回傳 token。

## 技術挑戰與解決方案

**1. 中文語意精準度**
問題:使用者輸入的措詞與行程資料的關鍵字差異較大(例:「帶小孩」vs「親子」)
解法:採用中文語意相似度訓練的句子轉換模型,而非關鍵字比對,大幅提升召回率

**2. RAG 系統啟動時間**
問題:每次啟動都需要重新編碼所有行程資料
解法:向量索引以記憶體方式快取,透過 `python manage.py init_rag` 指令或容器啟動時觸發一次即可

**3. 容器 image 瘦身**
問題:`sentence-transformers`/`torch` 這類 ML 套件體積龐大,若跟 Django 主服務放在同一個 image,會拖慢每次 build 的時間
解法:將語意搜尋拆分為獨立的 `rag_service` FastAPI 微服務,web/celery_worker 不再需要安裝 ML 套件,image 大幅減重

## 快速開始(本地開發)
```bash
# 1. 複製環境設定
cp .env.example .env

# 2. 啟動容器
docker-compose up -d

# 3. 初始化資料庫與 RAG
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py init_rag

# 4. 建立管理員帳號
docker-compose exec web python manage.py createsuperuser
```

## 授權
MIT License。詳情請參閱 LICENSE 文件。

---

**English**

## Overview
Django-RAG-Travel-Platform is an intelligent travel e-commerce platform combining a Django backend with a custom RAG (Retrieval-Augmented Generation) semantic search engine. Users interact with an AI chatbot in natural language and receive relevant trip recommendations they can book online.

## Tech Stack

| Category | Technology |
|---|---|
| Backend | Django 4.2 + Gunicorn |
| Database | PostgreSQL |
| Frontend | React |
| AI / Vector Search | Sentence Transformer (text2vec-base-chinese) |
| Similarity | Cosine similarity |
| Auth | django-allauth (password + Google OAuth, session-based) |
| Payments | PayPal Checkout Server SDK |
| Containerization | Docker + Docker Compose |
| Static files | WhiteNoise |

## RAG Design
**Why RAG instead of calling an LLM directly?**

Recommendations are grounded in the platform's own private trip database, which a general-purpose LLM has no knowledge of. The pipeline:

1. **Pre-encoding**: all trip records are encoded into an in-memory vector index at startup
2. **Semantic search**: the user's query is vectorized and matched against the index via cosine similarity
3. **Response generation**: top-K results are formatted and returned — no external LLM API call needed, reducing both latency and cost

**Model choice:** `shibing624/text2vec-base-chinese` (Hugging Face) — optimized for Traditional/Simplified Chinese semantic similarity, lightweight (~400MB), runs on CPU without a GPU, open-source with no API cost.

**Service separation:** semantic search runs as an independent FastAPI microservice communicating over HTTP, so the core Django service doesn't carry heavy ML dependencies like `torch`. Data import and index rebuilding run asynchronously via Celery + Redis, with a task-status polling API.

## API Examples

**Chat / trip recommendation**
```
POST /chatbot/chat/
Content-Type: application/json

{ "message": "Family trip to Southeast Asia, budget around 30,000 TWD" }

→ Returns top-K trips under "recommended_trips", each with a similarity_score
```

**Trip list (REST API, paginated, DRF)**
```
GET /trips/api/?page=1

→ Returns a paginated {count, next, previous, results} response
```
Full API docs (Swagger): `/api/docs/`

**Login (Google OAuth flow)**
```
GET /accounts/google/login/
GET /accounts/google/login/callback/
```
Login state is maintained via a Django session (`sessionid` cookie) — no JWT is issued. A `POST /user/api/login/` endpoint is also available for API testing tools (e.g. Postman) via email/password, which likewise sets a session cookie rather than returning a token.

## Key Technical Challenges

| Challenge | Solution |
|---|---|
| Chinese semantic mismatch (e.g. "bring kids" vs "family-friendly") | Used a Chinese-tuned sentence transformer instead of keyword matching |
| RAG startup latency | Vector index cached in memory; built once via a management command or on container start |
| ML dependency bloat in the main image | Split semantic search into an independent FastAPI microservice so the main image doesn't carry `torch`/`sentence-transformers` |

## Quick Start
```bash
cp .env.example .env
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py init_rag
```

## License
MIT License. See LICENSE for details.

